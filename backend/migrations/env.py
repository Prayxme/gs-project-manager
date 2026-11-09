"""Entorno de Alembic: usa la misma conexión que la app (DATABASE_URL en backend/.env)."""
from logging.config import fileConfig

from alembic import context

from app.core.database import database_url, get_engine
from app.modules.open_orders.models import metadata as open_orders_metadata

if context.config.config_file_name:
    fileConfig(context.config.config_file_name)

# Metadata de cada módulo con tablas. Agregar aquí la de los módulos futuros.
target_metadata = [open_orders_metadata]


def run_migrations_offline() -> None:
    context.configure(url=database_url(), target_metadata=target_metadata, literal_binds=True,
                      include_schemas=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    with get_engine().connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, include_schemas=True)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
