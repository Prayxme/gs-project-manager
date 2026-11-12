"""Reglas del Routing: margen, valores declarados, peso mínimo ROSS/DDSD, conciliación y reparto."""
import pytest

from app.modules.routing import rules


@pytest.mark.parametrize("estimado,enrutar", [
    (0, 0), (1, 2), (2, 3), (4, 6), (7, 9), (15, 18), (17, 20), (20, 23), (24, 28),
])
def test_margen_sobre_la_estimacion(estimado, enrutar):
    assert rules.pallets_a_enrutar(estimado) == enrutar


@pytest.mark.parametrize("estimado,ultima,enrutar", [
    (4, 0.30, 5), (4, 0.35, 5), (4, 0.36, 6), (4, None, 6),   # última pallet casi vacía: un pallet menos
    (17, 0.10, 19), (24, 0.20, 27),
    (2, 0.10, 3), (1, None, 2),                                # el margen nunca baja de un pallet
])
def test_margen_segun_el_llenado_de_la_ultima_pallet(estimado, ultima, enrutar):
    assert rules.pallets_a_enrutar(estimado, ultima) == enrutar


def test_cft_por_cliente():
    assert rules.cft_declarado("BURL", 3) == 270
    assert rules.cft_declarado("MODE", 3) == 270
    assert rules.cft_declarado("ROSS", 3) == 390
    assert rules.cft_declarado("MARS", 1) == 130


def test_peso_incluye_45_lb_por_pallet():
    assert rules.peso_declarado(490.5, 2) == 581   # 490.5 + 90 -> 580.5 -> 581


def test_limites_y_familia():
    assert rules.limite_pallets("ROSS") == rules.limite_pallets("DDSD") == 26
    assert rules.limite_pallets("BURL") == rules.limite_pallets("MARS") == 28
    assert rules.limite_pallets("MODE") == 28
    assert rules.familia("MODE120") != rules.familia("BURL120")   # portales distintos
    assert rules.familia("BURL120") != rules.familia("BURL240")   # divisiones de la misma tienda
    assert rules.familia(" burl120 ") == "BURL120"


def _po(po, pallets, weight=1000):
    return {"po": po, "pallets": pallets, "weight": weight}


def test_ross_sube_la_po_mas_pesada_a_3100_si_el_rts_no_llega():
    pos = [_po("A", 1, 800), _po("B", 1, 1200)]
    rules.aplicar_peso_minimo("ROSS", pos)
    assert [p["weight"] for p in pos] == [800, 3100]
    assert pos[1]["weight_adjusted_from"] == 1200 and "weight_adjusted_from" not in pos[0]


def test_ross_con_suma_mayor_a_3100_declara_valores_reales():
    pos = [_po("A", 2, 1500), _po("B", 2, 1700)]
    rules.aplicar_peso_minimo("DDSD", pos)
    assert [p["weight"] for p in pos] == [1500, 1700]


def test_otros_clientes_sin_peso_minimo():
    pos = [_po("A", 1, 500)]
    rules.aplicar_peso_minimo("BURL", pos)
    assert pos[0]["weight"] == 500


PORTAL = {"6849648": {"pick_ticket": "6849648", "po": "578810301", "ctns": "25", "cfrm_number": ""}}


def test_conciliacion_ok_y_diferencias():
    assert rules.conciliar("6849648", "578810301", 25, PORTAL)[0] == "OK"
    estado, difs, _ = rules.conciliar("6849648", "578810301", 26, PORTAL)
    assert estado == "MISMATCH" and "Cartones" in difs[0]
    assert rules.conciliar("6849648", "999", 25, PORTAL)[0] == "MISMATCH"
    assert rules.conciliar("1", "578810301", 25, PORTAL)[0] == "NOT_IN_PORTAL"
    assert rules.conciliar("6849648", "578810301", 25, None)[0] == "UNVERIFIED"


def test_conciliacion_ya_enrutada():
    portal = {"1": {"po": "P", "ctns": "1,000", "cfrm_number": "RTS123"}}
    assert rules.conciliar("1", "P", 1000, portal)[0] == "ALREADY_ROUTED"


def _grupo(po, cust="BURL", key="92408 570 E MILL ST", cancel="2026-11-17", division="120"):
    return {"po": po, "customer_code": cust, "family": rules.familia(cust + division), "address_key": key,
            "cancel_date": cancel}


def test_clave_de_grupo():
    assert rules.clave_grupo(_grupo("1")) == rules.clave_grupo(_grupo("2"))
    # BURL y MODE van al mismo DC 512 pero se enrutan en portales distintos.
    assert rules.clave_grupo(_grupo("1")) != rules.clave_grupo(_grupo("2", cust="MODE"))
    assert rules.clave_grupo(_grupo("1")) != rules.clave_grupo(_grupo("2", division="240"))
    assert rules.clave_grupo(_grupo("1")) != rules.clave_grupo(_grupo("2", cancel="2026-11-24"))
    assert rules.clave_grupo(_grupo("1")) != rules.clave_grupo(_grupo("2", key="92572 3404 INDIAN AVE"))
    # MARS / TJMA / NEWT: el prefijo de la PO separa DCs aunque la dirección coincida.
    assert rules.clave_grupo(_grupo("01061696", "MARS")) != rules.clave_grupo(_grupo("20061696", "MARS"))
    assert rules.clave_grupo(_grupo("01061696", "MARS")) == rules.clave_grupo(_grupo("01999999", "MARS"))
    # Sin dirección: cada PO va sola.
    assert rules.clave_grupo(_grupo("1", key="")) != rules.clave_grupo(_grupo("2", key=""))


def test_reparto_respeta_el_limite_y_minimiza_rts():
    pos = [_po(str(i), n) for i, n in enumerate([18, 9, 11, 8, 9, 2])]
    rts = rules.repartir_en_rts(pos, 28)
    assert all(sum(p["pallets"] for p in r) <= 28 for r in rts)
    assert len(rts) == 3 and sum(len(r) for r in rts) == 6


def test_po_que_supera_el_limite_va_sola():
    rts = rules.repartir_en_rts([_po("A", 30), _po("B", 2)], 28)
    assert [[p["po"] for p in r] for r in rts] == [["A"], ["B"]]
