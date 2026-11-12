"""Margen sobre la estimación de pallets.

Las órdenes llegan sin trabajar: solo conocemos las dimensiones de las cajas, no cómo quedarán
armadas. Por eso se enruta con un pequeño margen por encima (ejemplos del usuario: 2->3, 4->6,
7->9, 17->20; calibración: 15->18, 1->2).
"""
import math

TRAMOS = (        # (hasta n pallets estimados, pallets que se suman)
    (1, 1),
    (2, 1),
    (10, 2),
    (20, 3),
)
MARGEN_SOBRE_20 = 0.15


def pallets_a_enrutar(estimado: int) -> int:
    if estimado <= 0:
        return 0
    for hasta, extra in TRAMOS:
        if estimado <= hasta:
            return estimado + extra
    return math.ceil(estimado * (1 + MARGEN_SOBRE_20))
