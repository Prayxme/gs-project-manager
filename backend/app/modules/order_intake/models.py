"""Tablas del módulo Ingreso de Órdenes (schema PostgreSQL `order_intake`)."""
from sqlalchemy import JSON, Column, DateTime, Index, Integer, MetaData, String, Table, Text

SCHEMA = "order_intake"
metadata = MetaData(schema=SCHEMA)

# Historial de todo lo escrito en la hoja (auditoría).
intake_log = Table(
    "intake_log", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("ts", DateTime(timezone=True), nullable=False),
    Column("piktik", String(32), nullable=False),
    Column("po", String(64)),
    Column("store", String(32)),
    Column("action", String(16), nullable=False),      # NEW | REVISION
    Column("sheet_row", Integer),
    Column("source", String(16), nullable=False),      # manual | gmail
    Column("source_ref", Text),                         # nombre del PDF / id del correo
    Column("details", JSON),                            # valores escritos o diferencias
    Index("ix_intake_log_piktik", "piktik"),
    Index("ix_intake_log_ts", "ts"),
)
