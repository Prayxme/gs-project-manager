"""Pre Routing: órdenes que llegan sin Pick Ticket, como una lista de líneas (Excel o a mano) con
Cust, PO#, Ship Date, Cancel Date, Qty, Cases, Weight y Cube. Weight y Cube vienen POR CARTÓN.

Aquí se limpian las líneas y se agrupan por PO (una PO puede traer varias líneas: estilo / color).
"""
import re
from typing import Dict, List, Optional, Tuple

from app.shared.dates import parse_date

_RE_NUMERO = re.compile(r"-?\d+(?:\.\d+)?")


def numero(valor) -> Optional[float]:
    """'9lb' -> 9.0 · '1,200' -> 1200.0 · 1.3 -> 1.3 · vacío o sin número -> None."""
    if valor is None or isinstance(valor, bool):
        return None
    if isinstance(valor, (int, float)):
        return float(valor)
    m = _RE_NUMERO.search(str(valor).replace(",", ""))
    return float(m.group()) if m else None


def texto(valor) -> str:
    """Texto limpio; un número de PO leído como 20338991.0 queda '20338991'."""
    if valor is None:
        return ""
    if isinstance(valor, float) and valor.is_integer():
        valor = int(valor)
    return str(valor).strip()


def _fecha(valor) -> str:
    d = parse_date(valor)
    return d.isoformat() if d else ""


def normalizar_linea(cruda: Dict, n: int) -> Tuple[Optional[Dict], List[str]]:
    """(línea limpia | None si no sirve, avisos). `n` = número de línea para los avisos."""
    cust, po = texto(cruda.get("cust")).upper(), texto(cruda.get("po"))
    if not cust and not po:
        return None, []                                  # fila vacía
    cases, cube = numero(cruda.get("cases")), numero(cruda.get("cube"))
    faltan = [nombre for nombre, ok in (("Cust", cust), ("PO#", po), ("Cases", cases and cases > 0),
                                        ("Cube", cube and cube > 0)) if not ok]
    if faltan:
        return None, [f"Línea {n} (PO {po or '?'}): falta {', '.join(faltan)}; no se toma en cuenta"]

    avisos = []
    weight, qty = numero(cruda.get("weight")), numero(cruda.get("qty"))
    if weight is None or weight <= 0:
        avisos.append(f"Línea {n} (PO {po}): sin peso por cartón; se toma 0 lb")
    linea = {
        "cust": cust, "po": po,
        "ship_date": _fecha(cruda.get("ship_date")), "cancel_date": _fecha(cruda.get("cancel_date")),
        "style": texto(cruda.get("style")), "color": texto(cruda.get("color")),
        "qty": int(qty) if qty and qty > 0 else None,
        "cases": int(cases), "weight": max(weight or 0.0, 0.0), "cube": cube,
        "ship_to": texto(cruda.get("ship_to")),
    }
    if not linea["cancel_date"]:
        avisos.append(f"Línea {n} (PO {po}): sin Cancel Date válida")
    return linea, avisos


def normalizar(crudas: List[Dict]) -> Tuple[List[Dict], List[str]]:
    lineas, avisos = [], []
    for n, cruda in enumerate(crudas, start=1):
        linea, notas = normalizar_linea(cruda, n)
        avisos += notas
        if linea:
            lineas.append(linea)
    return lineas, avisos


def agrupar_por_po(lineas: List[Dict]) -> Dict[Tuple[str, str], List[Dict]]:
    """{(Customer No, PO): líneas}, en el orden en que aparecen."""
    grupos: Dict[Tuple[str, str], List[Dict]] = {}
    for ln in lineas:
        grupos.setdefault((ln["cust"], ln["po"]), []).append(ln)
    return grupos
