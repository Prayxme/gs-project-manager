"""Fechas y horas comunes a todos los módulos."""
import re
from datetime import date, datetime, timezone
from typing import Optional
from zoneinfo import ZoneInfo

ISO_UTC = "%Y-%m-%dT%H:%M:%SZ"
DEFAULT_TIMEZONE = "America/Los_Angeles"

_RE_MDY = re.compile(r"^\s*(\d{1,2})/(\d{1,2})/(\d{2}|\d{4})\s*$")
_SHEETS_EPOCH = date(1899, 12, 30)


def parse_date(valor) -> Optional[date]:
    """Convierte a fecha de calendario: date/datetime, 'MM/DD/YY', 'MM/DD/YYYY',
    'YYYY-MM-DD' o número de serie de Google Sheets. Vacío o '00/00/00' -> None."""
    if valor is None or valor == "":
        return None
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    if isinstance(valor, (int, float)):
        return date.fromordinal(_SHEETS_EPOCH.toordinal() + int(valor))
    texto = str(valor).strip()
    m = _RE_MDY.match(texto)
    if m:
        mes, dia, anio = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if anio < 100:
            anio += 2000
        try:
            return date(anio, mes, dia)
        except ValueError:
            return None
    try:
        return date.fromisoformat(texto)
    except ValueError:
        return None


def utc_now() -> datetime:
    """Ahora en UTC, sin microsegundos."""
    return datetime.now(timezone.utc).replace(microsecond=0)


def as_utc(dt: Optional[datetime]) -> Optional[datetime]:
    """Normaliza a UTC con zona (SQLite devuelve fechas sin zona en las pruebas)."""
    if dt is None:
        return None
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)


def to_iso_utc(dt: Optional[datetime]) -> Optional[str]:
    """datetime -> '2026-11-12T07:20:29Z'."""
    return as_utc(dt).strftime(ISO_UTC) if dt else None


def safe_zone(nombre: Optional[str]) -> ZoneInfo:
    """Zona horaria por nombre IANA; si no es válida, la de California."""
    try:
        return ZoneInfo(nombre or DEFAULT_TIMEZONE)
    except Exception:
        return ZoneInfo(DEFAULT_TIMEZONE)


def local_date(iso_utc: Optional[str], tz: ZoneInfo) -> Optional[date]:
    """Fecha local de un instante guardado como texto ISO UTC."""
    if not iso_utc:
        return None
    return datetime.strptime(iso_utc, ISO_UTC).replace(tzinfo=timezone.utc).astimezone(tz).date()


def to_json(valor):
    """Fechas a texto (ISO) para respuestas JSON; el resto sin cambios."""
    if isinstance(valor, datetime):
        return to_iso_utc(valor)
    if isinstance(valor, date):
        return valor.isoformat()
    return valor
