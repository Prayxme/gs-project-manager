"""
Lectura de la tabla de pick tickets que devuelve el portal (ajcmd_show_list).

Estructura (portada del Apps Script): cada orden es un <tr class="tlist">.
Celdas: 0 #, 1 DV, 2 Pick Ticket, 3 Stg, 4 PO#, 5 Ship To, 6 Ship Date,
7 Cancel Date, 8 Cust#, 9 Wh, ... 18 Ctns. Los campos editables vienen en
<input id="DNUMxxx_n" value="...">.
"""
import re
from typing import Dict, List

from bs4 import BeautifulSoup

from app.shared.text import normalize_spaces as normalizar

INPUTS = {
    "rqst_date": "DNUMRQSTDAT",
    "cfrm_number": "DNUMCONFNO",
    "cfrm_date": "DNUMCONFDAT",
    "appt_date": "DNUMAPPTDAT",
    "appt_time": "DNUMAPPTTIME",
    "notes": "DNUMCOMMENT",
}
MIN_CELDAS = 19


class PortalResponseError(Exception):
    """La respuesta no es la tabla esperada (sesión vencida, error del portal, etc.)."""


def _celda(td) -> str:
    return normalizar(td.get_text(" ", strip=True))


def parse_table(html: str) -> List[Dict]:
    if not html or "<title>Login" in html:
        raise PortalResponseError("El portal devolvió la página de login (sesión no válida).")

    soup = BeautifulSoup(html, "html.parser")
    filas = soup.find_all("tr", class_="tlist")
    ordenes: List[Dict] = []
    for tr in filas:
        tds = tr.find_all("td", recursive=False)
        if len(tds) < MIN_CELDAS:
            continue

        def valor_input(prefijo: str) -> str:
            inp = tr.find("input", id=re.compile(rf"^{prefijo}_\d+$", re.I))
            return normalizar(inp.get("value", "")) if inp else ""

        pick_ticket = _celda(tds[2])
        if not pick_ticket:
            continue
        orden = {
            "row_number": _celda(tds[0]),
            "dv": _celda(tds[1]),
            "pick_ticket": pick_ticket,
            "stg": _celda(tds[3]),
            "po": _celda(tds[4]),
            "ship_to": _celda(tds[5]),
            "ship_date": _celda(tds[6]),
            "cancel_date": _celda(tds[7]),
            "cust": _celda(tds[8]),
            "wh": _celda(tds[9]),
            "ctns": _celda(tds[18]),
        }
        for campo, prefijo in INPUTS.items():
            orden[campo] = valor_input(prefijo)
        ordenes.append(orden)
    return ordenes
