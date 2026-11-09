"""
Actualización automática cada N minutos (se activa/desactiva desde la app).
Corre dentro del backend: funciona mientras el servidor esté encendido.
"""
import asyncio
import logging
import time
from typing import Callable, Optional

from app.modules.open_orders import config, service
from app.modules.open_orders.store import Store

log = logging.getLogger("open_orders.scheduler")
CHEQUEO_S = 20


async def bucle_auto_refresh(get_store: Callable[[], Store], fetch_html: Callable[[], str]) -> None:
    ultimo_intento: Optional[float] = None
    while True:
        try:
            store = get_store()
            if service.auto_refresh_activo(store):
                ahora = time.monotonic()
                if ultimo_intento is None or ahora - ultimo_intento >= config.AUTO_REFRESH_MINUTES * 60:
                    ultimo_intento = ahora
                    await asyncio.to_thread(service.refresh, store, fetch_html, "auto")
            else:
                ultimo_intento = None  # al reactivar, actualiza de inmediato
        except asyncio.CancelledError:
            raise
        except Exception as e:  # el error queda registrado en la tabla runs
            log.warning("Actualización automática falló: %s", e)
        await asyncio.sleep(CHEQUEO_S)
