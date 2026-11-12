"""Valores que se declaran por PO en el portal de routing: lb, CFT y límite por RTS."""
import math

from app.modules.routing import config


def familia(codigo: str) -> str:
    """Con quién puede compartir RTS una PO: solo con su mismo cliente.
    BURL y MODE son ambos Burlington, pero se enrutan en portales distintos: van separados."""
    return codigo


def cft_declarado(codigo: str, pallets: int) -> int:
    return config.CFT_POR_PALLET.get(codigo, config.CFT_POR_PALLET_DEFECTO) * pallets


def peso_declarado(peso_cajas: float, pallets: int) -> int:
    """lb de las cajas + 45 lb por pallet, redondeado hacia arriba."""
    return math.ceil(peso_cajas + config.PALLET_PESO_LB * pallets)


def limite_pallets(codigo: str) -> int:
    return config.LIMITE_PALLETS.get(codigo, config.LIMITE_PALLETS_DEFECTO)
