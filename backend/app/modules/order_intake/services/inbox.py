"""Acciones del usuario sobre la bandeja de Gmail: abrir un PDF para revisarlo, descartarlo o
restaurarlo, y marcarlo como escrito."""
from typing import Dict, Optional

from app.modules.order_intake.inbox_repository import InboxRepository
from app.modules.order_intake.rules import inbox as reglas
from app.modules.order_intake.services.analysis import analizar_pdf
from app.modules.order_intake.services.gmail_sync import ultima_revision
from app.modules.order_intake.sheets_client import SheetsGateway
from app.shared.dates import to_json, utc_now


class InboxItemNotFound(LookupError):
    pass


def _item(repo: InboxRepository, item_id: int, con_pdf: bool = False) -> Dict:
    item = repo.obtener(item_id, con_pdf=con_pdf)
    if item is None:
        raise InboxItemNotFound(f"No existe el registro {item_id} en la bandeja.")
    return item


def listar(repo: InboxRepository, todos: bool = False) -> Dict:
    estados = None if todos else [reglas.PENDING, reglas.ERROR]
    return {
        "items": repo.listar(estados),
        "pending": repo.contar(reglas.PENDING),
        "last_check": {**ultima_revision, "at": to_json(ultima_revision["at"])},
    }


def analizar_item(repo: InboxRepository, item_id: int, gateway: SheetsGateway) -> Dict:
    """Análisis completo del PDF guardado (igual que subirlo a mano) y estado actualizado."""
    item = _item(repo, item_id, con_pdf=True)
    r = analizar_pdf(item["pdf"], gateway)
    repo.actualizar(item_id, status=reglas.nuevo_estado(item["status"], r["summary"], None),
                    summary=r["summary"], piktiks=[o["piktik"] for o in r["orders"]],
                    error=None, checked_at=utc_now())
    return {**r, "file_name": item["filename"], "inbox_id": item_id, "subject": item["subject"]}


def cambiar_estado(repo: InboxRepository, item_id: int, estado: str) -> Dict:
    """DISMISSED (descartar) o PENDING (restaurar: se vuelve a comparar en la próxima revisión)."""
    _item(repo, item_id)
    repo.actualizar(item_id, status=estado)
    return _item(repo, item_id)


def marcar_aplicado(repo: InboxRepository, item_id: int) -> None:
    repo.actualizar(item_id, status=reglas.APPLIED, applied_at=utc_now())


def pdf(repo: InboxRepository, item_id: int) -> Dict:
    item = _item(repo, item_id, con_pdf=True)
    return {"filename": item["filename"], "content": item["pdf"]}


def referencia(repo: InboxRepository, item_id: Optional[int]) -> Optional[str]:
    """Texto para el historial de escrituras cuando la orden viene de Gmail."""
    if item_id is None:
        return None
    return f"Gmail: {_item(repo, item_id)['filename']}"
