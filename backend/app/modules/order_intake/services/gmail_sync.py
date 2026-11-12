"""
Revisión de Gmail (solo lectura): guarda en la bandeja cada PDF de Pick Tickets nuevo y lo compara
con la hoja. NO escribe en la hoja: cada PDF queda pendiente hasta que el usuario lo apruebe.
"""
import logging
import threading
from datetime import date, datetime
from typing import Dict, Optional

from app.modules.order_intake import config
from app.modules.order_intake.inbox_repository import InboxRepository
from app.modules.order_intake.rules import inbox as reglas
from app.modules.order_intake.services.analysis import clasificar_pdf, leer_contexto
from app.modules.order_intake.services.catalog_sync import sincronizar_catalogo
from app.modules.order_intake.sheets_client import SheetsGateway
from app.shared.dates import utc_now
from app.shared.google.gmail import GmailReader
from app.shared.pick_ticket_catalog import PickTicketCatalog

log = logging.getLogger("order_intake.gmail")
_lock = threading.Lock()  # una revisión a la vez (botón manual y revisión automática)

# Resultado de la última revisión (se muestra en la pantalla).
ultima_revision: Dict = {"at": None, "ok": None, "error": "", "new": 0}


def _guardar_nuevos(repo: InboxRepository, gmail: GmailReader, hoy: date) -> int:
    desde = reglas.fecha_busqueda(repo.ultimo_recibido(), hoy, config.GMAIL_LOOKBACK_DAYS)
    consulta = reglas.consulta_gmail(config.GMAIL_SENDER, config.GMAIL_SUBJECT_PREFIX, desde)
    conocidos = repo.mensajes_conocidos()
    nuevos = 0
    for mid in reversed(gmail.buscar(consulta, max_results=500)):   # del más viejo al más nuevo
        if mid in conocidos:
            continue
        correo = gmail.correo(mid, ".pdf")
        for adj in correo.adjuntos:
            if not reglas.es_pdf_de_pick_tickets(adj.filename, config.GMAIL_ATTACHMENT_PREFIX):
                continue
            repo.agregar({
                "message_id": correo.id, "filename": adj.filename, "subject": correo.subject,
                "received_at": correo.received_at, "fetched_at": utc_now(),
                "pdf": gmail.descargar(correo.id, adj.attachment_id), "status": reglas.PENDING,
            })
            nuevos += 1
    return nuevos


def comparar_pendientes(repo: InboxRepository, gateway: SheetsGateway) -> int:
    """Vuelve a comparar con la hoja los PDFs pendientes (una sola lectura de Google)."""
    items = repo.pdfs_por_estado(reglas.REEVALUABLES)
    if not items:
        return 0
    ctx = leer_contexto(gateway)
    for it in items:
        resumen: Optional[Dict] = None
        error = None
        piktiks = None
        try:
            r = clasificar_pdf(it["pdf"], ctx)
            resumen = r["summary"]
            piktiks = [o["piktik"] for o in r["orders"]]
        except Exception as e:  # PDF ilegible: queda en ERROR con el motivo
            error = str(e) or type(e).__name__
        repo.actualizar(it["id"], status=reglas.nuevo_estado(it["status"], resumen, error),
                        summary=resumen, piktiks=piktiks, error=error, checked_at=utc_now())
    return len(items)


def _al_catalogo(repo: InboxRepository, catalogo: Optional[PickTicketCatalog]) -> None:
    """El catálogo es un servicio para otros módulos: si falla, la bandeja sigue funcionando."""
    if catalogo is None:
        return
    try:
        sincronizar_catalogo(repo, catalogo)
    except Exception as e:
        log.warning("Catálogo de Pick Tickets: %s", e)


def revisar_gmail(repo: InboxRepository, gmail: GmailReader, gateway: SheetsGateway,
                  hoy: Optional[date] = None, catalogo: Optional[PickTicketCatalog] = None) -> Dict:
    with _lock:
        try:
            nuevos = _guardar_nuevos(repo, gmail, hoy or datetime.now().date())
            _al_catalogo(repo, catalogo)
            revisados = comparar_pendientes(repo, gateway)
        except Exception as e:
            ultima_revision.update(at=utc_now(), ok=False, error=str(e), new=0)
            raise
        ultima_revision.update(at=utc_now(), ok=True, error="", new=nuevos)
        return {"new": nuevos, "checked": revisados, "pending": repo.contar(reglas.PENDING)}
