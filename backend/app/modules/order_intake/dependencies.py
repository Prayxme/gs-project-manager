"""Dependencias de FastAPI del Ingreso de Órdenes (las pruebas las sustituyen)."""
from fastapi import HTTPException
from googleapiclient.errors import HttpError

from app.core.dependencies import repository_dependency
from app.modules.order_intake.inbox_repository import InboxRepository
from app.modules.order_intake.repository import IntakeLog
from app.modules.order_intake.sheets_client import SheetsGateway
from app.shared.google.auth import GoogleNotAuthorized
from app.shared.google.gmail import GmailReader

get_log = repository_dependency(IntakeLog)
get_inbox = repository_dependency(InboxRepository)

# Errores de Google -> 502 con un mensaje legible.
GOOGLE_ERROR = (HttpError, 502, lambda e: f"Google respondió con error: {e.reason}")


def _google(factory):
    try:
        return factory()
    except GoogleNotAuthorized as e:
        raise HTTPException(status_code=503, detail=str(e))


def get_gateway() -> SheetsGateway:
    return _google(SheetsGateway)


def get_gmail() -> GmailReader:
    return _google(GmailReader)
