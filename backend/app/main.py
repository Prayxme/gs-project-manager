"""Punto de entrada de la API: crea la app y monta los módulos registrados."""
import asyncio
import contextlib
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import ALLOWED_ORIGINS, APP_NAME, APP_VERSION
from app.core.registry import load_modules

MODULES = load_modules()


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Tareas de fondo declaradas por los módulos (p. ej. actualización automática del monitor).
    tareas = [asyncio.create_task(fabrica()) for m in MODULES for fabrica in m.background_tasks]
    yield
    for tarea in tareas:
        tarea.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await tarea


app = FastAPI(
    title=f"{APP_NAME} API",
    version=APP_VERSION,
    description="Plataforma modular de Golden State: paletizador 3D, monitor de órdenes abiertas "
                "e ingreso de órdenes Wiesner.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for modulo in MODULES:
    app.include_router(modulo.router)


@app.get("/health", tags=["Health Check"])
async def health_check():
    return {"status": "online", "system": APP_NAME, "version": APP_VERSION,
            "modules": [m.id for m in MODULES]}
