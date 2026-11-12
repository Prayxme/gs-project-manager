"""Dependencias de FastAPI reutilizables por los módulos."""
from typing import Callable, Optional, TypeVar

from fastapi import HTTPException
from sqlalchemy import Engine

from app.core.database import DatabaseNotConfigured, get_engine

T = TypeVar("T")


def repository_dependency(factory: Callable[[Engine], T]) -> Callable[[], T]:
    """Crea (una sola vez) el repositorio de un módulo sobre la base de datos de la plataforma.
    Si la base no está configurada responde 503 con un mensaje claro."""
    instancia: Optional[T] = None

    def dependencia() -> T:
        nonlocal instancia
        if instancia is None:
            try:
                instancia = factory(get_engine())
            except DatabaseNotConfigured as e:
                raise HTTPException(status_code=503, detail=str(e))
        return instancia

    return dependencia
