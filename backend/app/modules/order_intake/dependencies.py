"""Dependencias de FastAPI del Ingreso de Órdenes (las pruebas las sustituyen)."""
from fastapi import HTTPException
from googleapiclient.errors import HttpError

from app.core.dependencies import repository_dependency
from app.modules.order_intake.repository import IntakeLog
from app.modules.order_intake.sheets_client import SheetsGateway
from app.shared.google.auth import GoogleNotAuthorized

get_log = repository_dependency(IntakeLog)

# Errores de Google -> 502 con un mensaje legible.
GOOGLE_ERROR = (HttpError, 502, lambda e: f"Google Sheets respondió con error: {e.reason}")


def get_gateway() -> SheetsGateway:
    try:
        return SheetsGateway()
    except GoogleNotAuthorized as e:
        raise HTTPException(status_code=503, detail=str(e))
