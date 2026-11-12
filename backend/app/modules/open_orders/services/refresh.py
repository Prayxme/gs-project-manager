"""
Actualización desde el portal: descargar, comparar con la foto anterior y guardar.
Si la respuesta es inválida o sospechosamente vacía, NO se toca la foto anterior.
"""
import threading
from datetime import datetime
from typing import Callable, Dict, List

from app.modules.open_orders import rules
from app.modules.open_orders.repository import OpenOrdersRepository
from app.shared.dates import to_iso_utc, utc_now
from app.shared.wiesner.portal import PortalResponseError, parse_table

_lock = threading.Lock()  # una actualización a la vez (manual o automática)

CAMPOS_ORDEN = ["row_number", "dv", "pick_ticket", "stg", "po", "ship_to", "ship_date", "cancel_date",
                "cust", "wh", "rqst_date", "cfrm_number", "cfrm_date", "appt_date", "appt_time", "notes", "ctns"]


def refresh(repo: OpenOrdersRepository, fetch_html: Callable[[], str], trigger: str = "manual") -> Dict:
    with _lock:
        inicio = utc_now()
        run_id = repo.start_run(inicio, trigger)
        try:
            registros = parse_table(fetch_html())
            previas = repo.load_orders()
            if not registros and previas:
                raise PortalResponseError(
                    "El portal devolvió una lista vacía; se conserva la información anterior por seguridad."
                )
            stats = _sincronizar(repo, registros, previas, inicio)
            fin = utc_now()
            repo.finish_run(run_id, fin, ok=True, stats=stats)
            return {"ok": True, **stats, "finished_at": to_iso_utc(fin)}
        except Exception as e:
            repo.finish_run(run_id, utc_now(), ok=False, error=str(e))
            raise


def _evento(pt: str, po, cust, nombre: str, ahora: datetime, old: str = "", new: str = "") -> Dict:
    return {"ts": ahora, "pick_ticket": pt, "po": po, "cust": cust, "event": nombre,
            "old_value": old, "new_value": new}


def _sincronizar(repo: OpenOrdersRepository, registros: List[Dict], previas: Dict[str, Dict],
                 ahora: datetime) -> Dict:
    """Calcula qué cambió y lo guarda en una sola transacción."""
    primera_vez = not previas and repo.last_ok_run() is None
    actuales = {r["pick_ticket"]: r for r in registros}
    ya_cerradas = repo.closed_pick_tickets()

    nuevas, actualizadas, cerradas, borrar, eventos = [], [], [], [], []
    cambiados = 0

    for pt, r in actuales.items():
        data = {k: r.get(k, "") for k in CAMPOS_ORDEN}
        anterior = previas.get(pt)
        if anterior is None:
            nombre = "INITIAL SYNC" if primera_vez else "NEW PICK TICKET"
            eventos.append(_evento(pt, r["po"], r["cust"], nombre, ahora))
            nuevas.append({"pick_ticket": pt, "data": data, "first_seen": ahora, "last_seen": ahora,
                           "last_change": "" if primera_vez else nombre,
                           "last_change_at": None if primera_vez else ahora})
            continue
        cambios = rules.detectar_cambios(anterior, r)
        valores = {"data": data, "last_seen": ahora}
        if cambios:
            cambiados += 1
            eventos += [_evento(pt, r["po"], r["cust"], ev, ahora, old, new) for ev, old, new in cambios]
            valores.update(last_change=cambios[-1][0], last_change_at=ahora)
        actualizadas.append((pt, valores))

    # Órdenes que desaparecieron del portal
    for pt, vieja in previas.items():
        if pt in actuales:
            continue
        borrar.append(pt)
        if pt not in ya_cerradas:
            estado, motivo = rules.clasificar_salida(vieja)
            cerradas.append({
                "pick_ticket": pt, "date_removed": ahora.date(), "removed_at": ahora, "final_status": estado,
                "reason": motivo, "po": vieja.get("po"), "cust": vieja.get("cust"),
                "ship_date": vieja.get("ship_date"), "cancel_date": vieja.get("cancel_date"),
                "cfrm_number": vieja.get("cfrm_number"), "appt_date": vieja.get("appt_date"),
                "notes": vieja.get("notes"), "source": "monitor",
            })
            eventos.append(_evento(pt, vieja.get("po"), vieja.get("cust"), f"ORDER {estado}", ahora, "", motivo))

    repo.save_sync(nuevas, actualizadas, cerradas, borrar, eventos)
    return {"total": len(actuales), "new": 0 if primera_vez else len(nuevas), "changed": cambiados,
            "removed": len(borrar), "initial_sync": primera_vez}
