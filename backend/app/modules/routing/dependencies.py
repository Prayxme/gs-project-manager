"""Dependencias del Routing: lectura del portal de Wiesner (reemplazable en pruebas)."""
from typing import Callable

from app.shared.wiesner.portal import fetch_portal_html


def get_fetcher() -> Callable[[], str]:
    return fetch_portal_html
