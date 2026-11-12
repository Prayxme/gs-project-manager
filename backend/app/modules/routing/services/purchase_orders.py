"""Una entrada por PO a partir de sus PikTiks (una PO puede venir en varios PikTiks).

Cada PikTik se concilia con el portal; la PO toma los datos del portal (la verdad) cuando
existen, suma los totales del PDF y calcula pallets, lb y CFT a declarar.
"""
from datetime import date
from typing import Dict, List, Optional

from app.modules.routing import rules
from app.modules.routing.services.estimate import estimar_pallets
from app.shared.dates import parse_date
from app.shared.wiesner import customer_code, routing_window

NO_ITEMS = "NO_ITEMS"   # el PDF no trae líneas de producto: no se puede estimar


def _iso(valor: str) -> str:
    d = parse_date(valor)
    return d.isoformat() if d else ""


def _cartones(pk: Dict) -> int:
    return pk["declared_cases"] if pk["declared_cases"] is not None else sum(i["qty"] for i in pk["items"])


def _peso_cajas(pk: Dict) -> float:
    if pk["declared_weight"]:
        return pk["declared_weight"]
    return sum(i["qty"] * i["weight"] for i in pk["items"])


def armar_po(po: str, piktiks: List[Dict], portal: Optional[Dict[str, Dict]], hoy: date) -> Dict:
    estados, avisos, filas = [], [], []
    for pk in piktiks:
        estado, difs, fila = rules.conciliar(pk["piktik"], po, _cartones(pk), portal)
        estados.append(estado)
        avisos += difs
        if fila:
            filas.append(fila)

    primero, fila = piktiks[0], (filas[0] if filas else {})
    cust = fila.get("cust") or primero["cust_no"]
    codigo = customer_code(cust)
    ship = fila.get("ship_date") or primero["ship_date"]
    cancel = fila.get("cancel_date") or primero["cancel_date"]
    deadline, _ = routing_window(parse_date(ship), parse_date(cancel), codigo)

    ship_to = primero.get("ship_to") or {}
    shpto = (fila.get("ship_to") or "").strip()
    if shpto and ship_to.get("code") and shpto.lstrip("0") != ship_to["code"].lstrip("0"):
        avisos.append(f"Shpto del portal ({shpto}) distinto del SHIP TO del PDF ({ship_to['code']})")
    if not ship_to.get("zip"):
        avisos.append("No se pudo leer la dirección SHIP TO completa: esta PO no se agrupa con otras")

    items = [{**i, "piktik": pk["piktik"]} for pk in piktiks for i in pk["items"]]
    estado = next((e for e in estados if e in rules.EXCLUIDOS), None)
    if estado is None and not items:
        estado, avisos = NO_ITEMS, avisos + ["El PDF no trae líneas de producto (dimensiones): no se puede estimar"]
    if estado is None:
        estado = rules.UNVERIFIED if portal is None else "OK"

    # Solo se estima lo que se va a enrutar: una PO ya enrutada en Wiesner (o con diferencias)
    # no necesita cálculo, solo se informa.
    enrutable = estado in ("OK", rules.UNVERIFIED)
    estimado, no_caben = estimar_pallets(po, items) if enrutable else (0, 0)
    if no_caben:
        avisos.append(f"{no_caben} cajas no caben en un pallet de 85 in (revisar dimensiones)")
    pallets = rules.pallets_a_enrutar(estimado)
    peso_cajas = sum(_peso_cajas(pk) for pk in piktiks)
    unidades = [pk["declared_units"] for pk in piktiks]

    return {
        "po": po,
        "piktiks": [pk["piktik"] for pk in piktiks],
        "cust": cust,
        "customer_code": codigo,
        "family": rules.familia(codigo),
        "ship_date": _iso(ship),
        "cancel_date": _iso(cancel),
        "deadline": deadline.isoformat() if deadline else "",
        "days_left": (deadline - hoy).days if deadline else None,
        "ship_to": ship_to,
        "address_key": ship_to.get("key", "") if ship_to.get("zip") else "",
        "portal_ship_to": shpto,
        "units": sum(unidades) if all(u is not None for u in unidades) else None,
        "cartons": sum(_cartones(pk) for pk in piktiks),
        "cases_weight": round(peso_cajas, 1),
        "estimated_pallets": estimado,
        "pallets": pallets,
        "weight": rules.peso_declarado(peso_cajas, pallets) if enrutable else 0,
        "cft": rules.cft_declarado(codigo, pallets),
        "status": estado,
        "issues": avisos,
        # Routing que ya figura en el portal de Wiesner (si lo hay).
        "cfrm_number": next((f["cfrm_number"] for f in filas if (f.get("cfrm_number") or "").strip()), ""),
        "cfrm_date": _iso(fila.get("cfrm_date", "")),
        "appt_date": _iso(fila.get("appt_date", "")),
    }
