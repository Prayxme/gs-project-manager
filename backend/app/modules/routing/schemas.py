"""Esquemas HTTP del Routing."""
from datetime import date
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class PreRouteLine(BaseModel):
    """Una línea de Pre Routing tal como la escribe el usuario o la trae el Excel
    (los valores se limpian en rules/preroute.py: '9lb', '11/13/26', números como texto...)."""
    cust: Any = None
    po: Any = None
    ship_date: Any = None
    cancel_date: Any = None
    style: Any = None
    color: Any = None
    qty: Any = None
    cases: Any = None
    weight: Any = None          # lb por cartón
    cube: Any = None            # CFT por cartón
    ship_to: Any = None         # destino / DC (solo hace falta fuera de TJMA, MARS y NEWT)


class PreRoutePlanRequest(BaseModel):
    lines: List[PreRouteLine] = Field(..., min_length=1, max_length=5000)
    today: Optional[date] = None
