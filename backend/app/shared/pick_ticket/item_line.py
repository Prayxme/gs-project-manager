"""Lectura de la línea de producto del Pick Ticket."""
from typing import Any, Dict

from app.shared.pick_ticket.patterns import RE_NUM


def to_int(s: str) -> int:
    return int(s.replace(",", ""))


def parse_item_line(line: str) -> Dict[str, Any]:
    """'3-M2056ST MARS P24 S40570 2 2 56 94 MENS 3 PACK ... 295344'
    -> sku = primer token; variant = tokens hasta la columna de cantidades;
       cases = último número de la primera racha numérica de >= 2 tokens
       (Qty Ord puede venir partido en miles: '2 2 56' = 2256, luego Cases);
       cust_sku = último token numérico de la línea."""
    tokens = line.split()
    sku = tokens[0] if tokens else ""
    cust_sku = tokens[-1] if len(tokens) > 1 and tokens[-1].isdigit() else ""
    rest = tokens[1:]
    i = 0
    while i < len(rest):
        if RE_NUM.match(rest[i]):
            j = i
            while j < len(rest) and RE_NUM.match(rest[j]):
                j += 1
            if j - i >= 2:
                return {
                    "sku": sku,
                    "variant": " ".join(rest[:i]),
                    "cust_sku": cust_sku,
                    "cases": to_int(rest[j - 1]),
                }
            i = j
        else:
            i += 1
    return {"sku": sku, "variant": "", "cust_sku": cust_sku, "cases": None}
