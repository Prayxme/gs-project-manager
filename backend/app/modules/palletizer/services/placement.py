"""Búsqueda de la mejor posición para una caja dentro de un pallet (gravedad + física)."""
from itertools import permutations
from typing import List, Optional, Tuple

from app.modules.palletizer.services.layer_patterns import Patron
from app.modules.palletizer.services.models import Linea, Pallet
from app.modules.palletizer.services.physics_engine import EPS, PlacedBox, altura_asiento, puede_colocar


def _orientaciones(l: float, w: float, h: float) -> Tuple[List[Tuple], List[Tuple]]:
    """(de pie, otras). Cada una es (extensión x, alto, extensión z)."""
    unicas = {tuple(p) for p in permutations((l, w, h))}
    de_pie, otras = [], []
    for ext_x, alto, ext_z in sorted(unicas):
        (de_pie if abs(alto - h) < EPS else otras).append((ext_x, alto, ext_z))
    return de_pie, otras


def _mejor_en_orientaciones(
    boxes: List[PlacedBox], oris: List[Tuple], weight: float, W: float, D: float, H: float,
    peso_max: Optional[float],
) -> Optional[Tuple[Tuple, Tuple]]:
    """Posición válida más baja (y luego más al fondo / a la izquierda) entre los puntos candidatos."""
    mejor = None
    for (w, h, d) in oris:
        xs = {0.0, round(W - w, 3)}
        zs = {0.0, round(D - d, 3)}
        for b in boxes:
            xs.update((round(b.x, 3), round(b.x2, 3), round(b.x - w, 3)))
            zs.update((round(b.z, 3), round(b.z2, 3), round(b.z - d, 3)))
        xs = [x for x in xs if -EPS <= x <= W - w + EPS]
        zs = [z for z in zs if -EPS <= z <= D - d + EPS]
        for z in zs:
            for x in xs:
                y = round(altura_asiento(boxes, x, z, w, d), 3)
                if y + h > H + EPS:
                    continue
                if not puede_colocar(boxes, x, y, z, w, h, d, weight, W, D, H, peso_max):
                    continue
                score = (y, round(z, 3), round(x, 3))
                if mejor is None or score < mejor[0]:
                    mejor = (score, (x, y, z, w, h, d))
    return mejor


def colocar_en_pallet(pallet: Pallet, ln: Linea, W: float, D: float, H: float,
                      peso_max: Optional[float]) -> Optional[PlacedBox]:
    """Coloca una caja de la línea en el pallet (o None si no cabe en ningún sitio)."""
    if ln.clave in pallet._fallos:
        return None
    de_pie, otras = _orientaciones(ln.l, ln.w, ln.h)
    # Se prefiere la caja "de pie"; solo se rota si de pie no cabe en ningún sitio.
    res = _mejor_en_orientaciones(pallet.boxes, de_pie, ln.weight, W, D, H, peso_max)
    if res is None:
        res = _mejor_en_orientaciones(pallet.boxes, otras, ln.weight, W, D, H, peso_max)
    if res is None:
        pallet._fallos.add(ln.clave)
        return None
    x, y, z, w, h, d = res[1]
    box = PlacedBox(ln.sku, x, y, z, w, h, d, ln.weight, ln.po, ln.piktik, ln.dc, ln.h)
    pallet.agregar(box)
    return box


def pallet_desde_patron(ln: Linea, patron: Patron, n: int) -> Pallet:
    """Pallet con n cajas de la línea dispuestas según el patrón de capas."""
    boxes = [
        PlacedBox(ln.sku, x, y, z, w, h, d, ln.weight, ln.po, ln.piktik, ln.dc, ln.h)
        for (x, y, z, w, h, d) in patron.posiciones(n)
    ]
    return Pallet(boxes)
