"""Plan de routing de Pre Routing: POs sin Pick Ticket, estimadas por cubo.

Cada PO suma sus líneas (cartones, unidades, lb = cartones x peso por cartón, cubo = cartones x cubo
por cartón), se estima por cubo y pasa por las mismas reglas que las POs de Pick Tickets: margen,
lb y CFT a declarar, límite de pallets por RTS y peso mínimo de ROSS / DDSD.

Sin PDF no hay dirección SHIP TO: en TJMA / MARS / NEWT el destino sale de los 2 primeros dígitos
de la PO (si el catálogo conoce ese DC, se usa su dirección); en los demás clientes hay que
indicar el destino en la línea para poder juntar POs.
"""
from collections import defaultdict
from datetime import date
from typing import Dict, List, Optional

from app.modules.routing import config, rules
from app.modules.routing.rules.cube import estimar_por_cubo
from app.modules.routing.rules.preroute import agrupar_por_po, normalizar
from app.modules.routing.rules.reconcile import ALREADY_ROUTED, MISMATCH
from app.modules.routing.services.plan import armar_plan
from app.shared.dates import parse_date
from app.shared.pick_ticket_catalog import PickTicketCatalog
from app.shared.wiesner import customer_code, routing_window

PRE_ROUTE = "PRE_ROUTE"       # PO sin Pick Ticket: no está en el portal, no se puede conciliar
ORIGEN = "preroute"


def _entero(valor) -> int:
    try:
        return int(str(valor).replace(",", "").strip())
    except (TypeError, ValueError):
        return 0


def _destino(cust: str, codigo: str, po: str, indicado: str, catalogo: Optional[PickTicketCatalog]) -> Dict:
    """SHIP TO de la PO: {name, ..., key} ('key' vacía = no se junta con ninguna otra)."""
    if codigo in config.PREFIJO_PO_DC:
        prefijo = po[:config.LARGO_PREFIJO_PO]
        conocido = catalogo.destino_por_prefijo(cust, prefijo) if catalogo is not None else None
        return conocido or {"name": f"DC de las POs {prefijo}…", "key": f"PRE {cust} {prefijo}"}
    if indicado:
        return {"name": indicado, "key": f"PRE {cust} {indicado.upper()}"}
    return {"name": "", "key": ""}


def _estado(po: str, cartones: int, portal: Optional[Dict[str, List[Dict]]]):
    """(estado, avisos, fila del portal). El portal es la verdad cuando la PO ya figura en él."""
    if portal is None:
        return rules.UNVERIFIED, [], {}
    filas = portal.get(po, [])
    if not filas:
        return PRE_ROUTE, [], {}
    enrutada = next((f for f in filas if (f.get("cfrm_number") or "").strip()), None)
    if enrutada:
        return ALREADY_ROUTED, [f"Ya tiene Cfrm Number {enrutada['cfrm_number']}"], enrutada
    en_portal = sum(_entero(f.get("ctns")) for f in filas)
    if en_portal != cartones:
        return MISMATCH, [f"Cartones: portal {en_portal} / Pre Route {cartones}"], filas[0]
    return "OK", [], filas[0]


def armar_po_preroute(cust: str, po: str, lineas: List[Dict], portal: Optional[Dict[str, List[Dict]]],
                      hoy: date, catalogo: Optional[PickTicketCatalog]) -> Dict:
    primera, codigo = lineas[0], customer_code(cust)
    cartones = sum(ln["cases"] for ln in lineas)
    peso_cajas = sum(ln["cases"] * ln["weight"] for ln in lineas)
    cubo = sum(ln["cases"] * ln["cube"] for ln in lineas)
    unidades = [ln["qty"] for ln in lineas]

    estado, avisos, fila = _estado(po, cartones, portal)
    if any((ln["ship_date"], ln["cancel_date"]) != (primera["ship_date"], primera["cancel_date"]) for ln in lineas):
        avisos.append("Las líneas de esta PO traen fechas distintas: se usó la primera")
    deadline, _ = routing_window(parse_date(primera["ship_date"]), parse_date(primera["cancel_date"]), codigo)

    destino = _destino(cust, codigo, po, next((ln["ship_to"] for ln in lineas if ln["ship_to"]), ""), catalogo)
    if not destino["key"]:
        avisos.append("Sin destino (SHIP TO): esta PO no se agrupa con otras; indícalo en la línea")

    enrutable = estado not in rules.EXCLUIDOS
    estimado, ultima = estimar_por_cubo(cubo) if enrutable else (0, None)
    pallets = rules.pallets_a_enrutar(estimado, ultima)
    return {
        "po": po, "piktiks": [], "source": ORIGEN,
        "cust": cust, "customer_code": codigo, "family": rules.familia(cust),
        "ship_date": primera["ship_date"], "cancel_date": primera["cancel_date"],
        "deadline": deadline.isoformat() if deadline else "",
        "days_left": (deadline - hoy).days if deadline else None,
        "ship_to": destino, "address_key": destino["key"],
        "portal_ship_to": (fila.get("ship_to") or "").strip(),
        "units": sum(unidades) if all(u is not None for u in unidades) else None,
        "cartons": cartones,
        "cases_weight": round(peso_cajas, 1),
        "cube": round(cubo, 1),                       # cubo real: cartones x cubo por cartón
        "estimated_pallets": estimado, "pallets": pallets,
        "last_pallet_fill": ultima,
        "margin_reduced": pallets < estimado + rules.margen_base(estimado),
        "weight": rules.peso_declarado(peso_cajas, pallets) if enrutable else 0,
        "cft": rules.cft_declarado(codigo, pallets),
        "status": estado, "issues": avisos,
        "cfrm_number": (fila.get("cfrm_number") or "").strip(),
        "cfrm_date": "", "appt_date": "",
        "items": [],                                  # sin dimensiones no hay armado 3D
        "lines": [{k: ln[k] for k in ("style", "color", "qty", "cases", "weight", "cube")} for ln in lineas],
    }


def plan_preroute(crudas: List[Dict], portal: Dict, hoy: date,
                  catalogo: Optional[PickTicketCatalog] = None) -> Dict:
    """`crudas`: líneas tal como llegan del Excel o del formulario."""
    lineas, avisos = normalizar(crudas)
    por_po: Optional[Dict[str, List[Dict]]] = None
    if portal["orders"] is not None:
        por_po = defaultdict(list)
        for fila in portal["orders"].values():
            por_po[(fila.get("po") or "").strip()].append(fila)
    pos = [armar_po_preroute(cust, po, grupo, por_po, hoy, catalogo)
           for (cust, po), grupo in agrupar_por_po(lineas).items()]
    plan = armar_plan(pos, portal, hoy, avisos)
    plan["source"] = ORIGEN
    plan["preroute"] = {"lines": len(lineas), "cube": round(sum(p["cube"] for p in pos), 1),
                        "cft_per_pallet": config.CFT_UTIL_POR_PALLET}
    return plan
