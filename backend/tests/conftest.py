import os
import sys
from pathlib import Path

# Permite `import app...` al ejecutar pytest desde backend/
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Las pruebas nunca arrancan tareas de fondo (revisión de Gmail, refresco del portal).
os.environ["GS_DISABLE_BACKGROUND_TASKS"] = "1"

import pytest  # noqa: E402


@pytest.fixture(autouse=True)
def sin_base_de_datos_real(monkeypatch):
    """Ninguna prueba abre la base de datos real: un repositorio que no fue sustituido por uno de
    SQLite responde "base no configurada" (503) en vez de leer o escribir datos del usuario."""
    from app.core import dependencies
    from app.core.database import DatabaseNotConfigured

    def _bloqueado():
        raise DatabaseNotConfigured("Las pruebas no usan la base de datos real.")

    monkeypatch.setattr(dependencies, "get_engine", _bloqueado)
