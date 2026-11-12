"""Endpoints del módulo Ingreso de Órdenes (/api/order-intake/...). Solo capa HTTP."""
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.core.errors import http_errors
from app.modules.order_intake import services
from app.modules.order_intake.dependencies import GOOGLE_ERROR, get_gateway, get_inbox, get_log
from app.modules.order_intake.inbox_repository import InboxRepository
from app.modules.order_intake.inbox_router import NO_EXISTE
from app.modules.order_intake.inbox_router import router as inbox_router
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
    inbox_id: Optional[int] = None      # si las órdenes vienen de un PDF de la bandeja de Gmail


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
def apply(body: ApplyRequest, gw: SheetsGateway = Depends(get_gateway), log: IntakeLog = Depends(get_log),
          inbox: InboxRepository = Depends(get_inbox)):
    ordenes = [o.model_dump() for o in body.orders]
    with http_errors(NO_EXISTE, GOOGLE_ERROR):
        ref_gmail = services.inbox.referencia(inbox, body.inbox_id)
        r = services.aplicar(ordenes, gw, log, source="gmail" if ref_gmail else "manual",
                             source_ref=ref_gmail or body.source_ref)
        if body.inbox_id is not None:
            services.inbox.marcar_aplicado(inbox, body.inbox_id)
    return r


@router.get("/suggestions")
def suggestions(gw: SheetsGateway = Depends(get_gateway)):
    with http_errors(GOOGLE_ERROR):
        return {"suggestions": services.sugerencias(gw)}


@router.get("/log")
def log(limit: int = 200, log: IntakeLog = Depends(get_log)):
    return {"log": log.recientes(limit)}


router.include_router(inbox_router)
