"""Plan de routing: PDFs leídos + portal -> POs conciliadas y estimadas -> RTS propuestos."""
from collections import defaultdict
from datetime import date
from typing import Callable, Dict, List, Optional

from app.modules.routing import rules
from app.modules.routing.services.purchase_orders import NO_ITEMS, armar_po
from app.shared.wiesner.portal import parse_table


def leer_portal(fetch_html: Callable[[], str]) -> Dict:
    """{'orders': {pick_ticket: fila} | None, 'error': str | None}. Nunca lanza."""
    try:
        return {"orders": {o["pick_ticket"]: o for o in parse_table(fetch_html())}, "error": None}
    except Exception as e:  # el portal caído no impide estimar; las POs quedan "sin verificar"
        return {"orders": None, "error": str(e) or e.__class__.__name__}


def _piktiks_por_po(pdfs: List[Dict], avisos: List[str]) -> Dict[str, List[Dict]]:
    """Agrupa los PikTiks de todos los PDFs por PO. Si un PikTik se repite, vale el último archivo."""
    por_pikitk: Dict[str, Dict] = {}
    for pdf in pdfs:
        avisos += [f"{pdf['filename']}: {w}" for w in pdf.get("warnings", [])]
        for o in pdf["orders"]:
            if o["piktik"] in por_pikitk:
                avisos.append(f"PikTik {o['piktik']} repetido; se usó el de {pdf['filename']}")
            por_pikitk[o["piktik"]] = o
    por_po: Dict[str, List[Dict]] = defaultdict(list)
    for o in por_pikitk.values():
        por_po[o["po"]].append(o)
    return por_po


def _rts(clave, pos: List[Dict], numero: int) -> Dict:
    codigo = pos[0]["customer_code"]
    rules.aplicar_peso_minimo(codigo, pos)
    limite = rules.limite_pallets(codigo)
    pallets = sum(p["pallets"] for p in pos)
    deadlines = [p["deadline"] for p in pos if p["deadline"]]
    dias = [p["days_left"] for p in pos if p["days_left"] is not None]
    return {
        "number": numero,
        "family": clave[0],
        "ship_to": pos[0]["ship_to"],
        "cancel_date": clave[2],
        "po_prefix": clave[3],
        "deadline": min(deadlines) if deadlines else "",
        "days_left": min(dias) if dias else None,
        "limit": limite,
        "over_limit": pallets > limite,
        "pallets": pallets,
        "units": sum(p["units"] or 0 for p in pos),
        "cartons": sum(p["cartons"] for p in pos),
        "weight": sum(p["weight"] for p in pos),
        "cft": sum(p["cft"] for p in pos),
        "verified": all(p["status"] == "OK" for p in pos),
        "pos": sorted(pos, key=lambda p: p["po"]),
    }


def construir_plan(pdfs: List[Dict], portal: Dict, hoy: date) -> Dict:
    avisos: List[str] = []
    ordenes = portal["orders"]
    pos = [armar_po(po, pks, ordenes, hoy) for po, pks in _piktiks_por_po(pdfs, avisos).items()]

    no_enrutables = rules.EXCLUIDOS + (NO_ITEMS,)
    grupos: Dict[tuple, List[Dict]] = defaultdict(list)
    for p in pos:
        if p["status"] not in no_enrutables:
            grupos[rules.clave_grupo(p)].append(p)

    bloques = []
    for clave, lista in grupos.items():
        limite = rules.limite_pallets(lista[0]["customer_code"])
        bloques += [(clave, b) for b in rules.repartir_en_rts(lista, limite)]
    # Primero lo que vence antes; dentro, por destino y cantidad de pallets.
    bloques.sort(key=lambda cb: (min((p["deadline"] or "9999") for p in cb[1]), cb[0][1], cb[0],
                                 -sum(p["pallets"] for p in cb[1])))
    rts = [_rts(clave, b, n) for n, (clave, b) in enumerate(bloques, start=1)]

    excluidas = sorted((p for p in pos if p["status"] in no_enrutables), key=lambda p: (p["status"], p["po"]))
    return {
        "today": hoy.isoformat(),
        "portal": {"ok": ordenes is not None, "error": portal["error"],
                   "orders": len(ordenes) if ordenes is not None else 0},
        "summary": {
            "pdfs": len(pdfs),
            "pos": len(pos),
            "routable": sum(len(r["pos"]) for r in rts),
            "excluded": len(excluidas),
            "rts": len(rts),
            "pallets": sum(r["pallets"] for r in rts),
        },
        "rts": rts,
        "excluded": excluidas,
        "warnings": avisos,
    }
