"""Estimación de pallets de una PO con el motor de empaque compartido (el del Paletizador 3D).

El motor respeta: pallet 48x40 sin voladizo, altura máxima 85 in contando la base (79.5 útiles),
soporte >= 65 %, lo pesado abajo y las 6 orientaciones de caja (ropa: se pueden voltear).
"""
from dataclasses import dataclass
from typing import Dict, List, Optional

from app.modules.routing import config
from app.shared.packing import Linea, empacar_grupo

ALTURA_UTIL_IN = config.PALLET_ALTURA_MAX_IN - config.PALLET_BASE_IN


@dataclass(frozen=True)
class Estimacion:
    pallets: int = 0
    no_caben: int = 0                       # cajas que no caben en ningún pallet
    ultima_llena: Optional[float] = None    # pallet menos lleno / promedio de los demás (None con 1 pallet)


def lineas_validas(items: List[Dict]) -> List[Dict]:
    """Líneas que el motor puede empacar (con cantidad y dimensiones)."""
    return [i for i in items if i["qty"] > 0 and min(i["l"], i["w"], i["h"]) > 0]


def _ultima_llena(volumenes: List[float]) -> Optional[float]:
    if len(volumenes) < 2:
        return None
    orden = sorted(volumenes)
    promedio = sum(orden[1:]) / len(orden[1:])
    return round(orden[0] / promedio, 3) if promedio else None


def estimar_pallets(po: str, items: List[Dict]) -> Estimacion:
    lineas = [
        Linea(sku=i["sku"] or "SKU", l=i["l"], w=i["w"], h=i["h"], weight=i["weight"], qty=i["qty"],
              po=po, piktik=i.get("piktik", ""), dc="")
        for i in lineas_validas(items)
    ]
    if not lineas:
        return Estimacion()
    pallets, sobrantes = empacar_grupo(lineas, config.PALLET_ANCHO_IN, config.PALLET_LARGO_IN,
                                       ALTURA_UTIL_IN, None)
    return Estimacion(len(pallets), sum(s["count"] for s in sobrantes),
                      _ultima_llena([p.volumen for p in pallets]))
