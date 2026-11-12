"""Catálogo compartido de Pick Tickets leídos (schema pick_tickets).

Revision ID: 0005_pick_ticket_catalog
Revises: 0004_intake_inbox
Create Date: 2026-11-12
"""
import sqlalchemy as sa
from alembic import op

revision = "0005_pick_ticket_catalog"
down_revision = "0004_intake_inbox"
branch_labels = None
depends_on = None

S = "pick_tickets"


def upgrade() -> None:
    op.execute(f"CREATE SCHEMA IF NOT EXISTS {S}")
    op.create_table(
        "files",
        sa.Column("filename", sa.String(255), primary_key=True),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source", sa.String(16), nullable=False),
        sa.Column("orders", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error", sa.Text()),
        sa.Column("stored_at", sa.DateTime(timezone=True), nullable=False),
        schema=S,
    )
    op.create_table(
        "orders",
        sa.Column("piktik", sa.String(32), primary_key=True),
        sa.Column("po", sa.String(64)),
        sa.Column("cust_no", sa.String(32)),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.Column("source_file", sa.String(255), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        schema=S,
    )
    op.create_index("ix_pick_tickets_orders_po", "orders", ["po"], schema=S)


def downgrade() -> None:
    op.drop_table("orders", schema=S)
    op.drop_table("files", schema=S)
    op.execute(f"DROP SCHEMA IF EXISTS {S}")
