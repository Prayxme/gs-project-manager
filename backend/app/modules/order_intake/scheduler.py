"""
Revisión automática de Gmail cada N minutos (INTAKE_GMAIL_POLL_MINUTES; 0 la desactiva).
Corre dentro del backend mientras el servidor esté encendido. Solo LEE: nada se escribe en la
hoja sin la aprobación del usuario.
"""
import asyncio
import logging

from app.modules.order_intake import config
from app.modules.order_intake.dependencies import get_inbox
from app.modules.order_intake.services.gmail_sync import revisar_gmail
from app.modules.order_intake.sheets_client import SheetsGateway
from app.shared.google.gmail import GmailReader

log = logging.getLogger("order_intake.scheduler")


def _una_revision() -> dict:
    return revisar_gmail(get_inbox(), GmailReader(), SheetsGateway())


async def bucle_gmail() -> None:
    if config.GMAIL_POLL_MINUTES <= 0:
        return
    ultimo_error = ""
    while True:
        try:
            r = await asyncio.to_thread(_una_revision)
            if r["new"]:
                log.info("Gmail: %s PDF(s) nuevos de Pick Tickets; %s pendientes.", r["new"], r["pending"])
            ultimo_error = ""
        except asyncio.CancelledError:
            raise
        except Exception as e:  # sin autorización, sin base de datos, sin red...
            msg = getattr(e, "detail", None) or str(e)
            if msg != ultimo_error:  # no repetir el mismo aviso en cada vuelta
                log.warning("Revisión de Gmail: %s", msg)
                ultimo_error = msg
        await asyncio.sleep(config.GMAIL_POLL_MINUTES * 60)
