"""SHIP TO por posición, dirección normalizada y línea TOTAL completa (casos de PDFs reales)."""
from app.shared.pick_ticket import parsear_paginas
from app.shared.pick_ticket.address import clave_direccion, parse_ship_to
from app.shared.pick_ticket.ship_to_block import ship_to_lines


def _w(text, x0, top):
    return {"text": text, "x0": x0, "top": top}


def _fila(top, izquierda, derecha):
    """Palabras de una línea con la columna SOLD TO (x=30) y la SHIP TO (x=323)."""
    ws, x = [], 30.0
    for t in izquierda.split():
        ws.append(_w(t, x, top))
        x += 30
    x = 323.0
    for t in derecha.split():
        ws.append(_w(t, x, top))
        x += 30
    return ws


WORDS_BURL = (
    _fila(100, "SOLD TO:", "SHIP TO: 512")
    + _fila(110, "MODECRAFT FASHIONS", "BURLINGTON DC # 512")
    + _fila(120, "1830 ROUTE 130 N.", "570 EAST MILL STREET")
    + _fila(130, "ACCOUNTS PAYABLE DEPT.", "")
    + _fila(140, "BURLINGTON, NJ 08016", "SAN BERNARDINO, CA 92408")
    + _fila(150, "For STORE #: 512", "")
)


def test_bloque_ship_to_separa_la_columna_del_sold_to():
    assert ship_to_lines(WORDS_BURL) == [
        "SHIP TO: 512", "BURLINGTON DC # 512", "570 EAST MILL STREET", "SAN BERNARDINO, CA 92408"]


def test_sin_ship_to_devuelve_none():
    assert ship_to_lines([_w("hola", 10, 10)]) is None


def test_direccion_burlington():
    d = parse_ship_to(ship_to_lines(WORDS_BURL))
    assert d["code"] == "512" and d["name"] == "BURLINGTON DC # 512"
    assert (d["street"], d["city"], d["state"], d["zip"]) == (
        "570 EAST MILL STREET", "SAN BERNARDINO", "CA", "92408")
    assert d["key"] == "92408 570 E MILL ST"


def test_misma_direccion_escrita_distinto_tiene_la_misma_clave():
    # ROSS "SHIP TO: 1" y ROSS "SHIP TO: DC" van al mismo DC de Perris.
    a = parse_ship_to(["SHIP TO: 1", "ROSS STORES INC", "DISTRIBUTION CENTER", "3404 INDIAN AVENUE",
                       "PERRIS, CA 92572"])
    b = parse_ship_to(["SHIP TO: DC", "ROSS PROCUREMENT, INC. SWDC", "3404 INDIAN AVE", "PERRIS, CA 92572"])
    assert a["key"] == b["key"] == "92572 3404 INDIAN AVE"
    assert clave_direccion("7145 RICKENBACKER, PKWY W", "43217") == clave_direccion(
        "7145 RICKENBACKER PKWY W", "43217")
    assert clave_direccion("4100 EASTLONE MOUNTAIN ROAD", "89081") == clave_direccion(
        "4100 EASTLONE MOUNTAIN RD", "89081")


def test_direcciones_distintas_no_coinciden():
    phoenix = parse_ship_to(["SHIP TO: 881", "MARSHALLS D/C #881", "3000 S 55TH AVENUE", "PHOENIX, AZ 85043"])
    el_paso = parse_ship_to(["SHIP TO: 884", "MARSHALLS DC #884", "3900 GLOBAL RANCH DRIVE", "EL PASO, TX 79925"])
    assert phoenix["key"] != el_paso["key"]


def test_calle_con_linea_extra_y_ciudad_con_doble_coma():
    d = parse_ship_to(["SHIP TO: DC", "ALL STAR COMMERCE GROUP LLC", "766 SHREWSBURY AVE, SUITE 401",
                       "TINTON FALLS,, NJ 07724"])
    assert d["city"] == "TINTON FALLS" and d["zip"] == "07724"
    d = parse_ship_to(["SHIP TO: 893", "TJ MAXX", "PIT: PITTSTON", "DC # 893", "4000 OLDFIELD BLVD",
                       "PITTSTON, PA 18640"])
    assert d["street"] == "4000 OLDFIELD BLVD"
    d = parse_ship_to(["SHIP TO: 115", "BEALLS DIST CENTER #115", "2100 47TH TER E", "BRADENTON, FL 34203-3774"])
    assert d["zip"] == "34203"


PAGINA = """6849648 W6849648
PICK TICKET
WIESNER PRODUCTS, INC.
1410 Broadway, 8th Floor
PikTik Date PikTik No Page
11/12/2026 6849648 1
SOLD TO: SHIP TO: 512
Order No Order Date Cust No Rep PO No Ship Date Cancel Date Ship Via FOB
1651260 04/30/2026 BURL120 120 578810301 11/18/2026 11/24/2026 ROUTING INFO CC
ITEM # MPO Qty Ord Cases Description / Container#:ETA Cust-SKU# / Color
4-L7467AK BURL P48 S90944 1 2 00 25 LADIES ANNE KLEIN 4PK COZY CRE 025634421069
BOX LxWxH: 12.992x21.654x19.685 IN, 19.621 LB, 3.205 CFT FFAU6441937:10/23 BURL ASSORTED
TOTAL: 1,200 25 TOT WEIGHT: 3,490.5 LB TOT DIMENSION: 1,080.13 CFT
"""


def test_total_completo_y_ship_to_en_la_orden():
    [o] = parsear_paginas([PAGINA], [ship_to_lines(WORDS_BURL)])["orders"]
    assert (o["declared_units"], o["declared_cases"], o["declared_weight"], o["declared_cft"]) == (
        1200, 25, 3490.5, 1080.13)
    assert o["ship_to"]["key"] == "92408 570 E MILL ST"


def test_total_sin_lb_tras_el_peso():
    # NEWT125 sin líneas: "TOT WEIGHT: 0.0 TOT DIMENSION: 0.00 CFT" (sin "LB").
    p = PAGINA.replace("TOTAL: 1,200 25 TOT WEIGHT: 3,490.5 LB TOT DIMENSION: 1,080.13 CFT",
                       "TOTAL: 0 320 TOT WEIGHT: 0.0 TOT DIMENSION: 0.00 CFT")
    [o] = parsear_paginas([p])["orders"]
    assert (o["declared_units"], o["declared_cases"], o["declared_weight"], o["declared_cft"]) == (0, 320, 0.0, 0.0)


def test_sin_bloque_ship_to_la_orden_queda_sin_direccion():
    [o] = parsear_paginas([PAGINA])["orders"]
    assert o["ship_to"] is None and o["declared_units"] == 1200
