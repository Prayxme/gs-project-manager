"""
Lógica del monitor: actualizar desde el portal, detectar cambios y salidas,
y armar las vistas (órdenes, indicadores, historial, completadas).
"""
import csv
import io
import json
import threading
from datetime import date, datetime, timezone
from typing import Callable, Dict, List, Optional
from zoneinfo import ZoneInfo

from app.modules.open_orders import config, rules
from app.modules.open_orders.parser import PortalResponseError, parse_table
from app.modules.open_orders.store import Store

_lock = threading.Lock()


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _tz(nombre: Optional[str]) -> ZoneInfo:
    try:
        return ZoneInfo(nombre or config.DEFAULT_TIMEZONE)
    except Exception:
        return ZoneInfo(config.DEFAULT_TIMEZONE)


def _fecha_local(ts_utc: Optional[str], tz: ZoneInfo) -> Optional[date]:
    if not ts_utc:
        return None
    dt = datetime.strptime(ts_utc, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    return dt.astimezone(tz).date()


CAMPOS_ORDEN = ["row_number", "dv", "pick_ticket", "stg", "po", "ship_to", "ship_date", "cancel_date",
                "cust", "wh", "rqst_date", "cfrm_number", "cfrm_date", "appt_date", "appt_time", "notes", "ctns"]


# ---------------------------------------------------------------------------
# Actualización
# ---------------------------------------------------------------------------
def refresh(store: Store, fetch_html: Callable[[], str], trigger: str = "manual") -> Dict:
    """Descarga la lista, la compara con la foto anterior y guarda todo en una transacción.
    Si la respuesta es inválida o sospechosamente vacía, NO toca la foto anterior."""
    with _lock:
        inicio = _utcnow()
        with store.conn() as c:
            run_id = c.execute("INSERT INTO runs(started_at, trigger) VALUES(?, ?)", (inicio, trigger)).lastrowid
        try:
            registros = parse_table(fetch_html())
            previas = store.load_orders()
            if not registros and previas:
                raise PortalResponseError(
                    "El portal devolvió una lista vacía; se conserva la información anterior por seguridad."
                )
            stats = _aplicar(store, registros, previas, inicio)
            with store.conn() as c:
                c.execute("UPDATE runs SET finished_at=?, ok=1, total=?, new_count=?, changed_count=?, "
                          "removed_count=? WHERE id=?",
                          (_utcnow(), stats["total"], stats["new"], stats["changed"], stats["removed"], run_id))
            return {"ok": True, **stats, "finished_at": _utcnow()}
        except Exception as e:
            with store.conn() as c:
                c.execute("UPDATE runs SET finished_at=?, ok=0, error=? WHERE id=?", (_utcnow(), str(e), run_id))
            raise


def _aplicar(store: Store, registros: List[Dict], previas: Dict[str, Dict], ahora: str) -> Dict:
    primera_vez = not previas and store.last_ok_run() is None
    actuales = {r["pick_ticket"]: r for r in registros}
    ya_cerradas = store.closed_pick_tickets()
    nuevos = cambiados = salidas = 0

    with store.conn() as c:
        for pt, r in actuales.items():
            data = json.dumps({k: r.get(k, "") for k in CAMPOS_ORDEN})
            anterior = previas.get(pt)
            if anterior is None:
                evento = "INITIAL SYNC" if primera_vez else "NEW PICK TICKET"
                if not primera_vez:
                    nuevos += 1
                c.execute("INSERT INTO events(ts, pick_ticket, po, cust, event, old_value, new_value) "
                          "VALUES(?,?,?,?,?,?,?)", (ahora, pt, r["po"], r["cust"], evento, "", ""))
                c.execute("INSERT OR REPLACE INTO orders(pick_ticket, data, first_seen, last_seen, last_change, "
                          "last_change_at) VALUES(?,?,?,?,?,?)",
                          (pt, data, ahora, ahora, "" if primera_vez else evento, None if primera_vez else ahora))
                continue
            cambios = rules.detectar_cambios(anterior, r)
            if cambios:
                cambiados += 1
                for ev, old, new in cambios:
                    c.execute("INSERT INTO events(ts, pick_ticket, po, cust, event, old_value, new_value) "
                              "VALUES(?,?,?,?,?,?,?)", (ahora, pt, r["po"], r["cust"], ev, old, new))
                c.execute("UPDATE orders SET data=?, last_seen=?, last_change=?, last_change_at=? "
                          "WHERE pick_ticket=?", (data, ahora, cambios[-1][0], ahora, pt))
            else:
                c.execute("UPDATE orders SET data=?, last_seen=? WHERE pick_ticket=?", (data, ahora, pt))

        # Órdenes que desaparecieron del portal
        for pt, vieja in previas.items():
            if pt in actuales:
                continue
            salidas += 1
            if pt not in ya_cerradas:
                estado, motivo = rules.clasificar_salida(vieja)
                c.execute(
                    "INSERT INTO closed_orders(pick_ticket, date_removed, removed_at, final_status, reason, po, cust, "
                    "ship_date, cancel_date, cfrm_number, appt_date, notes, source) "
                    "VALUES(?,?,?,?,?,?,?,?,?,?,?,?, 'monitor')",
                    (pt, ahora[:10], ahora, estado, motivo, vieja.get("po"), vieja.get("cust"),
                     vieja.get("ship_date"), vieja.get("cancel_date"), vieja.get("cfrm_number"),
                     vieja.get("appt_date"), vieja.get("notes")))
                c.execute("INSERT INTO events(ts, pick_ticket, po, cust, event, old_value, new_value) "
                          "VALUES(?,?,?,?,?,?,?)", (ahora, pt, vieja.get("po"), vieja.get("cust"),
                                                     f"ORDER {estado}", "", motivo))
            c.execute("DELETE FROM orders WHERE pick_ticket=?", (pt,))

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

    # "Hoy" se mide con eventos fechados, no con el último cambio "pegajoso".
    eventos_hoy = [e for e in store.events(limit=5000) if _fecha_local(e["ts"], tz) == today]
    nuevos_hoy = sum(1 for e in eventos_hoy if e["event"] == "NEW PICK TICKET")
    citas_hoy = sum(1 for e in eventos_hoy if e["event"] == "APPOINTMENT ASSIGNED")
    completadas_hoy = 0
    for c in store.closed(limit=5000):
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


def _fecha_csv(valor: str) -> Optional[str]:
    try:
        return datetime.strptime(valor.strip(), "%m/%d/%Y").date().isoformat()
    except ValueError:
        return None


def importar_completadas_csv(store: Store, contenido: str) -> Dict:
    lector = csv.DictReader(io.StringIO(contenido.lstrip("﻿")))
    faltan = [c for c in _COLUMNAS_CSV if c not in (lector.fieldnames or [])]
    if faltan:
        raise ValueError(f"El CSV no tiene las columnas esperadas: {', '.join(faltan)}")
    existentes = store.closed_pick_tickets()
    insertadas = duplicadas = invalidas = 0
    with store.conn() as c:
        for fila in lector:
            d = {dest: rules.normalizar(fila.get(orig, "")) for orig, dest in _COLUMNAS_CSV.items()}
            fecha = _fecha_csv(d["date_removed"])
            if not d["pick_ticket"] or not fecha:
                invalidas += 1
                continue
            if d["pick_ticket"] in existentes:
                duplicadas += 1
                continue
            c.execute(
                "INSERT INTO closed_orders(pick_ticket, date_removed, removed_at, final_status, reason, po, cust, "
                "ship_date, cancel_date, cfrm_number, appt_date, notes, source) "
                "VALUES(?,?,NULL,?,?,?,?,?,?,?,?,?, 'import')",
                (d["pick_ticket"], fecha, d["final_status"], d["reason"], d["po"], d["cust"], d["ship_date"],
                 d["cancel_date"], d["cfrm_number"], d["appt_date"], d["notes"]))
            existentes.add(d["pick_ticket"])
            insertadas += 1
    return {"inserted": insertadas, "duplicates": duplicadas, "invalid": invalidas}
