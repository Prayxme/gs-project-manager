"""
Empaque de un grupo (una PO de un DC). Estrategia:
  1. Por cada línea (SKU): patrón de capa óptimo -> pallets completos clonados.
  2. Los remanentes (de pesado a liviano) se colocan caja por caja en los huecos
     de los pallets existentes (gravedad + soporte >= 65 % + lo pesado abajo).
     Si no cabe en ninguno, se abre un pallet nuevo sembrado con el patrón ordenado.
  3. Consolidación: se intenta vaciar los pallets menos llenos moviendo sus cajas
     a huecos de otros pallets; si todas caben, el pallet sobrante desaparece.
"""
from typing import Any, Dict, List, Optional, Tuple

from app.shared.packing.layer_patterns import Patron, mejor_patron_caja
from app.shared.packing.models import Linea, Pallet
from app.shared.packing.physics_engine import PlacedBox
from app.shared.packing.placement import colocar_en_pallet, pallet_desde_patron


def _linea_de_caja(b: PlacedBox) -> Linea:
    dims = [b.w, b.h, b.d]
    h0 = b.alto_orig or b.h
    dims.remove(min(dims, key=lambda v: abs(v - h0)))  # queda (l, w) originales
    return Linea(b.sku, dims[0], dims[1], h0, b.weight, 1, b.po, b.piktik, b.dc)


def _consolidar(pallets: List[Pallet], W: float, D: float, H: float, peso_max: Optional[float]) -> None:
    vol_util = W * D * H
    cambio = True
    while cambio:
        cambio = False
        for p in sorted(pallets, key=lambda q: q.volumen):
            libre_otros = sum(vol_util - q.volumen for q in pallets if q is not p)
            if p.volumen > libre_otros:
                continue
            otros = [q for q in pallets if q is not p]
            movidas: List[Tuple[Pallet, PlacedBox]] = []
            ok = True
            for b in sorted(p.boxes, key=lambda c: (-c.weight, -(c.w * c.h * c.d))):
                ln = _linea_de_caja(b)
                destino = None
                for q in sorted(otros, key=lambda q: -q.volumen):
                    nueva = colocar_en_pallet(q, ln, W, D, H, peso_max)
                    if nueva is not None:
                        destino = (q, nueva)
                        break
                if destino is None:
                    ok = False
                    break
                movidas.append(destino)
            if ok:
                pallets.remove(p)
                cambio = True
                break
            for q, nueva in movidas:  # revertir
                q.quitar(nueva)


def empacar_grupo(
    lineas: List[Linea], W: float, D: float, H: float, peso_max: Optional[float]
) -> Tuple[List[Pallet], List[Dict[str, Any]]]:
    """(pallets, cajas que no caben en ningún pallet)."""
    pallets: List[Pallet] = []
    no_colocadas: List[Dict[str, Any]] = []
    remanentes: List[Tuple[Linea, Patron, int]] = []

    # 1) Pallets completos por línea (patrón óptimo clonado)
    for ln in lineas:
        patron = mejor_patron_caja((ln.l, ln.w, ln.h), ln.h, W, D, H)
        cap = patron.capacidad if patron else 0
        if patron and peso_max is not None:
            cap = min(cap, int(peso_max // ln.weight))
        if patron is None or cap < 1:
            no_colocadas.append({"sku": ln.sku, "po": ln.po, "piktik": ln.piktik,
                                 "count": ln.qty, "reason": "la caja no cabe en el pallet"})
            continue
        completos, resto = divmod(ln.qty, cap)
        for _ in range(completos):
            pallets.append(pallet_desde_patron(ln, patron, cap))
        if resto:
            remanentes.append((ln, patron, resto))

    # 2) Remanentes: de pesado a liviano, rellenando huecos antes de abrir pallets
    remanentes.sort(key=lambda r: (-r[0].weight, -r[0].volumen, r[0].sku))
    for ln, patron, resto in remanentes:
        cap = patron.capacidad if peso_max is None else min(patron.capacidad, int(peso_max // ln.weight))
        faltan = resto
        while faltan > 0:
            colocada = False
            for p in sorted(pallets, key=lambda q: -q.volumen):
                if colocar_en_pallet(p, ln, W, D, H, peso_max) is not None:
                    colocada = True
                    break
            if colocada:
                faltan -= 1
                continue
            n = min(faltan, cap)
            pallets.append(pallet_desde_patron(ln, patron, n))
            faltan -= n

    # 3) Consolidación: vaciar pallets poco llenos en huecos de los demás
    _consolidar(pallets, W, D, H, peso_max)
    return pallets, no_colocadas
