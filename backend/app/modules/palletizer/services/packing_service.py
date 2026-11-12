"""
Motor de empaque propio: punto de entrada del servicio (POST /api/palletizer/pack).

Reglas de negocio:
  * Cada PO se empaca por separado: un pallet jamás mezcla POs ni DCs distintos.
  * Dentro de una PO sí se mezclan SKU para aprovechar huecos.
  * Lo más pesado va como base.
  * Cajas ordenadas en capas alineadas; límites del pallet siempre respetados.

El motor (patrones de capas, colocación, física) vive en app/shared/packing.
"""
from typing import Any, Dict, List, Tuple

from app.modules.palletizer.schemas import PackingRequest
from app.shared.packing.group_packer import empacar_grupo
from app.shared.packing.models import Linea
from app.shared.packing.physics_engine import construir_pallet_dict, validar_pallet


def _agrupar(request: PackingRequest) -> Dict[Tuple[str, str], List[Linea]]:
    """Líneas agrupadas por (DC, PO): nunca se mezclan entre sí."""
    grupos: Dict[Tuple[str, str], List[Linea]] = {}
    for it in request.items:
        ln = Linea(
            sku=it.sku.strip() or "SKU",
            l=it.dimensions.length_in, w=it.dimensions.width_in, h=it.dimensions.height_in,
            weight=it.weight_lbs, qty=it.quantity,
            po=(it.po or "").strip(), piktik=(it.piktik or "").strip(),
            dc=(it.ship_to_dc or "").strip(),
        )
        grupos.setdefault((ln.dc, ln.po), []).append(ln)
    return grupos


def _pct(volumen: float, vol_util: float, n_pallets: int) -> float:
    return round(100.0 * volumen / (vol_util * n_pallets), 1) if n_pallets else 0.0


def optimizar_orden_pallets(request: PackingRequest) -> Dict[str, Any]:
    config = request.pallet_config
    W, D = float(config.width_in), float(config.length_in)
    H = float(config.max_total_height_in - config.base_height_in)  # altura útil (79.5)
    peso_max = config.max_weight_lbs
    grupos = _agrupar(request)

    response_pallets: List[Dict[str, Any]] = []
    no_colocadas: List[Dict[str, Any]] = []
    resumen_grupos: List[Dict[str, Any]] = []
    contador = 1
    vol_util = W * D * H

    for (dc, po) in sorted(grupos):
        lineas = grupos[(dc, po)]
        pallets, sobrantes = empacar_grupo(lineas, W, D, H, peso_max)
        no_colocadas.extend(sobrantes)
        n_cajas = 0
        vol = 0.0
        for p in sorted(pallets, key=lambda q: (-q.volumen, -len(q.boxes))):
            d = construir_pallet_dict(p.boxes, config, f"PALLET-{contador}", po=po, dc=dc)
            errores = validar_pallet(p.boxes, W, D, H, peso_max)
            if errores:  # red de seguridad: nunca debería ocurrir
                d["metrics"]["voladizos_peligrosos"] = len(errores)
                d["metrics"]["alertas"] += errores
            response_pallets.append(d)
            contador += 1
            n_cajas += len(p.boxes)
            vol += p.volumen
        resumen_grupos.append({
            "po": po,
            "ship_to_dc": dc,
            "piktiks": sorted({ln.piktik for ln in lineas if ln.piktik}),
            "boxes_requested": sum(ln.qty for ln in lineas),
            "boxes_placed": n_cajas,
            "pallets": len(pallets),
            "volume_utilization_pct": _pct(vol, vol_util, len(pallets)),
        })

    vol_total = sum(
        b["rendered_dimensions"]["width_in"] * b["rendered_dimensions"]["height_in"]
        * b["rendered_dimensions"]["length_in"]
        for p in response_pallets for b in p["placed_items"]
    )
    return {
        "order_id": request.order_id,
        "pallets": response_pallets,
        "unplaced_boxes": sum(u["count"] for u in no_colocadas),
        "unplaced": no_colocadas,
        "groups": resumen_grupos,
        "summary": {
            "total_pallets": len(response_pallets),
            "pallets_homogeneous": sum(1 for p in response_pallets if p["pallet_type"] == "HOMOGENEO"),
            "pallets_mixed": sum(1 for p in response_pallets if p["pallet_type"] == "MIXTO"),
            "boxes_requested": sum(g["boxes_requested"] for g in resumen_grupos),
            "boxes_placed": sum(g["boxes_placed"] for g in resumen_grupos),
            "volume_utilization_pct": _pct(vol_total, vol_util, len(response_pallets)),
        },
    }
