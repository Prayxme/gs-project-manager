"""
Flujo del Ingreso de Órdenes:
  1. analizar(): lee el PDF, consulta la hoja BONNIE e INBOUND y clasifica cada PikTik
     como NEW (nuevo), REGISTERED (ya registrado, sin cambios) o REVISION (cambió algo).
  2. aplicar(): escribe en la hoja solo lo que el usuario confirmó, volviendo a leer la hoja
     justo antes (para no duplicar si alguien la editó mientras tanto), y lo registra en PostgreSQL.
"""
import threading
from datetime import date, datetime, timezone
from typing import Dict, List, Optional

from sqlalchemy import Engine, insert, select

from app.modules.order_intake import rules
from app.modules.order_intake.models import SCHEMA, intake_log, metadata
from app.modules.order_intake.sheets_client import SheetsGateway
from app.modules.palletizer.services.pdf_service import extraer_datos_pick_ticket

_lock = threading.Lock()  # una escritura a la vez sobre la hoja


def _iso(v):
    return v.isoformat() if isinstance(v, (date, datetime)) else v


def _valores_json(valores: Dict) -> Dict:
    return {k: _iso(v) for k, v in valores.items()}


class IntakeLog:
    def __init__(self, engine: Engine, create_tables: bool = False):
        if engine.dialect.name == "sqlite":
            engine = engine.execution_options(schema_translate_map={SCHEMA: None})
        self.engine = engine
        if create_tables:
            metadata.create_all(engine)

    def registrar(self, filas: List[Dict]) -> None:
        if filas:
            with self.engine.begin() as c:
                c.execute(insert(intake_log), filas)

    def recientes(self, limit: int = 200) -> List[Dict]:
        q = select(intake_log).order_by(intake_log.c.ts.desc(), intake_log.c.id.desc()).limit(limit)
        with self.engine.connect() as c:
            out = []
            for r in c.execute(q):
                d = dict(r._mapping)
                ts = d["ts"]
                d["ts"] = (ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")
                out.append(d)
            return out


# ---------------------------------------------------------------------------
# Análisis
# ---------------------------------------------------------------------------
def _clasificar(orden: Dict, indice: Dict, inbound: Dict[str, bool], tiendas: set) -> Dict:
    valores = rules.valores_orden(orden)
    g, avisos = rules.recibido(orden["containers"], inbound)
    existente = indice.get(orden["piktik"])
    if existente is None:
        estado, fila, difs = "NEW", None, []
    else:
        fila, valores_hoja = existente
        difs = rules.comparar(orden, valores_hoja)
        estado = "REVISION" if difs else "REGISTERED"
    if tiendas and orden["store"] not in tiendas:
        avisos.append(f"La tienda {orden['store']} no está en la lista del menú STORE (hoja LIST).")
    return {
        **orden,
        "status": estado,
        "sheet_row": fila,
        "received": g,
        "diffs": difs,
        "warnings": avisos,
        "values": _valores_json({**valores, "G": g}),
    }


def analizar_pdf(contenido: bytes, gateway: SheetsGateway) -> Dict:
    parsed = extraer_datos_pick_ticket(contenido)
    ordenes = [rules.desde_pdf(o) for o in parsed["orders"]]
    return analizar_ordenes(ordenes, gateway, parsed.get("warnings", []))


def analizar_ordenes(ordenes: List[Dict], gateway: SheetsGateway, avisos_pdf: Optional[List[str]] = None) -> Dict:
    _, indice = gateway.leer_bonnie()
    inbound = rules.indice_inbound(gateway.leer_inbound())
    tiendas = gateway.leer_tiendas()
    resultado = [_clasificar(o, indice, inbound, tiendas) for o in ordenes]
    resumen = {e: sum(1 for r in resultado if r["status"] == e) for e in ("NEW", "REGISTERED", "REVISION")}
    return {"orders": resultado, "summary": resumen, "pdf_warnings": avisos_pdf or []}


def sugerencias(gateway: SheetsGateway) -> List[Dict]:
    _, indice = gateway.leer_bonnie()
    inbound = rules.indice_inbound(gateway.leer_inbound())
    filas = sorted(indice.values(), key=lambda t: t[0])
    return rules.sugerencias_received(filas, inbound)


# ---------------------------------------------------------------------------
# Escritura
# ---------------------------------------------------------------------------
def aplicar(ordenes: List[Dict], gateway: SheetsGateway, log: IntakeLog,
            source: str = "manual", source_ref: str = "") -> Dict:
    """ordenes: órdenes de ingreso confirmadas por el usuario (pueden venir corregidas).
    Escribe las nuevas y actualiza las revisiones; ignora las ya registradas sin cambios."""
    with _lock:
        ultima, indice = gateway.leer_bonnie()          # estado fresco de la hoja
        inbound = rules.indice_inbound(gateway.leer_inbound())
        ahora = datetime.now(timezone.utc).replace(microsecond=0)

        nuevas, revisiones, sin_cambios, registros = [], [], [], []
        vistos = set()
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

        filas_nuevas = gateway.agregar_filas(ultima, [v for _, v in nuevas])
        for (o, valores), n in zip(nuevas, filas_nuevas):
            registros.append(_registro(ahora, o, "NEW", n, source, source_ref, _valores_json(valores)))

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


def _registro(ts, o, accion, fila, source, ref, detalles) -> Dict:
    return {"ts": ts, "piktik": str(o["piktik"]), "po": o.get("po"), "store": o.get("store"), "action": accion,
            "sheet_row": fila, "source": source, "source_ref": ref, "details": detalles}
