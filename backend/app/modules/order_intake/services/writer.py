"""
Escritura: aplica en la hoja solo lo que el usuario confirmó, volviendo a leerla justo antes
(para no duplicar si alguien la editó mientras tanto), y lo registra en la bitácora.
"""
import threading
from typing import Dict, List

from app.modules.order_intake import rules
from app.modules.order_intake.repository import IntakeLog
from app.modules.order_intake.services.analysis import valores_json
from app.modules.order_intake.sheets_client import SheetsGateway
from app.shared.dates import utc_now

_lock = threading.Lock()  # una escritura a la vez sobre la hoja


def _registro(ts, o, accion, fila, source, ref, detalles) -> Dict:
    return {"ts": ts, "piktik": str(o["piktik"]), "po": o.get("po"), "store": o.get("store"), "action": accion,
            "sheet_row": fila, "source": source, "source_ref": ref, "details": detalles}


def _separar(ordenes: List[Dict], indice: Dict, inbound: Dict[str, bool]):
    """Reparte las órdenes (sin PikTiks repetidos) en nuevas, revisiones y sin cambios."""
    nuevas, revisiones, sin_cambios, vistos = [], [], [], set()
    for o in ordenes:
        pt = str(o["piktik"])
        if pt in vistos:
            continue
        vistos.add(pt)
        if pt not in indice:
            valores = rules.valores_orden(o)
            valores["G"] = rules.recibido(o["containers"], inbound)[0]
            nuevas.append((o, valores))
        else:
            fila, valores_hoja = indice[pt]
            difs = rules.comparar(o, valores_hoja)
            if difs:
                revisiones.append((o, fila, difs))
            else:
                sin_cambios.append(pt)
    return nuevas, revisiones, sin_cambios


def aplicar(ordenes: List[Dict], gateway: SheetsGateway, log: IntakeLog,
            source: str = "manual", source_ref: str = "") -> Dict:
    """ordenes: órdenes de ingreso confirmadas por el usuario (pueden venir corregidas).
    Escribe las nuevas y actualiza las revisiones; ignora las ya registradas sin cambios."""
    with _lock:
        ultima, indice = gateway.leer_bonnie()          # estado fresco de la hoja
        inbound = rules.indice_inbound(gateway.leer_inbound())
        ahora = utc_now()
        nuevas, revisiones, sin_cambios = _separar(ordenes, indice, inbound)
        registros = []

        filas_nuevas = gateway.agregar_filas(ultima, [v for _, v in nuevas])
        for (o, valores), n in zip(nuevas, filas_nuevas):
            registros.append(_registro(ahora, o, "NEW", n, source, source_ref, valores_json(valores)))

        for o, fila, difs in revisiones:
            nuevos = rules.valores_orden(o)
            gateway.actualizar_celdas(fila, {d["col"]: nuevos[d["col"]] for d in difs})
            registros.append(_registro(ahora, o, "REVISION", fila, source, source_ref, {"diffs": difs}))

        log.registrar(registros)
        return {
            "written": [{"piktik": str(o["piktik"]), "row": n} for (o, _), n in zip(nuevas, filas_nuevas)],
            "revised": [{"piktik": str(o["piktik"]), "row": f, "diffs": d} for o, f, d in revisiones],
            "unchanged": sin_cambios,
        }
