"""Valores que se declaran por PO en el portal de routing: lb, CFT y límite por RTS."""
import math

from app.modules.routing import config


def familia(cust: str) -> str:
    """Con quién puede compartir RTS una PO: solo con su mismo Customer No.
    BURL120, BURL240 y BURL150 son divisiones de Burlington que se enrutan por separado (igual en
    las demás tiendas); BURL y MODE, además, se enrutan en portales distintos."""
    return (cust or "").strip().upper()


def cft_declarado(codigo: str, pallets: int) -> int:
    return config.CFT_POR_PALLET.get(codigo, config.CFT_POR_PALLET_DEFECTO) * pallets


def peso_declarado(peso_cajas: float, pallets: int) -> int:
    """lb de las cajas + 45 lb por pallet, redondeado hacia arriba."""
    return math.ceil(peso_cajas + config.PALLET_PESO_LB * pallets)


def limite_pallets(codigo: str) -> int:
    return config.LIMITE_PALLETS.get(codigo, config.LIMITE_PALLETS_DEFECTO)
