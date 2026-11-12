"""Valores que se declaran por PO en el portal de routing: lb, CFT y límite por RTS."""
import math

from app.modules.routing import config
from app.shared.wiesner import BURLINGTON


def familia(codigo: str) -> str:
    """Clientes que se enrutan como uno solo: BURL y MODE son Burlington."""
    return "BURL" if codigo in BURLINGTON else codigo


def cft_declarado(codigo: str, pallets: int) -> int:
    return config.CFT_POR_PALLET.get(codigo, config.CFT_POR_PALLET_DEFECTO) * pallets


def peso_declarado(peso_cajas: float, pallets: int) -> int:
    """lb de las cajas + 45 lb por pallet, redondeado hacia arriba."""
    return math.ceil(peso_cajas + config.PALLET_PESO_LB * pallets)


def limite_pallets(codigo: str) -> int:
    return config.LIMITE_PALLETS.get(codigo, config.LIMITE_PALLETS_DEFECTO)
