"""
Configuración de entorno de toda la plataforma.

backend/.env se carga UNA sola vez aquí; el resto del código lee variables con `env()`.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[2]
SECRETS_DIR = BACKEND_DIR / "secrets"          # credenciales locales (fuera de Git)

load_dotenv(BACKEND_DIR / ".env")


def env(nombre: str, por_defecto: str = "") -> str:
    """Variable de entorno sin espacios sobrantes."""
    return os.getenv(nombre, por_defecto).strip()
