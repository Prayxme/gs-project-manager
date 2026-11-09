"""Configuración del módulo Órdenes Abiertas (monitor de routing Wiesner)."""
import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[3]
load_dotenv(BACKEND_DIR / ".env")

# --- Portal (solo lectura: se usa ÚNICAMENTE ajcmd_show_list) ---------------------
PORTAL_BASE_URL = "https://wpinyweb.com"
LOGIN_URL = f"{PORTAL_BASE_URL}/edibs/menu/login.php"
ROUTING_PAGE_URL = f"{PORTAL_BASE_URL}/edibs/oe/oe_pikhdr_bl_entry_batch_routing.php"
ROUTING_AJAX_URL = f"{PORTAL_BASE_URL}/edibs/oe/oe_pikhdr_bl_entry_batch_routing_aj.php"
HTTP_TIMEOUT_S = 45.0

# Filtros fijos del portal (confirmados por el usuario: siempre los mismos).
SELECT_STAGE = "rc"
WAREHOUSE = "PM"

# --- Credenciales (solo desde backend/.env) ------------------------------------------
def credenciales() -> dict:
    return {
        "comp_code": os.getenv("WIESNER_COMPANY_CODE", "").strip(),
        "username": os.getenv("WIESNER_USERNAME", "").strip(),
        "password": os.getenv("WIESNER_PASSWORD", "").strip(),
    }


# --- Actualización automática ---------------------------------------------------------
# (La base de datos es PostgreSQL, configurada en app/core/database.py con DATABASE_URL.)
AUTO_REFRESH_MINUTES = 5

# --- Reglas de negocio -----------------------------------------------------------------
ATTENTION_DAYS = 3          # ATTENTION cuando faltan <= 3 días
DEFAULT_TIMEZONE = "America/Los_Angeles"
