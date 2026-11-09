"""
Motor de empaque propio (reemplaza la colocación de py3dbp).

Reglas de negocio:
  * Cada PO se empaca por separado: un pallet jamás mezcla POs ni DCs distintos.
  * Dentro de una PO sí se mezclan SKU para aprovechar huecos.
  * Lo más pesado va como base.
  * Cajas ordenadas en capas alineadas; límites del pallet siempre respetados.

Estrategia por PO:
  1. Por cada línea (SKU): patrón de capa óptimo -> pallets completos clonados.
  2. Los remanentes (de pesado a liviano) se colocan caja por caja en los huecos
     de los pallets existentes (gravedad + soporte >= 65 % + lo pesado abajo).
     Si no cabe en ninguno, se abre un pallet nuevo sembrado con el patrón ordenado.
  3. Consolidación: se intenta vaciar los pallets menos llenos moviendo sus cajas
     a huecos de otros pallets; si todas caben, el pallet sobrante desaparece.
"""
from dataclasses import dataclass
from itertools import permutations
from typing import Any, Dict, List, Optional, Tuple

from app.modules.palletizer.schemas import PackingRequest
from app.modules.palletizer.services.layer_patterns import Patron, mejor_patron_caja
from app.modules.palletizer.services.physics_engine import (
    EPS,
    PlacedBox,
    altura_asiento,
    construir_pallet_dict,
    puede_colocar,
    validar_pallet,
)


@dataclass(frozen=True)
class Linea:
    """Una línea de pedido: tipo de caja + cantidad + trazabilidad."""
    sku: str
    l: float
    w: float
    h: float
    weight: float
    qty: int
    po: str
    piktik: str
    dc: str

    @property
    def volumen(self) -> float:
        return self.l * self.w * self.h

    @property
    def clave(self) -> Tuple:
        return (self.sku, self.l, self.w, self.h, self.weight)


class Pallet:
    def __init__(self, boxes: Optional[List[PlacedBox]] = None):
        self.boxes: List[PlacedBox] = boxes or []
        self._fallos: set = set()  # tipos de caja que ya no caben (se limpia al cambiar)

    def agregar(self, b: PlacedBox) -> None:
        self.boxes.append(b)
        self._fallos.clear()

    def quitar(self, b: PlacedBox) -> None:
        self.boxes.remove(b)
        self._fallos.clear()

    @property
    def volumen(self) -> float:
        return sum(b.w * b.h * b.d for b in self.boxes)


# ----------------------------------------------------------------------------
# Búsqueda de la mejor posición para una caja dentro de un pallet
# ----------------------------------------------------------------------------
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


def _colocar_en_pallet(pallet: Pallet, ln: Linea, W: float, D: float, H: float,
                       peso_max: Optional[float]) -> Optional[PlacedBox]:
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


def _pallet_desde_patron(ln: Linea, patron: Patron, n: int) -> Pallet:
    boxes = [
        PlacedBox(ln.sku, x, y, z, w, h, d, ln.weight, ln.po, ln.piktik, ln.dc, ln.h)
        for (x, y, z, w, h, d) in patron.posiciones(n)
    ]
    return Pallet(boxes)


# ----------------------------------------------------------------------------
# Empaque de un grupo (una PO / un DC)
# ----------------------------------------------------------------------------
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
                    nueva = _colocar_en_pallet(q, ln, W, D, H, peso_max)
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


def _empacar_grupo(
    lineas: List[Linea], W: float, D: float, H: float, peso_max: Optional[float]
) -> Tuple[List[Pallet], List[Dict[str, Any]]]:
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
            pallets.append(_pallet_desde_patron(ln, patron, cap))
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
                if _colocar_en_pallet(p, ln, W, D, H, peso_max) is not None:
                    colocada = True
                    break
            if colocada:
                faltan -= 1
                continue
            n = min(faltan, cap)
            pallets.append(_pallet_desde_patron(ln, patron, n))
            faltan -= n

    # 3) Consolidación: vaciar pallets poco llenos en huecos de los demás
    _consolidar(pallets, W, D, H, peso_max)
    return pallets, no_colocadas


# ----------------------------------------------------------------------------
# API del servicio
# ----------------------------------------------------------------------------
def optimizar_orden_pallets(request: PackingRequest) -> Dict[str, Any]:
    config = request.pallet_config
    W, D = float(config.width_in), float(config.length_in)
    H = float(config.max_total_height_in - config.base_height_in)  # altura útil (79.5)
    peso_max = config.max_weight_lbs

    # Agrupar por (DC, PO): nunca se mezclan entre sí.
    grupos: Dict[Tuple[str, str], List[Linea]] = {}
    for it in request.items:
        ln = Linea(
            sku=it.sku.strip() or "SKU",
            l=it.dimensions.length_in, w=it.dimensions.width_in, h=it.dimensions.height_in,
            weight=it.weight_lbs, qty=it.quantity,
            po=(it.po or "").strip(), piktik=(it.piktik or "").strip(),
            dc=(it.ship_to_dc or "").strip(),
        )
        grupos.setdefault((ln.dc, ln.po), []).append(ln)

    response_pallets: List[Dict[str, Any]] = []
    no_colocadas: List[Dict[str, Any]] = []
    resumen_grupos: List[Dict[str, Any]] = []
    contador = 1
    vol_util = W * D * H

    for (dc, po) in sorted(grupos):
        lineas = grupos[(dc, po)]
        pallets, sobrantes = _empacar_grupo(lineas, W, D, H, peso_max)
        no_colocadas.extend(sobrantes)
        n_cajas = 0
        vol = 0.0
        for p in sorted(pallets, key=lambda q: (-q.volumen, -len(q.boxes))):
            d = construir_pallet_dict(p.boxes, config, f"PALLET-{contador}", po=po, dc=dc)
            errores = validar_pallet(p.boxes, W, D, H, peso_max)
            if errores:  # red de seguridad: nunca debería ocurrir
                d["metrics"]["voladizos_peligrosos"] = len(errores)
                d["metrics"]["alertas"] += errores
            response_pallets.append(d)
            contador += 1
            n_cajas += len(p.boxes)
            vol += p.volumen
        resumen_grupos.append({
            "po": po,
            "ship_to_dc": dc,
            "piktiks": sorted({ln.piktik for ln in lineas if ln.piktik}),
            "boxes_requested": sum(ln.qty for ln in lineas),
            "boxes_placed": n_cajas,
            "pallets": len(pallets),
            "volume_utilization_pct": round(100.0 * vol / (vol_util * len(pallets)), 1) if pallets else 0.0,
        })

    total_pedidas = sum(g["boxes_requested"] for g in resumen_grupos)
    total_colocadas = sum(g["boxes_placed"] for g in resumen_grupos)
    vol_total = sum(
        b["rendered_dimensions"]["width_in"] * b["rendered_dimensions"]["height_in"]
        * b["rendered_dimensions"]["length_in"]
        for p in response_pallets for b in p["placed_items"]
    )
    return {
        "order_id": request.order_id,
        "pallets": response_pallets,
        "unplaced_boxes": sum(u["count"] for u in no_colocadas),
        "unplaced": no_colocadas,
        "groups": resumen_grupos,
        "summary": {
            "total_pallets": len(response_pallets),
            "pallets_homogeneous": sum(1 for p in response_pallets if p["pallet_type"] == "HOMOGENEO"),
            "pallets_mixed": sum(1 for p in response_pallets if p["pallet_type"] == "MIXTO"),
            "boxes_requested": total_pedidas,
            "boxes_placed": total_colocadas,
            "volume_utilization_pct": round(
                100.0 * vol_total / (vol_util * len(response_pallets)), 1) if response_pallets else 0.0,
        },
    }
