"""Registro del módulo Paletizador 3D."""
from app.core.registry import ModuleSpec
from app.modules.palletizer.router import router

MODULE = ModuleSpec(id="palletizer", router=router)
