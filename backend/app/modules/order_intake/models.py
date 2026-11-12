"""Tablas del módulo Ingreso de Órdenes (schema PostgreSQL `order_intake`)."""
from sqlalchemy import (
    JSON, Column, DateTime, Index, Integer, LargeBinary, MetaData, String, Table, Text, UniqueConstraint,
)

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

# Bandeja de Gmail: un registro por PDF de Pick Tickets recibido (se guarda el PDF).
# status: PENDING (hay nuevas o revisiones) | NO_CHANGES (todo ya registrado)
#         APPLIED (escrito desde la app) | DISMISSED (descartado) | ERROR (no se pudo leer)
inbox = Table(
    "inbox", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("message_id", String(64), nullable=False),
    Column("filename", String(255), nullable=False),
    Column("subject", Text),
    Column("received_at", DateTime(timezone=True), nullable=False),
    Column("fetched_at", DateTime(timezone=True), nullable=False),
    Column("pdf", LargeBinary, nullable=False),
    Column("status", String(16), nullable=False),
    Column("summary", JSON),                            # {"NEW": n, "REVISION": n, "REGISTERED": n}
    Column("piktiks", JSON),                            # lista de PikTiks del PDF
    Column("error", Text),
    Column("checked_at", DateTime(timezone=True)),      # última comparación con la hoja
    Column("applied_at", DateTime(timezone=True)),
    UniqueConstraint("message_id", "filename", name="uq_inbox_message_file"),
    Index("ix_inbox_received_at", "received_at"),
    Index("ix_inbox_status", "status"),
)
