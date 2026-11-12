"""
Acceso a Google Sheets con la cuenta del usuario (los cambios figuran a su nombre).

Hoja BONNIE: solo se escriben las columnas A, B, C, D, E, F, G, H, I y V.
- Filas nuevas: justo después del último PikTik (columna E).
- Las filas vacías ya tienen el formato de la hoja; solo les faltan la casilla (A) y el
  menú Yes/No (G): se copian ESAS DOS validaciones desde la última fila con datos.
- Revisiones: se actualizan únicamente las celdas que cambiaron.
Hoja INBOUND: solo lectura.
"""
from datetime import date
from typing import Dict, List, Optional, Sequence, Tuple

from googleapiclient.discovery import build

from app.modules.order_intake import config
from app.shared.google import auth as google_auth
from app.shared.spreadsheet import col_idx

COLS_ESCRITURA = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "V"]


def _q(tab: str) -> str:
    return "'" + tab.replace("'", "''") + "'"


class SheetsGateway:
    def __init__(self, service=None):
        self._svc = service or build(
            "sheets", "v4", credentials=google_auth.credenciales(), cache_discovery=False
        ).spreadsheets()
        self._sheet_gid: Optional[int] = None

    # -- lectura -----------------------------------------------------------------
    def leer_bonnie(self) -> Tuple[int, Dict[str, Tuple[int, List]]]:
        """(última fila con PikTik, {piktik: (número de fila, valores A..V)})."""
        primera = config.PICKTICKET_FIRST_DATA_ROW
        r = self._svc.values().get(
            spreadsheetId=config.PICKTICKET_SHEET_ID,
            range=f"{_q(config.PICKTICKET_TAB)}!A{primera}:V",
            valueRenderOption="UNFORMATTED_VALUE",
            dateTimeRenderOption="SERIAL_NUMBER",
        ).execute()
        filas = r.get("values", [])
        indice: Dict[str, Tuple[int, List]] = {}
        ultima = primera - 1
        for i, fila in enumerate(filas):
            pt = fila[col_idx("E")] if len(fila) > col_idx("E") else ""
            if str(pt).strip():
                n = primera + i
                indice[str(int(pt)) if isinstance(pt, (int, float)) else str(pt).strip()] = (n, fila)
                ultima = n
        return ultima, indice

    def leer_inbound(self) -> List[List]:
        r = self._svc.values().get(
            spreadsheetId=config.CONTAINERS_SHEET_ID,
            range=f"{_q(config.CONTAINERS_TAB)}!A2:X",
        ).execute()
        return r.get("values", [])

    def leer_tiendas(self) -> set:
        """Valores permitidos del menú STORE (LIST!C2:C191)."""
        r = self._svc.values().get(spreadsheetId=config.PICKTICKET_SHEET_ID, range="'LIST'!C2:C").execute()
        return {str(v[0]).strip() for v in r.get("values", []) if v and str(v[0]).strip()}

    # -- escritura ------------------------------------------------------------------
    def _gid(self) -> int:
        if self._sheet_gid is None:
            meta = self._svc.get(spreadsheetId=config.PICKTICKET_SHEET_ID,
                                 fields="sheets.properties(sheetId,title)").execute()
            self._sheet_gid = next(s["properties"]["sheetId"] for s in meta["sheets"]
                                   if s["properties"]["title"] == config.PICKTICKET_TAB)
        return self._sheet_gid

    def agregar_filas(self, ultima_fila_datos: int, filas: Sequence[Dict[str, object]]) -> List[int]:
        """Escribe filas nuevas a partir de la fila siguiente a la última con datos.
        Devuelve los números de fila usados."""
        if not filas:
            return []
        inicio = ultima_fila_datos + 1
        fin = inicio + len(filas) - 1
        gid = self._gid()

        # 1) Casilla (A) y menú Yes/No (G): copiar SOLO la validación de la última fila con datos.
        def copiar_validacion(col: str) -> Dict:
            c = col_idx(col)
            return {"copyPaste": {
                "source": {"sheetId": gid, "startRowIndex": ultima_fila_datos - 1, "endRowIndex": ultima_fila_datos,
                           "startColumnIndex": c, "endColumnIndex": c + 1},
                "destination": {"sheetId": gid, "startRowIndex": inicio - 1, "endRowIndex": fin,
                                "startColumnIndex": c, "endColumnIndex": c + 1},
                "pasteType": "PASTE_DATA_VALIDATION",
            }}
        self._svc.batchUpdate(spreadsheetId=config.PICKTICKET_SHEET_ID,
                              body={"requests": [copiar_validacion("A"), copiar_validacion("G")]}).execute()

        # 2) Valores. USER_ENTERED para casilla, números y fechas; RAW para la PO (texto con ceros).
        tab = _q(config.PICKTICKET_TAB)
        user, raw = [], []
        for k, f in enumerate(filas):
            n = inicio + k
            user.append({"range": f"{tab}!A{n}:C{n}", "values": [["FALSE", f["B"], f["C"]]]})
            raw.append({"range": f"{tab}!D{n}", "values": [[f["D"]]]})
            user.append({"range": f"{tab}!E{n}:I{n}",
                         "values": [[f["E"], f["F"], f["G"], _fecha(f["H"]), _fecha(f["I"])]]})
            user.append({"range": f"{tab}!V{n}", "values": [[f["V"]]]})
        self._escribir(user, "USER_ENTERED")
        self._escribir(raw, "RAW")
        return list(range(inicio, fin + 1))

    def actualizar_celdas(self, fila: int, cambios: Dict[str, object]) -> None:
        """Revisión: solo las celdas indicadas (D, F, H, I, V)."""
        tab = _q(config.PICKTICKET_TAB)
        user, raw = [], []
        for col, valor in cambios.items():
            if col == "D":
                raw.append({"range": f"{tab}!D{fila}", "values": [[valor]]})
            else:
                v = _fecha(valor) if col in ("H", "I") else valor
                user.append({"range": f"{tab}!{col}{fila}", "values": [[v]]})
        self._escribir(user, "USER_ENTERED")
        self._escribir(raw, "RAW")

    def _escribir(self, data: List[Dict], modo: str) -> None:
        if data:
            self._svc.values().batchUpdate(
                spreadsheetId=config.PICKTICKET_SHEET_ID,
                body={"valueInputOption": modo, "data": data},
            ).execute()


def _fecha(valor) -> str:
    """Fecha ISO: Google Sheets la interpreta como fecha sin depender del idioma de la hoja."""
    return valor.isoformat() if isinstance(valor, date) else (valor or "")
