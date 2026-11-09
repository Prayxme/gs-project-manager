from decimal import Decimal
from typing import List, Tuple, Dict, Any
from app.core.config import (
    TOLERANCIA_ALTURA_SOPORTE,
    UMBRAL_MINIMO_SOPORTE,
    TOLERANCIA_DESBALANCE_COG,
)

def aplicar_gravedad(b_items: list, max_h_util: float = 79.5) -> list:
    """
    Aplica gravedad física estable. 
    Una caja solo se detiene en un nivel si al menos el 65% de su área base 
    está efectivamente apoyada sobre cajas inferiores sólidas o sobre el piso.
    """
    b_items.sort(key=lambda item: float(item.position[1]))
    items_validos = []
    
    for i in range(len(b_items)):
        caja = b_items[i]
        pos_x = float(caja.position[0])
        pos_z = float(caja.position[2])
        w, h, d = [float(val) for val in caja.get_dimension()]
        area_base = w * d
        
        # Recolectar todos los techos posibles debajo de la caja
        alturas_potenciales = {0.0}  # El suelo siempre es una opción
        for otra in items_validos:
            alturas_potenciales.add(float(otra.position[1]) + float(otra.get_dimension()[1]))
            
        # Probar desde el techo más alto hacia abajo hasta encontrar un soporte real
        alturas_ordenadas = sorted(list(alturas_potenciales), reverse=True)
        altura_final = 0.0
        
        for y_candidato in alturas_ordenadas:
            if y_candidato == 0.0:
                altura_final = 0.0
                break
                
            # Calcular cuánta área de soporte real tiene a este nivel
            area_soporte = 0.0
            for otra in items_validos:
                y_otra_techo = float(otra.position[1]) + float(otra.get_dimension()[1])
                # Si la caja de abajo coincide con este nivel de apoyo
                if abs(y_otra_techo - y_candidato) < 0.1:
                    ox = float(otra.position[0])
                    oz = float(otra.position[2])
                    ow, _, od = [float(val) for val in otra.get_dimension()]
                    
                    ix_izq = max(pos_x, ox)
                    ix_der = min(pos_x + w, ox + ow)
                    iz_front = max(pos_z, oz)
                    iz_tras = min(pos_z + d, oz + od)
                    
                    if ix_der > ix_izq and iz_tras > iz_front:
                        area_soporte += (ix_der - ix_izq) * (iz_tras - iz_front)
            
            # Solo si tiene al menos el 65% de apoyo se queda en este nivel
            if (area_soporte / area_base) >= 0.65:
                altura_final = y_candidato
                break
        
        # Validar que no sobrepase el límite máximo de altura
        if altura_final + h <= max_h_util + 0.5:
            caja.position[1] = Decimal(str(round(altura_final, 2)))
            items_validos.append(caja)

    b_items.clear()
    b_items.extend(items_validos)
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

    cog_x = sum_x / total_w
    cog_z = sum_z / total_w
    ideal_x, ideal_z = pallet_w / 2.0, pallet_l / 2.0
    warnings = []
    status = "ESTABLE"

    if abs(cog_x - ideal_x) > (pallet_w * TOLERANCIA_DESBALANCE_COG):
        status = "INESTABLE"
        warnings.append(f"Desbalance lateral (CoG X: {cog_x:.1f} in).")
    if abs(cog_z - ideal_z) > (pallet_l * TOLERANCIA_DESBALANCE_COG):
        status = "INESTABLE"
        warnings.append(f"Desbalance frontal (CoG Z: {cog_z:.1f} in).")

    return {"x": round(cog_x, 2), "z": round(cog_z, 2)}, status, warnings

def construir_pallet_dict(bin_obj, config, pallet_id_str: str) -> Dict[str, Any]:
    cog, status_eq, warn_eq = analizar_equilibrio(bin_obj.items, config.width_in, config.length_in)
    warn_sop = analizar_soporte(bin_obj.items)
    alertas = warn_eq + [w["mensaje"] for w in warn_sop]

    pallet_data = {
        "pallet_id": pallet_id_str,
        "metrics": {
            "total_weight_lbs": round(sum(float(item.weight) for item in bin_obj.items), 2),
            "boxes_count": len(bin_obj.items),
            "balance_status": status_eq,
            "center_of_gravity": cog,
            "voladizos_peligrosos": len(warn_sop),
            "alertas": alertas
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
            "position": {"x": px, "y": round(py + base_h, 3), "z": pz},
            "rendered_dimensions": {"width_in": fw, "height_in": fh, "length_in": fd}
        })
    return pallet_data