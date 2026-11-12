"""Tablas del catálogo de Pick Tickets (schema PostgreSQL `pick_tickets`), compartido por los módulos."""
from sqlalchemy import JSON, Column, DateTime, Index, Integer, MetaData, String, Table, Text

SCHEMA = "pick_tickets"
metadata = MetaData(schema=SCHEMA)

# Cada PDF ya procesado (para no volver a leerlo), con cuántos PikTiks trajo o por qué falló.
files = Table(
    "files", metadata,
    Column("filename", String(255), primary_key=True),
    Column("received_at", DateTime(timezone=True), nullable=False),
    Column("source", String(16), nullable=False),          # gmail | upload
    Column("orders", Integer, nullable=False, server_default="0"),
    Column("error", Text),
    Column("stored_at", DateTime(timezone=True), nullable=False),
)

# Un registro por PikTik con la orden ya leída (líneas con dimensiones, totales, SHIP TO).
# Si el mismo PikTik llega en varios PDFs, vale el del PDF recibido más recientemente.
orders = Table(
    "orders", metadata,
    Column("piktik", String(32), primary_key=True),
    Column("po", String(64)),
    Column("cust_no", String(32)),
    Column("data", JSON, nullable=False),
    Column("source_file", String(255), nullable=False),
    Column("received_at", DateTime(timezone=True), nullable=False),
    Index("ix_pick_tickets_orders_po", "po"),
)
