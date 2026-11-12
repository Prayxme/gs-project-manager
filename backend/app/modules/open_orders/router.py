"""Endpoints HTTP del módulo Órdenes Abiertas (/api/open-orders/...). Solo validan y delegan."""
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from pydantic import BaseModel

from app.core.errors import http_errors
from app.modules.open_orders import services
from app.modules.open_orders.dependencies import get_fetcher, get_repository
from app.modules.open_orders.repository import OpenOrdersRepository
from app.shared.wiesner.portal import PortalAuthError, PortalResponseError

router = APIRouter(prefix="/api/open-orders", tags=["Órdenes Abiertas"])
Repo = OpenOrdersRepository


class AutoRefreshBody(BaseModel):
    enabled: bool


def _hoy(today: Optional[str]) -> date:
    if not today:
        return date.today()
    try:
        return date.fromisoformat(today)
    except ValueError:
        raise HTTPException(status_code=422, detail="Parámetro 'today' inválido (use AAAA-MM-DD).")


@router.get("/orders")
def orders(today: Optional[str] = Query(None, description="Fecha local del usuario AAAA-MM-DD"),
           repo: Repo = Depends(get_repository)):
    hoy = _hoy(today)
    return {"today": hoy.isoformat(), "orders": services.listar(repo, hoy)}


@router.get("/summary")
def summary(today: Optional[str] = None, tz: Optional[str] = None, repo: Repo = Depends(get_repository)):
    return services.resumen(repo, _hoy(today), tz)


@router.post("/refresh")
def refresh(repo: Repo = Depends(get_repository), fetch=Depends(get_fetcher)):
    with http_errors((PortalAuthError, 502, None), (PortalResponseError, 502, None),
                     (Exception, 502, "No se pudo consultar el portal: ")):
        return services.refresh(repo, fetch, trigger="manual")


@router.get("/auto-refresh")
def get_auto_refresh(repo: Repo = Depends(get_repository)):
    return {"enabled": services.auto_refresh_activo(repo)}


@router.put("/auto-refresh")
def set_auto_refresh(body: AutoRefreshBody, repo: Repo = Depends(get_repository)):
    repo.set_setting("auto_refresh", "1" if body.enabled else "0")
    return {"enabled": body.enabled}


@router.get("/events")
def events(limit: int = Query(500, ge=1, le=5000), repo: Repo = Depends(get_repository)):
    return {"events": repo.events(limit=limit)}


@router.get("/closed")
def closed(limit: int = Query(2000, ge=1, le=20000), repo: Repo = Depends(get_repository)):
    return {"closed": repo.closed(limit=limit)}


@router.post("/import-completed")
async def import_completed(file: UploadFile = File(...), repo: Repo = Depends(get_repository)):
    if not (file.filename or "").lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="El archivo debe ser un CSV.")
    contenido = (await file.read()).decode("utf-8", errors="replace")
    with http_errors((ValueError, 422, None)):
        return services.importar_completadas_csv(repo, contenido)
