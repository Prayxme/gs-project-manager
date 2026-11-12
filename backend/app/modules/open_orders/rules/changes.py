"""Detección de cambios entre dos fotos de la misma orden (todos los cambios, no solo el primero)."""
from typing import Dict, List, Tuple

from app.modules.open_orders.rules.cfrm import cfrm_type
from app.shared.text import normalize_spaces

CAMPOS_VIGILADOS = [
    ("ship_date", "SHIP DATE CHANGED"),
    ("cancel_date", "CANCEL DATE CHANGED"),
    ("appt_date", "APPOINTMENT DATE CHANGED"),
    ("appt_time", "APPOINTMENT TIME CHANGED"),
    ("notes", "NOTES UPDATED"),
    ("ctns", "CARTONS CHANGED"),
]


def _evento_cfrm(oc: str, nc: str) -> str:
    ot, nt = cfrm_type(oc), cfrm_type(nc)
    if not oc:
        return "APPOINTMENT ASSIGNED" if nt == "APPOINTMENT" else "ROUTING ADDED"
    if not nc:
        return "ROUTING REMOVED"
    if nt == "APPOINTMENT" and ot != "APPOINTMENT":
        return "APPOINTMENT ASSIGNED"
    if nt == "APPOINTMENT" and ot == "APPOINTMENT":
        return "APPOINTMENT CHANGED"
    if nt == "ROUTING" and ot == "ROUTING":
        return "ROUTING NUMBER CHANGED"
    return "CFRM NUMBER CHANGED"


def detectar_cambios(old: Dict, new: Dict) -> List[Tuple[str, str, str]]:
    """Lista de (evento, valor_anterior, valor_nuevo) entre dos fotos de la misma orden."""
    eventos: List[Tuple[str, str, str]] = []
    oc, nc = normalize_spaces(old.get("cfrm_number")), normalize_spaces(new.get("cfrm_number"))
    if oc != nc:
        eventos.append((_evento_cfrm(oc, nc), oc, nc))
    for campo, ev in CAMPOS_VIGILADOS:
        if campo not in old:  # foto anterior sin ese campo (p. ej. versión previa): no es un cambio
            continue
        a, b = normalize_spaces(old.get(campo)), normalize_spaces(new.get(campo))
        if a != b:
            eventos.append((ev, a, b))
    return eventos
