"""Estimación de pallets de una PO con el motor de empaque compartido (el del Paletizador 3D).

El motor respeta: pallet 48x40 sin voladizo, altura máxima 85 in contando la base (79.5 útiles),
soporte >= 65 %, lo pesado abajo y las 6 orientaciones de caja (ropa: se pueden voltear).
"""
from typing import Dict, List, Tuple

from app.modules.routing import config
from app.shared.packing import Linea, empacar_grupo

ALTURA_UTIL_IN = config.PALLET_ALTURA_MAX_IN - config.PALLET_BASE_IN


def estimar_pallets(po: str, items: List[Dict]) -> Tuple[int, int]:
    """(pallets estimados, cajas que no caben en ningún pallet)."""
    lineas = [
        Linea(sku=i["sku"] or "SKU", l=i["l"], w=i["w"], h=i["h"], weight=i["weight"], qty=i["qty"],
              po=po, piktik=i.get("piktik", ""), dc="")
        for i in items if i["qty"] > 0 and min(i["l"], i["w"], i["h"]) > 0
    ]
    if not lineas:
        return 0, 0
    pallets, sobrantes = empacar_grupo(lineas, config.PALLET_ANCHO_IN, config.PALLET_LARGO_IN,
                                       ALTURA_UTIL_IN, None)
    return len(pallets), sum(s["count"] for s in sobrantes)
