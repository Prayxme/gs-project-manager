"""Estado, prioridad y alerta de cada orden para una fecha dada (el "hoy" del usuario)."""
from datetime import date
from typing import Dict, List, Optional

from app.modules.open_orders.config import ATTENTION_DAYS
from app.modules.open_orders.rules.cfrm import cfrm_type
from app.modules.open_orders.rules.window import customer_code, routing_window
from app.shared.dates import parse_date

STATUS_ORDER = ["OVERDUE", "LAST DAY", "ATTENTION", "SAFE", "TOO EARLY", "ROUTED"]

PRIORITY = {
    "OVERDUE": "CRITICAL",
    "LAST DAY": "HIGH",
    "ATTENTION": "MEDIUM",
    "SAFE": "LOW",
    "TOO EARLY": "ON HOLD",
    "ROUTED": "COMPLETE",
}
PRIORITY_RANK = {"CRITICAL": 1, "HIGH": 2, "MEDIUM": 3, "LOW": 4, "ON HOLD": 5, "COMPLETE": 6}

ALERT = {
    "ROUTED": "Routing Completed",
    "OVERDUE": "Routing Past Due",
    "LAST DAY": "Routing Required Today",
    "ATTENTION": "Deadline Approaching",
    "TOO EARLY": "Window Not Open Yet",
}


def determine_status(deadline: Optional[date], earliest: Optional[date], cfrm: str, today: date) -> str:
    if cfrm and cfrm.strip():
        return "ROUTED"
    if deadline is None:
        return ""
    if earliest and today < earliest:
        return "TOO EARLY"
    dias = (deadline - today).days
    if dias < 0:
        return "OVERDUE"
    if dias == 0:
        return "LAST DAY"
    if dias <= ATTENTION_DAYS:
        return "ATTENTION"
    return "SAFE"


def evaluar(order: Dict, today: date) -> Dict:
    """Agrega a una orden los campos calculados para 'today' (fecha local del usuario)."""
    code = customer_code(order.get("cust", ""))
    ship = parse_date(order.get("ship_date"))
    cancel = parse_date(order.get("cancel_date"))
    deadline, earliest = routing_window(ship, cancel, code)
    status = determine_status(deadline, earliest, order.get("cfrm_number", ""), today)
    dias = (deadline - today).days if (deadline and status != "ROUTED") else None
    prioridad = PRIORITY.get(status, "LOW")
    return {
        **order,
        "customer_code": code,
        "routing_deadline": deadline.isoformat() if deadline else None,
        "routing_earliest": earliest.isoformat() if earliest else None,
        "days_remaining": dias,
        "status": status,
        "priority": prioridad,
        "priority_rank": PRIORITY_RANK.get(prioridad, 99),
        "alert": ALERT.get(status, ""),
        "cfrm_type": cfrm_type(order.get("cfrm_number", "")),
    }


def ordenar(orders: List[Dict]) -> List[Dict]:
    """Por prioridad y luego por días restantes (lo más urgente primero)."""
    return sorted(orders, key=lambda o: (
        o["priority_rank"],
        o["days_remaining"] if o["days_remaining"] is not None else 10**6,
        o.get("pick_ticket", ""),
    ))
