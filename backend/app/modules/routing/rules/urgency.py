"""Órdenes urgentes del portal: sin routing (sin Cfrm Number) y con la fecha límite vencida,
hoy o dentro de los próximos `dias` días. La fecha límite sale de la Cancel Date según el cliente
(la misma regla del Monitor de Órdenes Abiertas)."""
from datetime import date
from typing import Dict, Iterable, List

from app.shared.dates import parse_date
from app.shared.wiesner import customer_code, routing_window


def ordenes_urgentes(filas: Iterable[Dict], hoy: date, dias: int) -> List[Dict]:
    urgentes = []
    for f in filas:
        if (f.get("cfrm_number") or "").strip():
            continue                                    # ya enrutada
        deadline, _ = routing_window(parse_date(f.get("ship_date")), parse_date(f.get("cancel_date")),
                                     customer_code(f.get("cust", "")))
        if deadline is None or (deadline - hoy).days > dias:
            continue
        cancel = parse_date(f.get("cancel_date"))
        urgentes.append({
            "pick_ticket": f["pick_ticket"], "po": f.get("po", ""), "cust": f.get("cust", ""),
            "ctns": f.get("ctns", ""), "ship_to": f.get("ship_to", ""),
            "cancel_date": cancel.isoformat() if cancel else "",
            "deadline": deadline.isoformat(), "days_left": (deadline - hoy).days,
        })
    return sorted(urgentes, key=lambda u: (u["deadline"], u["cust"], u["po"]))
