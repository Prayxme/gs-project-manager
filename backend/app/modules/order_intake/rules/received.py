"""
Recepción de contenedores (columna G "Received") según la hoja INBOUND (Incoming Containers).
Recibido = STATUS "Returned" y columnas P..X en YES, EXCLUYENDO T (decisión del usuario).
"""
from typing import Dict, Iterable, List, Sequence, Tuple

from app.shared.containers import find_containers
from app.shared.spreadsheet import cell, col_idx

INBOUND_COL_CONTAINER = "B"
INBOUND_COL_STATUS = "D"
INBOUND_CHECK_COLS = ["P", "Q", "R", "S", "U", "V", "W", "X"]  # sin T
STATUS_RECIBIDO = "returned"


def indice_inbound(filas: Iterable[Sequence]) -> Dict[str, bool]:
    """{contenedor: recibido?} a partir de las filas de INBOUND (sin encabezado)."""
    ib, ist = col_idx(INBOUND_COL_CONTAINER), col_idx(INBOUND_COL_STATUS)
    checks = [col_idx(c) for c in INBOUND_CHECK_COLS]
    out: Dict[str, bool] = {}
    for fila in filas:
        celda = lambda i: str(fila[i]).strip() if i < len(fila) and fila[i] is not None else ""
        ok = celda(ist).lower() == STATUS_RECIBIDO and all(celda(i).upper() == "YES" for i in checks)
        for c in find_containers(celda(ib)):
            out[c] = out.get(c, False) or ok
    return out


def recibido(conts: Sequence[str], inbound: Dict[str, bool]) -> Tuple[str, List[str]]:
    """('Yes'|'No', avisos). Yes solo si TODOS los contenedores están recibidos.
    Un contenedor ausente en INBOUND cuenta como no recibido."""
    if not conts:
        return "No", ["La orden no tiene contenedores."]
    faltan = [c for c in conts if c not in inbound]
    pendientes = [c for c in conts if c in inbound and not inbound[c]]
    avisos = []
    if faltan:
        avisos.append(f"No están en INBOUND: {', '.join(faltan)}")
    if pendientes:
        avisos.append(f"Aún no recibidos: {', '.join(pendientes)}")
    return ("Yes" if not faltan and not pendientes else "No"), avisos


def sugerencias_received(filas_hoja: Iterable[Tuple[int, Sequence]], inbound: Dict[str, bool]) -> List[Dict]:
    """Filas con G='No' cuyos contenedores ya están todos recibidos: se SUGIERE cambiarlas
    a 'Yes' manualmente (la app no lo hace sola)."""
    out = []
    for num_fila, fila in filas_hoja:
        g = str(cell(fila, "G", "")).strip()
        pt = cell(fila, "E")
        if g != "No" or not pt:
            continue
        conts = find_containers(cell(fila, "F", ""))
        if conts and recibido(conts, inbound)[0] == "Yes":
            out.append({"row": num_fila, "piktik": str(pt), "containers": conts})
    return out
