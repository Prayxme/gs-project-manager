import copy
from typing import Dict, Any, List
from py3dbp import Bin, Item, Packer
from decimal import Decimal
from app.models.schemas import PackingRequest
from app.services.physics_engine import aplicar_gravedad, construir_pallet_dict

def optimizar_orden_pallets(request: PackingRequest) -> Dict[str, Any]:
    config = request.pallet_config
    net_height = float(config.max_total_height_in - config.base_height_in)
    response_pallets: List[Dict[str, Any]] = []
    pool_mixto: List[Dict[str, Any]] = []
    
    pallets_homogeneos = [] # Almacenará objetos intermedios para hacerles "Topping Off"
    
    # =========================================================================
    # FASE 1: CREAR PLANTILLAS HOMOGÉNEAS (Sin sellar)
    # =========================================================================
    for item in request.items:
        vol_caja = item.dimensions.length_in * item.dimensions.width_in * item.dimensions.height_in
        vol_util = config.width_in * config.length_in * net_height
        max_teorico = max(1, int(vol_util / vol_caja) + 6)
        candidatos = min(item.quantity, max_teorico)

        test_packer = Packer()
        test_packer.add_bin(Bin('TEST', config.width_in, net_height, config.length_in, config.max_weight_lbs))
        for idx in range(candidatos):
            test_packer.add_item(Item(
                f"{item.sku}###{idx}",
                item.dimensions.width_in,
                item.dimensions.height_in,
                item.dimensions.length_in,
                item.weight_lbs
            ))
        test_packer.pack()

        test_bin = test_packer.bins[0]
        aplicar_gravedad(test_bin.items, max_h_util=net_height)
        capacidad_pallet = len(test_bin.items)

        if capacidad_pallet > 0 and item.quantity >= capacidad_pallet:
            pallets_completos = item.quantity // capacidad_pallet
            remanente = item.quantity % capacidad_pallet
            
            # Guardar las plantillas en lugar de convertirlas a JSON de inmediato
            for _ in range(pallets_completos):
                pallets_homogeneos.append({
                    "items": copy.deepcopy(test_bin.items),
                })

            # El sobrante va al pool mixto
            for rem_idx in range(remanente):
                pool_mixto.append({
                    "sku": item.sku, "w": item.dimensions.width_in, "h": item.dimensions.height_in,
                    "d": item.dimensions.length_in, "weight": item.weight_lbs, "name": f"{item.sku}###REM_{rem_idx}"
                })
        else:
            for rem_idx in range(item.quantity):
                pool_mixto.append({
                    "sku": item.sku, "w": item.dimensions.width_in, "h": item.dimensions.height_in,
                    "d": item.dimensions.length_in, "weight": item.weight_lbs, "name": f"{item.sku}###REM_{rem_idx}"
                })

    # =========================================================================
    # FASE 2: TOP-OFF (Relleno) Y EMPAQUE MIXTO
    # =========================================================================
    mixed_packer = Packer()
    
    # 2.A: Habilitar el espacio sobrante de los pallets homogéneos como "Bins Virtuales"
    for p_idx, pallet in enumerate(pallets_homogeneos):
        highest_y = max((float(i.position[1]) + float(i.get_dimension()[1]) for i in pallet["items"]), default=0.0)
        peso_usado = sum(float(i.weight) for i in pallet["items"])
        
        espacio_y = net_height - highest_y
        peso_libre = float(config.max_weight_lbs) - peso_usado
        
        # Si sobra más de 4 pulgadas de alto y tolera más de 10 lbs, habilitar relleno
        if espacio_y >= 4.0 and peso_libre >= 10.0:
            mixed_packer.add_bin(Bin(f'TOPOFF-{p_idx}', config.width_in, espacio_y, config.length_in, peso_libre))

    # 2.B: Agregar Bins Mixtos vacíos tradicionales para las cajas que no quepan en los rellenos
    vol_cajas_mixtas = sum(c["w"] * c["h"] * c["d"] for c in pool_mixto) if pool_mixto else 0
    vol_pallet = config.width_in * config.length_in * net_height
    bins_necesarios = max(5, int((vol_cajas_mixtas / (vol_pallet * 0.65))) + 2) if pool_mixto else 0
    
    for i in range(bins_necesarios):
        mixed_packer.add_bin(Bin(f'MIXED-{i}', config.width_in, net_height, config.length_in, config.max_weight_lbs))
        
    # 2.C: Empacar todo el pool mixto ordenado por peso (los pesados primero)
    if pool_mixto:
        pool_mixto.sort(key=lambda x: x["weight"], reverse=True)
        for c in pool_mixto:
            mixed_packer.add_item(Item(c["name"], c["w"], c["h"], c["d"], c["weight"]))
        mixed_packer.pack()

    # =========================================================================
    # FASE 3: CONSOLIDACIÓN Y APLICACIÓN DE GRAVEDAD
    # =========================================================================
    pallet_counter = 1
    
    # 3.A Procesar resultados de los Bins Virtuales (Cajas de Relleno)
    for mb in mixed_packer.bins:
        if not mb.items:
            continue
            
        if mb.name.startswith('TOPOFF-'):
            p_idx = int(mb.name.split('-')[-1])
            original_pallet = pallets_homogeneos[p_idx]
            highest_y = max((float(i.position[1]) + float(i.get_dimension()[1]) for i in original_pallet["items"]), default=0.0)
            
            # Desplazar las cajas de relleno hacia arriba y unirlas al pallet original
            for item in mb.items:
                item.position[1] = Decimal(str(float(item.position[1]) + highest_y))
            
            original_pallet["items"].extend(mb.items)

    # 3.B Transformar Pallets Homogéneos (ahora rellenados) a Diccionarios Finales
    for pallet in pallets_homogeneos:
        # Re-aplicar gravedad para asentar perfectamente las cajas mixtas sobre las homogéneas
        aplicar_gravedad(pallet["items"], max_h_util=net_height)
        
        dummy_bin = Bin('DUMMY', config.width_in, net_height, config.length_in, config.max_weight_lbs)
        dummy_bin.items = pallet["items"]
        
        p_dict = construir_pallet_dict(dummy_bin, config, f"PALLET-{pallet_counter}")
        response_pallets.append(p_dict)
        pallet_counter += 1

    # 3.C Procesar los Bins Mixtos estándar
    for mb in mixed_packer.bins:
        if mb.name.startswith('MIXED-') and mb.items:
            aplicar_gravedad(mb.items, max_h_util=net_height)
            if mb.items:
                p_dict = construir_pallet_dict(mb, config, f"PALLET-{pallet_counter}")
                response_pallets.append(p_dict)
                pallet_counter += 1

    return {
        "order_id": request.order_id,
        "pallets": response_pallets,
        "unplaced_boxes": 0
    }