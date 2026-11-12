"""Estado de routing de una orden para una fecha dada. Lo comparten el Monitor de Órdenes Abiertas
(que lo muestra) y Routing (que calcula las órdenes de un estado)."""
from datetime import date
from typing import Optional

ATTENTION_DAYS = 3          # ATTENTION cuando faltan <= 3 días

STATUS_ORDER = ["OVERDUE", "LAST DAY", "ATTENTION", "SAFE", "TOO EARLY", "ROUTED"]
URGENT_STATUSES = ("OVERDUE", "LAST DAY", "ATTENTION")


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
