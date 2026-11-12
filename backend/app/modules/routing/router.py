"""Endpoints HTTP del Routing (/api/routing/...). Solo validan y delegan."""
import logging
from datetime import date
from typing import Callable, List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile

from app.core.errors import http_errors
from app.modules.routing import services
from app.modules.routing.dependencies import get_catalog, get_catalog_opcional, get_fetcher
from app.shared.dates import utc_now
from app.shared.pick_ticket import extraer_datos_pick_ticket
from app.shared.pick_ticket_catalog import PickTicketCatalog, fecha_del_archivo, registrar_pdf
from app.shared.wiesner import STATUS_ORDER, URGENT_STATUSES

router = APIRouter(prefix="/api/routing", tags=["Routing"])
log = logging.getLogger("routing")

ESTADOS_ENRUTABLES = [s for s in STATUS_ORDER if s != "ROUTED"]


def _estados(pedidos: List[str]) -> List[str]:
    desconocidos = [s for s in pedidos if s not in ESTADOS_ENRUTABLES]
    if desconocidos:
        raise HTTPException(status_code=422, detail=f"Estado no válido: {', '.join(desconocidos)}. "
                                                    f"Use {', '.join(ESTADOS_ENRUTABLES)}.")
    return pedidos


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
         status: List[str] = Form([]), cust: Optional[str] = Form(None),
         fetch_html: Callable[[], str] = Depends(get_fetcher),
         catalogo: Optional[PickTicketCatalog] = Depends(get_catalog_opcional)):
    """Lee los Pick Tickets (PDF), los concilia con el portal y propone los RTS.
    `today` = fecha del usuario (navegador); por defecto, la del servidor.
    Con `status` (y `cust`) solo se toman de los PDFs las órdenes de esa selección del Monitor,
    junto con las que ya estaban en el catálogo."""
    estados = _estados(status)
    pdfs = []
    for f in files:
        if not (f.filename or "").lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail=f"{f.filename}: debe ser un PDF.")
        with http_errors((ValueError, 422, f"{f.filename}: "), (Exception, 500, f"{f.filename}: error leyendo el PDF: ")):
            leido = extraer_datos_pick_ticket(f.file.read())
        _al_catalogo(catalogo, f.filename, leido)
        pdfs.append({"filename": f.filename, **leido})
    portal, hoy = services.leer_portal(fetch_html), today or date.today()
    if not estados:
        return services.construir_plan(pdfs, portal, hoy)
    with http_errors((services.PortalNoDisponible, 502, None)):
        return services.plan_seleccion(catalogo, portal, hoy, estados, cust, pdfs)


@router.get("/selection")
def selection(status: List[str] = Query(..., description="Estados del Monitor: OVERDUE, LAST DAY, ..."),
              cust: Optional[str] = Query(None, description="Customer No, p. ej. BURL120"),
              today: Optional[date] = None,
              fetch_html: Callable[[], str] = Depends(get_fetcher),
              catalogo: PickTicketCatalog = Depends(get_catalog)):
    """Plan de las órdenes del portal sin routing que están en esos estados (y de ese Customer No),
    con los Pick Tickets ya recibidos (sin subir PDFs)."""
    with http_errors((services.PortalNoDisponible, 502, None)):
        return services.plan_seleccion(catalogo, services.leer_portal(fetch_html), today or date.today(),
                                       _estados(status), cust)


@router.get("/urgent")
def urgent(today: Optional[date] = None,
           fetch_html: Callable[[], str] = Depends(get_fetcher),
           catalogo: PickTicketCatalog = Depends(get_catalog)):
    """Atajo de /selection con los estados urgentes: vencidas, último día y atención."""
    with http_errors((services.PortalNoDisponible, 502, None)):
        return services.plan_seleccion(catalogo, services.leer_portal(fetch_html), today or date.today(),
                                       list(URGENT_STATUSES))
