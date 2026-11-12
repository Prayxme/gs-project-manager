"""Traducción de excepciones a HTTPException (app/core/errors.py)."""
import pytest
from fastapi import HTTPException

from app.core.errors import http_errors


class ErrorExterno(Exception):
    reason = "Forbidden"


def _lanzar(exc, *reglas):
    with pytest.raises(HTTPException) as info:
        with http_errors(*reglas):
            raise exc
    return info.value


def test_texto_de_la_excepcion_y_prefijo():
    assert _lanzar(ValueError("malo"), (ValueError, 422, None)).detail == "malo"
    e = _lanzar(RuntimeError("x"), (RuntimeError, 500, "Error interno: "))
    assert (e.status_code, e.detail) == (500, "Error interno: x")


def test_mensaje_con_funcion():
    e = _lanzar(ErrorExterno(), (ErrorExterno, 502, lambda ex: f"Google: {ex.reason}"))
    assert (e.status_code, e.detail) == (502, "Google: Forbidden")


def test_primera_regla_gana_y_http_exception_pasa_intacta():
    assert _lanzar(ValueError("v"), (ValueError, 400, None), (Exception, 500, None)).status_code == 400
    assert _lanzar(HTTPException(404, "no"), (Exception, 500, None)).status_code == 404


def test_sin_regla_la_excepcion_sigue():
    with pytest.raises(KeyError):
        with http_errors((ValueError, 422, None)):
            raise KeyError("k")
