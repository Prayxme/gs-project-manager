"""Flujo de análisis y escritura con una hoja simulada (sin Google)."""
import re

import pytest
from intake_fakes import FakeGateway, fila, inbound_ok, motor_sqlite, orden

from app.modules.order_intake import services as service
from app.modules.order_intake.repository import IntakeLog


@pytest.fixture
def log():
    return IntakeLog(motor_sqlite(), create_tables=True)


def test_clasifica_nuevo_registrado_y_revision():
    gw = FakeGateway({482: fila(6849411), 483: fila(6849412, ctns=70)})
    r = service.analizar_ordenes([orden(6849411), orden(6849412, ctns=75), orden(6849999, store="XXX999")], gw)
    estados = {o["piktik"]: o["status"] for o in r["orders"]}
    assert estados == {"6849411": "REGISTERED", "6849412": "REVISION", "6849999": "NEW"}
    rev = next(o for o in r["orders"] if o["piktik"] == "6849412")
    assert rev["diffs"] == [{"col": "V", "campo": "QTY CTNS", "antes": "70", "ahora": "75"}]
    nuevo = next(o for o in r["orders"] if o["piktik"] == "6849999")
    assert any("XXX999" in a for a in nuevo["warnings"])
    assert r["summary"] == {"NEW": 1, "REGISTERED": 1, "REVISION": 1}


def test_aplicar_escribe_nuevas_al_final_y_solo_celdas_cambiadas(log):
    gw = FakeGateway({482: fila(6849411), 483: fila(6849412, ctns=70)}, inbound=[inbound_ok("HAMU4749408")])
    r = service.aplicar([orden(6849411), orden(6849412, ctns=75), orden(6849999), orden(6849999)], gw, log,
                        source_ref="prueba.pdf")
    assert r["written"] == [{"piktik": "6849999", "row": 484}]          # al final, sin duplicar
    assert [x["piktik"] for x in r["revised"]] == ["6849412"]
    assert r["unchanged"] == ["6849411"]
    nueva = gw.escrituras[0][2]
    assert nueva["G"] == "Yes" and nueva["D"] == "01347018" and nueva["V"] == 147
    assert ("UPDATE", 483, {"V": 75}) in gw.escrituras                  # solo la celda que cambió
    recientes = log.recientes()
    acciones = [(x["piktik"], x["action"], x["sheet_row"]) for x in recientes]
    assert set(acciones) == {("6849999", "NEW", 484), ("6849412", "REVISION", 483)}
    assert all(re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", x["ts"]) for x in recientes)  # UTC con Z
    nueva_log = next(x for x in recientes if x["action"] == "NEW")
    assert nueva_log["details"]["H"] == "2026-11-06"                    # fechas en ISO dentro del detalle


def test_aplicar_relee_la_hoja_y_no_duplica(log):
    gw = FakeGateway({482: fila(6849411)})
    service.aplicar([orden(6849500)], gw, log)
    r = service.aplicar([orden(6849500)], gw, log)                       # segunda vez: ya existe
    assert r["written"] == [] and r["unchanged"] == ["6849500"]


def test_contenedor_ausente_escribe_no(log):
    gw = FakeGateway({482: fila(6849411)})
    service.aplicar([orden(6849600, containers=["ZZZU1234567"])], gw, log)
    assert gw.escrituras[0][2]["G"] == "No"


def test_sugerencias_solo_filas_en_no_ya_recibidas():
    gw = FakeGateway({482: fila(6849411), 483: fila(6849412, g="Yes"), 484: fila(6849413, conts="ZZZU1234567")},
                     inbound=[inbound_ok("HAMU4749408")])
    assert [s["row"] for s in service.sugerencias(gw)] == [482]
