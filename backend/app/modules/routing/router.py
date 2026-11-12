"""Endpoints HTTP del Routing (/api/routing/...). Solo validan y delegan."""
from datetime import date
from typing import Callable, List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.core.errors import http_errors
from app.modules.routing import services
from app.modules.routing.dependencies import get_fetcher
from app.shared.pick_ticket import extraer_datos_pick_ticket

router = APIRouter(prefix="/api/routing", tags=["Routing"])


@router.post("/plan")
def plan(files: List[UploadFile] = File(...), today: Optional[date] = Form(None),
         fetch_html: Callable[[], str] = Depends(get_fetcher)):
    """Lee los Pick Tickets (PDF), los concilia con el portal y propone los RTS.
    `today` = fecha del usuario (navegador); por defecto, la del servidor."""
    pdfs = []
    for f in files:
        if not (f.filename or "").lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail=f"{f.filename}: debe ser un PDF.")
        with http_errors((ValueError, 422, f"{f.filename}: "), (Exception, 500, f"{f.filename}: error leyendo el PDF: ")):
            pdfs.append({"filename": f.filename, **extraer_datos_pick_ticket(f.file.read())})
    return services.construir_plan(pdfs, services.leer_portal(fetch_html), today or date.today())
