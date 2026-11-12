"""Endpoints HTTP del módulo Paletizador (/api/palletizer/...).
Solo validan y delegan; la lógica vive en services/."""
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.errors import http_errors
from app.modules.palletizer.schemas import PackingRequest
from app.modules.palletizer.services.packing_service import optimizar_orden_pallets
from app.shared.pick_ticket import extraer_datos_pick_ticket
from app.shared.pick_ticket.schemas import ParsedPdfResponse

router = APIRouter(prefix="/api/palletizer", tags=["Paletizador"])


@router.post("/parse-pdf", response_model=ParsedPdfResponse)
async def parse_pdf(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="El archivo proporcionado debe ser un documento PDF.")
    with http_errors((ValueError, 422, None), (Exception, 500, "Error analizando el archivo PDF: ")):
        content = await file.read()
        return extraer_datos_pick_ticket(content)


@router.post("/pack")
async def calculate_packing(request: PackingRequest):
    with http_errors((Exception, 500, "Error en el motor de optimización: ")):
        return optimizar_orden_pallets(request)
