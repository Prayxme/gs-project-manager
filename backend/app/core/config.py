"""Configuración global de la plataforma (común a todos los módulos).
La configuración propia de cada módulo vive en app/modules/<modulo>/config.py."""
from typing import List

APP_NAME: str = "Golden State Project Manager - Wiesner"
APP_VERSION: str = "0.15.0"

# Constantes del Servidor y CORS
ALLOWED_ORIGINS: List[str] = ["*"]
