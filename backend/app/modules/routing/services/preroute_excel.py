"""Lector del Excel de Pre Routing (p. ej. "TJMAXX Pre Route POs.xlsx").

Busca la fila de encabezados (Cust, PO#, Ship Dat, Cncl Dat, Style, Color, Qty, Cases, Weight, Cube)
en cualquier hoja y devuelve las filas como líneas crudas; la limpieza es de rules/preroute.py.
"""
import io
import re
from typing import Dict, List, Optional

from openpyxl import load_workbook

# Encabezado normalizado (minúsculas, solo letras y números) -> campo.
ALIAS = {
    "cust": "cust", "customer": "cust", "custno": "cust", "customerno": "cust",
    "po": "po", "pono": "po", "ponumber": "po",
    "shipdat": "ship_date", "shipdate": "ship_date", "ship": "ship_date",
    "cncldat": "cancel_date", "cncldate": "cancel_date", "canceldat": "cancel_date",
    "canceldate": "cancel_date", "cancel": "cancel_date",
    "style": "style", "color": "color",
    "qty": "qty", "qtyord": "qty", "units": "qty", "quantity": "qty",
    "cases": "cases", "ctns": "cases", "cartons": "cases", "cartones": "cases",
    "weight": "weight", "wt": "weight", "lb": "weight", "lbs": "weight", "peso": "weight",
    "cube": "cube", "cft": "cube", "cubefeet": "cube", "cubicfeet": "cube",
    "shipto": "ship_to", "dc": "ship_to", "shpto": "ship_to",
}
OBLIGATORIOS = ("cust", "po", "cases", "cube")
FILAS_DE_BUSQUEDA = 15          # el encabezado debe estar entre las primeras filas


def _campo(celda) -> Optional[str]:
    return ALIAS.get(re.sub(r"[^a-z0-9]", "", str(celda or "").lower()))


def _encabezado(fila) -> Optional[Dict[int, str]]:
    """{índice de columna: campo} si la fila trae los encabezados obligatorios."""
    columnas: Dict[int, str] = {}
    for i, celda in enumerate(fila):
        campo = _campo(celda)
        if campo and campo not in columnas.values():
            columnas[i] = campo
    return columnas if all(c in columnas.values() for c in OBLIGATORIOS) else None


def leer_excel(contenido: bytes) -> List[Dict]:
    """Líneas crudas {campo: valor} de la primera hoja que tenga los encabezados. ValueError si ninguna."""
    try:
        libro = load_workbook(io.BytesIO(contenido), data_only=True, read_only=True)
    except Exception as e:
        raise ValueError(f"no se pudo abrir como Excel (.xlsx): {e}") from e
    for hoja in libro.worksheets:
        columnas = None
        lineas: List[Dict] = []
        for n, fila in enumerate(hoja.iter_rows(values_only=True)):
            if columnas is None:
                if n >= FILAS_DE_BUSQUEDA:
                    break
                columnas = _encabezado(fila)
                continue
            linea = {campo: fila[i] for i, campo in columnas.items() if i < len(fila)}
            if any(v not in (None, "") for v in linea.values()):
                lineas.append(linea)
        if columnas is not None:
            return lineas
    raise ValueError("no se encontraron los encabezados Cust, PO#, Cases y Cube en ninguna hoja")
