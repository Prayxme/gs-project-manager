"""Reglas de la bandeja de Gmail (funciones puras)."""
from datetime import date, datetime
from typing import Dict, Optional

PENDING = "PENDING"          # hay órdenes nuevas o con revisión por escribir
NO_CHANGES = "NO_CHANGES"    # todo el PDF ya está registrado tal cual
APPLIED = "APPLIED"          # se escribió desde la app
DISMISSED = "DISMISSED"      # el usuario lo descartó
ERROR = "ERROR"              # el PDF no se pudo leer

# Estados que se vuelven a comparar con la hoja en cada revisión (alguien pudo registrarlas a
# mano). NO_CHANGES no se repite: ya está todo en la hoja y la bandeja crece cada día.
REEVALUABLES = (PENDING, ERROR)


def consulta_gmail(remitente: str, asunto: str, desde: date) -> str:
    """Búsqueda de Gmail: correos del remitente con ese asunto y adjunto PDF, desde una fecha."""
    return f'from:{remitente} subject:"{asunto}" has:attachment filename:pdf after:{desde:%Y/%m/%d}'


def es_pdf_de_pick_tickets(nombre: str, prefijo: str) -> bool:
    """Solo el PDF de Pick Tickets; el 'wave report' que viene en el mismo correo se ignora."""
    n = (nombre or "").lower()
    return n.endswith(".pdf") and n.startswith(prefijo.lower())


def estado_por_resumen(resumen: Dict[str, int]) -> str:
    return PENDING if resumen.get("NEW", 0) + resumen.get("REVISION", 0) > 0 else NO_CHANGES


def nuevo_estado(actual: str, resumen: Optional[Dict[str, int]], error: Optional[str]) -> str:
    """Estado tras volver a comparar con la hoja. APPLIED y DISMISSED son decisiones del usuario
    y no cambian solas."""
    if actual not in REEVALUABLES:
        return actual
    if error:
        return ERROR
    return estado_por_resumen(resumen or {})


def fecha_busqueda(ultimo_recibido: Optional[datetime], hoy: date, dias_atras: int) -> date:
    """Desde cuándo buscar: el día del último correo guardado (Gmail filtra por día; los
    repetidos se descartan por id) o, la primera vez, `dias_atras` días."""
    if ultimo_recibido:
        return ultimo_recibido.date()
    return date.fromordinal(hoy.toordinal() - dias_atras)
