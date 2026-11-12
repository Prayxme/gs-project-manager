"""Fase 2: bandeja de Gmail (sin Google: Gmail, hoja y lector de PDF simulados)."""
from datetime import date, datetime, timezone

import pytest
from fastapi.testclient import TestClient
from intake_fakes import FakeGateway, FakeGmail, fila, leer_pdf_falso, motor_sqlite, pdf_falso

from app.modules.order_intake import dependencies as deps
from app.modules.order_intake import services
from app.modules.order_intake.inbox_repository import InboxRepository
from app.modules.order_intake.repository import IntakeLog
from app.modules.order_intake.rules import inbox as reglas
from app.modules.order_intake.services import analysis

ASUNTO = "PICK-TICKETS - 00WPI - Whse:PM - Cust:MARS125 - 2026-11-11"
HOY = date(2026, 11, 12)


@pytest.fixture(autouse=True)
def lector_falso(monkeypatch):
    monkeypatch.setattr(analysis, "extraer_datos_pick_ticket", leer_pdf_falso)


@pytest.fixture
def repo():
    return InboxRepository(motor_sqlite(), create_tables=True)


def gmail_de_prueba():
    return FakeGmail({
        "m1": (ASUNTO, [("oe_piktik_00WPI_PM_MARS125-1.pdf", pdf_falso(6849411)),       # ya registrada
                        ("oe_wave_report-1.pdf", b"wave")]),                             # se ignora
        "m2": (ASUNTO, [("oe_piktik_00WPI_PM_MARS125-2.pdf", pdf_falso(6849411, 6849500))]),  # trae una nueva
        "m3": (ASUNTO, [("oe_piktik_00WPI_PM_MARS125-3.pdf", b"no es un pick ticket")]),  # ilegible
    })


def por_archivo(repo):
    return {i["filename"][-5:]: i for i in repo.listar()}


# --- reglas ------------------------------------------------------------------------------------
def test_reglas_de_la_bandeja():
    assert reglas.es_pdf_de_pick_tickets("oe_piktik_00WPI_PM_ROSS250-x.pdf", "oe_piktik")
    assert not reglas.es_pdf_de_pick_tickets("oe_wave_report-x.pdf", "oe_piktik")
    assert not reglas.es_pdf_de_pick_tickets("PO_BA_Container_Tally_Sheet.pdf", "oe_piktik")
    assert reglas.fecha_busqueda(None, HOY, 7) == date(2026, 11, 5)
    assert reglas.fecha_busqueda(datetime(2026, 11, 11, 23, 0, tzinfo=timezone.utc), HOY, 7) == date(2026, 11, 11)
    assert 'subject:"PICK-TICKETS - 00WPI - Whse:PM"' in reglas.consulta_gmail("a@b.com", "PICK-TICKETS - 00WPI - Whse:PM", HOY)
    assert reglas.nuevo_estado(reglas.PENDING, {"NEW": 0, "REVISION": 0, "REGISTERED": 3}, None) == reglas.NO_CHANGES
    assert reglas.nuevo_estado(reglas.PENDING, {"NEW": 1}, None) == reglas.PENDING
    assert reglas.nuevo_estado(reglas.DISMISSED, {"NEW": 1}, None) == reglas.DISMISSED   # decisión del usuario
    assert reglas.nuevo_estado(reglas.PENDING, None, "ilegible") == reglas.ERROR


# --- revisión de Gmail -------------------------------------------------------------------------
def test_guarda_solo_pick_tickets_y_clasifica(repo):
    gw = FakeGateway({482: fila(6849411)})
    r = services.revisar_gmail(repo, gmail_de_prueba(), gw, hoy=HOY)
    assert r == {"new": 3, "checked": 3, "pending": 1}
    items = por_archivo(repo)
    assert len(items) == 3                                               # el wave report no se guarda
    assert items["1.pdf"]["status"] == reglas.NO_CHANGES
    assert items["2.pdf"]["status"] == reglas.PENDING
    assert items["2.pdf"]["summary"] == {"NEW": 1, "REGISTERED": 1, "REVISION": 0}
    assert items["2.pdf"]["piktiks"] == ["6849411", "6849500"]
    assert items["3.pdf"]["status"] == reglas.ERROR and "PikTik" in items["3.pdf"]["error"]
    assert gw.lecturas == 1                                              # la hoja se lee una sola vez
    assert gw.escrituras == []                                           # nunca escribe en la hoja


def test_no_duplica_y_actualiza_si_la_registraron_a_mano(repo):
    gmail = gmail_de_prueba()
    gw = FakeGateway({482: fila(6849411)})
    services.revisar_gmail(repo, gmail, gw, hoy=HOY)
    gw.filas[483] = fila(6849500)                                        # alguien la escribió a mano
    r = services.revisar_gmail(repo, gmail, gw, hoy=HOY)
    assert r["new"] == 0 and r["pending"] == 0
    assert por_archivo(repo)["2.pdf"]["status"] == reglas.NO_CHANGES
    assert "after:2026/11/11" in gmail.consultas[-1]                     # sigue desde el último correo


def test_descartado_no_vuelve_solo_y_se_puede_restaurar(repo):
    services.revisar_gmail(repo, gmail_de_prueba(), FakeGateway({482: fila(6849411)}), hoy=HOY)
    item = por_archivo(repo)["2.pdf"]
    services.inbox.cambiar_estado(repo, item["id"], reglas.DISMISSED)
    services.revisar_gmail(repo, gmail_de_prueba(), FakeGateway({}), hoy=HOY)
    assert repo.obtener(item["id"])["status"] == reglas.DISMISSED
    services.inbox.cambiar_estado(repo, item["id"], reglas.PENDING)
    assert services.inbox.listar(repo)["pending"] == 1


# --- API ---------------------------------------------------------------------------------------
@pytest.fixture
def cliente(repo):
    from app.main import app

    gw = FakeGateway({482: fila(6849411)})
    log = IntakeLog(motor_sqlite(), create_tables=True)
    app.dependency_overrides.update({
        deps.get_inbox: lambda: repo, deps.get_log: lambda: log,
        deps.get_gateway: lambda: gw, deps.get_gmail: gmail_de_prueba,
    })
    with TestClient(app) as c:
        yield c, gw, log
    app.dependency_overrides.clear()


def test_api_flujo_completo_desde_gmail(cliente, repo):
    c, gw, log = cliente
    assert c.post("/api/order-intake/inbox/check").json()["new"] == 3
    lista = c.get("/api/order-intake/inbox").json()
    assert lista["pending"] == 1 and lista["last_check"]["ok"] is True
    assert {i["status"] for i in lista["items"]} == {reglas.PENDING, reglas.ERROR}   # por defecto, lo accionable
    assert len(c.get("/api/order-intake/inbox", params={"all": True}).json()["items"]) == 3
    item = next(i for i in lista["items"] if i["status"] == reglas.PENDING)

    analisis = c.post(f"/api/order-intake/inbox/{item['id']}/analyze").json()
    assert analisis["inbox_id"] == item["id"] and analisis["summary"]["NEW"] == 1
    nuevas = [o for o in analisis["orders"] if o["status"] == "NEW"]
    campos = ("piktik", "company", "store", "po", "containers", "ship_date", "cancel_date", "ctns")
    r = c.post("/api/order-intake/apply", json={
        "orders": [{k: o[k] for k in campos} for o in nuevas], "inbox_id": item["id"]}).json()
    assert r["written"] == [{"piktik": "6849500", "row": 483}]
    assert repo.obtener(item["id"])["status"] == reglas.APPLIED
    entrada = log.recientes()[0]
    assert entrada["source"] == "gmail" and entrada["source_ref"].startswith("Gmail: oe_piktik")

    pdf = c.get(f"/api/order-intake/inbox/{item['id']}/pdf")
    assert pdf.headers["content-type"] == "application/pdf" and pdf.content == pdf_falso(6849411, 6849500)
    assert c.post("/api/order-intake/inbox/9999/dismiss").status_code == 404
