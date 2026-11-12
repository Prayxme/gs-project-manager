"""Registro del módulo Ingreso de Órdenes."""
from app.core.registry import ModuleSpec
from app.modules.order_intake.router import router
from app.modules.order_intake.scheduler import bucle_gmail

MODULE = ModuleSpec(id="order-intake", router=router, background_tasks=[bucle_gmail])
