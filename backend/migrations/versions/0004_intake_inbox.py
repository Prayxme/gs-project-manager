"""Ingreso de Órdenes, Fase 2: bandeja de PDFs recibidos por Gmail.

Revision ID: 0004_intake_inbox
Revises: 0003_reclassify_imported_removed
Create Date: 2026-11-12
"""
import sqlalchemy as sa
from alembic import op

revision = "0004_intake_inbox"
down_revision = "0003_reclassify_imported_removed"
branch_labels = None
depends_on = None

S = "order_intake"


def upgrade() -> None:
    op.create_table(
        "inbox",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("message_id", sa.String(64), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("subject", sa.Text()),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("pdf", sa.LargeBinary(), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("summary", sa.JSON()),
        sa.Column("piktiks", sa.JSON()),
        sa.Column("error", sa.Text()),
        sa.Column("checked_at", sa.DateTime(timezone=True)),
        sa.Column("applied_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("message_id", "filename", name="uq_inbox_message_file"),
        schema=S,
    )
    op.create_index("ix_inbox_received_at", "inbox", ["received_at"], schema=S)
    op.create_index("ix_inbox_status", "inbox", ["status"], schema=S)


def downgrade() -> None:
    op.drop_table("inbox", schema=S)
