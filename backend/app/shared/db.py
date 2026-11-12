"""Apoyo común para los repositorios de base de datos de cada módulo."""
from typing import Dict

from sqlalchemy import Engine, MetaData

from app.shared.dates import to_json


def prepare_engine(engine: Engine, schema: str, metadata: MetaData, create_tables: bool = False) -> Engine:
    """Ajusta el engine al schema del módulo.
    En PostgreSQL las tablas viven en su schema (p. ej. open_orders.orders).
    SQLite (pruebas) no tiene schemas: se usan las tablas sin prefijo.
    create_tables=True solo para pruebas; en producción la estructura la crea Alembic."""
    if engine.dialect.name == "sqlite":
        engine = engine.execution_options(schema_translate_map={schema: None})
    if create_tables:
        metadata.create_all(engine)
    return engine


def row_to_dict(row) -> Dict:
    """Fila SQLAlchemy -> dict con fechas en texto ISO (UTC con 'Z')."""
    return {k: to_json(v) for k, v in row._mapping.items()}
