"""Pruebas del motor de empaque y de las reglas físicas."""
import pytest

from app.modules.palletizer.schemas import Dimensions, OrderItem, PackingRequest, PalletConfig
from app.shared.packing.layer_patterns import mejor_patron_2d, mejor_patron_caja
from app.modules.palletizer.services.packing_service import optimizar_orden_pallets
from app.shared.packing.physics_engine import PlacedBox, soporte, validar_pallet

W, D, H = 40.0, 48.0, 79.5


def item(sku, qty, l, w, h, wt, po="P1", dc="882", piktik="PK1"):
    return OrderItem(sku=sku, quantity=qty, dimensions=Dimensions(length_in=l, width_in=w, height_in=h),
                     weight_lbs=wt, po=po, piktik=piktik, ship_to_dc=dc)


def correr(items, **cfg):
    return optimizar_orden_pallets(PackingRequest(order_id="t", pallet_config=PalletConfig(**cfg), items=items))


def cajas_de(resp):
    return [b for p in resp["pallets"] for b in p["placed_items"]]


def a_placed(p):
    base = 5.5
    return [PlacedBox(b["sku"], b["position"]["x"], b["position"]["y"] - base, b["position"]["z"],
                      b["rendered_dimensions"]["width_in"], b["rendered_dimensions"]["height_in"],
                      b["rendered_dimensions"]["length_in"], b["weight_lbs"]) for b in p["placed_items"]]


# --- patrones 2D --------------------------------------------------------------
def test_patron_2d_no_se_sale_ni_se_solapa():
    rects = mejor_patron_2d(W, D, 19.685, 9.449)
    assert rects
    for i, (x, z, w, d) in enumerate(rects):
        assert x >= 0 and z >= 0 and x + w <= W + 1e-6 and z + d <= D + 1e-6
        for (x2, z2, w2, d2) in rects[i + 1:]:
            assert not (x < x2 + w2 - 1e-6 and x + w > x2 + 1e-6 and z < z2 + d2 - 1e-6 and z + d > z2 + 1e-6)


def test_patron_caja_respeta_altura():
    pat = mejor_patron_caja((19.685, 9.449, 12.992), 12.992, W, D, H)
    assert pat.alto_total <= H + 1e-6 and pat.capacidad >= 50


# --- conservación de cajas --------------------------------------------------
@pytest.mark.parametrize("qty", [1, 7, 60, 61, 125, 333])
def test_nunca_se_pierden_ni_duplican_cajas(qty):
    r = correr([item("A", qty, 19.685, 9.449, 12.992, 8.8)])
    assert len(cajas_de(r)) == qty and r["unplaced_boxes"] == 0
    assert r["summary"]["boxes_placed"] == qty


def test_cero_items():
    r = correr([])
    assert r["pallets"] == [] and r["unplaced_boxes"] == 0


def test_caja_que_no_cabe_se_reporta():
    r = correr([item("GIGANTE", 3, 60, 60, 100, 5)])
    assert r["unplaced_boxes"] == 3 and r["pallets"] == []
    assert r["unplaced"][0]["sku"] == "GIGANTE"


# --- reglas físicas en todos los pallets generados --------------------------------
def test_todos_los_pallets_son_fisicamente_validos():
    items = [
        item("PESADA", 275, 18.5, 21.65, 12.99, 33.5),
        item("MED1", 94, 21.654, 10.63, 11.811, 17.7),
        item("MED2", 140, 21.654, 10.63, 11.811, 17.7),
        item("LIV", 70, 21.654, 10.63, 11.811, 16.2),
    ]
    r = correr(items)
    assert r["summary"]["boxes_placed"] == 579
    for p in r["pallets"]:
        assert validar_pallet(a_placed(p), W, D, H) == [], p["pallet_id"]
        assert p["metrics"]["max_height_in"] <= 85.0 + 0.05


# --- negocio: no mezclar POs ---------------------------------------------------
def test_pallets_no_mezclan_pos_ni_dcs():
    items = [
        item("X", 13, 15.7, 9.8, 13.0, 5.7, po="PO-A", dc="881"),
        item("X", 11, 15.7, 9.8, 13.0, 5.7, po="PO-B", dc="884"),
        item("Y", 9, 15.7, 9.8, 13.0, 5.7, po="PO-A", dc="881"),
    ]
    r = correr(items)
    for p in r["pallets"]:
        assert len({(b["po"], b["ship_to_dc"]) for b in p["placed_items"]}) == 1
    assert sum(1 for b in cajas_de(r) if b["po"] == "PO-B") == 11
    assert len(cajas_de(r)) == 33


# --- negocio: rellenar huecos con otros SKU de la misma PO ---------------------------
def test_sobrantes_de_distintos_sku_comparten_pallet():
    # Dos SKU con 10 cajas c/u: por separado serían 2 pallets; juntos caben en 1.
    r = correr([item("A", 10, 19.685, 9.449, 12.992, 8.8), item("B", 10, 17.7, 9.05, 11.4, 8.8)])
    assert len(r["pallets"]) == 1
    assert set(r["pallets"][0]["metrics"]["sku_breakdown"]) == {"A", "B"}
    assert r["pallets"][0]["pallet_type"] == "MIXTO"


def test_misma_po_en_dos_piktiks_comparte_pallet():
    # Misma PO repetida con PikTiks distintos (cantidades distintas) es válida y se combina.
    r = correr([item("A", 10, 19.685, 9.449, 12.992, 8.8, po="PO-1", piktik="PK-1"),
                item("B", 10, 17.7, 9.05, 11.4, 8.8, po="PO-1", piktik="PK-2")])
    assert len(r["pallets"]) == 1
    assert {b["piktik"] for b in r["pallets"][0]["placed_items"]} == {"PK-1", "PK-2"}


def test_po_distintas_nunca_se_combinan_aunque_sobre_espacio():
    r = correr([item("A", 10, 19.685, 9.449, 12.992, 8.8, po="PO-1"),
                item("A", 10, 19.685, 9.449, 12.992, 8.8, po="PO-2")])
    assert len(r["pallets"]) == 2
    assert [p["po"] for p in r["pallets"]] == ["PO-1", "PO-2"]


def test_lo_pesado_queda_abajo():
    r = correr([item("LIVIANA", 10, 19.685, 9.449, 12.992, 3.0), item("PESADA", 10, 17.7, 9.05, 11.4, 30.0)])
    for p in r["pallets"]:
        cajas = a_placed(p)
        for b in cajas:
            _, apoyos = soporte([o for o in cajas if o is not b], b.x, b.y, b.z, b.w, b.d)
            assert all(b.weight <= a.weight + 1e-6 for a in apoyos)


# --- límite de peso opcional --------------------------------------------------------
def test_peso_maximo_opcional():
    sin = correr([item("A", 60, 19.685, 9.449, 12.992, 20.0)])
    con = correr([item("A", 60, 19.685, 9.449, 12.992, 20.0)], max_weight_lbs=500.0)
    assert len(cajas_de(con)) == 60 and len(con["pallets"]) > len(sin["pallets"])
    assert all(p["metrics"]["total_weight_lbs"] <= 500.0 + 1e-6 for p in con["pallets"])


def test_resultado_determinista():
    items = [item("A", 70, 21.654, 10.63, 11.811, 16.2), item("B", 45, 18.5, 21.65, 12.99, 33.5)]
    assert correr(items) == correr(items)


def test_coordenadas_a_un_decimal():
    r = correr([item("A", 20, 19.685, 9.449, 12.992, 8.8)])
    for b in cajas_de(r):
        for v in (*b["position"].values(), *b["rendered_dimensions"].values()):
            assert round(v, 1) == v
