"""Registro del módulo Monitor de Órdenes Abiertas."""
from app.core.registry import ModuleSpec
from app.modules.open_orders.router import router
from app.modules.open_orders.scheduler import bucle_auto_refresh

MODULE = ModuleSpec(id="open-orders", router=router, background_tasks=[bucle_auto_refresh])
