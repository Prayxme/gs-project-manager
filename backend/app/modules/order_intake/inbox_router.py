"""Endpoints de la bandeja de Gmail (/api/order-intake/inbox/...). Solo capa HTTP."""
from urllib.parse import quote

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from app.core.errors import http_errors
from app.modules.order_intake import services
from app.modules.order_intake.dependencies import GOOGLE_ERROR, get_catalog, get_gateway, get_gmail, get_inbox
from app.modules.order_intake.inbox_repository import InboxRepository
from app.modules.order_intake.rules import inbox as reglas
from app.modules.order_intake.services.inbox import InboxItemNotFound
from app.modules.order_intake.sheets_client import SheetsGateway
from app.shared.google.gmail import GmailReader
from app.shared.pick_ticket_catalog import PickTicketCatalog

router = APIRouter(prefix="/inbox")
NO_EXISTE = (InboxItemNotFound, 404, None)


@router.get("")
def listar(all: bool = False, repo: InboxRepository = Depends(get_inbox)):
    """Pendientes (o todos con ?all=true), cuántos quedan y el resultado de la última revisión."""
    return services.inbox.listar(repo, todos=all)


@router.post("/check")
def revisar_ahora(repo: InboxRepository = Depends(get_inbox), gmail: GmailReader = Depends(get_gmail),
                  gw: SheetsGateway = Depends(get_gateway), catalogo: PickTicketCatalog = Depends(get_catalog)):
    """Busca correos nuevos en Gmail y vuelve a comparar los pendientes con la hoja."""
    with http_errors(GOOGLE_ERROR):
        return services.revisar_gmail(repo, gmail, gw, catalogo=catalogo)


@router.post("/{item_id}/analyze")
def analizar(item_id: int, repo: InboxRepository = Depends(get_inbox), gw: SheetsGateway = Depends(get_gateway)):
    with http_errors(NO_EXISTE, GOOGLE_ERROR, (ValueError, 422, None)):
        return services.inbox.analizar_item(repo, item_id, gw)


@router.post("/{item_id}/dismiss")
def descartar(item_id: int, repo: InboxRepository = Depends(get_inbox)):
    with http_errors(NO_EXISTE):
        return services.inbox.cambiar_estado(repo, item_id, reglas.DISMISSED)


@router.post("/{item_id}/restore")
def restaurar(item_id: int, repo: InboxRepository = Depends(get_inbox)):
    with http_errors(NO_EXISTE):
        return services.inbox.cambiar_estado(repo, item_id, reglas.PENDING)


@router.get("/{item_id}/pdf")
def ver_pdf(item_id: int, repo: InboxRepository = Depends(get_inbox)):
    with http_errors(NO_EXISTE):
        archivo = services.inbox.pdf(repo, item_id)
    return Response(archivo["content"], media_type="application/pdf",
                    headers={"Content-Disposition": f"inline; filename*=UTF-8''{quote(archivo['filename'])}"})
