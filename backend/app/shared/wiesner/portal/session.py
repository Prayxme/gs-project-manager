"""Un solo cliente del portal para toda la aplicación: conserva la cookie de sesión y evita
iniciar sesión en cada consulta (lo usan el Monitor y el Routing)."""
import threading
from typing import Optional

from app.shared.wiesner.portal.client import PortalClient

_client: Optional[PortalClient] = None
_lock = threading.Lock()


def fetch_portal_html() -> str:
    """HTML de la lista de pick tickets (solo lectura: ajcmd_show_list)."""
    global _client
    with _lock:
        if _client is None:
            _client = PortalClient()
        return _client.fetch_routing_list()
