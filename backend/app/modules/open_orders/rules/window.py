"""Cliente y ventana de routing (fecha límite y fecha más temprana) por cliente."""
import re
from datetime import date, timedelta
from typing import Optional, Tuple


def customer_code(cust: str) -> str:
    """'MARS125' -> 'MARS'; 'S&JS120' -> 'S&JS' (el Apps Script devolvía 'S')."""
    m = re.match(r"^\s*([^\d\s]+)", cust or "")
    return m.group(1).upper() if m else (cust or "").strip().upper()


def routing_window(ship: Optional[date], cancel: Optional[date], code: str) -> Tuple[Optional[date], Optional[date]]:
    """(deadline, earliest) según el cliente.
    BURL: deadline = Cancel - 5 días naturales (nunca antes del Ship Date); earliest = Ship - 21.
    ROSS/DDSD: deadline = Cancel; earliest = Ship - 21.
    MACY: deadline = Cancel; earliest = Ship - 7.
    Resto: deadline = Cancel; sin earliest."""
    if cancel is None:
        return None, None
    deadline, earliest = cancel, None
    if code == "BURL" and ship:
        menos5 = cancel - timedelta(days=5)
        deadline = ship if menos5 < ship else menos5
        earliest = ship - timedelta(days=21)
    elif code in ("ROSS", "DDSD") and ship:
        earliest = ship - timedelta(days=21)
    elif code == "MACY" and ship:
        earliest = ship - timedelta(days=7)
    return deadline, earliest
