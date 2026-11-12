"""Vistas del monitor: órdenes evaluadas para 'hoy' e indicadores."""
from datetime import date, datetime, time, timedelta, timezone
from typing import Dict, List, Optional

from app.modules.open_orders import config, rules
from app.modules.open_orders.repository import OpenOrdersRepository
from app.shared.dates import local_date, safe_zone


def listar(repo: OpenOrdersRepository, today: date) -> List[Dict]:
    return rules.ordenar([rules.evaluar(o, today) for o in repo.load_orders().values()])


def auto_refresh_activo(repo: OpenOrdersRepository) -> bool:
    return repo.get_setting("auto_refresh", "0") == "1"


def _conteo_por_estado(ordenes: List[Dict]) -> Dict[str, int]:
    conteo = {s: 0 for s in rules.STATUS_ORDER}
    for o in ordenes:
        if o["status"] in conteo:
            conteo[o["status"]] += 1
    return conteo


def _completadas_hoy(repo: OpenOrdersRepository, today: date, tz) -> int:
    total = 0
    for c in repo.closed(limit=20000):
        dia = local_date(c["removed_at"], tz) if c["removed_at"] else date.fromisoformat(c["date_removed"])
        if dia == today and c["final_status"] == "COMPLETED":
            total += 1
    return total


def resumen(repo: OpenOrdersRepository, today: date, tz_name: Optional[str]) -> Dict:
    tz = safe_zone(tz_name)
    ordenes = listar(repo, today)

    # "Hoy" se mide con eventos fechados (últimos 2 días UTC cubren cualquier zona horaria).
    desde = datetime.combine(today - timedelta(days=1), time.min, tzinfo=timezone.utc)
    eventos_hoy = [e for e in repo.events(limit=20000, since=desde) if local_date(e["ts"], tz) == today]

    ultima = repo.last_runs(1)
    ok = repo.last_ok_run()
    return {
        "total_active": len(ordenes),
        "by_status": _conteo_por_estado(ordenes),
        "new_today": sum(1 for e in eventos_hoy if e["event"] == "NEW PICK TICKET"),
        "appointments_today": sum(1 for e in eventos_hoy if e["event"] == "APPOINTMENT ASSIGNED"),
        "completed_today": _completadas_hoy(repo, today, tz),
        "last_run": ultima[0] if ultima else None,
        "last_success_at": ok["finished_at"] if ok else None,
        "auto_refresh": auto_refresh_activo(repo),
        "auto_refresh_minutes": config.AUTO_REFRESH_MINUTES,
    }
