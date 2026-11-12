"""Endpoints HTTP del Routing (/api/routing/...). Solo validan y delegan."""
import logging
from datetime import date
from typing import Callable, List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile

from app.core.errors import http_errors
from app.modules.routing import config, services
from app.modules.routing.dependencies import get_catalog, get_catalog_opcional, get_fetcher
from app.shared.dates import utc_now
from app.shared.pick_ticket import extraer_datos_pick_ticket
from app.shared.pick_ticket_catalog import PickTicketCatalog, fecha_del_archivo, registrar_pdf

router = APIRouter(prefix="/api/routing", tags=["Routing"])
log = logging.getLogger("routing")


def _al_catalogo(catalogo: Optional[PickTicketCatalog], filename: str, leido: dict) -> None:
    """Guarda el PDF subido para poder enrutar sus órdenes después desde el Monitor (si falla, no importa)."""
    if catalogo is None:
        return
    try:
        registrar_pdf(catalogo, b"", filename, fecha_del_archivo(filename) or utc_now(), "upload", leido=leido)
    except Exception as e:
        log.warning("Catálogo de Pick Tickets: %s", e)


@router.post("/plan")
def plan(files: List[UploadFile] = File(...), today: Optional[date] = Form(None),
         fetch_html: Callable[[], str] = Depends(get_fetcher),
         catalogo: Optional[PickTicketCatalog] = Depends(get_catalog_opcional)):
    """Lee los Pick Tickets (PDF), los concilia con el portal y propone los RTS.
    `today` = fecha del usuario (navegador); por defecto, la del servidor."""
    pdfs = []
    for f in files:
        if not (f.filename or "").lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail=f"{f.filename}: debe ser un PDF.")
        with http_errors((ValueError, 422, f"{f.filename}: "), (Exception, 500, f"{f.filename}: error leyendo el PDF: ")):
            leido = extraer_datos_pick_ticket(f.file.read())
        _al_catalogo(catalogo, f.filename, leido)
        pdfs.append({"filename": f.filename, **leido})
    return services.construir_plan(pdfs, services.leer_portal(fetch_html), today or date.today())


@router.get("/urgent")
def urgent(today: Optional[date] = None, days: int = Query(config.DIAS_URGENTE, ge=0, le=60),
           fetch_html: Callable[[], str] = Depends(get_fetcher),
           catalogo: PickTicketCatalog = Depends(get_catalog)):
    """Plan de las órdenes del portal sin routing que vencen hoy o en los próximos `days` días,
    con los Pick Tickets ya recibidos (sin subir PDFs)."""
    with http_errors((services.PortalNoDisponible, 502, None)):
        return services.plan_urgente(catalogo, services.leer_portal(fetch_html), today or date.today(), days)
