"""Reglas del monitor de routing (portadas del Apps Script + correcciones)."""
from datetime import date

import pytest

from app.modules.open_orders import rules


# --- fechas y cliente ------------------------------------------------------------
def test_parse_mmddyy():
    assert rules.parse_mmddyy("10/19/26") == date(2026, 10, 19)
    assert rules.parse_mmddyy("00/00/00") is None
    assert rules.parse_mmddyy("") is None
    assert rules.parse_mmddyy("basura") is None


@pytest.mark.parametrize("cust,code", [("MARS125", "MARS"), ("BURL043", "BURL"), ("S&JS120", "S&JS"),
                                       ("DDSD230", "DDSD"), ("ALLS120", "ALLS")])
def test_customer_code(cust, code):
    assert rules.customer_code(cust) == code


# --- ventana de routing por cliente ---------------------------------------------------
def test_burl_cinco_dias_naturales():
    deadline, earliest = rules.routing_window(date(2026, 10, 14), date(2026, 10, 20), "BURL")
    assert deadline == date(2026, 10, 15)          # 20 - 5 días naturales
    assert earliest == date(2026, 9, 23)           # ship - 21


def test_burl_nunca_antes_del_ship_date():
    deadline, _ = rules.routing_window(date(2026, 10, 18), date(2026, 10, 20), "BURL")
    assert deadline == date(2026, 10, 18)


def test_ross_ddsd_macy_y_resto():
    ship, cancel = date(2026, 11, 2), date(2026, 11, 5)
    assert rules.routing_window(ship, cancel, "ROSS") == (cancel, date(2026, 10, 12))
    assert rules.routing_window(ship, cancel, "DDSD") == (cancel, date(2026, 10, 12))
    assert rules.routing_window(ship, cancel, "MACY") == (cancel, date(2026, 10, 26))
    assert rules.routing_window(ship, cancel, "MARS") == (cancel, None)
    assert rules.routing_window(ship, None, "MARS") == (None, None)


# --- estados -------------------------------------------------------------------------
@pytest.mark.parametrize("dias,estado", [(-1, "OVERDUE"), (0, "LAST DAY"), (1, "ATTENTION"),
                                         (3, "ATTENTION"), (4, "SAFE")])
def test_estados_por_dias(dias, estado):
    hoy = date(2026, 11, 9)
    deadline = date.fromordinal(hoy.toordinal() + dias)
    assert rules.determine_status(deadline, None, "", hoy) == estado


def test_routed_y_too_early():
    hoy = date(2026, 11, 9)
    assert rules.determine_status(date(2026, 11, 1), None, "CS123", hoy) == "ROUTED"
    assert rules.determine_status(date(2026, 12, 1), date(2026, 11, 20), "", hoy) == "TOO EARLY"


def test_sin_error_por_cambio_de_horario():
    # El Apps Script dividía milisegundos y perdía un día al cruzar el cambio de horario de marzo.
    o = rules.evaluar({"cust": "MARS125", "ship_date": "03/01/26", "cancel_date": "03/10/26",
                       "cfrm_number": ""}, date(2026, 3, 7))
    assert o["days_remaining"] == 3 and o["status"] == "ATTENTION"


def test_orden_por_prioridad():
    hoy = date(2026, 11, 9)
    base = {"cust": "MARS125", "ship_date": "11/01/26", "cfrm_number": ""}
    ordenes = [rules.evaluar({**base, "pick_ticket": pt, "cancel_date": c}, hoy)
               for pt, c in [("A", "11/30/26"), ("B", "11/08/26"), ("C", "11/09/26"), ("D", "11/11/26")]]
    assert [o["pick_ticket"] for o in rules.ordenar(ordenes)] == ["B", "C", "D", "A"]


# --- tipo de Cfrm Number (formatos reales del histórico) ------------------------------------
@pytest.mark.parametrize("valor,tipo", [
    ("CS02489696", "APPOINTMENT"),
    ("Load ID\t10624682", "APPOINTMENT"),
    ("LOAD ID # 10624681", "APPOINTMENT"),   # el Apps Script lo trataba como routing (bug)
    ("Load ID  : 213244568", "APPOINTMENT"),
    ("Load Id 213301152", "APPOINTMENT"),
    ("LOAD ID # 8WM9935", "APPOINTMENT"),
    ("LOAD ID CT0122980-81", "APPOINTMENT"),
    ("CT0123623-24R-A", "APPOINTMENT"),
    ("Tracking ID 877971527033", "APPOINTMENT"),
    ("879382044275", "APPOINTMENT"),
    ("RTS 2402037", "ROUTING"),
    ("REF# 42420825", "ROUTING"),
    ("D12345", "ROUTING"),
    ("42566632", "ROUTING"),                 # BURL/NEWT sin prefijo (portal real, sin cita)
    ("PJ# 9224591", "ROUTING"),              # MACY
    ("RTS 15200006 / RTS 152000", "ROUTING"),
    ("algo raro", "OTHER"),
    ("", ""),
])
def test_cfrm_type(valor, tipo):
    assert rules.cfrm_type(valor) == tipo


def test_clasificar_salida():
    assert rules.clasificar_salida({"cfrm_number": "LOAD ID # 10624681"}) == ("COMPLETED", "SHIPPED")
    assert rules.clasificar_salida({"cfrm_number": "RTS 2402037"}) == ("REMOVED", "REMOVED BEFORE APPOINTMENT")
    assert rules.clasificar_salida({"cfrm_number": ""}) == ("CANCELLED", "CANCELLED BEFORE ROUTING")


# --- detección de cambios --------------------------------------------------------------------
def test_registra_todos_los_cambios_de_una_corrida():
    old = {"cfrm_number": "", "ship_date": "10/01/26", "cancel_date": "10/10/26", "notes": "",
           "appt_date": "", "appt_time": "", "ctns": "10"}
    new = {**old, "cfrm_number": "RTS 1", "cancel_date": "10/12/26", "notes": "llamar"}
    eventos = [e[0] for e in rules.detectar_cambios(old, new)]
    assert eventos == ["ROUTING ADDED", "CANCEL DATE CHANGED", "NOTES UPDATED"]


@pytest.mark.parametrize("antes,despues,evento", [
    ("", "CS1", "APPOINTMENT ASSIGNED"),
    ("RTS 1", "CS1", "APPOINTMENT ASSIGNED"),
    ("CS1", "CS2", "APPOINTMENT CHANGED"),
    ("RTS 1", "RTS 2", "ROUTING NUMBER CHANGED"),
    ("CS1", "", "ROUTING REMOVED"),
])
def test_eventos_de_cfrm(antes, despues, evento):
    assert rules.detectar_cambios({"cfrm_number": antes}, {"cfrm_number": despues})[0][0] == evento


def test_sin_cambios_no_hay_eventos():
    o = {"cfrm_number": "Load ID\t1", "notes": " x "}
    assert rules.detectar_cambios(o, {"cfrm_number": "Load ID 1", "notes": "x"}) == []
