"""Conciliación PDF <-> portal de Wiesner. El portal es la verdad: PO, PikTik y cartones
deben coincidir siempre; si no, esa PO no se enruta hasta revisarla."""
from typing import Dict, List, Optional, Tuple

OK = "OK"
NOT_IN_PORTAL = "NOT_IN_PORTAL"      # el PikTik no está entre las órdenes abiertas del portal
MISMATCH = "MISMATCH"                # PO o cartones distintos entre PDF y portal
ALREADY_ROUTED = "ALREADY_ROUTED"    # el portal ya tiene Cfrm Number
UNVERIFIED = "UNVERIFIED"            # el portal no respondió: datos solo del PDF

EXCLUIDOS = (NOT_IN_PORTAL, MISMATCH, ALREADY_ROUTED)


def _entero(valor) -> Optional[int]:
    try:
        return int(str(valor).replace(",", "").strip())
    except (TypeError, ValueError):
        return None


def conciliar(piktik: str, po: str, cartones: Optional[int],
              portal: Optional[Dict[str, Dict]]) -> Tuple[str, List[str], Optional[Dict]]:
    """(estado, diferencias, fila del portal). `portal` = None si no se pudo consultar."""
    if portal is None:
        return UNVERIFIED, [], None
    fila = portal.get(piktik)
    if fila is None:
        return NOT_IN_PORTAL, [f"PikTik {piktik} no está en las órdenes abiertas del portal"], None
    difs = []
    if (fila.get("po") or "").strip() != po:
        difs.append(f"PO: portal {fila.get('po')} / PDF {po}")
    if _entero(fila.get("ctns")) != cartones:
        difs.append(f"Cartones: portal {fila.get('ctns')} / PDF {cartones}")
    if difs:
        return MISMATCH, difs, fila
    if (fila.get("cfrm_number") or "").strip():
        return ALREADY_ROUTED, [f"Ya tiene Cfrm Number {fila['cfrm_number']}"], fila
    return OK, [], fila
