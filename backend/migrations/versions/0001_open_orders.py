"""Módulo Órdenes Abiertas: schema open_orders y sus tablas.

Revision ID: 0001_open_orders
Revises:
Create Date: 2026-11-09
"""
import sqlalchemy as sa
from alembic import op

revision = "0001_open_orders"
down_revision = None
branch_labels = None
depends_on = None

S = "open_orders"


def upgrade() -> None:
    op.execute(f"CREATE SCHEMA IF NOT EXISTS {S}")

    op.create_table(
        "orders",
        sa.Column("pick_ticket", sa.String(32), primary_key=True),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.Column("first_seen", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_change", sa.String(64), nullable=False, server_default=""),
        sa.Column("last_change_at", sa.DateTime(timezone=True)),
        schema=S,
    )
    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("pick_ticket", sa.String(32), nullable=False),
        sa.Column("po", sa.String(64)),
        sa.Column("cust", sa.String(32)),
        sa.Column("event", sa.String(64), nullable=False),
        sa.Column("old_value", sa.Text()),
        sa.Column("new_value", sa.Text()),
        schema=S,
    )
    op.create_index("ix_events_ts", "events", ["ts"], schema=S)
    op.create_index("ix_events_pick_ticket", "events", ["pick_ticket"], schema=S)
    op.create_table(
        "closed_orders",
        sa.Column("pick_ticket", sa.String(32), primary_key=True),
        sa.Column("date_removed", sa.Date(), nullable=False),
        sa.Column("removed_at", sa.DateTime(timezone=True)),
        sa.Column("final_status", sa.String(16), nullable=False),
        sa.Column("reason", sa.String(64), nullable=False),
        sa.Column("po", sa.String(64)),
        sa.Column("cust", sa.String(32)),
        sa.Column("ship_date", sa.String(16)),
        sa.Column("cancel_date", sa.String(16)),
        sa.Column("cfrm_number", sa.String(128)),
        sa.Column("appt_date", sa.String(16)),
        sa.Column("notes", sa.Text()),
        sa.Column("source", sa.String(16), nullable=False, server_default="monitor"),
        sa.Column("original_status", sa.String(16)),
        sa.Column("original_reason", sa.String(64)),
        schema=S,
    )
    op.create_index("ix_closed_date_removed", "closed_orders", ["date_removed"], schema=S)
    op.create_table(
        "runs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("trigger", sa.String(16), nullable=False),
        sa.Column("ok", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("total", sa.Integer()),
        sa.Column("new_count", sa.Integer()),
        sa.Column("changed_count", sa.Integer()),
        sa.Column("removed_count", sa.Integer()),
        sa.Column("error", sa.Text()),
        schema=S,
    )
    op.create_table(
        "settings",
        sa.Column("key", sa.String(64), primary_key=True),
        sa.Column("value", sa.Text(), nullable=False),
        schema=S,
    )


def downgrade() -> None:
    for tabla in ("settings", "runs", "closed_orders", "events", "orders"):
        op.drop_table(tabla, schema=S)
    op.execute(f"DROP SCHEMA IF EXISTS {S}")
