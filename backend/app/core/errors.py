"""Traducción de errores de dominio a respuestas HTTP, común a todos los routers."""
from contextlib import contextmanager
from typing import Callable, Iterator, Optional, Tuple, Type, Union

from fastapi import HTTPException

# Mensaje: None (texto de la excepción), un prefijo, o una función excepción -> texto.
Mensaje = Union[None, str, Callable[[BaseException], str]]
Regla = Tuple[Type[BaseException], int, Mensaje]


def _detalle(e: BaseException, mensaje: Mensaje) -> str:
    if callable(mensaje):
        return mensaje(e)
    return f"{mensaje or ''}{e}"


@contextmanager
def http_errors(*reglas: Regla) -> Iterator[None]:
    """Convierte excepciones en HTTPException según reglas (tipo, status, mensaje).
    La primera regla que coincide gana; las HTTPException ya armadas pasan intactas.

        with http_errors((ValueError, 422, None), (Exception, 500, "Error interno: ")):
            ...
    """
    try:
        yield
    except HTTPException:
        raise
    except BaseException as e:
        for tipo, status, mensaje in reglas:
            if isinstance(e, tipo):
                raise HTTPException(status_code=status, detail=_detalle(e, mensaje)) from e
        raise
