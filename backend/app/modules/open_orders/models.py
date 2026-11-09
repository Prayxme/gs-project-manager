"""Tablas del módulo Órdenes Abiertas (schema PostgreSQL `open_orders`)."""
from sqlalchemy import (
    JSON, Boolean, Column, Date, DateTime, Index, Integer, MetaData, String, Table, Text,
)

SCHEMA = "open_orders"
metadata = MetaData(schema=SCHEMA)

# Foto actual de las órdenes abiertas en el portal (una fila por pick ticket).
orders = Table(
    "orders", metadata,
    Column("pick_ticket", String(32), primary_key=True),
    Column("data", JSON, nullable=False),
    Column("first_seen", DateTime(timezone=True), nullable=False),
    Column("last_seen", DateTime(timezone=True), nullable=False),
    Column("last_change", String(64), nullable=False, server_default=""),
    Column("last_change_at", DateTime(timezone=True)),
)

# Historial de cambios (uno por cada cambio detectado, con fecha y hora).
events = Table(
    "events", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("ts", DateTime(timezone=True), nullable=False),
    Column("pick_ticket", String(32), nullable=False),
    Column("po", String(64)),
    Column("cust", String(32)),
    Column("event", String(64), nullable=False),
    Column("old_value", Text),
    Column("new_value", Text),
    Index("ix_events_ts", "ts"),
    Index("ix_events_pick_ticket", "pick_ticket"),
)

# Órdenes que salieron del portal (enviadas, removidas, canceladas) + histórico importado.
closed_orders = Table(
    "closed_orders", metadata,
    Column("pick_ticket", String(32), primary_key=True),
    Column("date_removed", Date, nullable=False),
    Column("removed_at", DateTime(timezone=True)),
    Column("final_status", String(16), nullable=False),
    Column("reason", String(64), nullable=False),
    Column("po", String(64)),
    Column("cust", String(32)),
    Column("ship_date", String(16)),
    Column("cancel_date", String(16)),
    Column("cfrm_number", String(128)),
    Column("appt_date", String(16)),
    Column("notes", Text),
    Column("source", String(16), nullable=False, server_default="monitor"),
    # Si una fila importada se reclasifica, aquí queda el valor original (auditoría).
    Column("original_status", String(16)),
    Column("original_reason", String(64)),
    Index("ix_closed_date_removed", "date_removed"),
)

# Bitácora de cada actualización desde el portal.
runs = Table(
    "runs", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("started_at", DateTime(timezone=True), nullable=False),
    Column("finished_at", DateTime(timezone=True)),
    Column("trigger", String(16), nullable=False),
    Column("ok", Boolean, nullable=False, server_default="false"),
    Column("total", Integer),
    Column("new_count", Integer),
    Column("changed_count", Integer),
    Column("removed_count", Integer),
    Column("error", Text),
)

# Preferencias del módulo (p. ej. actualización automática).
settings = Table(
    "settings", metadata,
    Column("key", String(64), primary_key=True),
    Column("value", Text, nullable=False),
)
