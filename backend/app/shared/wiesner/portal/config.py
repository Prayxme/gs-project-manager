"""Portal de Wiesner (wpinyweb.com): direcciones, filtros y credenciales (solo desde backend/.env)."""
from app.core.settings import env

# Solo lectura: se usa ÚNICAMENTE ajcmd_show_list.
PORTAL_BASE_URL = "https://wpinyweb.com"
LOGIN_URL = f"{PORTAL_BASE_URL}/edibs/menu/login.php"
ROUTING_PAGE_URL = f"{PORTAL_BASE_URL}/edibs/oe/oe_pikhdr_bl_entry_batch_routing.php"
ROUTING_AJAX_URL = f"{PORTAL_BASE_URL}/edibs/oe/oe_pikhdr_bl_entry_batch_routing_aj.php"
HTTP_TIMEOUT_S = 45.0

# Filtros fijos del portal (confirmados por el usuario: siempre los mismos).
SELECT_STAGE = "rc"
WAREHOUSE = "PM"


def credenciales() -> dict:
    return {
        "comp_code": env("WIESNER_COMPANY_CODE"),
        "username": env("WIESNER_USERNAME"),
        "password": env("WIESNER_PASSWORD"),
    }
