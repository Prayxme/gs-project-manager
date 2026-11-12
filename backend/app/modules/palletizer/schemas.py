from typing import List, Optional
from pydantic import BaseModel, Field


# --------------------------------------------------------------------------
# Solicitud de empaque (POST /api/pack)
# --------------------------------------------------------------------------
class Dimensions(BaseModel):
    length_in: float = Field(..., gt=0, description="Largo de la caja en pulgadas")
    width_in: float = Field(..., gt=0, description="Ancho de la caja en pulgadas")
    height_in: float = Field(..., gt=0, description="Alto de la caja en pulgadas")


class OrderItem(BaseModel):
    sku: str
    quantity: int = Field(..., gt=0, description="Cantidad de cartones/cajas")
    dimensions: Dimensions
    weight_lbs: float = Field(..., gt=0, description="Peso por caja en libras")
    # Trazabilidad. Los pallets NUNCA mezclan cajas de POs/DCs distintos.
    po: Optional[str] = None
    piktik: Optional[str] = None
    ship_to_dc: Optional[str] = None


class PalletConfig(BaseModel):
    length_in: float = Field(48.0, gt=0)
    width_in: float = Field(40.0, gt=0)
    base_height_in: float = Field(5.5, ge=0)
    max_total_height_in: float = Field(85.0, gt=0)
    # None = sin límite de peso por pallet (regla de negocio aún por confirmar).
    max_weight_lbs: Optional[float] = Field(None, gt=0)


class PackingRequest(BaseModel):
    order_id: str
    pallet_config: PalletConfig = PalletConfig()
    items: List[OrderItem]


# --------------------------------------------------------------------------
# Respuesta del parser de PDF (POST /api/parse-pdf)
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
    declared_cases: Optional[int] = None
    items: List[ParsedItem]


class ParsedPdfResponse(BaseModel):
    company: str
    cust_no: str
    orders: List[ParsedOrder]
    warnings: List[str] = []
