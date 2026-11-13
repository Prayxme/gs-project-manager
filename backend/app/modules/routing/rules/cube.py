"""Estimación de pallets por cubo (Pre Routing): no hay dimensiones de la caja, solo sus pies cúbicos.

Pallets = cubo total / CFT que caben en un pallet armado. El último pallet lleva el resto, y su
llenado frente a los demás (que van llenos) alimenta la misma regla de margen que con Pick Tickets.
"""
import math
from typing import Optional, Tuple

from app.modules.routing import config


def estimar_por_cubo(cube_total: float) -> Tuple[int, Optional[float]]:
    """(pallets estimados, llenado del último pallet; None si hay uno solo)."""
    capacidad = config.CFT_UTIL_POR_PALLET
    if cube_total <= 0:
        return 0, None
    pallets = max(1, math.ceil(cube_total / capacidad - 1e-9))
    if pallets < 2:
        return pallets, None
    resto = cube_total - capacidad * (pallets - 1)
    return pallets, round(resto / capacidad, 3)
