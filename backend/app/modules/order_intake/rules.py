"""
Reglas del módulo Ingreso de Órdenes (PDF Pick Ticket -> hoja BONNIE).

Funciones puras: no tocan Google ni la base de datos, para poder probarlas.

Columnas de la hoja BONNIE que escribe la app (las demás NUNCA se tocan):
  A ##          casilla sin marcar (FALSE) en filas nuevas
  B COMPANY     empresa del encabezado del PDF (WIESNER, FASHION OPTION, ...)
  C STORE       Cust No (MARS125)
  D PO #        texto, conserva ceros a la izquierda
  E PICK TICKET número
  F Container   contenedores separados por espacio
  G Received    Yes / No según la hoja INBOUND (solo al crear la fila)
  H STAR DATE   Ship Date
  I CANCEL DATE Cancel Date
  V QTY CTNS    total de cartones
"""
import re
from datetime import date, datetime
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

RE_CONTAINER = re.compile(r"[A-Z]{4}\d{7}")

# INBOUND: B = contenedor, D = STATUS, P..X = verificaciones (T se excluye por decisión del usuario).
INBOUND_COL_CONTAINER = "B"
INBOUND_COL_STATUS = "D"
INBOUND_CHECK_COLS = ["P", "Q", "R", "S", "U", "V", "W", "X"]  # sin T
STATUS_RECIBIDO = "returned"

# Campos que cuentan como "revisión" de un PikTik ya registrado.
CAMPOS_REVISION = {
    "D": "PO #",
    "F": "Container",
    "H": "STAR DATE (Ship)",
    "I": "CANCEL DATE",
    "V": "QTY CTNS",
}

_SUFIJOS_EMPRESA = {"INC", "LLC", "CO", "CORP", "LTD", "PRODUCTS", "SOCKS"}


def col_idx(letra: str) -> int:
    """'A' -> 0, 'V' -> 21, 'AB' -> 27."""
    n = 0
    for ch in letra.upper():
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def empresa(nombre_pdf: str) -> str:
    """'Wiesner Products, Inc.' -> 'WIESNER'; 'Soled Out Socks.' -> 'SOLED OUT'."""
    palabras = re.sub(r"[^A-Za-z0-9& ]+", " ", nombre_pdf or "").upper().split()
    while palabras and palabras[-1] in _SUFIJOS_EMPRESA:
        palabras.pop()
    return " ".join(palabras)


def contenedores(texto) -> List[str]:
    """Códigos de contenedor en un texto ('FFAU2892254 (LTL)' -> ['FFAU2892254'])."""
    return list(dict.fromkeys(RE_CONTAINER.findall(str(texto or "").upper())))


def parse_fecha(valor) -> Optional[date]:
    """Acepta date/datetime, 'MM/DD/YYYY', 'MM/DD/YY', 'YYYY-MM-DD' o número de serie de Sheets."""
    if valor is None or valor == "":
        return None
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    if isinstance(valor, (int, float)):  # serie de Google Sheets (días desde 1899-12-30)
        return date.fromordinal(date(1899, 12, 30).toordinal() + int(valor))
    s = str(valor).strip()
    for fmt in ("%m/%d/%Y", "%m/%d/%y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def _int(valor) -> Optional[int]:
    try:
        return int(float(str(valor).replace(",", "").strip()))
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Recepción de contenedores (columna G)
# ---------------------------------------------------------------------------
def indice_inbound(filas: Iterable[Sequence]) -> Dict[str, bool]:
    """{contenedor: recibido?} a partir de las filas de INBOUND (sin encabezado).
    Recibido = STATUS 'Returned' y P..X (sin T) todas en YES."""
    ib, ist = col_idx(INBOUND_COL_CONTAINER), col_idx(INBOUND_COL_STATUS)
    checks = [col_idx(c) for c in INBOUND_CHECK_COLS]
    out: Dict[str, bool] = {}
    for fila in filas:
        celda = lambda i: str(fila[i]).strip() if i < len(fila) and fila[i] is not None else ""
        ok = celda(ist).lower() == STATUS_RECIBIDO and all(celda(i).upper() == "YES" for i in checks)
        for c in contenedores(celda(ib)):
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


# ---------------------------------------------------------------------------
# Fila nueva y revisión
# ---------------------------------------------------------------------------
def desde_pdf(orden: Dict) -> Dict:
    """Orden del lector de PDF -> orden de ingreso (lo que el usuario revisa y puede corregir)."""
    return {
        "piktik": str(orden["piktik"]),
        "company": empresa(orden.get("company", "")),
        "store": orden.get("cust_no", ""),
        "po": orden.get("po", ""),
        "containers": list(orden.get("containers", [])),
        "ship_date": orden.get("ship_date", ""),
        "cancel_date": orden.get("cancel_date", ""),
        "ctns": sum(int(it.get("qty", 0)) for it in orden.get("items", [])),
    }


def valores_orden(orden: Dict) -> Dict[str, object]:
    """Valores de las columnas de datos (sin A ni G). Acepta una orden de ingreso o una del PDF."""
    o = orden if "store" in orden else desde_pdf(orden)
    return {
        "B": o["company"],
        "C": o["store"],
        "D": str(o["po"]).strip(),
        "E": int(o["piktik"]),
        "F": " ".join(contenedores(" ".join(o["containers"]))),
        "H": parse_fecha(o["ship_date"]),
        "I": parse_fecha(o["cancel_date"]),
        "V": int(o["ctns"]),
    }


def comparar(orden: Dict, fila_hoja: Sequence) -> List[Dict]:
    """Diferencias en los campos de revisión entre el PDF y la fila ya registrada."""
    nuevo = valores_orden(orden)
    celda = lambda letra: fila_hoja[col_idx(letra)] if col_idx(letra) < len(fila_hoja) else None
    difs = []
    for letra, nombre in CAMPOS_REVISION.items():
        antes, ahora = celda(letra), nuevo[letra]
        if letra == "F":
            igual = set(contenedores(antes)) == set(contenedores(ahora))
        elif letra in ("H", "I"):
            igual = parse_fecha(antes) == ahora
        elif letra == "V":
            igual = _int(antes) == ahora
        else:
            igual = str(antes or "").strip() == str(ahora or "").strip()
        if not igual:
            difs.append({"col": letra, "campo": nombre, "antes": _texto(antes, letra), "ahora": _texto(ahora, letra)})
    return difs


def _texto(valor, letra: str) -> str:
    if letra in ("H", "I"):
        f = parse_fecha(valor)
        return f.strftime("%m/%d/%Y") if f else str(valor or "")
    return "" if valor is None else str(valor)


def sugerencias_received(filas_hoja: Iterable[Tuple[int, Sequence]], inbound: Dict[str, bool]) -> List[Dict]:
    """Filas con G='No' cuyos contenedores ya están todos recibidos: se SUGIERE cambiarlas
    a 'Yes' manualmente (la app no lo hace sola)."""
    out = []
    for num_fila, fila in filas_hoja:
        g = str(fila[col_idx("G")] if len(fila) > col_idx("G") else "").strip()
        pt = fila[col_idx("E")] if len(fila) > col_idx("E") else None
        if g != "No" or not pt:
            continue
        conts = contenedores(fila[col_idx("F")] if len(fila) > col_idx("F") else "")
        if conts and recibido(conts, inbound)[0] == "Yes":
            out.append({"row": num_fila, "piktik": str(pt), "containers": conts})
    return out
