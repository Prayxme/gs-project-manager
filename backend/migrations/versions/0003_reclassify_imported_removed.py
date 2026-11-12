"""Datos: histórico importado REMOVED con carga asignada (LOAD ID, CITI, FedEx) -> COMPLETED.

El Apps Script anterior marcaba REMOVED órdenes que sí se enviaron. Se aplica la misma regla
que usa el monitor (rules.cfrm.reclasificar_importada) y se guarda el valor original en
original_status / original_reason. El downgrade lo restaura.

Revision ID: 0003_reclassify_imported_removed
Revises: 0002_order_intake
Create Date: 2026-11-12
"""
import sqlalchemy as sa
from alembic import op

from app.modules.open_orders.rules.cfrm import reclasificar_importada

revision = "0003_reclassify_imported_removed"
down_revision = "0002_order_intake"
branch_labels = None
depends_on = None

T = "open_orders.closed_orders"


def upgrade() -> None:
    conn = op.get_bind()
    filas = conn.execute(sa.text(
        f"SELECT pick_ticket, final_status, reason, cfrm_number FROM {T} "
        "WHERE source = 'import' AND final_status = 'REMOVED' AND original_status IS NULL"
    )).mappings().all()
    cambios = [{"pt": f["pick_ticket"], **c} for f in filas if (c := reclasificar_importada(dict(f)))]
    if cambios:
        conn.execute(sa.text(
            f"UPDATE {T} SET final_status = :final_status, reason = :reason, "
            "original_status = :original_status, original_reason = :original_reason "
            "WHERE pick_ticket = :pt"
        ), cambios)


def downgrade() -> None:
    op.execute(
        f"UPDATE {T} SET final_status = original_status, reason = original_reason, "
        "original_status = NULL, original_reason = NULL "
        "WHERE source = 'import' AND original_status IS NOT NULL"
    )
