"""Configuración de la cuenta de Google del usuario (OAuth), compartida por los módulos.

Un solo token para toda la plataforma: los cambios en Sheets figuran a nombre del usuario.
"""
from app.core.settings import SECRETS_DIR

OAUTH_CLIENT_FILE = SECRETS_DIR / "google_oauth_client.json"
OAUTH_TOKEN_FILE = SECRETS_DIR / "google_token.json"

# Permisos pedidos al autorizar. Agregar aquí si un módulo nuevo necesita otro servicio de Google
# (y volver a autorizar una vez).
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",       # leer/escribir hojas
    "https://www.googleapis.com/auth/gmail.readonly",     # leer correos (solo lectura)
]
