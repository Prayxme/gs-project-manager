"""
Autorización OAuth con la cuenta de Google Workspace del usuario.

Uso (una sola vez, desde backend/):
    .\\venv\\Scripts\\python -m app.shared.google.auth

Abre el navegador para iniciar sesión y aceptar los permisos. El token queda en
backend/secrets/google_token.json (excluido de Git) y se renueva solo.
"""
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from app.shared.google import config


class GoogleNotAuthorized(RuntimeError):
    pass


def credenciales() -> Credentials:
    """Credenciales vigentes (renueva el token si venció). No abre el navegador."""
    if not config.OAUTH_TOKEN_FILE.exists():
        raise GoogleNotAuthorized(
            "Google no está autorizado todavía. Ejecute: "
            ".\\venv\\Scripts\\python -m app.shared.google.auth"
        )
    creds = Credentials.from_authorized_user_file(str(config.OAUTH_TOKEN_FILE), config.SCOPES)
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            config.OAUTH_TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
        else:
            raise GoogleNotAuthorized("La autorización de Google ya no es válida; vuelva a autorizar.")
    return creds


def autorizar() -> Credentials:
    from google_auth_oauthlib.flow import InstalledAppFlow

    if not config.OAUTH_CLIENT_FILE.exists():
        raise SystemExit(f"Falta el archivo de credenciales: {config.OAUTH_CLIENT_FILE}")
    flow = InstalledAppFlow.from_client_secrets_file(str(config.OAUTH_CLIENT_FILE), config.SCOPES)
    creds = flow.run_local_server(port=0, prompt="consent")
    config.SECRETS_DIR.mkdir(parents=True, exist_ok=True)
    config.OAUTH_TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
    return creds


if __name__ == "__main__":
    c = autorizar()
    print("Autorización guardada. Permisos concedidos:")
    for scope in sorted(c.scopes or config.SCOPES):
        print(" -", scope)
