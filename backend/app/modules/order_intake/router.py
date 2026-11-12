"""Endpoints del módulo Ingreso de Órdenes (/api/order-intake/...)."""
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from googleapiclient.errors import HttpError
from pydantic import BaseModel, Field

from app.core.database import DatabaseNotConfigured, get_engine
from app.modules.order_intake import service
from app.shared.google.auth import GoogleNotAuthorized
from app.modules.order_intake.sheets_client import SheetsGateway

router = APIRouter(prefix="/api/order-intake", tags=["Ingreso de Órdenes"])
_log: Optional[service.IntakeLog] = None


def get_log() -> service.IntakeLog:
    global _log
    if _log is None:
        try:
            _log = service.IntakeLog(get_engine())
        except DatabaseNotConfigured as e:
            raise HTTPException(status_code=503, detail=str(e))
    return _log


def get_gateway() -> SheetsGateway:
    try:
        return SheetsGateway()
    except GoogleNotAuthorized as e:
        raise HTTPException(status_code=503, detail=str(e))


def _google(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except HttpError as e:
        raise HTTPException(status_code=502, detail=f"Google Sheets respondió con error: {e.reason}")


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
    try:
        r = _google(service.analizar_pdf, contenido, gw)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return {**r, "file_name": file.filename}


@router.post("/check")
def check(body: ApplyRequest, gw: SheetsGateway = Depends(get_gateway)):
    """Vuelve a clasificar órdenes (p. ej. después de corregirlas en pantalla)."""
    return _google(service.analizar_ordenes, [o.model_dump() for o in body.orders], gw)


@router.post("/apply")
def apply(body: ApplyRequest, gw: SheetsGateway = Depends(get_gateway), log: service.IntakeLog = Depends(get_log)):
    ordenes = [o.model_dump() for o in body.orders]
    return _google(service.aplicar, ordenes, gw, log, source="manual", source_ref=body.source_ref)


@router.get("/suggestions")
def suggestions(gw: SheetsGateway = Depends(get_gateway)):
    return {"suggestions": _google(service.sugerencias, gw)}


@router.get("/log")
def log(limit: int = 200, log: service.IntakeLog = Depends(get_log)):
    return {"log": log.recientes(limit)}
