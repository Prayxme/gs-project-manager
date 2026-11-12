"""Revisión de un PikTik ya registrado: solo cuentan PO, contenedores, fechas y cartones."""
from typing import Dict, List, Sequence

from app.modules.order_intake.rules.columns import valores_orden
from app.shared.containers import find_containers
from app.shared.dates import parse_date
from app.shared.spreadsheet import cell
from app.shared.text import to_int

CAMPOS_REVISION = {
    "D": "PO #",
    "F": "Container",
    "H": "STAR DATE (Ship)",
    "I": "CANCEL DATE",
    "V": "QTY CTNS",
}


def _iguales(letra: str, antes, ahora) -> bool:
    if letra == "F":
        nuevos = set(find_containers(ahora))
        # Si el PDF no muestra contenedores (p. ej. no se pudieron leer sus líneas) no es un cambio:
        # nunca se borra de la hoja un dato que el PDF simplemente no trae.
        return not nuevos or set(find_containers(antes)) == nuevos
    if letra in ("H", "I"):
        return parse_date(antes) == ahora
    if letra == "V":
        return to_int(antes) == ahora
    return str(antes or "").strip() == str(ahora or "").strip()


def _texto(valor, letra: str) -> str:
    if letra in ("H", "I"):
        f = parse_date(valor)
        return f.strftime("%m/%d/%Y") if f else str(valor or "")
    return "" if valor is None else str(valor)


def comparar(orden: Dict, fila_hoja: Sequence) -> List[Dict]:
    """Diferencias en los campos de revisión entre el PDF y la fila ya registrada."""
    nuevo = valores_orden(orden)
    difs = []
    for letra, nombre in CAMPOS_REVISION.items():
        antes, ahora = cell(fila_hoja, letra), nuevo[letra]
        if not _iguales(letra, antes, ahora):
            difs.append({"col": letra, "campo": nombre, "antes": _texto(antes, letra), "ahora": _texto(ahora, letra)})
    return difs
