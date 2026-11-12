"""Catálogo de Pick Tickets ya leídos (por PikTik), compartido por los módulos.

Ingreso de Órdenes lo alimenta con los PDFs que llegan por Gmail; Routing lo usa para estimar
pallets de las órdenes urgentes sin volver a subir el PDF (y guarda los que se suben a mano).
"""
from app.shared.pick_ticket_catalog.repository import PickTicketCatalog
from app.shared.pick_ticket_catalog.service import fecha_del_archivo, registrar_pdf

__all__ = ["PickTicketCatalog", "fecha_del_archivo", "registrar_pdf"]
