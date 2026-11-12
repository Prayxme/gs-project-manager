"""Importación del histórico ROUTING_COMPLETED (CSV exportado del Google Sheet)."""
import csv
import io
from datetime import date, datetime
from typing import Dict, List, Optional

from app.modules.open_orders.repository import OpenOrdersRepository
from app.shared.text import normalize_spaces

COLUMNAS_CSV = {
    "Date Removed": "date_removed", "Final Status": "final_status", "Reason": "reason",
    "Pick Ticket": "pick_ticket", "PO#": "po", "Customer": "cust", "Ship Date": "ship_date",
    "Cancel Date": "cancel_date", "Cfrm Number": "cfrm_number", "Appt Date": "appt_date", "Notes": "notes",
}


def _fecha_csv(valor: str) -> Optional[date]:
    try:
        return datetime.strptime(valor.strip(), "%m/%d/%Y").date()
    except ValueError:
        return None


def importar_completadas_csv(repo: OpenOrdersRepository, contenido: str) -> Dict:
    lector = csv.DictReader(io.StringIO(contenido.lstrip("﻿")))
    faltan = [c for c in COLUMNAS_CSV if c not in (lector.fieldnames or [])]
    if faltan:
        raise ValueError(f"El CSV no tiene las columnas esperadas: {', '.join(faltan)}")
    existentes = repo.closed_pick_tickets()
    filas: List[Dict] = []
    duplicadas = invalidas = 0
    for fila in lector:
        d = {dest: normalize_spaces(fila.get(orig, "")) for orig, dest in COLUMNAS_CSV.items()}
        fecha = _fecha_csv(d["date_removed"])
        if not d["pick_ticket"] or not fecha or not d["final_status"]:
            invalidas += 1
            continue
        if d["pick_ticket"] in existentes:
            duplicadas += 1
            continue
        existentes.add(d["pick_ticket"])
        filas.append({**d, "date_removed": fecha, "removed_at": None, "source": "import"})
    repo.insert_closed(filas)
    return {"inserted": len(filas), "duplicates": duplicadas, "invalid": invalidas}
