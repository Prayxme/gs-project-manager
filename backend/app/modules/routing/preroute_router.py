"""Endpoints de Pre Routing (/api/routing/preroute/...): POs sin Pick Ticket, estimadas por cubo."""
from datetime import date
from typing import Callable, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.core.errors import http_errors
from app.modules.routing import services
from app.modules.routing.dependencies import get_catalog_opcional, get_fetcher
from app.modules.routing.rules.preroute import normalizar
from app.modules.routing.schemas import PreRoutePlanRequest
from app.modules.routing.services.preroute import plan_preroute
from app.modules.routing.services.preroute_excel import leer_excel
from app.shared.pick_ticket_catalog import PickTicketCatalog

router = APIRouter(prefix="/preroute")

EXTENSIONES = (".xlsx", ".xlsm")


@router.post("/parse")
def parse(file: UploadFile = File(...)):
    """Lee el Excel de Pre Routing y devuelve sus líneas ya limpias, para revisarlas antes de calcular."""
    if not (file.filename or "").lower().endswith(EXTENSIONES):
        raise HTTPException(status_code=400, detail=f"{file.filename}: debe ser un Excel (.xlsx).")
    with http_errors((ValueError, 422, f"{file.filename}: ")):
        lineas, avisos = normalizar(leer_excel(file.file.read()))
    return {"filename": file.filename, "lines": lineas, "warnings": avisos}


@router.post("/plan")
def plan(body: PreRoutePlanRequest,
         fetch_html: Callable[[], str] = Depends(get_fetcher),
         catalogo: Optional[PickTicketCatalog] = Depends(get_catalog_opcional)):
    """Estima por cubo las POs de las líneas y propone los RTS (mismas reglas que con Pick Tickets)."""
    crudas = [ln.model_dump() for ln in body.lines]
    return plan_preroute(crudas, services.leer_portal(fetch_html), body.today or date.today(), catalogo)
