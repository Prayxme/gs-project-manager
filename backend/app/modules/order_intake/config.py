"""Configuración del módulo Ingreso de Órdenes (PDF/Gmail -> hoja BONNIE)."""
import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[3]
load_dotenv(BACKEND_DIR / ".env")

# --- Hojas de Google (IDs en backend/.env) ------------------------------------------
PICKTICKET_SHEET_ID = os.getenv("INTAKE_PICKTICKET_SHEET_ID", "").strip()
PICKTICKET_TAB = os.getenv("INTAKE_PICKTICKET_TAB", "BONNIE 11-18-2025").strip()
PICKTICKET_FIRST_DATA_ROW = 4          # filas 1-2 encabezado, fila 3 '**'

CONTAINERS_SHEET_ID = os.getenv("INTAKE_CONTAINERS_SHEET_ID", "").strip()
CONTAINERS_TAB = os.getenv("INTAKE_CONTAINERS_TAB", "INBOUND").strip()

# --- OAuth con la cuenta del usuario (los cambios figuran a su nombre) -----------------
SECRETS_DIR = BACKEND_DIR / "secrets"                     # excluida de Git
OAUTH_CLIENT_FILE = SECRETS_DIR / "google_oauth_client.json"
OAUTH_TOKEN_FILE = SECRETS_DIR / "google_token.json"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",       # leer/escribir las hojas
    "https://www.googleapis.com/auth/gmail.readonly",     # Fase 2: leer correos (solo lectura)
]

# --- Correos de Pick Tickets (Fase 2) ---------------------------------------------------
GMAIL_SENDER = "wpireports@wpiny.com"
GMAIL_SUBJECT_PREFIX = "PICK-TICKETS - 00WPI - Whse:PM"
