"""Registro del módulo Routing (RTS)."""
from app.core.registry import ModuleSpec
from app.modules.routing.router import router

MODULE = ModuleSpec(id="routing", router=router)
