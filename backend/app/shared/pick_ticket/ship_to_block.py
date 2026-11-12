"""Bloque "SHIP TO:" leído por POSICIÓN en la página.

En el Pick Ticket, SOLD TO y SHIP TO van lado a lado: en el texto plano sus líneas salen
mezcladas ("1830 ROUTE 130 N. 570 EAST MILL STREET"). Por eso se usan las palabras con su
coordenada x (pdfplumber.extract_words) y se toma solo la columna del SHIP TO.
"""
from typing import Dict, List, Optional, Sequence

TOLERANCIA_LINEA = 2.0     # pt: palabras con 'top' a esta distancia son la misma línea
MARGEN_COLUMNA = 3.0       # pt: holgura a la izquierda del inicio de "SHIP TO:"
FIN_DE_BLOQUE = ("For STORE", "Dept", "Order No")


def _lineas(words: Sequence[Dict]) -> List[List[Dict]]:
    filas: List[List[Dict]] = []
    for w in sorted(words, key=lambda w: (round(w["top"]), w["x0"])):
        if filas and abs(filas[-1][0]["top"] - w["top"]) <= TOLERANCIA_LINEA:
            filas[-1].append(w)
        else:
            filas.append([w])
    return [sorted(f, key=lambda w: w["x0"]) for f in filas]


def ship_to_lines(words: Sequence[Dict]) -> Optional[List[str]]:
    """Líneas de la columna SHIP TO, incluida la cabecera ('SHIP TO: 512'). None si no existe."""
    filas = _lineas(words)
    inicio = x = None
    for n, fila in enumerate(filas):
        for a, b in zip(fila, fila[1:]):
            if a["text"] == "SHIP" and b["text"].startswith("TO"):
                inicio, x = n, a["x0"]
                break
        if inicio is not None:
            break
    if inicio is None:
        return None
    lineas: List[str] = []
    for fila in filas[inicio:]:
        if " ".join(w["text"] for w in fila).startswith(FIN_DE_BLOQUE):
            break
        texto = " ".join(w["text"] for w in fila if w["x0"] >= x - MARGEN_COLUMNA)
        if texto:
            lineas.append(texto)
    return lineas
