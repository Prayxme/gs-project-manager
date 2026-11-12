"""Expresiones regulares del Pick Ticket de Wiesner (texto extraído con pdfplumber)."""
import re

# "10/21/2026 6846787 1"  -> fecha, PikTik, página
RE_PIKTIK = re.compile(r"^(\d{2}/\d{2}/\d{4})\s+(\d{5,})\s+(\d+)\s*$", re.MULTILINE)

# Fila "Order No | Order Date | Cust No | Rep | PO No | Ship Date | Cancel Date".
# La PO puede ser alfanumérica (p. ej. S&JS: TR0926MN35).
RE_PO_ROW = re.compile(
    r"^(\d+)\s+(\d{2}/\d{2}/\d{4})\s+(\S+)\s+\d+\s+(\S+)\s+(\d{2}/\d{2}/\d{4})\s+(\d{2}/\d{2}/\d{4})",
    re.MULTILINE,
)
RE_SHIP_DC = re.compile(r"SHIP TO:\s*(?:DC\s*#?\s*)?(\d+)", re.IGNORECASE)
RE_STORE_DC = re.compile(r"For STORE #:\s*(?:DC\s*#?\s*)?(\d+)", re.IGNORECASE)
RE_CITY = re.compile(r"([A-Z][A-Z .'\-]+?),+\s*([A-Z]{2})\s+(\d{5})")
RE_BOX = re.compile(
    r"BOX LxWxH:\s*([\d.]+)\s*x\s*([\d.]+)\s*x\s*([\d.]+)\s*IN,\s*([\d.,]+)\s*LB", re.IGNORECASE
)
# "TOTAL: 1200 25 TOT WEIGHT: 490.5 LB TOT DIMENSION: 80.13 CFT" -> unidades, cartones, lb, CFT
RE_TOTAL = re.compile(
    r"^TOTAL:\s*([\d,]+)\s+([\d,]+)\s+TOT WEIGHT:?\s*([\d,.]+)?\s*(?:LB)?"
    r"(?:\s*TOT DIMENSION:?\s*([\d,.]+))?",
    re.MULTILINE,
)
RE_NUM = re.compile(r"^[\d,]+$")
