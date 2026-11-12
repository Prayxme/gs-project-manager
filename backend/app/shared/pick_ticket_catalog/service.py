"""Lectura de un PDF de Pick Tickets hacia el catálogo."""
import re
from datetime import datetime
from typing import Dict, Optional
from zoneinfo import ZoneInfo

from app.shared.pick_ticket import extraer_datos_pick_ticket
from app.shared.pick_ticket_catalog.repository import PickTicketCatalog

# "oe_piktik_00WPI_PM_BURL120-20261112-103329am-927419.pdf": fecha y hora en que Wiesner (Nueva York)
# generó el PDF.
RE_FECHA_ARCHIVO = re.compile(r"-(\d{8})-(\d{6})(am|pm)-", re.IGNORECASE)
ZONA_WIESNER = ZoneInfo("America/New_York")


def fecha_del_archivo(filename: str) -> Optional[datetime]:
    """Momento de generación del PDF según su nombre (para saber cuál es más reciente al subirlo
    a mano); None si el nombre no trae la fecha."""
    m = RE_FECHA_ARCHIVO.search(filename or "")
    if not m:
        return None
    try:
        return datetime.strptime(f"{m.group(1)} {m.group(2)}{m.group(3).upper()}", "%Y%m%d %I%M%S%p").replace(
            tzinfo=ZONA_WIESNER)
    except ValueError:
        return None


def registrar_pdf(catalogo: PickTicketCatalog, content: bytes, filename: str, received_at: datetime,
                  source: str, leido: Optional[Dict] = None) -> int:
    """Lee el PDF (o usa `leido`, si ya se leyó) y guarda sus PikTiks. Nunca lanza por un PDF
    ilegible: lo deja anotado con su error para no reintentarlo en cada revisión."""
    try:
        datos = leido if leido is not None else extraer_datos_pick_ticket(content)
    except Exception as e:
        return catalogo.guardar(filename, received_at, source, [], error=str(e) or type(e).__name__)
    return catalogo.guardar(filename, received_at, source, datos["orders"])
