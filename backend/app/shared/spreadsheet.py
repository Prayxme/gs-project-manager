"""Utilidades para hojas de cálculo (Google Sheets / Excel)."""
from typing import Sequence


def col_idx(letra: str) -> int:
    """Letra de columna -> índice base 0: 'A' -> 0, 'V' -> 21, 'AB' -> 27."""
    n = 0
    for ch in letra.upper():
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def cell(fila: Sequence, letra: str, default=None):
    """Valor de una fila por letra de columna (las filas de la API pueden venir recortadas)."""
    i = col_idx(letra)
    return fila[i] if i < len(fila) else default
