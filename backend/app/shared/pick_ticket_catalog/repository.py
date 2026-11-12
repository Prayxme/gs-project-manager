"""Acceso a datos del catálogo de Pick Tickets."""
from datetime import datetime
from typing import Dict, Iterable, List, Optional, Set

from sqlalchemy import Engine, insert, select, update

from app.shared.dates import as_utc, utc_now
from app.shared.db import prepare_engine
from app.shared.pick_ticket_catalog.models import SCHEMA, files, metadata, orders

LOTE = 500  # PikTiks por consulta (límite de parámetros en un IN)


class PickTicketCatalog:
    def __init__(self, engine: Engine, create_tables: bool = False):
        """create_tables=True solo para pruebas; en producción la estructura la crea Alembic."""
        self.engine = prepare_engine(engine, SCHEMA, metadata, create_tables)

    def archivos_conocidos(self) -> Set[str]:
        with self.engine.connect() as c:
            return {r[0] for r in c.execute(select(files.c.filename))}

    def guardar(self, filename: str, received_at: datetime, source: str,
                ordenes: List[Dict], error: Optional[str] = None) -> int:
        """Registra el PDF y sus PikTiks en una transacción. Devuelve cuántos PikTiks quedaron de este PDF
        (un PikTik ya guardado desde un PDF más reciente no se reemplaza)."""
        recibido = as_utc(received_at)
        guardados = 0
        with self.engine.begin() as c:
            if c.execute(select(files.c.filename).where(files.c.filename == filename)).first() is None:
                c.execute(insert(files).values(filename=filename, received_at=recibido, source=source,
                                               orders=len(ordenes), error=error, stored_at=utc_now()))
            for o in ordenes:
                valores = {"po": o.get("po"), "cust_no": o.get("cust_no"), "data": o,
                           "source_file": filename, "received_at": recibido}
                previo = c.execute(select(orders.c.received_at).where(orders.c.piktik == o["piktik"])).first()
                if previo is None:
                    c.execute(insert(orders).values(piktik=o["piktik"], **valores))
                elif as_utc(previo[0]) <= recibido:
                    c.execute(update(orders).where(orders.c.piktik == o["piktik"]).values(**valores))
                else:
                    continue
                guardados += 1
        return guardados

    def ordenes(self, piktiks: Iterable[str]) -> Dict[str, Dict]:
        """{piktik: orden leída} de los PikTiks pedidos que estén en el catálogo."""
        lista = list(dict.fromkeys(piktiks))
        out: Dict[str, Dict] = {}
        with self.engine.connect() as c:
            for i in range(0, len(lista), LOTE):
                q = select(orders.c.piktik, orders.c.data).where(orders.c.piktik.in_(lista[i:i + LOTE]))
                out.update({r.piktik: dict(r.data) for r in c.execute(q)})
        return out
