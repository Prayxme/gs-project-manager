"""Qué POs pueden ir juntas en un RTS y cómo se reparten respetando el límite de pallets.

Pueden ir juntas solo si coinciden en:
  * familia de cliente (BURL y MODE son Burlington; los demás, su propio código),
  * dirección SHIP TO del PDF (calle + código postal normalizados),
  * Cancel Date (nuestra fecha de referencia),
  * en TJMA / MARS / NEWT, los 2 primeros dígitos de la PO (indican el DC).
"""
from typing import Dict, List, Tuple

from app.modules.routing import config


def clave_grupo(po: Dict) -> Tuple[str, str, str, str]:
    prefijo = po["po"][:config.LARGO_PREFIJO_PO] if po["customer_code"] in config.PREFIJO_PO_DC else ""
    # Sin dirección leída la PO no se junta con ninguna otra (clave propia).
    direccion = po["address_key"] or f"sin-direccion:{po['po']}"
    return po["family"], direccion, po["cancel_date"], prefijo


def repartir_en_rts(pos: List[Dict], limite: int) -> List[List[Dict]]:
    """Primero las POs con más pallets; cada una entra en el primer RTS donde quepa
    (first-fit decreasing). Una PO que sola supera el límite va en su propio RTS."""
    rts: List[List[Dict]] = []
    ocupado: List[int] = []
    for po in sorted(pos, key=lambda p: (-p["pallets"], p["po"])):
        for i, usados in enumerate(ocupado):
            if usados + po["pallets"] <= limite:
                rts[i].append(po)
                ocupado[i] += po["pallets"]
                break
        else:
            rts.append([po])
            ocupado.append(po["pallets"])
    return rts
