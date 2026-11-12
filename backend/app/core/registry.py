"""
Registro de módulos de la plataforma.

Cada módulo expone en `app/modules/<id>/module.py` una variable MODULE (ModuleSpec):
su router y, si los necesita, tareas de fondo que arrancan con el servidor.
Para agregar un módulo nuevo basta con crear su module.py y sumarlo a MODULES.
"""
from dataclasses import dataclass, field
from typing import Awaitable, Callable, List

from fastapi import APIRouter


@dataclass(frozen=True)
class ModuleSpec:
    id: str
    router: APIRouter
    background_tasks: List[Callable[[], Awaitable[None]]] = field(default_factory=list)


def load_modules() -> List[ModuleSpec]:
    from app.modules.open_orders.module import MODULE as open_orders
    from app.modules.order_intake.module import MODULE as order_intake
    from app.modules.palletizer.module import MODULE as palletizer
    from app.modules.routing.module import MODULE as routing

    return [palletizer, open_orders, order_intake, routing]
