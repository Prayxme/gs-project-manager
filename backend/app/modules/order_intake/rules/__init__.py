"""Reglas del Ingreso de Órdenes (funciones puras: no tocan Google ni la base de datos).
Cada tema vive en su archivo; aquí se expone la API pública del paquete."""
from app.modules.order_intake.rules.columns import desde_pdf, empresa, valores_orden
from app.modules.order_intake.rules.received import (
    INBOUND_CHECK_COLS, indice_inbound, recibido, sugerencias_received,
)
from app.modules.order_intake.rules.revision import CAMPOS_REVISION, comparar
from app.shared.containers import find_containers as contenedores
from app.shared.dates import parse_date as parse_fecha
from app.shared.spreadsheet import col_idx

__all__ = [
    "CAMPOS_REVISION", "INBOUND_CHECK_COLS", "col_idx", "comparar", "contenedores", "desde_pdf",
    "empresa", "indice_inbound", "parse_fecha", "recibido", "sugerencias_received", "valores_orden",
]
