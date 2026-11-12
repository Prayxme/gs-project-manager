"""Plan de routing de una selección de órdenes del portal (las que muestra el Monitor: por estado
y, si se pide, por Customer No), con los Pick Tickets del catálogo y los PDFs que se suban.
De los PDFs solo se toman las órdenes de la selección; las demás se ignoran."""
from datetime import date
from typing import Dict, List, Optional, Sequence

from app.modules.routing import rules
from app.modules.routing.services.plan import construir_plan
from app.shared.pick_ticket_catalog import PickTicketCatalog

ORIGEN = "Catálogo de Pick Tickets"


class PortalNoDisponible(Exception):
    """Sin el portal no se sabe qué órdenes están abiertas ni cuáles ya se enrutaron."""


def plan_seleccion(catalogo: Optional[PickTicketCatalog], portal: Dict, hoy: date, estados: Sequence[str],
                   cust: Optional[str] = None, pdfs: Optional[List[Dict]] = None) -> Dict:
    if portal["orders"] is None:
        raise PortalNoDisponible(f"No se pudo consultar el portal de Wiesner: {portal['error']}")
    elegidas = rules.seleccionar(portal["orders"].values(), hoy, estados, cust)
    interesan = {e["pick_ticket"] for e in elegidas}

    guardadas = catalogo.ordenes(interesan) if catalogo is not None else {}
    subidas, ignoradas = [], 0
    for pdf in pdfs or []:                       # lo recién subido manda sobre el catálogo
        propias = [o for o in pdf["orders"] if o["piktik"] in interesan]
        ignoradas += len(pdf["orders"]) - len(propias)
        for o in propias:
            guardadas.pop(o["piktik"], None)
        subidas.append({**pdf, "orders": propias})
    fuentes = [{"filename": ORIGEN, "orders": list(guardadas.values()), "warnings": []}] + subidas

    con_pdf = {o["piktik"] for f in fuentes for o in f["orders"]}
    faltantes = [e for e in elegidas if e["pick_ticket"] not in con_pdf]
    plan = construir_plan(fuentes, portal, hoy, faltantes)
    plan["summary"]["pdfs"] = len(subidas)
    plan["selection"] = {"statuses": list(estados), "cust": (cust or "").strip().upper(),
                         "orders": len(elegidas), "ignored": ignoradas}
    return plan
