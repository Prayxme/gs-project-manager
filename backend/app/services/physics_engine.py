from decimal import Decimal
from typing import List, Tuple, Dict, Any
from app.core.config import (
    TOLERANCIA_ALTURA_SOPORTE,
    UMBRAL_MINIMO_SOPORTE,
    TOLERANCIA_DESBALANCE_COG,
)

def aplicar_gravedad(b_items: list, max_h_util: float = 79.5, min_support_pct: float = 0.65) -> list:
    """
    Gravedad física estricta:
    1. Ordena cajas de abajo hacia arriba.
    2. Hace descender cada caja hasta el obstáculo más alto debajo de su huella.
    3. Descarta cualquier caja que sobrepase el techo útil o no tenga soporte sólido (>=65%).
    """
    b_items.sort(key=lambda item: float(item.position[1]))
    items_asentados = []
    
    for caja in b_items:
        pos_x = float(caja.position[0])
        pos_z = float(caja.position[2])
        w, h, d = [float(val) for val in caja.get_dimension()]
        area_base = w * d
        
        # Encontrar el techo más alto debajo de la base de esta caja
        max_y_obstaculo = 0.0
        for otra in items_asentados:
            ox = float(otra.position[0])
            oz = float(otra.position[2])
            ow, _, od = [float(val) for val in otra.get_dimension()]
            
            # Chequeo de solapamiento en el plano X-Z
            if (pos_x < ox + ow - 0.05) and (pos_x + w > ox + 0.05):
                if (pos_z < oz + od - 0.05) and (pos_z + d > oz + 0.05):
                    techo = float(otra.position[1]) + float(otra.get_dimension()[1])
                    if techo > max_y_obstaculo:
                        max_y_obstaculo = techo
                        
        altura_asiento = max_y_obstaculo
        
        # Medir área real de apoyo
        if altura_asiento <= 0.1:
            soporte_pct = 1.0  # Suelo del pallet
        else:
            area_soporte = 0.0
            for otra in items_asentados:
                y_techo = float(otra.position[1]) + float(otra.get_dimension()[1])
                if abs(y_techo - altura_asiento) < 0.15:
                    ox = float(otra.position[0])
                    oz = float(otra.position[2])
                    ow, _, od = [float(val) for val in otra.get_dimension()]
                    
                    ix_izq = max(pos_x, ox)
                    ix_der = min(pos_x + w, ox + ow)
                    iz_front = max(pos_z, oz)
                    iz_tras = min(pos_z + d, oz + od)
                    
                    if ix_der > ix_izq and iz_tras > iz_front:
                        area_soporte += (ix_der - ix_izq) * (iz_tras - iz_front)
            soporte_pct = area_soporte / area_base if area_base > 0 else 0.0

        # CONDICIÓN ESTRICTA: Solo se conserva si tiene soporte y no rompe el techo
        if soporte_pct >= min_support_pct:
            if altura_asiento + h <= max_h_util + 0.1:
                caja.position[1] = Decimal(str(round(altura_asiento, 2)))
                items_asentados.append(caja)

    b_items.clear()
    b_items.extend(items_asentados)
    return b_items

def calcular_area_interseccion(caja_arriba, caja_abajo) -> float:
    x1_arriba, _, z1_arriba = [float(val) for val in caja_arriba.position]
    w_arriba, _, d_arriba = [float(val) for val in caja_arriba.get_dimension()]
    x2_arriba, z2_arriba = x1_arriba + w_arriba, z1_arriba + d_arriba

    x1_abajo, _, z1_abajo = [float(val) for val in caja_abajo.position]
    w_abajo, _, d_abajo = [float(val) for val in caja_abajo.get_dimension()]
    x2_abajo, z2_abajo = x1_abajo + w_abajo, z1_abajo + d_abajo

    ix_izq, ix_der = max(x1_arriba, x1_abajo), min(x2_arriba, x2_abajo)
    iz_front, iz_tras = max(z1_arriba, z1_abajo), min(z2_arriba, z2_abajo)

    if ix_der > ix_izq and iz_tras > iz_front:
        return (ix_der - ix_izq) * (iz_tras - iz_front)
    return 0.0

def analizar_soporte(b_items: list) -> List[Dict[str, str]]:
    warnings = []
    for caja in b_items:
        pos_y = float(caja.position[1])
        w, _, d = [float(val) for val in caja.get_dimension()]
        if pos_y <= TOLERANCIA_ALTURA_SOPORTE:
            continue
            
        area_base = w * d
        area_soportada = 0.0
        for otra in b_items:
            y_ab = float(otra.position[1])
            _, h_ab, _ = [float(val) for val in otra.get_dimension()]
            if abs((y_ab + h_ab) - pos_y) <= TOLERANCIA_ALTURA_SOPORTE:
                area_soportada += calcular_area_interseccion(caja, otra)

        pct = area_soportada / area_base if area_base > 0 else 1.0
        if pct < UMBRAL_MINIMO_SOPORTE:
            sku_limpio = caja.name.split('###')[0]
            warnings.append({
                "sku": sku_limpio, 
                "mensaje": f"Soporte bajo en {sku_limpio}: {round(pct * 100, 1)}% apoyado."
            })
    return warnings

def analizar_equilibrio(b_items: list, pallet_w: float = 40.0, pallet_l: float = 48.0) -> Tuple[Dict[str, float], str, List[str]]:
    total_w, sum_x, sum_z = 0.0, 0.0, 0.0
    for item in b_items:
        peso = float(item.weight)
        fw, _, fd = [float(val) for val in item.get_dimension()]
        px, _, pz = [float(val) for val in item.position]
        sum_x += (px + fw / 2.0) * peso
        sum_z += (pz + fd / 2.0) * peso
        total_w += peso

    if total_w == 0:
        return {"x": 0.0, "z": 0.0}, "VACIA", []

    cog_x, cog_z = sum_x / total_w, sum_z / total_w
    ideal_x, ideal_z = pallet_w / 2.0, pallet_l / 2.0
    warnings = []
    status = "ESTABLE"

    if abs(cog_x - ideal_x) > (pallet_w * TOLERANCIA_DESBALANCE_COG):
        status, warnings = "INESTABLE", warnings + [f"Desbalance lateral (CoG X: {cog_x:.1f} in)."]
    if abs(cog_z - ideal_z) > (pallet_l * TOLERANCIA_DESBALANCE_COG):
        status, warnings = "INESTABLE", warnings + [f"Desbalance frontal (CoG Z: {cog_z:.1f} in)."]

    return {"x": round(cog_x, 2), "z": round(cog_z, 2)}, status, warnings

def construir_pallet_dict(bin_obj, config, pallet_id_str: str) -> Dict[str, Any]:
    net_height = float(config.max_total_height_in - config.base_height_in)
    
    # Asentar la carga físicamente
    aplicar_gravedad(bin_obj.items, max_h_util=net_height)

    cog, status_eq, warn_eq = analizar_equilibrio(bin_obj.items, config.width_in, config.length_in)
    warn_sop = analizar_soporte(bin_obj.items)

    pallet_data = {
        "pallet_id": pallet_id_str,
        "metrics": {
            "total_weight_lbs": round(sum(float(item.weight) for item in bin_obj.items), 2),
            "boxes_count": len(bin_obj.items),
            "balance_status": status_eq,
            "center_of_gravity": cog,
            "voladizos_peligrosos": len(warn_sop),
            "alertas": warn_eq + [w["mensaje"] for w in warn_sop]
        },
        "placed_items": []
    }

    base_h = float(config.base_height_in)
    for idx, item in enumerate(bin_obj.items):
        fw, fh, fd = [float(v) for v in item.get_dimension()]
        px, py, pz = [float(v) for v in item.position]
        pallet_data["placed_items"].append({
            "step_order": idx + 1,
            "sku": item.name.split('###')[0],
            "position": {"x": round(px, 1), "y": round(py + base_h, 1), "z": round(pz, 1)},
            "rendered_dimensions": {"width_in": round(fw, 1), "height_in": round(fh, 1), "length_in": round(fd, 1)}
        })
    return pallet_data