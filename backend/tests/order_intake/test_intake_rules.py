"""Reglas del ingreso de órdenes: mapeo a columnas, recepción de contenedores y revisiones."""
from datetime import date

from app.modules.order_intake import rules

ORDEN = {
    "piktik": "6849411", "po": "01347018", "cust_no": "MARS125", "company": "Wiesner Products, Inc.",
    "ship_date": "11/06/2026", "cancel_date": "11/13/2026", "containers": ["HAMU4749408", "CSNU8090823"],
    "items": [{"qty": 147}],
}


def fila_hoja(**cambios):
    """Fila tal como la devuelve la hoja BONNIE (A..V)."""
    f = [""] * 22
    valores = {"A": True, "B": "WIESNER", "C": "MARS125", "D": "01347018", "E": 6849411,
               "F": "HAMU4749408 CSNU8090823", "G": "No", "H": "11/06/2026", "I": "11/13/2026", "V": 147}
    valores.update(cambios)
    for letra, v in valores.items():
        f[rules.col_idx(letra)] = v
    return f


def inbound(*filas):
    """Filas de INBOUND: (contenedor, status, valor de P..X); T queda en NO a propósito."""
    out = []
    for cont, status, check in filas:
        f = [""] * 25
        f[1], f[3] = cont, status
        for letra in "PQRSUVWX":
            f[rules.col_idx(letra)] = check
        f[rules.col_idx("T")] = "NO"  # T se excluye de la regla
        out.append(f)
    return rules.indice_inbound(out)


def test_empresa():
    assert rules.empresa("Wiesner Products, Inc.") == "WIESNER"
    assert rules.empresa("Soled Out Socks.") == "SOLED OUT"
    assert rules.empresa("Fashion Option") == "FASHION OPTION"
    assert rules.empresa("Kids With Character") == "KIDS WITH CHARACTER"


def test_contenedores_ignora_texto_extra():
    assert rules.contenedores("FFAU2892254 (LTL)") == ["FFAU2892254"]
    assert rules.contenedores("EITU8240613 EGSU1233180") == ["EITU8240613", "EGSU1233180"]
    assert rules.contenedores("CANCELED\nKOCU9003877") == ["KOCU9003877"]


def test_valores_de_fila_nueva():
    v = rules.valores_orden(ORDEN)
    assert v == {"B": "WIESNER", "C": "MARS125", "D": "01347018", "E": 6849411,
                 "F": "HAMU4749408 CSNU8090823", "H": date(2026, 11, 6), "I": date(2026, 11, 13), "V": 147}


# --- columna G -----------------------------------------------------------------
def test_cartones_usa_el_total_declarado_y_si_no_la_suma():
    assert rules.desde_pdf({**ORDEN, "declared_cases": 147})["ctns"] == 147
    # Alguna línea no se pudo leer: manda el TOTAL del PDF (así lo registra la persona a mano).
    assert rules.desde_pdf({**ORDEN, "items": [{"qty": 210}], "declared_cases": 426})["ctns"] == 426
    assert rules.desde_pdf({**ORDEN, "items": [], "declared_cases": 150})["ctns"] == 150
    assert rules.desde_pdf({**ORDEN, "items": [{"qty": 100}, {"qty": 47}]})["ctns"] == 147  # sin TOTAL


def test_recibido_si_todos_returned_y_yes_aunque_T_sea_no():
    ib = inbound(("HAMU4749408", "Returned", "YES"), ("CSNU8090823", "Returned", "YES"))
    assert rules.recibido(ORDEN["containers"], ib) == ("Yes", [])


def test_no_recibido_si_uno_no_esta_returned():
    ib = inbound(("HAMU4749408", "Returned", "YES"), ("CSNU8090823", "Scheduled", "YES"))
    g, avisos = rules.recibido(ORDEN["containers"], ib)
    assert g == "No" and "CSNU8090823" in avisos[0]


def test_no_recibido_si_falta_un_yes():
    ib = inbound(("HAMU4749408", "Returned", "YES"), ("CSNU8090823", "Returned", "NO"))
    assert rules.recibido(ORDEN["containers"], ib)[0] == "No"


def test_contenedor_ausente_en_inbound_es_no():
    ib = inbound(("HAMU4749408", "Returned", "YES"))
    g, avisos = rules.recibido(ORDEN["containers"], ib)
    assert g == "No" and "No están en INBOUND" in avisos[0]


# --- revisiones ------------------------------------------------------------------
def test_sin_cambios_no_hay_revision():
    assert rules.comparar(ORDEN, fila_hoja()) == []


def test_fechas_de_la_hoja_en_cualquier_formato():
    assert rules.comparar(ORDEN, fila_hoja(H=46332, I="2026-11-13")) == []  # 46332 = 2026-11-06


def test_orden_distinto_de_contenedores_no_es_revision():
    assert rules.comparar(ORDEN, fila_hoja(F="CSNU8090823 HAMU4749408")) == []


def test_detecta_revision_de_cartones_po_fechas_y_contenedores():
    difs = rules.comparar(ORDEN, fila_hoja(D="01347000", F="HAMU4749408", H="11/05/2026", I="11/12/2026", V="140"))
    assert [d["col"] for d in difs] == ["D", "F", "H", "I", "V"]
    v = next(d for d in difs if d["col"] == "V")
    assert (v["antes"], v["ahora"]) == ("140", "147")


def test_pdf_sin_contenedores_no_borra_los_de_la_hoja():
    sin_lineas = {**ORDEN, "containers": [], "items": [], "declared_cases": 147}
    assert rules.comparar(sin_lineas, fila_hoja()) == []


def test_cambios_en_columnas_manuales_no_cuentan():
    assert rules.comparar(ORDEN, fila_hoja(G="Yes", B="OTRA", C="OTRA")) == []


# --- sugerencias de G ---------------------------------------------------------------
def test_sugiere_received_cuando_ya_llegaron_los_contenedores():
    ib = inbound(("HAMU4749408", "Returned", "YES"), ("CSNU8090823", "Returned", "YES"))
    filas = [(438, fila_hoja()), (439, fila_hoja(E=6849412, G="Yes")), (440, fila_hoja(E=6849413, F="XXXU1234567"))]
    assert rules.sugerencias_received(filas, ib) == [
        {"row": 438, "piktik": "6849411", "containers": ["HAMU4749408", "CSNU8090823"]}
    ]
