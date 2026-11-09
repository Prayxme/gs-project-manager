"""
Acceso a datos del monitor (PostgreSQL vía SQLAlchemy Core).

Las fechas/horas se devuelven como texto ISO en UTC terminado en 'Z' para que el
frontend las interprete siempre igual.
"""
from datetime import date, datetime, timezone
from typing import Dict, List, Optional

from sqlalchemy import Engine, func, insert, select, update

from app.modules.open_orders.models import SCHEMA, closed_orders, events, metadata, orders, runs, settings


def utc(dt: Optional[datetime]) -> Optional[datetime]:
    """Normaliza a UTC con zona (SQLite devuelve fechas sin zona en las pruebas)."""
    if dt is None:
        return None
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)


def iso(valor):
    if isinstance(valor, datetime):
        return utc(valor).strftime("%Y-%m-%dT%H:%M:%SZ")
    if isinstance(valor, date):
        return valor.isoformat()
    return valor


def _fila(row) -> Dict:
    return {k: iso(v) for k, v in row._mapping.items()}


class Store:
    def __init__(self, engine: Engine, create_tables: bool = False):
        """create_tables=True solo para pruebas; en producción la estructura la crea Alembic."""
        if engine.dialect.name == "sqlite":
            # SQLite (pruebas) no tiene schemas: se usan las tablas sin prefijo.
            engine = engine.execution_options(schema_translate_map={SCHEMA: None})
        self.engine = engine
        if create_tables:
            metadata.create_all(engine)

    # -- órdenes -----------------------------------------------------------------
    def load_orders(self) -> Dict[str, Dict]:
        with self.engine.connect() as c:
            rows = c.execute(select(orders)).all()
        out = {}
        for r in rows:
            d = dict(r.data)
            d.update(first_seen=iso(r.first_seen), last_seen=iso(r.last_seen),
                     last_change=r.last_change, last_change_at=iso(r.last_change_at))
            out[r.pick_ticket] = d
        return out

    # -- configuración ---------------------------------------------------------------
    def get_setting(self, key: str, default: str = "") -> str:
        with self.engine.connect() as c:
            v = c.execute(select(settings.c.value).where(settings.c.key == key)).scalar()
        return default if v is None else v

    def set_setting(self, key: str, value: str) -> None:
        with self.engine.begin() as c:
            if c.execute(update(settings).where(settings.c.key == key).values(value=value)).rowcount == 0:
                c.execute(insert(settings).values(key=key, value=value))

    # -- consultas -------------------------------------------------------------------
    def events(self, limit: int = 500, since: Optional[datetime] = None) -> List[Dict]:
        q = select(events).order_by(events.c.ts.desc(), events.c.id.desc()).limit(limit)
        if since is not None:
            q = q.where(events.c.ts >= since)
        with self.engine.connect() as c:
            return [_fila(r) for r in c.execute(q)]

    def closed(self, limit: int = 2000) -> List[Dict]:
        q = (select(closed_orders)
             .order_by(closed_orders.c.date_removed.desc(), closed_orders.c.pick_ticket.desc())
             .limit(limit))
        with self.engine.connect() as c:
            return [_fila(r) for r in c.execute(q)]

    def closed_pick_tickets(self) -> set:
        with self.engine.connect() as c:
            return set(c.execute(select(closed_orders.c.pick_ticket)).scalars())

    def count_closed(self) -> int:
        with self.engine.connect() as c:
            return c.execute(select(func.count()).select_from(closed_orders)).scalar_one()

    def last_runs(self, limit: int = 1) -> List[Dict]:
        with self.engine.connect() as c:
            return [_fila(r) for r in c.execute(select(runs).order_by(runs.c.id.desc()).limit(limit))]

    def last_ok_run(self) -> Optional[Dict]:
        with self.engine.connect() as c:
            r = c.execute(select(runs).where(runs.c.ok.is_(True)).order_by(runs.c.id.desc()).limit(1)).first()
        return _fila(r) if r else None
