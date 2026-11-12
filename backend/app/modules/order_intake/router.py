"""Endpoints del módulo Ingreso de Órdenes (/api/order-intake/...). Solo capa HTTP."""
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.core.errors import http_errors
from app.modules.order_intake import services
from app.modules.order_intake.dependencies import GOOGLE_ERROR, get_gateway, get_log
from app.modules.order_intake.repository import IntakeLog
from app.modules.order_intake.sheets_client import SheetsGateway

router = APIRouter(prefix="/api/order-intake", tags=["Ingreso de Órdenes"])


class IntakeOrder(BaseModel):
    piktik: str = Field(..., min_length=5)
    company: str
    store: str
    po: str = Field(..., min_length=1)
    containers: List[str] = []
    ship_date: str
    cancel_date: str
    ctns: int = Field(..., ge=0)


class ApplyRequest(BaseModel):
    orders: List[IntakeOrder]
    source_ref: str = ""


@router.post("/analyze")
async def analyze(file: UploadFile = File(...), gw: SheetsGateway = Depends(get_gateway)):
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="El archivo debe ser un PDF.")
    contenido = await file.read()
    with http_errors(GOOGLE_ERROR, (ValueError, 422, None)):
        r = services.analizar_pdf(contenido, gw)
    return {**r, "file_name": file.filename}


@router.post("/check")
def check(body: ApplyRequest, gw: SheetsGateway = Depends(get_gateway)):
    """Vuelve a clasificar órdenes (p. ej. después de corregirlas en pantalla)."""
    with http_errors(GOOGLE_ERROR):
        return services.analizar_ordenes([o.model_dump() for o in body.orders], gw)


@router.post("/apply")
def apply(body: ApplyRequest, gw: SheetsGateway = Depends(get_gateway), log: IntakeLog = Depends(get_log)):
    ordenes = [o.model_dump() for o in body.orders]
    with http_errors(GOOGLE_ERROR):
        return services.aplicar(ordenes, gw, log, source="manual", source_ref=body.source_ref)


@router.get("/suggestions")
def suggestions(gw: SheetsGateway = Depends(get_gateway)):
    with http_errors(GOOGLE_ERROR):
        return {"suggestions": services.sugerencias(gw)}


@router.get("/log")
def log(limit: int = 200, log: IntakeLog = Depends(get_log)):
    return {"log": log.recientes(limit)}
