"""Esquemas de la lectura de Pick Tickets (compartidos)."""
from typing import List, Optional

from pydantic import BaseModel


# --------------------------------------------------------------------------
# Respuesta del lector de Pick Tickets
# --------------------------------------------------------------------------
class ParsedItem(BaseModel):
    sku: str
    variant: str = ""
    cust_sku: str = ""
    qty: int
    l: float
    w: float
    h: float
    weight: float
    containers: List[str] = []


class ShipTo(BaseModel):
    """Destino del PO (columna SHIP TO del PDF). `key` = calle + código postal normalizados."""
    code: str = ""
    name: str = ""
    street: str = ""
    city: str = ""
    state: str = ""
    zip: str = ""
    text: str = ""
    key: str = ""


class ParsedOrder(BaseModel):
    piktik: str
    po: str
    cust_no: str = ""
    company: str = ""
    order_no: str = ""
    order_date: str = ""
    ship_date: str = ""
    cancel_date: str = ""
    containers: List[str] = []
    ship_to_dc: str = ""
    destination: str = ""
    pages: int = 1
    ship_to: Optional[ShipTo] = None
    declared_units: Optional[int] = None
    declared_cases: Optional[int] = None
    declared_weight: Optional[float] = None
    declared_cft: Optional[float] = None
    items: List[ParsedItem]


class ParsedPdfResponse(BaseModel):
    company: str
    cust_no: str
    orders: List[ParsedOrder]
    warnings: List[str] = []
