"""Estructuras de trabajo del motor de empaque: línea de pedido y pallet en construcción."""
from dataclasses import dataclass
from typing import List, Optional, Tuple

from app.shared.packing.physics_engine import PlacedBox


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
