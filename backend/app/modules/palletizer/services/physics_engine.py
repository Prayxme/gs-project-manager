"""
Reglas físicas del pallet, independientes de cualquier librería de empaque.

Sistema de coordenadas (pulgadas, origen en la esquina del pallet):
  x = ancho del pallet (40), z = largo del pallet (48), y = altura sobre la base.

Reglas:
  - Impenetrabilidad (AABB): ninguna caja atraviesa a otra.
  - Dentro de límites: 0 <= x+w <= W, 0 <= z+d <= D, y+h <= H útil.
  - Soporte basal >= 65 % (o apoyada directamente en el piso del pallet).
  - Peso: una caja no descansa sobre cajas más livianas (lo pesado va abajo).
  - Centro de gravedad horizontal dentro del 15 % del centro (alerta).
"""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from app.modules.palletizer.config import (
    EPSILON_SOLAPE,
    TOLERANCIA_ALTURA_SOPORTE,
    TOLERANCIA_DESBALANCE_COG,
    UMBRAL_MINIMO_SOPORTE,
)

EPS = 1e-6  # holgura numérica de punto flotante en comparaciones de límites


@dataclass
class PlacedBox:
    sku: str
    x: float
    y: float
    z: float
    w: float   # extensión en x
    h: float   # extensión en y
    d: float   # extensión en z
    weight: float
    po: str = ""
    piktik: str = ""
    dc: str = ""
    alto_orig: float = 0.0  # alto declarado de la caja (para preferir orientación "de pie")

    @property
    def x2(self) -> float:
        return self.x + self.w

    @property
    def z2(self) -> float:
        return self.z + self.d

    @property
    def top(self) -> float:
        return self.y + self.h

    def copy(self) -> "PlacedBox":
        return PlacedBox(self.sku, self.x, self.y, self.z, self.w, self.h, self.d,
                         self.weight, self.po, self.piktik, self.dc, self.alto_orig)


def _solape_1d(a1: float, a2: float, b1: float, b2: float) -> float:
    return min(a2, b2) - max(a1, b1)


def altura_asiento(boxes: List[PlacedBox], x: float, z: float, w: float, d: float) -> float:
    """Techo más alto debajo de la huella (x, z, w, d); 0 si no hay obstáculos."""
    y = 0.0
    for b in boxes:
        if _solape_1d(x, x + w, b.x, b.x2) > EPSILON_SOLAPE and _solape_1d(z, z + d, b.z, b.z2) > EPSILON_SOLAPE:
            if b.top > y:
                y = b.top
    return y


def soporte(
    boxes: List[PlacedBox], x: float, y: float, z: float, w: float, d: float
) -> Tuple[float, List[PlacedBox]]:
    """(ratio de soporte basal, cajas que lo proporcionan)."""
    if y <= TOLERANCIA_ALTURA_SOPORTE:
        return 1.0, []
    area = 0.0
    apoyos: List[PlacedBox] = []
    for b in boxes:
        if abs(b.top - y) <= TOLERANCIA_ALTURA_SOPORTE:
            ix = _solape_1d(x, x + w, b.x, b.x2)
            iz = _solape_1d(z, z + d, b.z, b.z2)
            if ix > 0 and iz > 0:
                area += ix * iz
                apoyos.append(b)
    base = w * d
    return (area / base if base > 0 else 0.0), apoyos


def puede_colocar(
    boxes: List[PlacedBox],
    x: float, y: float, z: float, w: float, h: float, d: float,
    weight: float,
    W: float, D: float, H: float,
    peso_max: Optional[float] = None,
) -> bool:
    if x < -EPS or z < -EPS or x + w > W + EPS or z + d > D + EPS or y + h > H + EPS:
        return False
    if peso_max is not None and sum(b.weight for b in boxes) + weight > peso_max + EPS:
        return False
    ratio, apoyos = soporte(boxes, x, y, z, w, d)
    if ratio < UMBRAL_MINIMO_SOPORTE - EPS:
        return False
    # Lo pesado va abajo: nunca sobre una caja más liviana.
    return all(weight <= a.weight + EPS for a in apoyos)


def validar_pallet(
    boxes: List[PlacedBox], W: float, D: float, H: float, peso_max: Optional[float] = None
) -> List[str]:
    """Verificación independiente de un pallet terminado. Lista vacía = válido."""
    errores: List[str] = []
    for i, b in enumerate(boxes):
        if b.x < -EPS or b.z < -EPS or b.y < -EPS or b.x2 > W + EPS or b.z2 > D + EPS or b.top > H + EPS:
            errores.append(f"{b.sku}#{i}: fuera de los límites del pallet")
        for j in range(i + 1, len(boxes)):
            o = boxes[j]
            if (_solape_1d(b.x, b.x2, o.x, o.x2) > EPSILON_SOLAPE
                    and _solape_1d(b.z, b.z2, o.z, o.z2) > EPSILON_SOLAPE
                    and _solape_1d(b.y, b.top, o.y, o.top) > EPSILON_SOLAPE):
                errores.append(f"{b.sku}#{i} y {o.sku}#{j}: se atraviesan")
        ratio, apoyos = soporte([o for o in boxes if o is not b], b.x, b.y, b.z, b.w, b.d)
        if ratio < UMBRAL_MINIMO_SOPORTE - EPS:
            errores.append(f"{b.sku}#{i}: soporte {ratio:.0%} < {UMBRAL_MINIMO_SOPORTE:.0%}")
        if any(b.weight > a.weight + EPS for a in apoyos):
            errores.append(f"{b.sku}#{i}: descansa sobre una caja más liviana")
    if peso_max is not None and sum(b.weight for b in boxes) > peso_max + EPS:
        errores.append("peso total excede el máximo del pallet")
    return errores


def analizar_equilibrio(
    boxes: List[PlacedBox], pallet_w: float, pallet_l: float
) -> Tuple[Dict[str, float], str, List[str]]:
    total = sum(b.weight for b in boxes)
    if total <= 0:
        return {"x": 0.0, "z": 0.0}, "VACIA", []
    cog_x = sum(b.weight * (b.x + b.w / 2.0) for b in boxes) / total
    cog_z = sum(b.weight * (b.z + b.d / 2.0) for b in boxes) / total
    warnings: List[str] = []
    status = "ESTABLE"
    if abs(cog_x - pallet_w / 2.0) > pallet_w * TOLERANCIA_DESBALANCE_COG:
        status = "INESTABLE"
        warnings.append(f"Desbalance lateral (CoG X: {cog_x:.1f} in).")
    if abs(cog_z - pallet_l / 2.0) > pallet_l * TOLERANCIA_DESBALANCE_COG:
        status = "INESTABLE"
        warnings.append(f"Desbalance frontal (CoG Z: {cog_z:.1f} in).")
    return {"x": round(cog_x, 2), "z": round(cog_z, 2)}, status, warnings


def construir_pallet_dict(
    boxes: List[PlacedBox], config: Any, pallet_id: str, po: str = "", dc: str = ""
) -> Dict[str, Any]:
    """Serializa un pallet para el frontend. Coordenadas y dimensiones a 1 decimal
    (evita huellas duplicadas por coma flotante). 'y' incluye la altura de la base."""
    net_height = float(config.max_total_height_in - config.base_height_in)
    cog, status_eq, warn_eq = analizar_equilibrio(boxes, config.width_in, config.length_in)
    vol_cajas = sum(b.w * b.h * b.d for b in boxes)
    vol_util = config.width_in * config.length_in * net_height
    base_h = float(config.base_height_in)

    ordenadas = sorted(boxes, key=lambda b: (round(b.y, 3), round(b.z, 3), round(b.x, 3)))
    placed = []
    for idx, b in enumerate(ordenadas):
        placed.append({
            "step_order": idx + 1,
            "sku": b.sku,
            "po": b.po,
            "piktik": b.piktik,
            "ship_to_dc": b.dc,
            "weight_lbs": round(b.weight, 3),
            "position": {"x": round(b.x, 1), "y": round(b.y + base_h, 1), "z": round(b.z, 1)},
            "rendered_dimensions": {
                "width_in": round(b.w, 1), "height_in": round(b.h, 1), "length_in": round(b.d, 1)
            },
        })

    skus: Dict[str, int] = {}
    for b in boxes:
        skus[b.sku] = skus.get(b.sku, 0) + 1
    altura = max((b.top for b in boxes), default=0.0)

    return {
        "pallet_id": pallet_id,
        "po": po,
        "ship_to_dc": dc,
        "pallet_type": "HOMOGENEO" if len(skus) == 1 else "MIXTO",
        "metrics": {
            "total_weight_lbs": round(sum(b.weight for b in boxes), 2),
            "boxes_count": len(boxes),
            "sku_breakdown": skus,
            "volume_utilization_pct": round(100.0 * vol_cajas / vol_util, 1) if vol_util > 0 else 0.0,
            "max_height_in": round(altura + base_h, 1),
            "balance_status": status_eq,
            "center_of_gravity": cog,
            "voladizos_peligrosos": 0,
            "alertas": warn_eq,
        },
        "placed_items": placed,
    }
