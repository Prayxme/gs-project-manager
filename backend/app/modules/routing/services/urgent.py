"""Plan de routing de las órdenes urgentes del portal (las que vigila el Monitor), usando los
Pick Tickets ya guardados en el catálogo: no hace falta volver a subir el PDF."""
from datetime import date
from typing import Dict

from app.modules.routing import rules
from app.modules.routing.services.plan import construir_plan
from app.shared.pick_ticket_catalog import PickTicketCatalog

ORIGEN = "Catálogo de Pick Tickets"


class PortalNoDisponible(Exception):
    """Sin el portal no se sabe qué órdenes están abiertas ni cuáles ya se enrutaron."""


def plan_urgente(catalogo: PickTicketCatalog, portal: Dict, hoy: date, dias: int) -> Dict:
    if portal["orders"] is None:
        raise PortalNoDisponible(f"No se pudo consultar el portal de Wiesner: {portal['error']}")
    urgentes = rules.ordenes_urgentes(portal["orders"].values(), hoy, dias)
    leidas = catalogo.ordenes(u["pick_ticket"] for u in urgentes)
    faltantes = [u for u in urgentes if u["pick_ticket"] not in leidas]
    pdfs = [{"filename": ORIGEN, "orders": list(leidas.values()), "warnings": []}]
    plan = construir_plan(pdfs, portal, hoy, faltantes)
    plan.update(scope="urgent", days=dias, urgent=len(urgentes))
    return plan
