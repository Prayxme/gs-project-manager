"""Plan de routing completo (PDFs ya leídos + portal falso) y endpoint /api/routing/plan."""
from datetime import date

from fastapi.testclient import TestClient

from app.modules.routing import dependencies as routing_deps
from app.modules.routing import router as routing_router
from app.modules.routing.services import construir_plan, leer_portal

HOY = date(2026, 11, 12)
BURL = {"code": "512", "name": "BURLINGTON DC # 512", "street": "570 EAST MILL STREET",
        "city": "SAN BERNARDINO", "state": "CA", "zip": "92408", "text": "", "key": "92408 570 E MILL ST"}
ROSS = {"code": "1", "name": "ROSS STORES INC", "street": "3404 INDIAN AVENUE", "city": "PERRIS",
        "state": "CA", "zip": "92572", "text": "", "key": "92572 3404 INDIAN AVE"}
CAJA = {"sku": "S1", "variant": "", "cust_sku": "", "l": 12.992, "w": 21.654, "h": 19.685,
        "weight": 19.621, "containers": []}


def _orden(piktik, po, cajas, cust="BURL120", ship_to=BURL, ship="11/11/2026", cancel="11/17/2026"):
    return {"piktik": piktik, "po": po, "cust_no": cust, "ship_date": ship, "cancel_date": cancel,
            "ship_to": ship_to, "declared_units": cajas * 48, "declared_cases": cajas,
            "declared_weight": round(cajas * 19.621, 1), "declared_cft": None,
            "items": [{**CAJA, "qty": cajas}] if cajas else []}


def _fila(piktik, po, ctns, cust="BURL120", cfrm=""):
    return {"pick_ticket": piktik, "po": po, "ctns": str(ctns), "cust": cust, "ship_to": "512",
            "ship_date": "11/11/26", "cancel_date": "11/17/26", "cfrm_number": cfrm}


def _plan(ordenes, filas):
    portal = {"orders": {f["pick_ticket"]: f for f in filas} if filas is not None else None,
              "error": None if filas is not None else "sin conexión"}
    return construir_plan([{"filename": "a.pdf", "orders": ordenes, "warnings": []}], portal, HOY)


def test_pos_de_la_misma_direccion_y_fecha_van_en_un_rts():
    p = _plan([_orden("1", "A", 25), _orden("2", "B", 50)], [_fila("1", "A", 25), _fila("2", "B", 50)])
    assert p["summary"]["rts"] == 1 and p["summary"]["routable"] == 2
    [rts] = p["rts"]
    assert rts["deadline"] == "2026-11-12" and rts["days_left"] == 0      # BURL: Cancel - 5
    a = next(x for x in rts["pos"] if x["po"] == "A")
    assert (a["estimated_pallets"], a["pallets"], a["cft"]) == (1, 2, 180)
    assert a["weight"] == 581 and a["units"] == 1200 and a["status"] == "OK"
    assert rts["pallets"] == sum(x["pallets"] for x in rts["pos"])


def test_destinos_o_cancel_distintos_no_se_juntan():
    p = _plan([_orden("1", "A", 25), _orden("2", "B", 25, cancel="11/24/2026"),
               _orden("3", "C", 25, cust="ROSS120", ship_to=ROSS)], None)
    assert p["summary"]["rts"] == 3
    assert not p["portal"]["ok"] and all(not r["verified"] for r in p["rts"])


def test_portal_manda_las_diferencias_excluyen_la_po():
    p = _plan([_orden("1", "A", 25), _orden("2", "B", 25), _orden("3", "C", 25), _orden("4", "D", 0)],
              [_fila("1", "A", 30), _fila("3", "C", 25, cfrm="RTS99"), _fila("4", "D", 0)])
    estados = {x["po"]: x["status"] for x in p["excluded"]}
    assert estados == {"A": "MISMATCH", "B": "NOT_IN_PORTAL", "C": "ALREADY_ROUTED", "D": "NO_ITEMS"}
    assert p["rts"] == []


def test_una_po_en_varios_pikitks_se_suma():
    p = _plan([_orden("1", "A", 25), _orden("2", "A", 25)], [_fila("1", "A", 25), _fila("2", "A", 25)])
    [po] = p["rts"][0]["pos"]
    assert po["piktiks"] == ["1", "2"] and po["cartons"] == 50 and po["units"] == 2400


def test_ross_aplica_peso_minimo_en_el_rts():
    p = _plan([_orden("1", "A", 25, cust="ROSS120", ship_to=ROSS)], [_fila("1", "A", 25, cust="ROSS120")])
    [po] = p["rts"][0]["pos"]
    assert po["weight"] == 3100 and po["weight_adjusted_from"] == 581
    assert p["rts"][0]["limit"] == 26 and p["rts"][0]["weight"] == 3100


def test_leer_portal_no_lanza():
    def falla():
        raise RuntimeError("caído")
    assert leer_portal(falla) == {"orders": None, "error": "caído"}


def test_endpoint_plan(monkeypatch):
    from app.main import app
    monkeypatch.setattr(routing_router, "extraer_datos_pick_ticket",
                        lambda b: {"company": "", "cust_no": "BURL120", "orders": [_orden("1", "A", 25)],
                                   "warnings": []})
    html = ('<table><tr class="tlist">' + "".join(f"<td>{v}</td>" for v in
            ["1", "W", "1", "40", "A", "512", "11/11/26", "11/17/26", "BURL120", "PM"] + [""] * 8 + ["25"])
            + "</tr></table>")
    app.dependency_overrides[routing_deps.get_fetcher] = lambda: (lambda: html)
    try:
        r = TestClient(app).post("/api/routing/plan", data={"today": "2026-11-12"},
                                 files=[("files", ("x.pdf", b"%PDF", "application/pdf"))])
        assert r.status_code == 200, r.text
        assert r.json()["summary"]["routable"] == 1 and r.json()["rts"][0]["pos"][0]["status"] == "OK"
        r = TestClient(app).post("/api/routing/plan", files=[("files", ("x.txt", b"x", "text/plain"))])
        assert r.status_code == 400
    finally:
        app.dependency_overrides.clear()
