"""Configuración del módulo Órdenes Abiertas (monitor de routing Wiesner).
El portal (direcciones, credenciales) se configura en app/shared/wiesner/portal/config.py."""

# --- Actualización automática ---------------------------------------------------------
# (La base de datos es PostgreSQL, configurada en app/core/database.py con DATABASE_URL.)
AUTO_REFRESH_MINUTES = 5

# --- Reglas de negocio -----------------------------------------------------------------
ATTENTION_DAYS = 3          # ATTENTION cuando faltan <= 3 días
