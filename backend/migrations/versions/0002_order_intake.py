"""Módulo Ingreso de Órdenes: schema order_intake y su historial.

Revision ID: 0002_order_intake
Revises: 0001_open_orders
Create Date: 2026-11-12
"""
import sqlalchemy as sa
from alembic import op

revision = "0002_order_intake"
down_revision = "0001_open_orders"
branch_labels = None
depends_on = None

S = "order_intake"


def upgrade() -> None:
    op.execute(f"CREATE SCHEMA IF NOT EXISTS {S}")
    op.create_table(
        "intake_log",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("piktik", sa.String(32), nullable=False),
        sa.Column("po", sa.String(64)),
        sa.Column("store", sa.String(32)),
        sa.Column("action", sa.String(16), nullable=False),
        sa.Column("sheet_row", sa.Integer()),
        sa.Column("source", sa.String(16), nullable=False),
        sa.Column("source_ref", sa.Text()),
        sa.Column("details", sa.JSON()),
        schema=S,
    )
    op.create_index("ix_intake_log_piktik", "intake_log", ["piktik"], schema=S)
    op.create_index("ix_intake_log_ts", "intake_log", ["ts"], schema=S)


def downgrade() -> None:
    op.drop_table("intake_log", schema=S)
    op.execute(f"DROP SCHEMA IF EXISTS {S}")
