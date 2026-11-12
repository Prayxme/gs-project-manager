"""Acceso a PostgreSQL de la bandeja de Gmail (PDFs recibidos y su estado)."""
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple

from sqlalchemy import Engine, func, insert, select, update

from app.modules.order_intake.models import SCHEMA, inbox, metadata
from app.shared.db import prepare_engine, row_to_dict

# Columnas para listar (sin el PDF, que puede pesar).
_LISTA = [c for c in inbox.c if c.name != "pdf"]


class InboxRepository:
    def __init__(self, engine: Engine, create_tables: bool = False):
        self.engine = prepare_engine(engine, SCHEMA, metadata, create_tables)

    def ultimo_recibido(self) -> Optional[datetime]:
        with self.engine.connect() as c:
            return c.execute(select(func.max(inbox.c.received_at))).scalar()

    def mensajes_conocidos(self) -> Set[str]:
        with self.engine.connect() as c:
            return {r[0] for r in c.execute(select(inbox.c.message_id).distinct())}

    def agregar(self, fila: Dict) -> int:
        with self.engine.begin() as c:
            return c.execute(insert(inbox).values(**fila)).inserted_primary_key[0]

    def listar(self, estados: Optional[List[str]] = None, limit: int = 300) -> List[Dict]:
        q = select(*_LISTA).order_by(inbox.c.received_at.desc(), inbox.c.id.desc()).limit(limit)
        if estados:
            q = q.where(inbox.c.status.in_(estados))
        with self.engine.connect() as c:
            return [row_to_dict(r) for r in c.execute(q)]

    def contar(self, estado: str) -> int:
        with self.engine.connect() as c:
            return c.execute(select(func.count()).select_from(inbox).where(inbox.c.status == estado)).scalar()

    def obtener(self, item_id: int, con_pdf: bool = False) -> Optional[Dict]:
        cols = list(inbox.c) if con_pdf else _LISTA
        with self.engine.connect() as c:
            r = c.execute(select(*cols).where(inbox.c.id == item_id)).first()
        if r is None:
            return None
        d = dict(r._mapping)
        return d if con_pdf else row_to_dict(r)

    def pdfs_por_estado(self, estados: Tuple[str, ...]) -> List[Dict]:
        """(id, estado, PDF) de los registros a volver a comparar con la hoja."""
        q = select(inbox.c.id, inbox.c.status, inbox.c.pdf).where(inbox.c.status.in_(estados))
        with self.engine.connect() as c:
            return [dict(r._mapping) for r in c.execute(q)]

    def actualizar(self, item_id: int, **valores) -> None:
        with self.engine.begin() as c:
            c.execute(update(inbox).where(inbox.c.id == item_id).values(**valores))
