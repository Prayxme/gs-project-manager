"""
Acceso a datos del monitor (PostgreSQL vía SQLAlchemy Core). Todo el SQL del módulo vive aquí.

Las fechas/horas se devuelven como texto ISO en UTC terminado en 'Z' para que el
frontend las interprete siempre igual.
"""
from datetime import datetime
from typing import Dict, Iterable, List, Optional, Tuple

from sqlalchemy import Engine, delete, func, insert, select, update

from app.modules.open_orders.models import SCHEMA, closed_orders, events, metadata, orders, runs, settings
from app.shared.db import prepare_engine, row_to_dict
from app.shared.dates import to_iso_utc


class OpenOrdersRepository:
    def __init__(self, engine: Engine, create_tables: bool = False):
        """create_tables=True solo para pruebas; en producción la estructura la crea Alembic."""
        self.engine = prepare_engine(engine, SCHEMA, metadata, create_tables)

    # -- órdenes -----------------------------------------------------------------
    def load_orders(self) -> Dict[str, Dict]:
        with self.engine.connect() as c:
            rows = c.execute(select(orders)).all()
        out = {}
        for r in rows:
            d = dict(r.data)
            d.update(first_seen=to_iso_utc(r.first_seen), last_seen=to_iso_utc(r.last_seen),
                     last_change=r.last_change, last_change_at=to_iso_utc(r.last_change_at))
            out[r.pick_ticket] = d
        return out

    def save_sync(self, nuevas: List[Dict], actualizadas: List[Tuple[str, Dict]], cerradas: List[Dict],
                  borrar: Iterable[str], eventos: List[Dict]) -> None:
        """Aplica el resultado de una actualización en UNA transacción."""
        with self.engine.begin() as c:
            for fila in nuevas:
                c.execute(insert(orders).values(**fila))
            for pt, valores in actualizadas:
                c.execute(update(orders).where(orders.c.pick_ticket == pt).values(**valores))
            for fila in cerradas:
                c.execute(insert(closed_orders).values(**fila))
            for pt in borrar:
                c.execute(delete(orders).where(orders.c.pick_ticket == pt))
            if eventos:
                c.execute(insert(events), eventos)

    # -- bitácora de actualizaciones ---------------------------------------------------
    def start_run(self, inicio: datetime, trigger: str) -> int:
        with self.engine.begin() as c:
            return c.execute(insert(runs).values(started_at=inicio, trigger=trigger, ok=False)
                             .returning(runs.c.id)).scalar_one()

    def finish_run(self, run_id: int, fin: datetime, ok: bool, stats: Optional[Dict] = None,
                   error: Optional[str] = None) -> None:
        valores = {"finished_at": fin, "ok": ok, "error": error}
        if stats:
            valores.update(total=stats["total"], new_count=stats["new"],
                           changed_count=stats["changed"], removed_count=stats["removed"])
        with self.engine.begin() as c:
            c.execute(update(runs).where(runs.c.id == run_id).values(**valores))

    def last_runs(self, limit: int = 1) -> List[Dict]:
        with self.engine.connect() as c:
            return [row_to_dict(r) for r in c.execute(select(runs).order_by(runs.c.id.desc()).limit(limit))]

    def last_ok_run(self) -> Optional[Dict]:
        with self.engine.connect() as c:
            r = c.execute(select(runs).where(runs.c.ok.is_(True)).order_by(runs.c.id.desc()).limit(1)).first()
        return row_to_dict(r) if r else None

    # -- historial y cerradas ------------------------------------------------------------
    def events(self, limit: int = 500, since: Optional[datetime] = None) -> List[Dict]:
        q = select(events).order_by(events.c.ts.desc(), events.c.id.desc()).limit(limit)
        if since is not None:
            q = q.where(events.c.ts >= since)
        with self.engine.connect() as c:
            return [row_to_dict(r) for r in c.execute(q)]

    def closed(self, limit: int = 2000) -> List[Dict]:
        q = (select(closed_orders)
             .order_by(closed_orders.c.date_removed.desc(), closed_orders.c.pick_ticket.desc())
             .limit(limit))
        with self.engine.connect() as c:
            return [row_to_dict(r) for r in c.execute(q)]

    def closed_pick_tickets(self) -> set:
        with self.engine.connect() as c:
            return set(c.execute(select(closed_orders.c.pick_ticket)).scalars())

    def count_closed(self) -> int:
        with self.engine.connect() as c:
            return c.execute(select(func.count()).select_from(closed_orders)).scalar_one()

    def insert_closed(self, filas: List[Dict]) -> None:
        if filas:
            with self.engine.begin() as c:
                c.execute(insert(closed_orders), filas)

    # -- configuración ---------------------------------------------------------------
    def get_setting(self, key: str, default: str = "") -> str:
        with self.engine.connect() as c:
            v = c.execute(select(settings.c.value).where(settings.c.key == key)).scalar()
        return default if v is None else v

    def set_setting(self, key: str, value: str) -> None:
        with self.engine.begin() as c:
            if c.execute(update(settings).where(settings.c.key == key).values(value=value)).rowcount == 0:
                c.execute(insert(settings).values(key=key, value=value))
