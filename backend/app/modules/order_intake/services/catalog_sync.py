"""Copia al catálogo compartido de Pick Tickets los PDFs de la bandeja que aún no estén en él
(los nuevos de Gmail y, la primera vez, todos los ya guardados)."""
from app.modules.order_intake.inbox_repository import InboxRepository
from app.shared.pick_ticket_catalog import PickTicketCatalog, registrar_pdf

MAX_ARCHIVOS = 5000


def sincronizar_catalogo(repo: InboxRepository, catalogo: PickTicketCatalog) -> int:
    """Devuelve cuántos PDFs se leyeron hacia el catálogo."""
    conocidos = catalogo.archivos_conocidos()
    pendientes = [it for it in repo.listar(limit=MAX_ARCHIVOS) if it["filename"] not in conocidos]
    for it in reversed(pendientes):          # del más viejo al más nuevo
        item = repo.obtener(it["id"], con_pdf=True)
        registrar_pdf(catalogo, item["pdf"], item["filename"], item["received_at"], "gmail")
    return len(pendientes)
