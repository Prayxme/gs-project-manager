"""Endpoints HTTP del módulo Órdenes Abiertas (/api/open-orders/...)."""
import threading
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from pydantic import BaseModel

from app.modules.open_orders import service
from app.modules.open_orders.parser import PortalResponseError
from app.modules.open_orders.portal_client import PortalAuthError, PortalClient
from app.modules.open_orders.store import Store

router = APIRouter(prefix="/api/open-orders", tags=["Órdenes Abiertas"])

_store: Optional[Store] = None
_client: Optional[PortalClient] = None
_client_lock = threading.Lock()


def get_store() -> Store:
    global _store
    if _store is None:
        _store = Store()
    return _store


def fetch_portal_html() -> str:
    """Un solo cliente reutilizado: conserva la cookie y evita iniciar sesión en cada consulta."""
    global _client
    with _client_lock:
        if _client is None:
            _client = PortalClient()
        return _client.fetch_routing_list()


def get_fetcher():
    return fetch_portal_html


def _hoy(today: Optional[str]) -> date:
    if not today:
        return date.today()
    try:
        return date.fromisoformat(today)
    except ValueError:
        raise HTTPException(status_code=422, detail="Parámetro 'today' inválido (use AAAA-MM-DD).")


@router.get("/orders")
def orders(today: Optional[str] = Query(None, description="Fecha local del usuario AAAA-MM-DD"),
           store: Store = Depends(get_store)):
    return {"today": _hoy(today).isoformat(), "orders": service.listar(store, _hoy(today))}


@router.get("/summary")
def summary(today: Optional[str] = None, tz: Optional[str] = None, store: Store = Depends(get_store)):
    return service.resumen(store, _hoy(today), tz)


@router.post("/refresh")
def refresh(store: Store = Depends(get_store), fetch=Depends(get_fetcher)):
    try:
        return service.refresh(store, fetch, trigger="manual")
    except (PortalAuthError, PortalResponseError) as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"No se pudo consultar el portal: {e}")


class AutoRefreshBody(BaseModel):
    enabled: bool


@router.get("/auto-refresh")
def get_auto_refresh(store: Store = Depends(get_store)):
    return {"enabled": service.auto_refresh_activo(store)}


@router.put("/auto-refresh")
def set_auto_refresh(body: AutoRefreshBody, store: Store = Depends(get_store)):
    store.set_setting("auto_refresh", "1" if body.enabled else "0")
    return {"enabled": body.enabled}


@router.get("/events")
def events(limit: int = Query(500, ge=1, le=5000), store: Store = Depends(get_store)):
    return {"events": store.events(limit=limit)}


@router.get("/closed")
def closed(limit: int = Query(2000, ge=1, le=20000), store: Store = Depends(get_store)):
    return {"closed": store.closed(limit=limit)}


@router.post("/import-completed")
async def import_completed(file: UploadFile = File(...), store: Store = Depends(get_store)):
    if not (file.filename or "").lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="El archivo debe ser un CSV.")
    contenido = (await file.read()).decode("utf-8", errors="replace")
    try:
        return service.importar_completadas_csv(store, contenido)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
