"""Acceso a PostgreSQL del Ingreso de Órdenes: bitácora de lo escrito en la hoja."""
from typing import Dict, List

from sqlalchemy import Engine, insert, select

from app.modules.order_intake.models import SCHEMA, intake_log, metadata
from app.shared.db import prepare_engine, row_to_dict


class IntakeLog:
    def __init__(self, engine: Engine, create_tables: bool = False):
        self.engine = prepare_engine(engine, SCHEMA, metadata, create_tables)

    def registrar(self, filas: List[Dict]) -> None:
        if filas:
            with self.engine.begin() as c:
                c.execute(insert(intake_log), filas)

    def recientes(self, limit: int = 200) -> List[Dict]:
        """Últimas entradas, la más reciente primero (ts en ISO UTC con 'Z')."""
        q = select(intake_log).order_by(intake_log.c.ts.desc(), intake_log.c.id.desc()).limit(limit)
        with self.engine.connect() as c:
            return [row_to_dict(r) for r in c.execute(q)]
