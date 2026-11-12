"""
Conexión a la base de datos de la plataforma (PostgreSQL), compartida por todos los módulos.

- La URL se lee de DATABASE_URL en backend/.env (nunca en el código).
- Cada módulo guarda sus tablas en su propio *schema* de PostgreSQL
  (p. ej. `open_orders.orders`), para que los módulos crezcan sin chocar entre sí.
- La estructura de tablas se versiona con Alembic (backend/migrations).
"""
from functools import lru_cache

from sqlalchemy import Engine, create_engine

from app.core.settings import env


class DatabaseNotConfigured(RuntimeError):
    pass


def database_url() -> str:
    url = env("DATABASE_URL")
    if not url:
        raise DatabaseNotConfigured(
            "La base de datos no está configurada: defina DATABASE_URL en backend/.env "
            "(formato: postgresql+psycopg://USUARIO:CONTRASEÑA@localhost:5432/NOMBRE_BASE) "
            "y reinicie el backend."
        )
    return url


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    return create_engine(database_url(), pool_pre_ping=True)
