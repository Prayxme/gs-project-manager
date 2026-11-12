"""Dependencias del Routing: portal de Wiesner y catálogo de Pick Tickets (reemplazables en pruebas)."""
from typing import Callable, Optional

from fastapi import HTTPException

from app.core.dependencies import repository_dependency
from app.shared.pick_ticket_catalog import PickTicketCatalog
from app.shared.wiesner.portal import fetch_portal_html

get_catalog = repository_dependency(PickTicketCatalog)


def get_catalog_opcional() -> Optional[PickTicketCatalog]:
    """Para subir PDFs a mano el catálogo es un extra: sin base de datos, el plan se calcula igual."""
    try:
        return get_catalog()
    except HTTPException:
        return None


def get_fetcher() -> Callable[[], str]:
    return fetch_portal_html
