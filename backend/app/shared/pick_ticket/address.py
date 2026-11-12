"""Dirección de destino (SHIP TO) y su clave normalizada para saber si dos POs van al mismo lugar.

La misma dirección llega escrita de varias formas ("3404 INDIAN AVENUE" / "3404 INDIAN AVE",
"4100 EASTLONE MOUNTAIN ROAD" / "... RD", "TINTON FALLS,, NJ"). El nombre también cambia
("BURLINGTON DC # 512" / "BURLINGTON DC NO 512"), así que la clave usa calle + código postal.
"""
import re
from typing import Dict, List, Optional

RE_CIUDAD = re.compile(r"^(.+?),+\s*([A-Z]{2})\s+(\d{5})(?:-?\d{4})?\s*$")
RE_CABECERA = re.compile(r"^SHIP TO:\s*(.*)$")

ABREVIATURAS = {
    "AVENUE": "AVE", "AV": "AVE", "STREET": "ST", "ROAD": "RD", "DRIVE": "DR", "BOULEVARD": "BLVD",
    "PARKWAY": "PKWY", "PKY": "PKWY", "HIGHWAY": "HWY", "LANE": "LN", "COURT": "CT", "PLACE": "PL",
    "TERRACE": "TER", "CIRCLE": "CIR", "SUITE": "STE", "NORTH": "N", "SOUTH": "S", "EAST": "E",
    "WEST": "W",
}


def normalizar_calle(calle: str) -> str:
    palabras = re.sub(r"[^A-Z0-9 ]", " ", calle.upper()).split()
    return " ".join(ABREVIATURAS.get(p, p) for p in palabras)


def clave_direccion(calle: str, zip5: str) -> str:
    return f"{zip5} {normalizar_calle(calle)}".strip()


def parse_ship_to(lineas: Optional[List[str]]) -> Optional[Dict[str, str]]:
    """['SHIP TO: 512', 'BURLINGTON DC # 512', '570 EAST MILL STREET', 'SAN BERNARDINO, CA 92408']
    -> {code, name, street, city, state, zip, text, key}."""
    if not lineas:
        return None
    cab = RE_CABECERA.match(lineas[0])
    codigo = cab.group(1).strip() if cab else ""
    cuerpo = [l for l in (lineas[1:] if cab else lineas) if l.strip()]
    i_ciudad = next((i for i in range(len(cuerpo) - 1, -1, -1) if RE_CIUDAD.match(cuerpo[i])), None)
    ciudad = estado = zip5 = ""
    antes = cuerpo
    if i_ciudad is not None:
        m = RE_CIUDAD.match(cuerpo[i_ciudad])
        ciudad, estado, zip5 = m.group(1).strip(" ,"), m.group(2), m.group(3)
        antes = cuerpo[:i_ciudad]
    # Calle: la última línea antes de la ciudad que empieza con número (p. ej. "63 AVENUE A",
    # aunque después venga "APT 3D"); si ninguna, la línea inmediatamente anterior.
    calle = next((l for l in reversed(antes) if l[:1].isdigit()), antes[-1] if len(antes) > 1 else "")
    return {
        "code": codigo,
        "name": cuerpo[0] if cuerpo else "",
        "street": calle,
        "city": ciudad,
        "state": estado,
        "zip": zip5,
        "text": " / ".join(cuerpo),
        "key": clave_direccion(calle, zip5) if zip5 else normalizar_calle(" ".join(cuerpo)),
    }
