"""
Lógica del monitor: actualizar desde el portal, detectar cambios y salidas,
y armar las vistas (órdenes, indicadores, historial, completadas).
"""
import csv
import io
import threading
from datetime import date, datetime, time, timedelta, timezone
from typing import Callable, Dict, List, Optional
from zoneinfo import ZoneInfo

from sqlalchemy import delete, insert, update

from app.modules.open_orders import config, rules
from app.modules.open_orders.models import closed_orders, events, orders, runs
from app.modules.open_orders.parser import PortalResponseError, parse_table
from app.modules.open_orders.store import Store

_lock = threading.Lock()

CAMPOS_ORDEN = ["row_number", "dv", "pick_ticket", "stg", "po", "ship_to", "ship_date", "cancel_date",
                "cust", "wh", "rqst_date", "cfrm_number", "cfrm_date", "appt_date", "appt_time", "notes", "ctns"]


def _ahora() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _tz(nombre: Optional[str]) -> ZoneInfo:
    try:
        return ZoneInfo(nombre or config.DEFAULT_TIMEZONE)
    except Exception:
        return ZoneInfo(config.DEFAULT_TIMEZONE)


def _fecha_local(ts_iso: Optional[str], tz: ZoneInfo) -> Optional[date]:
    if not ts_iso:
        return None
    dt = datetime.strptime(ts_iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    return dt.astimezone(tz).date()


# ---------------------------------------------------------------------------
# Actualización
# ---------------------------------------------------------------------------
def refresh(store: Store, fetch_html: Callable[[], str], trigger: str = "manual") -> Dict:
    """Descarga la lista, la compara con la foto anterior y guarda todo en una transacción.
    Si la respuesta es inválida o sospechosamente vacía, NO toca la foto anterior."""
    with _lock:
        inicio = _ahora()
        with store.engine.begin() as c:
            run_id = c.execute(insert(runs).values(started_at=inicio, trigger=trigger, ok=False)
                               .returning(runs.c.id)).scalar_one()
        try:
            registros = parse_table(fetch_html())
            previas = store.load_orders()
            if not registros and previas:
                raise PortalResponseError(
                    "El portal devolvió una lista vacía; se conserva la información anterior por seguridad."
                )
            stats = _aplicar(store, registros, previas, inicio)
            fin = _ahora()
            with store.engine.begin() as c:
                c.execute(update(runs).where(runs.c.id == run_id).values(
                    finished_at=fin, ok=True, total=stats["total"], new_count=stats["new"],
                    changed_count=stats["changed"], removed_count=stats["removed"]))
            return {"ok": True, **stats, "finished_at": fin.strftime("%Y-%m-%dT%H:%M:%SZ")}
        except Exception as e:
            with store.engine.begin() as c:
                c.execute(update(runs).where(runs.c.id == run_id).values(
                    finished_at=_ahora(), ok=False, error=str(e)))
            raise


def _evento(pt: str, po, cust, nombre: str, ahora: datetime, old: str = "", new: str = "") -> Dict:
    return {"ts": ahora, "pick_ticket": pt, "po": po, "cust": cust, "event": nombre,
            "old_value": old, "new_value": new}


def _aplicar(store: Store, registros: List[Dict], previas: Dict[str, Dict], ahora: datetime) -> Dict:
    primera_vez = not previas and store.last_ok_run() is None
    actuales = {r["pick_ticket"]: r for r in registros}
    ya_cerradas = store.closed_pick_tickets()
    nuevos = cambiados = salidas = 0
    nuevos_eventos: List[Dict] = []

    with store.engine.begin() as c:
        for pt, r in actuales.items():
            data = {k: r.get(k, "") for k in CAMPOS_ORDEN}
            anterior = previas.get(pt)
            if anterior is None:
                nombre = "INITIAL SYNC" if primera_vez else "NEW PICK TICKET"
                if not primera_vez:
                    nuevos += 1
                nuevos_eventos.append(_evento(pt, r["po"], r["cust"], nombre, ahora))
                c.execute(insert(orders).values(
                    pick_ticket=pt, data=data, first_seen=ahora, last_seen=ahora,
                    last_change="" if primera_vez else nombre, last_change_at=None if primera_vez else ahora))
                continue
            cambios = rules.detectar_cambios(anterior, r)
            valores = {"data": data, "last_seen": ahora}
            if cambios:
                cambiados += 1
                nuevos_eventos += [_evento(pt, r["po"], r["cust"], ev, ahora, old, new) for ev, old, new in cambios]
                valores.update(last_change=cambios[-1][0], last_change_at=ahora)
            c.execute(update(orders).where(orders.c.pick_ticket == pt).values(**valores))

        # Órdenes que desaparecieron del portal
        for pt, vieja in previas.items():
            if pt in actuales:
                continue
            salidas += 1
            if pt not in ya_cerradas:
                estado, motivo = rules.clasificar_salida(vieja)
                c.execute(insert(closed_orders).values(
                    pick_ticket=pt, date_removed=ahora.date(), removed_at=ahora, final_status=estado,
                    reason=motivo, po=vieja.get("po"), cust=vieja.get("cust"), ship_date=vieja.get("ship_date"),
                    cancel_date=vieja.get("cancel_date"), cfrm_number=vieja.get("cfrm_number"),
                    appt_date=vieja.get("appt_date"), notes=vieja.get("notes"), source="monitor"))
                nuevos_eventos.append(_evento(pt, vieja.get("po"), vieja.get("cust"), f"ORDER {estado}",
                                              ahora, "", motivo))
            c.execute(delete(orders).where(orders.c.pick_ticket == pt))

        if nuevos_eventos:
            c.execute(insert(events), nuevos_eventos)

    return {"total": len(actuales), "new": nuevos, "changed": cambiados, "removed": salidas,
            "initial_sync": primera_vez}


# ---------------------------------------------------------------------------
# Vistas
# ---------------------------------------------------------------------------
def listar(store: Store, today: date) -> List[Dict]:
    return rules.ordenar([rules.evaluar(o, today) for o in store.load_orders().values()])


def resumen(store: Store, today: date, tz_name: Optional[str]) -> Dict:
    tz = _tz(tz_name)
    ordenes = listar(store, today)
    conteo = {s: 0 for s in rules.STATUS_ORDER}
    for o in ordenes:
        if o["status"] in conteo:
            conteo[o["status"]] += 1

    # "Hoy" se mide con eventos fechados (últimos 2 días UTC cubren cualquier zona horaria).
    desde = datetime.combine(today - timedelta(days=1), time.min, tzinfo=timezone.utc)
    eventos_hoy = [e for e in store.events(limit=20000, since=desde) if _fecha_local(e["ts"], tz) == today]
    nuevos_hoy = sum(1 for e in eventos_hoy if e["event"] == "NEW PICK TICKET")
    citas_hoy = sum(1 for e in eventos_hoy if e["event"] == "APPOINTMENT ASSIGNED")
    completadas_hoy = 0
    for c in store.closed(limit=20000):
        dia = _fecha_local(c["removed_at"], tz) if c["removed_at"] else date.fromisoformat(c["date_removed"])
        if dia == today and c["final_status"] == "COMPLETED":
            completadas_hoy += 1

    ultima = store.last_runs(1)
    ok = store.last_ok_run()
    return {
        "total_active": len(ordenes),
        "by_status": conteo,
        "new_today": nuevos_hoy,
        "appointments_today": citas_hoy,
        "completed_today": completadas_hoy,
        "last_run": ultima[0] if ultima else None,
        "last_success_at": ok["finished_at"] if ok else None,
        "auto_refresh": auto_refresh_activo(store),
        "auto_refresh_minutes": config.AUTO_REFRESH_MINUTES,
    }


def auto_refresh_activo(store: Store) -> bool:
    return store.get_setting("auto_refresh", "0") == "1"


# ---------------------------------------------------------------------------
# Importación del histórico ROUTING_COMPLETED (CSV exportado del Google Sheet)
# ---------------------------------------------------------------------------
_COLUMNAS_CSV = {
    "Date Removed": "date_removed", "Final Status": "final_status", "Reason": "reason",
    "Pick Ticket": "pick_ticket", "PO#": "po", "Customer": "cust", "Ship Date": "ship_date",
    "Cancel Date": "cancel_date", "Cfrm Number": "cfrm_number", "Appt Date": "appt_date", "Notes": "notes",
}


def _fecha_csv(valor: str) -> Optional[date]:
    try:
        return datetime.strptime(valor.strip(), "%m/%d/%Y").date()
    except ValueError:
        return None


def importar_completadas_csv(store: Store, contenido: str) -> Dict:
    lector = csv.DictReader(io.StringIO(contenido.lstrip("﻿")))
    faltan = [c for c in _COLUMNAS_CSV if c not in (lector.fieldnames or [])]
    if faltan:
        raise ValueError(f"El CSV no tiene las columnas esperadas: {', '.join(faltan)}")
    existentes = store.closed_pick_tickets()
    filas: List[Dict] = []
    duplicadas = invalidas = 0
    for fila in lector:
        d = {dest: rules.normalizar(fila.get(orig, "")) for orig, dest in _COLUMNAS_CSV.items()}
        fecha = _fecha_csv(d["date_removed"])
        if not d["pick_ticket"] or not fecha or not d["final_status"]:
            invalidas += 1
            continue
        if d["pick_ticket"] in existentes:
            duplicadas += 1
            continue
        existentes.add(d["pick_ticket"])
        filas.append({**d, "date_removed": fecha, "removed_at": None, "source": "import"})
    if filas:
        with store.engine.begin() as c:
            c.execute(insert(closed_orders), filas)
    return {"inserted": len(filas), "duplicates": duplicadas, "invalid": invalidas}
