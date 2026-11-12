"""Lector de la tabla, actualización con historial, salvaguardas, importación CSV y API."""
from datetime import date, datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from app.modules.open_orders import dependencies as oo_deps
from app.modules.open_orders import services as service
from app.modules.open_orders.parser import PortalResponseError, parse_table
from app.modules.open_orders.repository import OpenOrdersRepository


def fila(n, pt, po, cust, ship, cancel, cfrm="", appt="", notes="", ctns="10"):
    celdas = [str(n), "", pt, "RC", po, "882", ship, cancel, cust, "PM"]
    celdas += [f'<input id="DNUMRQSTDAT_{n}" value="">',
               f'<input id="DNUMCONFNO_{n}" value="{cfrm}">',
               f'<input id="DNUMCONFDAT_{n}" value="">',
               f'<input id="DNUMAPPTDAT_{n}" value="{appt}">',
               f'<input id="DNUMAPPTTIME_{n}" value="">',
               f'<input id="DNUMCOMMENT_{n}" value="{notes}">', "", "", ctns, ""]
    return '<tr class="tlist">' + "".join(f"<td>{c}</td>" for c in celdas) + "</tr>"


def tabla(*filas):
    return "<table>" + "".join(filas) + "</table>"


@pytest.fixture
def store():
    # Pruebas sobre SQLite en memoria con el mismo código (SQLAlchemy); producción usa PostgreSQL.
    engine = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})
    return OpenOrdersRepository(engine, create_tables=True)


# --- lector -------------------------------------------------------------------------------
def test_parse_table():
    html = tabla(fila(1, "6846787", "02530856", "MARS125", "10/12/26", "10/19/26",
                      cfrm="Load ID&#9;10896771", notes="KNIGHT"))
    [o] = parse_table(html)
    assert o["pick_ticket"] == "6846787" and o["po"] == "02530856" and o["cust"] == "MARS125"
    assert o["cfrm_number"] == "Load ID 10896771" and o["notes"] == "KNIGHT" and o["ctns"] == "10"


def test_parse_table_rechaza_login():
    with pytest.raises(PortalResponseError):
        parse_table("<html><title>Login</title></html>")


# --- actualización -----------------------------------------------------------------------------
def test_flujo_completo_de_actualizaciones(store):
    a = fila(1, "100", "PO-A", "MARS125", "11/01/26", "11/20/26")
    b = fila(2, "200", "PO-B", "BURL043", "11/04/26", "11/10/26", cfrm="RTS 5")
    r1 = service.refresh(store, lambda: tabla(a, b))
    assert r1["initial_sync"] and r1["new"] == 0 and r1["total"] == 2

    # Segunda corrida igual: no debe generar eventos (el Apps Script duplicaba el historial).
    eventos_antes = len(store.events())
    service.refresh(store, lambda: tabla(a, b))
    assert len(store.events()) == eventos_antes

    # Tercera: llega C, B recibe cita, A desaparece sin routing.
    b2 = fila(2, "200", "PO-B", "BURL043", "11/04/26", "11/10/26", cfrm="CS0001", appt="11/09/26")
    c = fila(3, "300", "PO-C", "ROSS043", "11/12/26", "11/15/26")
    r3 = service.refresh(store, lambda: tabla(b2, c))
    assert (r3["new"], r3["changed"], r3["removed"]) == (1, 1, 1)
    nombres = [e["event"] for e in store.events()]
    assert "NEW PICK TICKET" in nombres and "APPOINTMENT ASSIGNED" in nombres
    assert "APPOINTMENT DATE CHANGED" in nombres and "ORDER CANCELLED" in nombres
    [cerrada] = store.closed()
    assert cerrada["pick_ticket"] == "100" and cerrada["final_status"] == "CANCELLED"

    # B sale con cita -> COMPLETED / SHIPPED
    service.refresh(store, lambda: tabla(c))
    estados = {x["pick_ticket"]: x["final_status"] for x in store.closed()}
    assert estados["200"] == "COMPLETED"


def test_respuesta_vacia_no_borra_la_informacion(store):
    service.refresh(store, lambda: tabla(fila(1, "100", "PO-A", "MARS125", "11/01/26", "11/20/26")))
    with pytest.raises(PortalResponseError):
        service.refresh(store, lambda: "<table></table>")
    assert list(store.load_orders()) == ["100"] and store.closed() == []
    assert store.last_runs(1)[0]["ok"] == 0


def test_resumen_cuenta_solo_lo_de_hoy(store):
    service.refresh(store, lambda: tabla(fila(1, "100", "PO-A", "MARS125", "11/01/26", "11/20/26")))
    service.refresh(store, lambda: tabla(fila(1, "100", "PO-A", "MARS125", "11/01/26", "11/20/26"),
                                         fila(2, "200", "PO-B", "MARS125", "11/01/26", "11/09/26")))
    hoy_utc = datetime.now(timezone.utc).date()
    r = service.resumen(store, hoy_utc, "UTC")
    assert r["new_today"] == 1 and r["total_active"] == 2
    assert service.resumen(store, date(2020, 1, 1), "UTC")["new_today"] == 0


# --- importación del histórico -------------------------------------------------------------------
CSV = (
    "Date Removed,Final Status,Reason,Pick Ticket,PO#,Customer,Ship Date,Cancel Date,Cfrm Number,Appt Date,Notes\n"
    "9/29/2026,COMPLETED,SHIPPED,6841553,2919262,MARS120,09/15/26,09/22/26,Load ID\t10624682,09/29/26,RXO\n"
    "9/30/2026,CANCELLED,CANCELLED BEFORE ROUTING,6843472,580650703,BURL120,10/14/26,10/20/26,,00/00/00,\n"
    "9/30/2026,CANCELLED,CANCELLED BEFORE ROUTING,6843472,580650703,BURL120,10/14/26,10/20/26,,00/00/00,\n"
    "fecha mala,COMPLETED,SHIPPED,1,1,X,,,,,\n"
)


def test_importar_csv(store):
    r = service.importar_completadas_csv(store, CSV)
    assert r == {"inserted": 2, "duplicates": 1, "invalid": 1}
    assert service.importar_completadas_csv(store, CSV)["inserted"] == 0  # idempotente
    c = {x["pick_ticket"]: x for x in store.closed()}
    assert c["6841553"]["cfrm_number"] == "Load ID 10624682" and c["6841553"]["date_removed"] == "2026-09-29"


def test_importar_csv_columnas_incorrectas(store):
    with pytest.raises(ValueError):
        service.importar_completadas_csv(store, "a,b\n1,2\n")


# --- API ------------------------------------------------------------------------------------------
def test_api(store):
    from app.main import app
    html = tabla(fila(1, "100", "PO-A", "MARS125", "11/01/26", "11/09/26"))
    app.dependency_overrides[oo_deps.get_repository] = lambda: store
    app.dependency_overrides[oo_deps.get_fetcher] = lambda: (lambda: html)
    try:
        c = TestClient(app)
        assert c.post("/api/open-orders/refresh").json()["total"] == 1
        o = c.get("/api/open-orders/orders", params={"today": "2026-11-09"}).json()["orders"][0]
        assert o["status"] == "LAST DAY" and o["priority"] == "HIGH" and o["days_remaining"] == 0
        assert c.put("/api/open-orders/auto-refresh", json={"enabled": True}).json() == {"enabled": True}
        s = c.get("/api/open-orders/summary", params={"today": "2026-11-09", "tz": "America/Los_Angeles"}).json()
        assert s["auto_refresh"] is True and s["by_status"]["LAST DAY"] == 1
        r = c.post("/api/open-orders/import-completed", files={"file": ("h.csv", CSV.encode(), "text/csv")})
        assert r.json()["inserted"] == 2
        assert len(c.get("/api/open-orders/closed").json()["closed"]) == 2
        assert c.get("/api/open-orders/orders", params={"today": "mal"}).status_code == 422
    finally:
        app.dependency_overrides.clear()


def test_api_error_del_portal_es_502(store):
    from app.main import app

    def falla():
        raise PortalResponseError("sesión no válida")

    app.dependency_overrides[oo_deps.get_repository] = lambda: store
    app.dependency_overrides[oo_deps.get_fetcher] = lambda: falla
    try:
        r = TestClient(app).post("/api/open-orders/refresh")
        assert r.status_code == 502 and "sesión" in r.json()["detail"]
    finally:
        app.dependency_overrides.clear()
