"""
Lectura de Gmail con la cuenta del usuario (permiso gmail.readonly: no marca, mueve ni borra nada).
Genérico: cada módulo arma su propia búsqueda.
"""
import base64
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Iterator, List, Optional

from googleapiclient.discovery import build

from app.shared.google import auth as google_auth


@dataclass
class Adjunto:
    filename: str
    attachment_id: str
    size: int


@dataclass
class Correo:
    id: str
    thread_id: str
    subject: str
    sender: str
    received_at: datetime
    adjuntos: List[Adjunto] = field(default_factory=list)


def _cabecera(payload: dict, nombre: str) -> str:
    for h in payload.get("headers", []):
        if h.get("name", "").lower() == nombre.lower():
            return h.get("value", "")
    return ""


def _partes(payload: dict) -> Iterator[dict]:
    yield payload
    for p in payload.get("parts", []) or []:
        yield from _partes(p)


class GmailReader:
    def __init__(self, service=None):
        self._svc = service or build(
            "gmail", "v1", credentials=google_auth.credenciales(), cache_discovery=False
        ).users()

    def buscar(self, query: str, max_results: int = 100) -> List[str]:
        """Ids de los mensajes que cumplen la búsqueda (sintaxis de Gmail), del más reciente al más viejo."""
        ids: List[str] = []
        token: Optional[str] = None
        while len(ids) < max_results:
            r = self._svc.messages().list(userId="me", q=query, pageToken=token,
                                          maxResults=min(100, max_results - len(ids))).execute()
            ids += [m["id"] for m in r.get("messages", [])]
            token = r.get("nextPageToken")
            if not token:
                break
        return ids

    def correo(self, message_id: str, extension: str = "") -> Correo:
        """Encabezados y adjuntos (opcionalmente solo los que terminan en `extension`)."""
        m = self._svc.messages().get(userId="me", id=message_id, format="full").execute()
        payload = m.get("payload", {})
        adjuntos = [
            Adjunto(p["filename"], p["body"]["attachmentId"], int(p["body"].get("size", 0)))
            for p in _partes(payload)
            if p.get("filename") and p.get("body", {}).get("attachmentId")
            and p["filename"].lower().endswith(extension.lower())
        ]
        return Correo(
            id=m["id"], thread_id=m.get("threadId", ""),
            subject=_cabecera(payload, "Subject"), sender=_cabecera(payload, "From"),
            received_at=datetime.fromtimestamp(int(m.get("internalDate", 0)) / 1000, tz=timezone.utc),
            adjuntos=adjuntos,
        )

    def descargar(self, message_id: str, attachment_id: str) -> bytes:
        r = self._svc.messages().attachments().get(userId="me", messageId=message_id, id=attachment_id).execute()
        return base64.urlsafe_b64decode(r["data"])
