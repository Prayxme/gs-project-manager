"""Configuración del módulo Ingreso de Órdenes (PDF/Gmail -> hoja BONNIE)."""
from app.core.settings import env

# --- Hojas de Google (IDs en backend/.env) ------------------------------------------
PICKTICKET_SHEET_ID = env("INTAKE_PICKTICKET_SHEET_ID")
PICKTICKET_TAB = env("INTAKE_PICKTICKET_TAB", "BONNIE 11-18-2025")
PICKTICKET_FIRST_DATA_ROW = 4          # filas 1-2 encabezado, fila 3 '**'

CONTAINERS_SHEET_ID = env("INTAKE_CONTAINERS_SHEET_ID")
CONTAINERS_TAB = env("INTAKE_CONTAINERS_TAB", "INBOUND")

# --- Correos de Pick Tickets (Fase 2: bandeja de Gmail) ----------------------------------
GMAIL_SENDER = "wpireports@wpiny.com"
GMAIL_SUBJECT_PREFIX = "PICK-TICKETS - 00WPI - Whse:PM"
# Cada correo trae el PDF de Pick Tickets (oe_piktik_...) y un "wave report" que se ignora.
GMAIL_ATTACHMENT_PREFIX = "oe_piktik"
# La primera revisión mira estos días hacia atrás; después, desde el último correo guardado.
GMAIL_LOOKBACK_DAYS = int(env("INTAKE_GMAIL_LOOKBACK_DAYS", "7"))
# Cada cuántos minutos el servidor revisa Gmail solo (0 = desactivado; queda el botón manual).
GMAIL_POLL_MINUTES = int(env("INTAKE_GMAIL_POLL_MINUTES", "10"))
