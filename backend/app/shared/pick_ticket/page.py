"""Lectura de UNA página del Pick Ticket (encabezado + líneas de producto)."""
import re
from typing import Any, Dict, List, Optional

from app.shared.containers import find_containers
from app.shared.pick_ticket.address import parse_ship_to
from app.shared.pick_ticket.item_line import parse_item_line, to_int
from app.shared.pick_ticket.patterns import (
    RE_BOX, RE_CITY, RE_PIKTIK, RE_PO_ROW, RE_SHIP_DC, RE_STORE_DC, RE_TOTAL,
)


def _empresa(lines: List[str]) -> str:
    """Línea inmediatamente anterior a la dirección '1410 Broadway'."""
    for i, l in enumerate(lines):
        if "broadway" in l.lower() and i > 0:
            return lines[i - 1]
    return ""


def _encabezado(text: str) -> Dict[str, Any]:
    po_m = RE_PO_ROW.search(text)
    grupo = (lambda n: po_m.group(n)) if po_m else (lambda n: "")
    dc_m = RE_SHIP_DC.search(text) or RE_STORE_DC.search(text)
    cities = RE_CITY.findall(text)
    tot_m = RE_TOTAL.search(text)
    return {
        "order_no": grupo(1),
        "order_date": grupo(2),
        "cust_no": grupo(3),
        "po": grupo(4),
        "ship_date": grupo(5),
        "cancel_date": grupo(6),
        "ship_to_dc": dc_m.group(1) if dc_m else "",
        # La primera ciudad suele ser el SOLD TO (Framingham); el destino es la última.
        "destination": f"{cities[-1][0].strip()}, {cities[-1][1]}" if cities else "",
        # Línea TOTAL (solo en la última página del PikTik): unidades, cartones, lb y CFT.
        "declared_units": to_int(tot_m.group(1)) if tot_m else None,
        "declared_cases": to_int(tot_m.group(2)) if tot_m else None,
        "declared_weight": _decimal(tot_m.group(3)) if tot_m else None,
        "declared_cft": _decimal(tot_m.group(4)) if tot_m else None,
    }


def _decimal(s: Optional[str]) -> Optional[float]:
    return float(s.replace(",", "")) if s else None


def _cartones_respaldo(lines: List[str], idx: int) -> int:
    """Fila 'Cartons ->' (solo si la columna Cases no se pudo leer)."""
    for k in range(idx + 1, min(idx + 8, len(lines))):
        if lines[k].lower().startswith("cartons"):
            nums = re.findall(r"[\d,]+", lines[k].split("->", 1)[-1])
            return to_int(nums[-1]) if nums else 0
    return 0


def _items(lines: List[str]) -> List[Dict[str, Any]]:
    """Cada 'BOX LxWxH:' va precedido por la línea del ítem."""
    items: List[Dict[str, Any]] = []
    for idx, l in enumerate(lines):
        bm = RE_BOX.search(l)
        if not bm:
            continue
        j = idx - 1
        while j >= 0 and not lines[j]:
            j -= 1
        info = parse_item_line(lines[j]) if j >= 0 else {"sku": "", "variant": "", "cust_sku": "", "cases": None}

        # Cartones: la columna "Cases" de la línea del ítem es la fuente de verdad.
        # (La fila "Cartons ->" redondea por talla y puede sobrar, p. ej. 20 vs 18.)
        qty = info.pop("cases") or 0
        if qty <= 0:
            qty = _cartones_respaldo(lines, idx)

        items.append({
            **info,
            # Contenedores (Container#:ETA) en la línea BOX: "HAMU4749408:11/08, CSNU8090823:10/22".
            "containers": find_containers(l[bm.end():]),
            "qty": qty,
            "l": float(bm.group(1)),
            "w": float(bm.group(2)),
            "h": float(bm.group(3)),
            "weight": float(bm.group(4).replace(",", "")),
        })
    return items


def parse_page(text: str, ship_to_lines: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
    """Datos de una página, o None si no tiene número de PikTik.
    ship_to_lines: columna SHIP TO leída por posición (ver ship_to_block); opcional."""
    m = RE_PIKTIK.search(text)
    if not m:
        return None
    lines = [l.strip() for l in text.split("\n")]
    return {
        "piktik": m.group(2),
        "page_no": int(m.group(3)),
        "company": _empresa(lines),
        **_encabezado(text),
        "ship_to": parse_ship_to(ship_to_lines),
        "items": _items(lines),
    }
