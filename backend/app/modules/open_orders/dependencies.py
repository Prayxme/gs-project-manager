"""Dependencias del módulo: repositorio y descarga del portal."""
import threading
from typing import Callable, Optional

from app.core.dependencies import repository_dependency
from app.modules.open_orders.repository import OpenOrdersRepository
from app.shared.wiesner.portal import PortalClient

get_repository = repository_dependency(OpenOrdersRepository)

_client: Optional[PortalClient] = None
_client_lock = threading.Lock()


def fetch_portal_html() -> str:
    """Un solo cliente reutilizado: conserva la cookie y evita iniciar sesión en cada consulta."""
    global _client
    with _client_lock:
        if _client is None:
            _client = PortalClient()
        return _client.fetch_routing_list()


def get_fetcher() -> Callable[[], str]:
    return fetch_portal_html
