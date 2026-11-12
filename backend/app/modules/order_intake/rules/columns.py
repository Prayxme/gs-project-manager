"""
Mapeo de una orden a las columnas de la hoja BONNIE (las demás columnas NUNCA se tocan):
  A ##          casilla sin marcar (FALSE) en filas nuevas
  B COMPANY     empresa del encabezado del PDF (WIESNER, FASHION OPTION, ...)
  C STORE       Cust No (MARS125)
  D PO #        texto, conserva ceros a la izquierda
  E PICK TICKET número
  F Container   contenedores separados por espacio
  G Received    Yes / No según la hoja INBOUND (solo al crear la fila) -> rules/received.py
  H STAR DATE   Ship Date
  I CANCEL DATE Cancel Date
  V QTY CTNS    total de cartones
"""
import re
from typing import Dict

from app.shared.containers import find_containers
from app.shared.dates import parse_date

_SUFIJOS_EMPRESA = {"INC", "LLC", "CO", "CORP", "LTD", "PRODUCTS", "SOCKS"}


def empresa(nombre_pdf: str) -> str:
    """'Wiesner Products, Inc.' -> 'WIESNER'; 'Soled Out Socks.' -> 'SOLED OUT'."""
    palabras = re.sub(r"[^A-Za-z0-9& ]+", " ", nombre_pdf or "").upper().split()
    while palabras and palabras[-1] in _SUFIJOS_EMPRESA:
        palabras.pop()
    return " ".join(palabras)


def desde_pdf(orden: Dict) -> Dict:
    """Orden del lector de PDF -> orden de ingreso (lo que el usuario revisa y puede corregir)."""
    return {
        "piktik": str(orden["piktik"]),
        "company": empresa(orden.get("company", "")),
        "store": orden.get("cust_no", ""),
        "po": orden.get("po", ""),
        "containers": list(orden.get("containers", [])),
        "ship_date": orden.get("ship_date", ""),
        "cancel_date": orden.get("cancel_date", ""),
        "ctns": sum(int(it.get("qty", 0)) for it in orden.get("items", [])),
    }


def valores_orden(orden: Dict) -> Dict[str, object]:
    """Valores de las columnas de datos (sin A ni G). Acepta una orden de ingreso o una del PDF."""
    o = orden if "store" in orden else desde_pdf(orden)
    return {
        "B": o["company"],
        "C": o["store"],
        "D": str(o["po"]).strip(),
        "E": int(o["piktik"]),
        "F": " ".join(find_containers(" ".join(o["containers"]))),
        "H": parse_date(o["ship_date"]),
        "I": parse_date(o["cancel_date"]),
        "V": int(o["ctns"]),
    }
