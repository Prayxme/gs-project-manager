"""ROSS / DDSD: peso mínimo por RTS.

Si la suma de lb de todas las POs del RTS ya llega a 3100, se declaran los valores reales.
Si no, al menos una PO debe declarar 3100 lb: se sube la más pesada (las demás quedan igual).
"""
from typing import Dict, List

from app.modules.routing import config


def aplicar_peso_minimo(codigo: str, pos: List[Dict]) -> None:
    """Modifica `weight` de la PO elegida y marca `weight_adjusted_from` con su valor real."""
    minimo = config.PESO_MINIMO_LB.get(codigo)
    if not minimo or not pos or sum(p["weight"] for p in pos) >= minimo:
        return
    mas_pesada = max(pos, key=lambda p: p["weight"])
    mas_pesada["weight_adjusted_from"] = mas_pesada["weight"]
    mas_pesada["weight"] = minimo
