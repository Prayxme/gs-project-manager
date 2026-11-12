"""
Lectura de Pick Tickets (PDF) de Wiesner Products — capacidad compartida por varios módulos
(Paletizador, Ingreso de Órdenes y los que vengan).

Estructura real observada: el PDF contiene N páginas; cada página lleva un
"PikTik No" y su "Page". Un mismo PikTik puede ocupar varias páginas (cuando
detalla muchos SKU). Cada PikTik tiene una única PO y un destino (SHIP TO / DC).

Salida: una orden por PikTik, con PO, DC, destino, fechas, contenedores y todas
sus líneas de SKU, acumuladas a través de sus páginas.
"""
import io
from typing import Any, Dict, List

import pdfplumber

from app.shared.pick_ticket.page import parse_page

CAMPOS_ORDEN = ("po", "cust_no", "company", "order_no", "order_date", "ship_date", "cancel_date",
                "ship_to_dc", "destination")


def extraer_datos_pick_ticket(content: bytes) -> Dict[str, Any]:
    """PDF (bytes) -> {company, cust_no, orders[], warnings[]}."""
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        pages_text = [(p.extract_text() or "") for p in pdf.pages]
    return parsear_paginas(pages_text)


def parsear_paginas(pages_text: List[str]) -> Dict[str, Any]:
    """Agrupa las páginas por PikTik y devuelve una orden por PikTik."""
    warnings: List[str] = []
    orders: Dict[str, Dict[str, Any]] = {}
    company = ""

    for n, text in enumerate(pages_text, start=1):
        page = parse_page(text)
        if page is None:
            warnings.append(f"Página {n}: no se encontró el número de PikTik; se omitió.")
            continue
        company = company or page["company"]
        order = orders.setdefault(page["piktik"], _orden_vacia(page))
        order["pages"] += 1
        for campo in CAMPOS_ORDEN:
            if not order[campo] and page[campo]:
                order[campo] = page[campo]
        if page["declared_cases"] is not None:
            order["declared_cases"] = page["declared_cases"]
        order["items"].extend(page["items"])

    result_orders = list(orders.values())
    for o in result_orders:
        _desambiguar_skus(o["items"])
        # Contenedores de la orden: unión de todas sus líneas, en orden de aparición.
        o["containers"] = list(dict.fromkeys(c for it in o["items"] for c in it.get("containers", [])))
        warnings.extend(_validar(o))

    if not result_orders:
        raise ValueError("No se detectó ningún PikTik en el PDF.")

    return {
        "company": company or "",
        "cust_no": result_orders[0]["cust_no"],
        "orders": result_orders,
        "warnings": warnings,
    }


def _orden_vacia(page: Dict[str, Any]) -> Dict[str, Any]:
    return {"piktik": page["piktik"], **{c: page[c] for c in CAMPOS_ORDEN},
            "pages": 0, "declared_cases": None, "items": []}


def _desambiguar_skus(items: List[Dict[str, Any]]) -> None:
    """Si una orden repite el mismo código de ítem con variantes distintas
    (p. ej. MLGO40416 001 / 025 / CARB), agrega la primera palabra de la
    variante para que cada línea conserve una identidad única."""
    conteo: Dict[str, int] = {}
    for it in items:
        conteo[it["sku"]] = conteo.get(it["sku"], 0) + 1
    for it in items:
        if conteo[it["sku"]] > 1 and it["variant"]:
            it["sku"] = f"{it['sku']} {it['variant'].split()[0]}"


def _validar(o: Dict[str, Any]) -> List[str]:
    avisos = []
    if not o["po"]:
        avisos.append(f"PikTik {o['piktik']}: no se pudo leer la PO.")
    if not o["ship_to_dc"]:
        avisos.append(f"PikTik {o['piktik']}: no se pudo leer el DC de destino.")
    if not o["items"]:
        avisos.append(f"PikTik {o['piktik']}: no se encontraron líneas de producto.")
    for it in o["items"]:
        if it["qty"] <= 0:
            avisos.append(f"PikTik {o['piktik']}, {it['sku']}: cantidad de cartones no detectada.")
    suma = sum(it["qty"] for it in o["items"])
    if o["declared_cases"] is not None and suma != o["declared_cases"]:
        avisos.append(
            f"PikTik {o['piktik']}: suma de cartones ({suma}) distinta del TOTAL declarado "
            f"({o['declared_cases']})."
        )
    return avisos
