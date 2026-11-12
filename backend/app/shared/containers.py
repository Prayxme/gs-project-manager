"""Códigos de contenedor marítimo (ISO 6346: 4 letras + 7 dígitos)."""
import re
from typing import List

CONTAINER_RE = re.compile(r"[A-Z]{4}\d{7}")


def find_containers(texto) -> List[str]:
    """Contenedores de un texto, sin repetir y en orden de aparición.
    'FFAU2892254 (LTL)' -> ['FFAU2892254']; 'HAMU4749408:11/08, CSNU8090823:10/22' -> ambos."""
    return list(dict.fromkeys(CONTAINER_RE.findall(str(texto or "").upper())))
