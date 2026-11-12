"""Pruebas del parser. Los textos replican lo que pdfplumber extrae de los
Pick Tickets reales (MARS125, MARS120, MARS240)."""
import os
from pathlib import Path

import pytest

from app.shared.pick_ticket import extraer_datos_pick_ticket, parsear_paginas
from app.shared.pick_ticket import parse_item_line as _parse_item_line

HEADER = """WIESNER PRODUCTS, INC.
1410 Broadway, 8th Floor
New York, NY 10018
TEL: 212-279-2466 FAX: 212-202-6116
Wave #: 88974 Whse: PM
{pk} W{pk} PICK TICKET
PikTik Date PikTik No Page
10/21/2026 {pk} {page}
SOLD TO: SHIP TO: {dc}
MARSHALLS MARSHALL'S PHOENIX DC # {dc}
FRAMINGHAM, MA 01701 PHOENIX, AZ 85043
For STORE #: {dc}
Order No Order Date Cust No Rep PO No Ship Date Cancel Date Ship Via FOB
1660645 07/17/2026 MARS125 125 {po} 10/12/2026 10/19/2026 ROUTING INFO
ITEM # MPO Qty Ord Cases Description / Container#:ETA Cust-SKU# / Color
"""

PAGE_1 = HEADER.format(pk="6844422", page=1, dc="882", po="02332062") + """3-M2056ST MARS P24 S40570 2 2 56 94 MENS 3 PACK WOOL WORK SOCKS 295344
BOX LxWxH: 21.654x10.630x11.811 IN, 17.747 LB, 1.573 CFT WHSU5648862:09/05 ASSORTED
 Size -> FP Total
 Cartons -> 94 94
3-M2057ST MARS P24 S40571 3 3 60 140 MENS 3 PACK WOOL WORK SOCKS 295348
BOX LxWxH: 21.654x10.630x11.811 IN, 17.747 LB, 1.573 CFT WHSU5648862:09/05 ASSORTED
 Cartons -> 140 140
"""
PAGE_2 = HEADER.format(pk="6844422", page=2, dc="882", po="02332062") + """8-M389ST MARS P24 S40448,S40233 6 6 00 275 MENS 8 PACK HALF CUSHION CREW 295366
BOX LxWxH: 18.504x21.654x12.992 IN, 33.510 LB, 3.013 CFT YMMU6866710:09/21 BLACK
 Cartons -> 275 275
TOTAL: 20088 509 TOT WEIGHT: 18,750.9 LB TOT DIMENSION: 1,712.60 CFT
"""
PAGE_OTRO = HEADER.format(pk="6846787", page=1, dc="884", po="02530856") + """6B4543MS RTCAMOP06 W708710 6000 1000 JUNGLE PRINT MOCCASIN CLOG 671208
BOX LxWxH: 19.685x9.449x12.992 IN, 8.818 LB, 1.398 CFT HAMU1280322:10/15 REAL TREE CAMO
 Cartons -> 1,000 1,000
TOTAL: 6000 1000 TOT WEIGHT: 8,818.0 LB TOT DIMENSION: 1,398.00 CFT
"""


def test_linea_item_cantidad_partida_en_miles():
    r = _parse_item_line("3-M2056ST MARS P24 S40570 2 2 56 94 MENS 3 PACK WOOL WORK SOCKS 295344")
    assert r["sku"] == "3-M2056ST" and r["cases"] == 94 and r["cust_sku"] == "295344"
    assert r["variant"] == "MARS P24 S40570"


def test_linea_item_con_variante_numerica():
    r = _parse_item_line("MLGO40416 001 MJF FA59197 6 2 64 261 FLEECE LINED WOVEN INVISIBLE C 410317")
    assert r["cases"] == 261 and r["variant"].startswith("001 MJF")


def test_un_pikitk_en_varias_paginas_es_una_sola_orden():
    r = parsear_paginas([PAGE_1, PAGE_2])
    assert len(r["orders"]) == 1
    o = r["orders"][0]
    assert o["piktik"] == "6844422" and o["po"] == "02332062" and o["ship_to_dc"] == "882"
    assert o["pages"] == 2
    assert [i["qty"] for i in o["items"]] == [94, 140, 275]
    assert r["warnings"] == []  # 94+140+275 == 509 declarado


def test_cada_pikitk_es_una_orden_distinta_con_su_destino():
    r = parsear_paginas([PAGE_1, PAGE_2, PAGE_OTRO])
    assert [o["piktik"] for o in r["orders"]] == ["6844422", "6846787"]
    otro = r["orders"][1]
    assert otro["po"] == "02530856" and otro["ship_to_dc"] == "884"
    assert otro["destination"] == "PHOENIX, AZ"
    assert otro["items"][0]["qty"] == 1000 and otro["items"][0]["l"] == 19.685


def test_advierte_si_total_no_coincide():
    mala = PAGE_2.replace("20088 509", "20088 600")
    r = parsear_paginas([PAGE_1, mala])
    assert any("TOTAL declarado" in w for w in r["warnings"])


def test_sin_pikitk_falla_claro():
    with pytest.raises(ValueError):
        parsear_paginas(["texto cualquiera"])


def test_variantes_del_mismo_codigo_se_desambiguan():
    pagina = HEADER.format(pk="6848652", page=1, dc="882", po="02566354") + """MLGO40416 001 MJF FA59197 6 2 64 261 FLEECE 410317
BOX LxWxH: 14.567x21.260x11.811 IN, 24.251 LB, 2.1 CFT X BLACK
MLGO40416 CARB MJF FA59197 3 5 28 147 FLEECE 410326
BOX LxWxH: 14.567x21.260x11.811 IN, 24.251 LB, 2.1 CFT X BLACK
TOTAL: 9000 408 TOT WEIGHT: 1.0 LB TOT DIMENSION: 1.00 CFT
"""
    skus = [i["sku"] for i in parsear_paginas([pagina])["orders"][0]["items"]]
    assert skus == ["MLGO40416 001", "MLGO40416 CARB"]


def _pdfs():
    base = os.environ.get("PIKTIK_PDF_DIR")
    return sorted(Path(base).glob("oe_piktik_*.pdf")) if base else []


@pytest.mark.skipif(not _pdfs(), reason="defina PIKTIK_PDF_DIR con PDFs reales para esta prueba")
@pytest.mark.parametrize("pdf", _pdfs(), ids=lambda p: p.name[:40])
def test_pdfs_reales_sin_advertencias(pdf):
    r = extraer_datos_pick_ticket(pdf.read_bytes())
    assert r["orders"] and r["warnings"] == []
