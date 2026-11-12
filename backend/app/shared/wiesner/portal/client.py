"""
Cliente HTTP del portal Wiesner (wpinyweb.com). SOLO LECTURA.

La página de routing del portal también permite registrar routing (escritura).
Este cliente únicamente envía `ajcmd=ajcmd_show_list`, que lista las órdenes.
No agregar otros comandos `ajcmd` sin una decisión explícita del usuario.
"""
from typing import Optional

import httpx

from app.shared.wiesner.portal import config


class PortalAuthError(Exception):
    pass


LIST_PAYLOAD = {
    "error_flg": "f", "sort_meth": "", "sort_col": "", "sav_sort_col": "", "output": "",
    "select_stage": config.SELECT_STAGE, "select_cust": "", "srch_bl_no": "",
    "sshipto_no": "", "eshipto_no": "", "spikhdrs_id": "", "epikhdrs_id": "",
    "sordhdrs_id": "", "eordhdrs_id": "", "scust_po": "", "ecust_po": "",
    "spik_dat": "", "epik_dat": "", "srch_whse": config.WAREHOUSE,
    "sload_id": "", "eload_id": "", "helpbox": "",
    "sel_routing_rqst_dat": "", "sel_routing_comment": "", "all_pikhdrs_bl_no": "",
    "sel_routing_conf_dat": "", "sel_routing_appt_dat": "", "sel_routing_appt_time": "",
    "ajcmd": "ajcmd_show_list",
}
assert LIST_PAYLOAD["ajcmd"] == "ajcmd_show_list"  # salvaguarda: solo lectura


class PortalClient:
    def __init__(self, client: Optional[httpx.Client] = None):
        self._client = client or httpx.Client(
            timeout=config.HTTP_TIMEOUT_S,
            follow_redirects=False,
            headers={"User-Agent": "GS-Project-Manager/1.0"},
        )

    def close(self) -> None:
        self._client.close()

    # -- sesión ---------------------------------------------------------------
    def _sesion_valida(self) -> bool:
        if not self._client.cookies:
            return False
        r = self._client.get(config.ROUTING_PAGE_URL)
        return r.status_code == 200 and "select_stage" in r.text and "<title>Login" not in r.text

    def login(self) -> None:
        cred = config.credenciales()
        if not all(cred.values()):
            raise PortalAuthError(
                "Faltan credenciales del portal: complete WIESNER_COMPANY_CODE, "
                "WIESNER_USERNAME y WIESNER_PASSWORD en backend/.env"
            )
        self._client.cookies.clear()
        r = self._client.post(config.LOGIN_URL, data=cred)
        if r.status_code >= 400:
            raise PortalAuthError(f"El portal rechazó el inicio de sesión (HTTP {r.status_code}).")
        if not self._sesion_valida():
            raise PortalAuthError("No se pudo iniciar sesión en el portal (revise las credenciales).")

    def asegurar_sesion(self) -> None:
        if not self._sesion_valida():
            self.login()

    # -- datos -----------------------------------------------------------------
    def fetch_routing_list(self) -> str:
        self.asegurar_sesion()
        r = self._client.post(
            config.ROUTING_AJAX_URL,
            data=LIST_PAYLOAD,
            headers={"X-Requested-With": "XMLHttpRequest"},
        )
        r.raise_for_status()
        return r.text
