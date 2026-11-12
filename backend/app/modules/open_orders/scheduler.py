"""
Actualización automática cada N minutos (se activa/desactiva desde la app).
Corre dentro del backend: funciona mientras el servidor esté encendido.
"""
import asyncio
import logging
import time
from typing import Callable, Optional

from app.modules.open_orders import config, services
from app.modules.open_orders.dependencies import fetch_portal_html, get_repository
from app.modules.open_orders.repository import OpenOrdersRepository

log = logging.getLogger("open_orders.scheduler")
CHEQUEO_S = 20


async def bucle_auto_refresh(
    get_repo: Callable[[], OpenOrdersRepository] = get_repository,
    fetch_html: Callable[[], str] = fetch_portal_html,
) -> None:
    ultimo_intento: Optional[float] = None
    ultimo_error = ""
    while True:
        try:
            repo = get_repo()
            if services.auto_refresh_activo(repo):
                ahora = time.monotonic()
                if ultimo_intento is None or ahora - ultimo_intento >= config.AUTO_REFRESH_MINUTES * 60:
                    ultimo_intento = ahora
                    await asyncio.to_thread(services.refresh, repo, fetch_html, "auto")
            else:
                ultimo_intento = None  # al reactivar, actualiza de inmediato
            ultimo_error = ""
        except asyncio.CancelledError:
            raise
        except Exception as e:  # el error de refresco queda además en la tabla runs
            msg = getattr(e, "detail", None) or str(e)
            if msg != ultimo_error:  # no repetir el mismo aviso cada 20 s
                log.warning("Monitor de órdenes: %s", msg)
                ultimo_error = msg
        await asyncio.sleep(CHEQUEO_S)
