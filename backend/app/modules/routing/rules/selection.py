"""Órdenes del portal que interesan para enrutar: las de ciertos estados del Monitor (vencidas,
último día, atención...) y, si se pide, de un solo Customer No (BURL120, BURL240...).
El estado sale de la misma regla del Monitor (app/shared/wiesner/status.py)."""
from datetime import date
from typing import Dict, Iterable, List, Optional, Sequence

from app.shared.dates import parse_date
from app.shared.wiesner import customer_code, determine_status, routing_window


def mismo_cliente(cust: str, pedido: Optional[str]) -> bool:
    return not pedido or (cust or "").strip().upper() == pedido.strip().upper()


def seleccionar(filas: Iterable[Dict], hoy: date, estados: Sequence[str], cust: Optional[str] = None) -> List[Dict]:
    """Filas del portal sin routing (sin Cfrm Number) cuyo estado está en `estados`."""
    elegidas = []
    for f in filas:
        if not mismo_cliente(f.get("cust", ""), cust):
            continue
        cancel = parse_date(f.get("cancel_date"))
        deadline, earliest = routing_window(parse_date(f.get("ship_date")), cancel,
                                            customer_code(f.get("cust", "")))
        estado = determine_status(deadline, earliest, f.get("cfrm_number", ""), hoy)
        if estado in ("", "ROUTED") or estado not in estados:
            continue
        elegidas.append({
            "pick_ticket": f["pick_ticket"], "po": f.get("po", ""), "cust": f.get("cust", ""),
            "ctns": f.get("ctns", ""), "ship_to": f.get("ship_to", ""), "status": estado,
            "cancel_date": cancel.isoformat() if cancel else "",
            "deadline": deadline.isoformat(), "days_left": (deadline - hoy).days,
        })
    return sorted(elegidas, key=lambda u: (u["deadline"], u["cust"], u["po"]))
