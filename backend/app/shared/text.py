"""Utilidades de texto comunes."""
import re


def normalize_spaces(valor) -> str:
    """Quita NBSP/tabs y espacios repetidos: 'Load ID\\t10624682' -> 'Load ID 10624682'."""
    return re.sub(r"\s+", " ", str(valor or "").replace(" ", " ")).strip()


def to_int(valor):
    """'1,086' / 147 / '147.0' -> int; inválido -> None."""
    try:
        return int(float(str(valor).replace(",", "").strip()))
    except (TypeError, ValueError):
        return None
