from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import ALLOWED_ORIGINS, APP_NAME, APP_VERSION
from app.modules.palletizer.router import router as palletizer_router

app = FastAPI(
    title=f"{APP_NAME} API",
    version=APP_VERSION,
    description="Plataforma modular de Golden State: paletizador 3D (pick tickets, estiba y tráilers) "
                "y próximos módulos de operación de bodega.",
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


@app.get("/health", tags=["Health Check"])
async def health_check():
    return {"status": "online", "system": APP_NAME, "version": APP_VERSION}
