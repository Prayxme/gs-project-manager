"""
Análisis (solo lectura): lee el PDF, consulta las hojas BONNIE e INBOUND y clasifica cada PikTik
como NEW (nuevo), REGISTERED (ya registrado, sin cambios) o REVISION (cambió algo).
"""
from typing import Dict, List, Optional

from app.modules.order_intake import rules
from app.modules.order_intake.sheets_client import SheetsGateway
from app.shared.dates import to_json
from app.shared.pick_ticket import extraer_datos_pick_ticket

ESTADOS = ("NEW", "REGISTERED", "REVISION")


def valores_json(valores: Dict) -> Dict:
    """Valores de columnas con fechas en ISO (para responder JSON o guardar en la bitácora)."""
    return {k: to_json(v) for k, v in valores.items()}


def _clasificar(orden: Dict, indice: Dict, inbound: Dict[str, bool], tiendas: set) -> Dict:
    valores = rules.valores_orden(orden)
    g, avisos = rules.recibido(orden["containers"], inbound)
    existente = indice.get(orden["piktik"])
    if existente is None:
        estado, fila, difs = "NEW", None, []
    else:
        fila, valores_hoja = existente
        difs = rules.comparar(orden, valores_hoja)
        estado = "REVISION" if difs else "REGISTERED"
    if tiendas and orden["store"] not in tiendas:
        avisos.append(f"La tienda {orden['store']} no está en la lista del menú STORE (hoja LIST).")
    return {
        **orden,
        "status": estado,
        "sheet_row": fila,
        "received": g,
        "diffs": difs,
        "warnings": avisos,
        "values": valores_json({**valores, "G": g}),
    }


def analizar_pdf(contenido: bytes, gateway: SheetsGateway) -> Dict:
    parsed = extraer_datos_pick_ticket(contenido)
    ordenes = [rules.desde_pdf(o) for o in parsed["orders"]]
    return analizar_ordenes(ordenes, gateway, parsed.get("warnings", []))


def analizar_ordenes(ordenes: List[Dict], gateway: SheetsGateway, avisos_pdf: Optional[List[str]] = None) -> Dict:
    _, indice = gateway.leer_bonnie()
    inbound = rules.indice_inbound(gateway.leer_inbound())
    tiendas = gateway.leer_tiendas()
    resultado = [_clasificar(o, indice, inbound, tiendas) for o in ordenes]
    resumen = {e: sum(1 for r in resultado if r["status"] == e) for e in ESTADOS}
    return {"orders": resultado, "summary": resumen, "pdf_warnings": avisos_pdf or []}


def sugerencias(gateway: SheetsGateway) -> List[Dict]:
    """Filas con Received='No' cuyos contenedores ya llegaron (solo se sugieren)."""
    _, indice = gateway.leer_bonnie()
    inbound = rules.indice_inbound(gateway.leer_inbound())
    filas = sorted(indice.values(), key=lambda t: t[0])
    return rules.sugerencias_received(filas, inbound)
