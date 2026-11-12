"""
Lectura de Pick Tickets (PDF) de Wiesner Products.

Estructura real observada: el PDF contiene N páginas; cada página lleva un
"PikTik No" y su "Page". Un mismo PikTik puede ocupar varias páginas (cuando
detalla muchos SKU). Cada PikTik tiene una única PO y un destino (SHIP TO / DC).

Salida: una orden por PikTik, con PO, DC, destino y todas sus líneas de SKU,
acumuladas a través de sus páginas.
"""
import io
import re
from typing import Any, Dict, List, Optional

import pdfplumber

_RE_PIKTIK = re.compile(r"^(\d{2}/\d{2}/\d{4})\s+(\d{5,})\s+(\d+)\s*$", re.MULTILINE)
# Fila "Order No | Order Date | Cust No | Rep | PO No | Ship Date | Cancel Date".
# La PO puede ser alfanumérica (p. ej. S&JS: TR0926MN35).
_RE_PO_ROW = re.compile(
    r"^(\d+)\s+(\d{2}/\d{2}/\d{4})\s+(\S+)\s+\d+\s+(\S+)\s+(\d{2}/\d{2}/\d{4})\s+(\d{2}/\d{2}/\d{4})",
    re.MULTILINE,
)
_RE_CONTAINER = re.compile(r"\b([A-Z]{4}\d{7})\b")
_RE_SHIP_DC = re.compile(r"SHIP TO:\s*(?:DC\s*#?\s*)?(\d+)", re.IGNORECASE)
_RE_STORE_DC = re.compile(r"For STORE #:\s*(?:DC\s*#?\s*)?(\d+)", re.IGNORECASE)
_RE_CITY = re.compile(r"([A-Z][A-Z .'\-]+?),+\s*([A-Z]{2})\s+(\d{5})")
_RE_BOX = re.compile(
    r"BOX LxWxH:\s*([\d.]+)\s*x\s*([\d.]+)\s*x\s*([\d.]+)\s*IN,\s*([\d.,]+)\s*LB", re.IGNORECASE
)
_RE_TOTAL = re.compile(r"^TOTAL:\s*[\d,]+\s+([\d,]+)\s+TOT WEIGHT", re.MULTILINE)
_RE_NUM = re.compile(r"^[\d,]+$")


def _to_int(s: str) -> int:
    return int(s.replace(",", ""))


def _parse_item_line(line: str) -> Dict[str, Any]:
    """'3-M2056ST MARS P24 S40570 2 2 56 94 MENS 3 PACK ... 295344'
    -> sku = primer token; variant = tokens hasta la columna de cantidades;
       cases = último número de la primera racha numérica de >= 2 tokens
       (Qty Ord puede venir partido en miles: '2 2 56' = 2256, luego Cases);
       cust_sku = último token numérico de la línea."""
    tokens = line.split()
    sku = tokens[0] if tokens else ""
    cust_sku = tokens[-1] if len(tokens) > 1 and tokens[-1].isdigit() else ""
    rest = tokens[1:]
    i = 0
    while i < len(rest):
        if _RE_NUM.match(rest[i]):
            j = i
            while j < len(rest) and _RE_NUM.match(rest[j]):
                j += 1
            if j - i >= 2:
                return {
                    "sku": sku,
                    "variant": " ".join(rest[:i]),
                    "cust_sku": cust_sku,
                    "cases": _to_int(rest[j - 1]),
                }
            i = j
        else:
            i += 1
    return {"sku": sku, "variant": "", "cust_sku": cust_sku, "cases": None}


def _parse_page(text: str) -> Optional[Dict[str, Any]]:
    m = _RE_PIKTIK.search(text)
    if not m:
        return None
    lines = [l.strip() for l in text.split("\n")]
    page: Dict[str, Any] = {"piktik": m.group(2), "page_no": int(m.group(3))}

    # Compañía: línea inmediatamente anterior a la dirección "1410 Broadway".
    company = ""
    for i, l in enumerate(lines):
        if "broadway" in l.lower() and i > 0:
            company = lines[i - 1]
            break
    page["company"] = company

    po_m = _RE_PO_ROW.search(text)
    page["order_no"] = po_m.group(1) if po_m else ""
    page["order_date"] = po_m.group(2) if po_m else ""
    page["cust_no"] = po_m.group(3) if po_m else ""
    page["po"] = po_m.group(4) if po_m else ""
    page["ship_date"] = po_m.group(5) if po_m else ""
    page["cancel_date"] = po_m.group(6) if po_m else ""

    dc_m = _RE_SHIP_DC.search(text) or _RE_STORE_DC.search(text)
    page["ship_to_dc"] = dc_m.group(1) if dc_m else ""

    cities = _RE_CITY.findall(text)
    # La primera ciudad suele ser el SOLD TO (Framingham); el destino es la última.
    page["destination"] = f"{cities[-1][0].strip()}, {cities[-1][1]}" if cities else ""

    tot_m = _RE_TOTAL.search(text)
    page["declared_cases"] = _to_int(tot_m.group(1)) if tot_m else None

    # Líneas de producto: cada "BOX LxWxH:" va precedido por la línea del ítem.
    items: List[Dict[str, Any]] = []
    for idx, l in enumerate(lines):
        bm = _RE_BOX.search(l)
        if not bm:
            continue
        j = idx - 1
        while j >= 0 and not lines[j]:
            j -= 1
        info = _parse_item_line(lines[j]) if j >= 0 else {"sku": "", "variant": "", "cust_sku": "", "cases": None}

        # Cartones: la columna "Cases" de la línea del ítem es la fuente de verdad.
        # (La fila "Cartons ->" redondea por talla y puede sobrar, p. ej. 20 vs 18.)
        qty = info.pop("cases") or 0
        if qty <= 0:
            for k in range(idx + 1, min(idx + 8, len(lines))):
                if lines[k].lower().startswith("cartons"):
                    nums = re.findall(r"[\d,]+", lines[k].split("->", 1)[-1])
                    if nums:
                        qty = _to_int(nums[-1])
                    break

        # Contenedores (Container#:ETA) en la línea BOX, p. ej. "HAMU4749408:11/08, CSNU8090823:10/22".
        contenedores = list(dict.fromkeys(_RE_CONTAINER.findall(l[bm.end():])))

        items.append(
            {
                **info,
                "containers": contenedores,
                "qty": qty,
                "l": float(bm.group(1)),
                "w": float(bm.group(2)),
                "h": float(bm.group(3)),
                "weight": float(bm.group(4).replace(",", "")),
            }
        )
    page["items"] = items
    return page


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


def extraer_datos_pick_ticket(content: bytes) -> Dict[str, Any]:
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        pages_text = [(p.extract_text() or "") for p in pdf.pages]
    return parsear_paginas(pages_text)


def parsear_paginas(pages_text: List[str]) -> Dict[str, Any]:
    """Agrupa las páginas por PikTik y devuelve una orden por PikTik."""
    warnings: List[str] = []
    orders: Dict[str, Dict[str, Any]] = {}
    company = ""

    for n, text in enumerate(pages_text, start=1):
        page = _parse_page(text)
        if page is None:
            warnings.append(f"Página {n}: no se encontró el número de PikTik; se omitió.")
            continue
        company = company or page["company"]
        order = orders.setdefault(
            page["piktik"],
            {
                "piktik": page["piktik"],
                "po": page["po"],
                "cust_no": page["cust_no"],
                "company": page["company"],
                "order_no": page["order_no"],
                "order_date": page["order_date"],
                "ship_date": page["ship_date"],
                "cancel_date": page["cancel_date"],
                "ship_to_dc": page["ship_to_dc"],
                "destination": page["destination"],
                "pages": 0,
                "declared_cases": None,
                "items": [],
            },
        )
        order["pages"] += 1
        for campo in ("po", "cust_no", "company", "order_no", "order_date", "ship_date", "cancel_date",
                      "ship_to_dc", "destination"):
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
        if not o["po"]:
            warnings.append(f"PikTik {o['piktik']}: no se pudo leer la PO.")
        if not o["ship_to_dc"]:
            warnings.append(f"PikTik {o['piktik']}: no se pudo leer el DC de destino.")
        if not o["items"]:
            warnings.append(f"PikTik {o['piktik']}: no se encontraron líneas de producto.")
        for it in o["items"]:
            if it["qty"] <= 0:
                warnings.append(f"PikTik {o['piktik']}, {it['sku']}: cantidad de cartones no detectada.")
        suma = sum(it["qty"] for it in o["items"])
        if o["declared_cases"] is not None and suma != o["declared_cases"]:
            warnings.append(
                f"PikTik {o['piktik']}: suma de cartones ({suma}) distinta del TOTAL declarado "
                f"({o['declared_cases']})."
            )

    if not result_orders:
        raise ValueError("No se detectó ningún PikTik en el PDF.")

    return {
        "company": company or "",
        "cust_no": result_orders[0]["cust_no"],
        "orders": result_orders,
        "warnings": warnings,
    }
