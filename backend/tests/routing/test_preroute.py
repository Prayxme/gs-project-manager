"""Pre Routing: POs sin Pick Ticket (Excel o a mano), estimadas por cubo."""
import io
from datetime import date, datetime, timezone

import pytest
from fastapi.testclient import TestClient
from openpyxl import Workbook
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from app.modules.routing import config
from app.modules.routing import dependencies as routing_deps
from app.modules.routing.rules.cube import estimar_por_cubo
from app.modules.routing.rules.preroute import normalizar, numero, texto
from app.modules.routing.services.preroute import plan_preroute
from app.modules.routing.services.preroute_excel import leer_excel
from app.shared.pick_ticket_catalog import PickTicketCatalog

HOY = date(2026, 11, 13)
ENCABEZADO = ["Cust", "PO#", "Ship Dat", "Cncl Dat", "Style", "Color", "Qty", "Cases", "Weight", "Cube"]
SIN_PORTAL = {"orders": {}, "error": None}


def _linea(po, cases, cube=1.3, weight="9lb", cust="MARS125", **extra):
    return {"cust": cust, "po": po, "ship_date": "11/06/26", "cancel_date": "11/13/26", "style": "S1",
            "color": "BLACK", "qty": cases * 6, "cases": cases, "weight": weight, "cube": cube, **extra}


def _excel(filas, encabezado=ENCABEZADO, antes=()):
    libro = Workbook()
    hoja = libro.active
    for fila in [*antes, encabezado, *filas]:
        hoja.append(fila)
    salida = io.BytesIO()
    libro.save(salida)
    return salida.getvalue()


def test_numeros_y_textos_del_excel():
    assert numero("9lb") == 9 and numero("13.5 lb") == 13.5 and numero("1,200") == 1200 and numero(1.48) == 1.48
    assert numero("") is None and numero(None) is None and numero("lb") is None
    assert texto(20338991.0) == "20338991" and texto(" 01347014 ") == "01347014" and texto(None) == ""


@pytest.mark.parametrize("cubo,pallets,ultima", [
    (0, 0, None), (71.5, 1, None), (72.0, 1, None), (144.0, 2, 1.0), (144.3, 3, 0.004), (167.7, 3, 0.329),
])
def test_estimacion_por_cubo(cubo, pallets, ultima):
    assert config.CFT_UTIL_POR_PALLET == 72.0
    assert estimar_por_cubo(cubo) == (pallets, ultima)


def test_lineas_invalidas_se_descartan_con_aviso():
    lineas, avisos = normalizar([_linea("A", 10), {"cust": "", "po": ""}, _linea("B", 0), _linea("C", 5, cube=None),
                                 _linea("D", 5, weight="")])
    assert [ln["po"] for ln in lineas] == ["A", "D"]
    assert lineas[0] == {"cust": "MARS125", "po": "A", "ship_date": "2026-11-06", "cancel_date": "2026-11-13",
                         "style": "S1", "color": "BLACK", "qty": 60, "cases": 10, "weight": 9.0, "cube": 1.3,
                         "ship_to": ""}
    assert len(avisos) == 3 and "Cases" in avisos[0] and "Cube" in avisos[1] and "sin peso" in avisos[2]


def test_excel_con_filas_vacias_titulo_arriba_y_columnas_en_otro_orden():
    datos = leer_excel(_excel([["NEWT125", "20338991", "11/06/26", "11/13/26", "6TRB", "CHSTNT", 600, 100, "9lb", 1.48],
                               [None] * 10,
                               ["MARS125", 1347014, datetime(2026, 11, 6), datetime(2026, 11, 13), "6B", "CAMO", 666, 111, 9, 1.3]],
                              antes=[["Pre Route POs"], []]))
    lineas, avisos = normalizar(datos)
    assert avisos == [] and [(ln["po"], ln["cases"], ln["weight"], ln["cancel_date"]) for ln in lineas] == [
        ("20338991", 100, 9.0, "2026-11-13"), ("1347014", 111, 9.0, "2026-11-13")]
    otro = leer_excel(_excel([[5, 1.3, "X1", "BURL120"]], encabezado=["Ctns", "CFT", "PO", "Customer"]))
    assert otro == [{"cases": 5, "cube": 1.3, "po": "X1", "cust": "BURL120"}]
    with pytest.raises(ValueError):
        leer_excel(_excel([["a", "b"]], encabezado=["Uno", "Dos"]))
    with pytest.raises(ValueError):
        leer_excel(b"esto no es un excel")


def test_po_suma_sus_lineas_y_calcula_peso_y_cubo_totales():
    p = plan_preroute([_linea("06411417", 43, weight="14lb"), _linea("06411417", 77, weight="14lb"),
                       _linea("06411417", 31, weight="14lb")], SIN_PORTAL, HOY)
    [po] = p["rts"][0]["pos"]
    assert (po["cartons"], po["units"], po["cube"], po["cases_weight"]) == (151, 906, 196.3, 2114.0)
    assert (po["estimated_pallets"], po["last_pallet_fill"], po["pallets"]) == (3, 0.726, 5)
    assert po["weight"] == 2114 + 45 * 5 and po["cft"] == 130 * 5        # mismas reglas que con Pick Ticket
    assert po["status"] == "PRE_ROUTE" and po["piktiks"] == [] and po["items"] == [] and len(po["lines"]) == 3
    assert p["source"] == "preroute" and p["preroute"]["lines"] == 3 and p["rts"][0]["cube"] == 196.3
    assert p["rts"][0]["deadline"] == "2026-11-13" and p["rts"][0]["days_left"] == 0


def test_ultima_pallet_casi_vacia_tambien_reduce_el_margen_por_cubo():
    [po] = plan_preroute([_linea("01347014", 111)], SIN_PORTAL, HOY)["rts"][0]["pos"]     # 144.3 CFT
    assert (po["estimated_pallets"], po["pallets"], po["margin_reduced"]) == (3, 4, True)


def test_se_agrupa_por_customer_no_y_dc_de_la_po():
    p = plan_preroute([_linea("06347014", 50), _linea("06347016", 50), _linea("08347014", 50),
                       _linea("20347147", 50, cust="NEWT125"), _linea("X1", 50, cust="BURL120"),
                       _linea("X2", 50, cust="BURL120"), _linea("Y1", 50, cust="ROSS125", ship_to="Perris"),
                       _linea("Y2", 50, cust="ROSS125", ship_to="PERRIS")], SIN_PORTAL, HOY)
    grupos = sorted(sorted(x["po"] for x in r["pos"]) for r in p["rts"])
    assert grupos == [["06347014", "06347016"], ["08347014"], ["20347147"], ["X1"], ["X2"], ["Y1", "Y2"]]
    burl = next(x for r in p["rts"] for x in r["pos"] if x["po"] == "X1")
    assert "Sin destino" in burl["issues"][0]


def test_destino_conocido_sale_del_catalogo():
    cat = PickTicketCatalog(create_engine("sqlite://", poolclass=StaticPool,
                                          connect_args={"check_same_thread": False}), create_tables=True)
    destino = {"code": "886", "name": "MARSHALLS D/C #886", "street": "701 N MAIN STREET", "city": "BRIDGEWATER",
               "state": "VA", "zip": "22812", "text": "", "key": "22812 701 N MAIN ST"}
    cat.guardar("a.pdf", datetime(2026, 11, 12, tzinfo=timezone.utc), "gmail",
                [{"piktik": "1", "po": "06338569", "cust_no": "MARS125", "ship_to": destino, "items": []}])
    p = plan_preroute([_linea("06347014", 50), _linea("08347014", 50)], SIN_PORTAL, HOY, cat)
    por_po = {x["po"]: x for r in p["rts"] for x in r["pos"]}
    assert por_po["06347014"]["ship_to"]["city"] == "BRIDGEWATER"
    assert por_po["06347014"]["address_key"] == "22812 701 N MAIN ST"
    assert por_po["08347014"]["ship_to"]["name"] == "DC de las POs 08…"       # DC desconocido: por prefijo


def test_si_la_po_ya_esta_en_el_portal_el_portal_manda():
    def fila(pt, po, ctns, cfrm=""):
        return {"pick_ticket": pt, "po": po, "ctns": str(ctns), "cust": "MARS125", "cfrm_number": cfrm, "ship_to": "886"}
    portal = {"orders": {f["pick_ticket"]: f for f in [fila("1", "06000001", 50, "RTS9"), fila("2", "06000002", 40),
                                                       fila("3", "06000003", 50)]}, "error": None}
    p = plan_preroute([_linea("06000001", 50), _linea("06000002", 50), _linea("06000003", 50),
                       _linea("06000004", 50)], portal, HOY)
    assert [(x["po"], x["cfrm_number"]) for x in p["already_routed"]] == [("06000001", "RTS9")]
    assert [(x["po"], x["status"]) for x in p["excluded"]] == [("06000002", "MISMATCH")]
    assert {x["po"]: x["status"] for x in p["rts"][0]["pos"]} == {"06000003": "OK", "06000004": "PRE_ROUTE"}
    sin = plan_preroute([_linea("06000004", 50)], {"orders": None, "error": "caído"}, HOY)
    assert sin["rts"][0]["pos"][0]["status"] == "UNVERIFIED" and not sin["portal"]["ok"]


def test_endpoints_de_preroute():
    from app.main import app
    app.dependency_overrides[routing_deps.get_fetcher] = lambda: (lambda: "<table></table>")
    try:
        cliente = TestClient(app)
        xlsx = _excel([["MARS125", "06347014", "11/06/26", "11/13/26", "6B", "CAMO", 492, 82, "9lb", 1.3]])
        r = cliente.post("/api/routing/preroute/parse", files={"file": ("pre.xlsx", xlsx, "application/octet-stream")})
        assert r.status_code == 200, r.text
        lineas = r.json()["lines"]
        assert lineas[0]["po"] == "06347014" and lineas[0]["weight"] == 9.0
        assert cliente.post("/api/routing/preroute/parse", files={"file": ("pre.pdf", b"x", "x/y")}).status_code == 400
        assert cliente.post("/api/routing/preroute/parse", files={"file": ("pre.xlsx", b"x", "x/y")}).status_code == 422

        r = cliente.post("/api/routing/preroute/plan", json={"today": "2026-11-13", "lines": lineas})
        assert r.status_code == 200, r.text
        [po] = r.json()["rts"][0]["pos"]
        assert (po["po"], po["cartons"], po["cube"], po["pallets"]) == ("06347014", 82, 106.6, 3)
        assert cliente.post("/api/routing/preroute/plan", json={"lines": []}).status_code == 422
    finally:
        app.dependency_overrides.clear()
