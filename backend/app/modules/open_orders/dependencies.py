"""Dependencias del módulo: repositorio y descarga del portal."""
from typing import Callable

from app.core.dependencies import repository_dependency
from app.modules.open_orders.repository import OpenOrdersRepository
from app.shared.wiesner.portal import fetch_portal_html

get_repository = repository_dependency(OpenOrdersRepository)


def get_fetcher() -> Callable[[], str]:
    return fetch_portal_html
