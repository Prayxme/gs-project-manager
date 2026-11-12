"""Tipo de número de confirmación (Cfrm Number) y clasificación de órdenes que salen del portal.
Formatos confirmados por el usuario con datos reales del portal."""
import re
from typing import Dict, Tuple

from app.shared.text import normalize_spaces

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
    v = normalize_spaces(value)
    if not v:
        return ""
    if any(r.match(v) for r in _RE_APPOINTMENT):
        return "APPOINTMENT"
    if any(r.match(v) for r in _RE_ROUTING):
        return "ROUTING"
    return "OTHER"


def clasificar_salida(order: Dict) -> Tuple[str, str]:
    """Una orden desapareció del portal: (estado final, motivo)."""
    tipo = cfrm_type(order.get("cfrm_number"))
    if tipo == "APPOINTMENT":
        return "COMPLETED", "SHIPPED"
    if tipo:
        return "REMOVED", "REMOVED BEFORE APPOINTMENT"
    return "CANCELLED", "CANCELLED BEFORE ROUTING"
