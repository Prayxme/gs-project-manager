"""Plan de routing completo (PDFs ya leídos + portal falso) y endpoint /api/routing/plan."""
from datetime import date, datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from app.modules.routing import dependencies as routing_deps
from app.modules.routing import router as routing_router
from app.modules.routing import rules
from app.modules.routing.services import PortalNoDisponible, construir_plan, leer_portal, plan_seleccion
from app.modules.routing.services import purchase_orders
from app.modules.routing.services.estimate import Estimacion, estimar_pallets
from app.shared.pick_ticket_catalog import PickTicketCatalog, fecha_del_archivo
from app.shared.wiesner import URGENT_STATUSES

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
    p = _plan([_orden("1", "A", 25), _orden("2", "B", 25), _orden("4", "D", 0)],
              [_fila("1", "A", 30), _fila("4", "D", 0)])
    estados = {x["po"]: x["status"] for x in p["excluded"]}
    assert estados == {"A": "MISMATCH", "B": "NOT_IN_PORTAL", "D": "NO_ITEMS"}
    assert p["rts"] == [] and p["already_routed"] == []


def test_ya_enrutada_en_wiesner_no_se_estima_solo_se_informa(monkeypatch):
    estimadas = []
    monkeypatch.setattr(purchase_orders, "estimar_pallets", lambda po, items: estimadas.append(po) or Estimacion(1))
    p = _plan([_orden("1", "A", 25), _orden("3", "C", 25)],
              [_fila("1", "A", 25), _fila("3", "C", 25, cfrm="RTS99")])
    assert estimadas == ["A"]                                   # la ya enrutada no se calcula
    [c] = p["already_routed"]
    assert (c["po"], c["cfrm_number"], c["pallets"], c["status"]) == ("C", "RTS99", 0, "ALREADY_ROUTED")
    assert p["excluded"] == [] and p["summary"]["already_routed"] == 1
    assert [x["po"] for x in p["rts"][0]["pos"]] == ["A"]


# --- urgentes del portal con el catálogo de Pick Tickets ---------------------------------------------
def _catalogo(*ordenes):
    cat = PickTicketCatalog(create_engine("sqlite://", poolclass=StaticPool,
                                          connect_args={"check_same_thread": False}), create_tables=True)
    cat.guardar("a.pdf", datetime(2026, 11, 12, tzinfo=timezone.utc), "gmail", list(ordenes))
    return cat


def test_seleccion_por_estado_y_customer_no():
    filas = [_fila("1", "A", 25),                                   # BURL cancel 11/17 -> límite hoy
             _fila("2", "B", 25, cfrm="RTS1"),                      # ya enrutada
             {**_fila("3", "C", 25), "cancel_date": "12/20/26", "ship_date": "12/14/26"},   # muy pronto
             {**_fila("4", "D", 25, cust="MARS125"), "cancel_date": "11/14/26"},            # límite en 2 días
             {**_fila("5", "E", 25, cust="MARS125"), "cancel_date": "11/10/26"},            # vencida
             {**_fila("6", "F", 25, cust="MARS240"), "cancel_date": "11/10/26"}]            # vencida, otra división
    u = rules.seleccionar(filas, HOY, URGENT_STATUSES)
    assert [(x["po"], x["days_left"], x["status"]) for x in u] == [
        ("E", -2, "OVERDUE"), ("F", -2, "OVERDUE"), ("A", 0, "LAST DAY"), ("D", 2, "ATTENTION")]
    assert [x["po"] for x in rules.seleccionar(filas, HOY, ["OVERDUE"], "mars125")] == ["E"]
    assert [x["po"] for x in rules.seleccionar(filas, HOY, ["TOO EARLY"])] == ["C"]
    assert rules.seleccionar(filas, HOY, ["ROUTED"]) == []          # las enrutadas nunca se calculan


def _portal(*filas):
    return {"orders": {f["pick_ticket"]: f for f in filas}, "error": None}


def test_plan_de_seleccion_usa_el_catalogo_y_avisa_lo_que_falta():
    portal = _portal(_fila("1", "A", 25), _fila("2", "B", 50), _fila("3", "C", 25, cfrm="RTS1"))
    p = plan_seleccion(_catalogo(_orden("1", "A", 25), _orden("3", "C", 25)), portal, HOY, URGENT_STATUSES)
    assert p["selection"] == {"statuses": list(URGENT_STATUSES), "cust": "", "orders": 2, "ignored": 0}
    assert [x["po"] for x in p["rts"][0]["pos"]] == ["A"]
    assert [(m["po"], m["ctns"]) for m in p["missing"]] == [("B", "50")]   # sin Pick Ticket
    assert p["already_routed"] == []                                # la enrutada ni se considera


def test_pdf_subido_con_seleccion_solo_aporta_las_ordenes_de_interes():
    portal = _portal(_fila("1", "A", 25), _fila("2", "B", 50), _fila("9", "Z", 25, cust="BURL240"))
    pdf = {"filename": "nuevo.pdf", "warnings": [],
           "orders": [_orden("2", "B", 50), _orden("9", "Z", 25, cust="BURL240")]}
    p = plan_seleccion(_catalogo(_orden("1", "A", 25)), portal, HOY, ["LAST DAY"], "BURL120", [pdf])
    assert sorted(x["po"] for x in p["rts"][0]["pos"]) == ["A", "B"]       # catálogo + PDF subido
    assert p["missing"] == [] and p["selection"]["ignored"] == 1    # Z es de otro Customer No
    # Sin base de datos (catálogo opcional) el PDF subido basta.
    p = plan_seleccion(None, portal, HOY, ["LAST DAY"], "BURL120", [pdf])
    assert [x["po"] for x in p["rts"][0]["pos"]] == ["B"] and [m["po"] for m in p["missing"]] == ["A"]


def test_plan_de_seleccion_sin_portal_falla_claro():
    with pytest.raises(PortalNoDisponible):
        plan_seleccion(_catalogo(), {"orders": None, "error": "caído"}, HOY, URGENT_STATUSES)


def test_divisiones_de_la_misma_tienda_no_comparten_rts():
    p = _plan([_orden("1", "A", 25), _orden("2", "B", 25, cust="BURL240")],
              [_fila("1", "A", 25), _fila("2", "B", 25, cust="BURL240")])
    assert sorted(r["family"] for r in p["rts"]) == ["BURL120", "BURL240"]


def test_ultima_pallet_casi_vacia_reduce_el_margen(monkeypatch):
    monkeypatch.setattr(purchase_orders, "estimar_pallets", lambda po, items: Estimacion(4, 0, 0.3))
    [po] = _plan([_orden("1", "A", 25)], [_fila("1", "A", 25)])["rts"][0]["pos"]
    assert (po["estimated_pallets"], po["pallets"], po["margin_reduced"], po["last_pallet_fill"]) == (4, 5, True, 0.3)
    monkeypatch.setattr(purchase_orders, "estimar_pallets", lambda po, items: Estimacion(4, 0, 0.8))
    [po] = _plan([_orden("1", "A", 25)], [_fila("1", "A", 25)])["rts"][0]["pos"]
    assert (po["pallets"], po["margin_reduced"]) == (6, False)


def test_estimacion_mide_el_pallet_menos_lleno_y_la_po_lleva_sus_lineas():
    assert estimar_pallets("A", [{**CAJA, "qty": 25}]).ultima_llena is None      # un solo pallet
    e = estimar_pallets("A", [{**CAJA, "qty": 300}])
    assert e.pallets > 1 and 0 < e.ultima_llena <= 1
    [po] = _plan([_orden("1", "A", 25)], [_fila("1", "A", 25)])["rts"][0]["pos"]
    assert po["items"] == [{"sku": "S1", "qty": 25, "l": 12.992, "w": 21.654, "h": 19.685,
                            "weight": 19.621, "piktik": "1"}]


def test_fecha_del_nombre_del_archivo():
    f = fecha_del_archivo("oe_piktik_00WPI_PM_BURL120-20261112-103329am-927419.pdf")
    assert f.astimezone(timezone.utc) == datetime(2026, 11, 12, 15, 33, 29, tzinfo=timezone.utc)
    assert fecha_del_archivo("otro.pdf") is None


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
        cliente = TestClient(app)
        # Sin base de datos el plan de PDFs subidos funciona igual (el catálogo es opcional)...
        r = cliente.post("/api/routing/plan", data={"today": "2026-11-12"},
                         files=[("files", ("x.pdf", b"%PDF", "application/pdf"))])
        assert r.status_code == 200, r.text
        assert r.json()["summary"]["routable"] == 1 and r.json()["rts"][0]["pos"][0]["status"] == "OK"
        assert cliente.post("/api/routing/plan", files=[("files", ("x.txt", b"x", "text/plain"))]).status_code == 400
        # ...y el de urgentes responde 503 porque sí lo necesita.
        assert cliente.get("/api/routing/urgent").status_code == 503

        # Con catálogo: el PDF subido queda guardado y luego sirve para el plan de urgentes.
        catalogo = _catalogo()
        app.dependency_overrides[routing_deps.get_catalog] = lambda: catalogo
        app.dependency_overrides[routing_deps.get_catalog_opcional] = lambda: catalogo
        cliente.post("/api/routing/plan", data={"today": "2026-11-12"},
                     files=[("files", ("oe_piktik_X-20261112-103329am-1.pdf", b"%PDF", "application/pdf"))])
        u = cliente.get("/api/routing/urgent", params={"today": "2026-11-12"}).json()
        assert u["selection"]["orders"] == 1 and u["missing"] == [] and u["rts"][0]["pos"][0]["po"] == "A"
        sel = cliente.get("/api/routing/selection", params={"today": "2026-11-12", "status": "LAST DAY",
                                                            "cust": "BURL120"}).json()
        assert sel["summary"]["routable"] == 1
        assert cliente.get("/api/routing/selection", params={"status": "ROUTED"}).status_code == 422
        # Subir un PDF con selección: las órdenes fuera de la selección se ignoran.
        r = cliente.post("/api/routing/plan", data={"today": "2026-11-12", "status": "OVERDUE"},
                         files=[("files", ("x.pdf", b"%PDF", "application/pdf"))]).json()
        assert r["selection"]["ignored"] == 1 and r["rts"] == []
    finally:
        app.dependency_overrides.clear()
