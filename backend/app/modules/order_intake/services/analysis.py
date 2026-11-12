"""
Análisis (solo lectura): lee el PDF, consulta las hojas BONNIE e INBOUND y clasifica cada PikTik
como NEW (nuevo), REGISTERED (ya registrado, sin cambios) o REVISION (cambió algo).
"""
from dataclasses import dataclass
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


@dataclass(frozen=True)
class ContextoHoja:
    """Lo que se lee de Google una sola vez para clasificar muchas órdenes."""
    indice: Dict
    inbound: Dict[str, bool]
    tiendas: set


def leer_contexto(gateway: SheetsGateway) -> ContextoHoja:
    _, indice = gateway.leer_bonnie()
    return ContextoHoja(indice, rules.indice_inbound(gateway.leer_inbound()), gateway.leer_tiendas())


def clasificar_ordenes(ordenes: List[Dict], ctx: ContextoHoja, avisos_pdf: Optional[List[str]] = None) -> Dict:
    resultado = [_clasificar(o, ctx.indice, ctx.inbound, ctx.tiendas) for o in ordenes]
    resumen = {e: sum(1 for r in resultado if r["status"] == e) for e in ESTADOS}
    return {"orders": resultado, "summary": resumen, "pdf_warnings": avisos_pdf or []}


def clasificar_pdf(contenido: bytes, ctx: ContextoHoja) -> Dict:
    parsed = extraer_datos_pick_ticket(contenido)
    ordenes = [rules.desde_pdf(o) for o in parsed["orders"]]
    return clasificar_ordenes(ordenes, ctx, parsed.get("warnings", []))


def analizar_pdf(contenido: bytes, gateway: SheetsGateway) -> Dict:
    return clasificar_pdf(contenido, leer_contexto(gateway))


def analizar_ordenes(ordenes: List[Dict], gateway: SheetsGateway, avisos_pdf: Optional[List[str]] = None) -> Dict:
    return clasificar_ordenes(ordenes, leer_contexto(gateway), avisos_pdf)


def sugerencias(gateway: SheetsGateway) -> List[Dict]:
    """Filas con Received='No' cuyos contenedores ya llegaron (solo se sugieren)."""
    _, indice = gateway.leer_bonnie()
    inbound = rules.indice_inbound(gateway.leer_inbound())
    filas = sorted(indice.values(), key=lambda t: t[0])
    return rules.sugerencias_received(filas, inbound)
