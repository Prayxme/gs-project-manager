import asyncio
import contextlib
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import ALLOWED_ORIGINS, APP_NAME, APP_VERSION
from app.modules.open_orders import router as open_orders
from app.modules.open_orders.scheduler import bucle_auto_refresh
from app.modules.order_intake.router import router as order_intake_router
from app.modules.palletizer.router import router as palletizer_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Tarea de actualización automática del monitor de órdenes (solo actúa si está activada).
    tarea = asyncio.create_task(bucle_auto_refresh(open_orders.get_store, open_orders.fetch_portal_html))
    yield
    tarea.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await tarea


app = FastAPI(
    title=f"{APP_NAME} API",
    version=APP_VERSION,
    description="Plataforma modular de Golden State: paletizador 3D (pick tickets, estiba y tráilers) "
                "y monitor de órdenes abiertas Wiesner (routing).",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Un router por módulo. Para un módulo nuevo: app/modules/<modulo>/router.py e incluirlo aquí.
app.include_router(palletizer_router)
app.include_router(open_orders.router)
app.include_router(order_intake_router)


@app.get("/health", tags=["Health Check"])
async def health_check():
    return {"status": "online", "system": APP_NAME, "version": APP_VERSION}
