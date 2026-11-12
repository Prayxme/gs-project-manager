"""Margen sobre la estimación de pallets.

Las órdenes llegan sin trabajar: solo conocemos las dimensiones de las cajas, no cómo quedarán
armadas. Por eso se enruta con un pequeño margen por encima (ejemplos del usuario: 2->3, 4->6,
7->9, 17->20; calibración: 15->18, 1->2).

Si el último pallet estimado va casi vacío comparado con los demás (p. ej. al 30 %), ese pallet
ya es en parte margen: se suma uno menos (4 -> 5 en vez de 4 -> 6).
"""
import math
from typing import Optional

from app.modules.routing import config

TRAMOS = (        # (hasta n pallets estimados, pallets que se suman)
    (1, 1),
    (2, 1),
    (10, 2),
    (20, 3),
)
MARGEN_SOBRE_20 = 0.15


def margen_base(estimado: int) -> int:
    for hasta, extra in TRAMOS:
        if estimado <= hasta:
            return extra
    return math.ceil(estimado * (1 + MARGEN_SOBRE_20)) - estimado


def ultima_pallet_baja(ultima_llena: Optional[float]) -> bool:
    return ultima_llena is not None and ultima_llena <= config.ULTIMA_PALLET_BAJA


def pallets_a_enrutar(estimado: int, ultima_llena: Optional[float] = None) -> int:
    """`ultima_llena`: volumen del pallet menos lleno / promedio de los demás (None si hay uno solo)."""
    if estimado <= 0:
        return 0
    extra = margen_base(estimado)
    if ultima_pallet_baja(ultima_llena) and extra > config.MARGEN_MINIMO:
        extra -= 1
    return estimado + extra
