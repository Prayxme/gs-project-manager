"""Registro del módulo Ingreso de Órdenes."""
from app.core.registry import ModuleSpec
from app.modules.order_intake.router import router

MODULE = ModuleSpec(id="order-intake", router=router)
