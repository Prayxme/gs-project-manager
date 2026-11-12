"""Motor de empaque de pallets (propio), compartido por el Paletizador 3D y el Routing.

Piezas:
  models.py        Linea / Pallet
  layer_patterns   patrón de capas óptimo por tipo de caja
  placement.py     mejor posición de una caja dentro de un pallet
  group_packer.py  empaque de una PO (pallets completos + huecos + consolidación)
  physics_engine   colisiones, soporte, validación y serialización
"""
from app.shared.packing.group_packer import empacar_grupo
from app.shared.packing.models import Linea, Pallet
from app.shared.packing.physics_engine import construir_pallet_dict, validar_pallet

__all__ = ["Linea", "Pallet", "construir_pallet_dict", "empacar_grupo", "validar_pallet"]
