"""
Reglas de negocio del monitor de routing (portadas del Apps Script, con correcciones).

Todas las funciones son puras (sin red ni base de datos) para poder probarlas.
Las fechas se manejan como `date` de calendario: sin errores por cambio de horario.
"""
import re
from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple

from app.modules.open_orders.config import ATTENTION_DAYS

# ---------------------------------------------------------------------------
# Fechas y cliente
# ---------------------------------------------------------------------------
def parse_mmddyy(value: Optional[str]) -> Optional[date]:
    """'10/19/26' -> date(2026, 10, 19). Vacío o '00/00/00' -> None."""
    if not value:
        return None
    m = re.match(r"^\s*(\d{1,2})/(\d{1,2})/(\d{2}|\d{4})\s*$", str(value))
    if not m:
        return None
    mes, dia, anio = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if mes == 0 or dia == 0:
        return None
    if anio < 100:
        anio += 2000
    try:
        return date(anio, mes, dia)
    except ValueError:
        return None


def customer_code(cust: str) -> str:
    """'MARS125' -> 'MARS'; 'S&JS120' -> 'S&JS' (el Apps Script devolvía 'S')."""
    m = re.match(r"^\s*([^\d\s]+)", cust or "")
    return m.group(1).upper() if m else (cust or "").strip().upper()


# ---------------------------------------------------------------------------
# Ventana de routing por cliente
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Estado, prioridad y alerta
# ---------------------------------------------------------------------------
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
    ship = parse_mmddyy(order.get("ship_date"))
    cancel = parse_mmddyy(order.get("cancel_date"))
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


# ---------------------------------------------------------------------------
# Tipo de número de confirmación (Cfrm Number)
# ---------------------------------------------------------------------------
def normalizar(value) -> str:
    """Quita NBSP/tabs y espacios repetidos: 'Load ID\\t10624682' -> 'Load ID 10624682'."""
    return re.sub(r"\s+", " ", str(value or "").replace(" ", " ")).strip()


_RE_APPOINTMENT = [
    re.compile(r"^CS\d+$", re.I),                          # cita del cliente (ROSS, BURL, DDSD, DICK)
    re.compile(r"^LOAD\s*(ID)?[\s#:]*[A-Z0-9][A-Z0-9-]*$", re.I),  # LOAD ID 123 / LOAD ID # 123 / Load ID : 123
    re.compile(r"^CT\d+[A-Z0-9-]*$", re.I),                # loads CITI (JB Hunt Intermodal)
    re.compile(r"^TRACKING\s*(ID)?[\s#:]*\d+$", re.I),     # guía FedEx
    re.compile(r"^\d{10,}$"),                              # guía numérica larga (FedEx)
]
_RE_ROUTING = [
    re.compile(r"^RTS\s*#?\s*\d+(\s*/\s*(RTS\s*#?\s*)?\d+)*$", re.I),  # RTS 123 / RTS 123 / RTS 456
    re.compile(r"^REF[#\s]*\d+$", re.I),
    re.compile(r"^D\d+$", re.I),
    re.compile(r"^PJ\s*#?\s*\d+$", re.I),                  # MACY
    re.compile(r"^\d{6,9}$"),                              # BURL/NEWT: número de solicitud sin prefijo
]


def cfrm_type(value) -> str:
    """'APPOINTMENT' (carga/cita asignada), 'ROUTING' (routing solicitado), 'OTHER' o ''."""
    v = normalizar(value)
    if not v:
        return ""
    if any(r.match(v) for r in _RE_APPOINTMENT):
        return "APPOINTMENT"
    if any(r.match(v) for r in _RE_ROUTING):
        return "ROUTING"
    return "OTHER"


# ---------------------------------------------------------------------------
# Detección de cambios (todos los cambios de una corrida, no solo el primero)
# ---------------------------------------------------------------------------
CAMPOS_VIGILADOS = [
    ("ship_date", "SHIP DATE CHANGED"),
    ("cancel_date", "CANCEL DATE CHANGED"),
    ("appt_date", "APPOINTMENT DATE CHANGED"),
    ("appt_time", "APPOINTMENT TIME CHANGED"),
    ("notes", "NOTES UPDATED"),
    ("ctns", "CARTONS CHANGED"),
]


def detectar_cambios(old: Dict, new: Dict) -> List[Tuple[str, str, str]]:
    """Lista de (evento, valor_anterior, valor_nuevo) entre dos fotos de la misma orden."""
    eventos: List[Tuple[str, str, str]] = []
    oc, nc = normalizar(old.get("cfrm_number")), normalizar(new.get("cfrm_number"))
    if oc != nc:
        ot, nt = cfrm_type(oc), cfrm_type(nc)
        if not oc:
            ev = "APPOINTMENT ASSIGNED" if nt == "APPOINTMENT" else "ROUTING ADDED"
        elif not nc:
            ev = "ROUTING REMOVED"
        elif nt == "APPOINTMENT" and ot != "APPOINTMENT":
            ev = "APPOINTMENT ASSIGNED"
        elif nt == "APPOINTMENT" and ot == "APPOINTMENT":
            ev = "APPOINTMENT CHANGED"
        elif nt == "ROUTING" and ot == "ROUTING":
            ev = "ROUTING NUMBER CHANGED"
        else:
            ev = "CFRM NUMBER CHANGED"
        eventos.append((ev, oc, nc))
    for campo, ev in CAMPOS_VIGILADOS:
        if campo not in old:  # foto anterior sin ese campo (p. ej. versión previa): no es un cambio
            continue
        a, b = normalizar(old.get(campo)), normalizar(new.get(campo))
        if a != b:
            eventos.append((ev, a, b))
    return eventos


def clasificar_salida(order: Dict) -> Tuple[str, str]:
    """Una orden desapareció del portal: (estado final, motivo)."""
    tipo = cfrm_type(order.get("cfrm_number"))
    if tipo == "APPOINTMENT":
        return "COMPLETED", "SHIPPED"
    if tipo:
        return "REMOVED", "REMOVED BEFORE APPOINTMENT"
    return "CANCELLED", "CANCELLED BEFORE ROUTING"
