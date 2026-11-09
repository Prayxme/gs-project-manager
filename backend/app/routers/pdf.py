from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.schemas import ParsedPdfResponse
from app.services.pdf_service import extraer_datos_pick_ticket

router = APIRouter(prefix="/api", tags=["WMS PDF Ingestion"])

@router.post("/parse-pdf", response_model=ParsedPdfResponse)
async def parse_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="El archivo proporcionado debe ser un documento PDF.")
        
    try:
        content = await file.read()
        return extraer_datos_pick_ticket(content)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analizando el archivo PDF: {str(e)}")