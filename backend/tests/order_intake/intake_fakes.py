"""Piezas falsas para probar el Ingreso de Órdenes sin Google: hoja, Gmail y órdenes de ejemplo."""
from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from app.modules.order_intake import rules
from app.shared.google.gmail import Adjunto, Correo


def motor_sqlite():
    return create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})


def fila(pt, po="01347018", ctns=147, conts="HAMU4749408", g="No", h=46332, i=46339):
    f = [""] * 22
    for col, v in {"A": False, "B": "WIESNER", "C": "MARS125", "D": po, "E": pt, "F": conts,
                   "G": g, "H": h, "I": i, "V": ctns}.items():
        f[rules.col_idx(col)] = v
    return f


class FakeGateway:
    """Imita SheetsGateway: hoja BONNIE desde la fila 4, INBOUND y LIST."""

    def __init__(self, filas, inbound=(), tiendas=("MARS125",)):
        self.filas = dict(filas)            # {num_fila: valores}
        self.inbound = list(inbound)
        self.tiendas = set(tiendas)
        self.escrituras = []
        self.lecturas = 0

    def leer_bonnie(self):
        self.lecturas += 1
        indice = {str(v[4]): (n, v) for n, v in self.filas.items()}
        return max(self.filas, default=3), indice

    def leer_inbound(self):
        return self.inbound

    def leer_tiendas(self):
        return self.tiendas

    def agregar_filas(self, ultima, filas):
        nums = list(range(ultima + 1, ultima + 1 + len(filas)))
        for n, f in zip(nums, filas):
            v = [""] * 22
            for col, val in f.items():
                v[rules.col_idx(col)] = val
            self.filas[n] = v
            self.escrituras.append(("NEW", n, f))
        return nums

    def actualizar_celdas(self, n, cambios):
        for col, val in cambios.items():
            self.filas[n][rules.col_idx(col)] = val
        self.escrituras.append(("UPDATE", n, cambios))


def orden(pt, **c):
    o = {"piktik": str(pt), "company": "WIESNER", "store": "MARS125", "po": "01347018",
         "containers": ["HAMU4749408"], "ship_date": "11/06/2026", "cancel_date": "11/13/2026", "ctns": 147}
    o.update(c)
    return o


def inbound_ok(cont):
    f = [""] * 25
    f[1], f[3] = cont, "Returned"
    for letra in "PQRSUVWX":
        f[rules.col_idx(letra)] = "YES"
    return f


# --- PDFs y Gmail ----------------------------------------------------------------------------
def pdf_falso(*piktiks) -> bytes:
    """'PDF' de prueba: el lector falso (leer_pdf_falso) lo convierte en órdenes."""
    return ("PDF:" + ",".join(str(p) for p in piktiks)).encode()


def leer_pdf_falso(contenido: bytes):
    """Reemplazo de extraer_datos_pick_ticket para las pruebas."""
    texto = contenido.decode()
    if not texto.startswith("PDF:"):
        raise ValueError("No se detectó ningún PikTik en el PDF.")
    ordenes = [{"piktik": pt, "po": "01347018", "cust_no": "MARS125", "company": "Wiesner Products, Inc.",
                "ship_date": "11/06/2026", "cancel_date": "11/13/2026", "containers": ["HAMU4749408"],
                "declared_cases": 147, "items": [{"qty": 147}]}
               for pt in texto[4:].split(",")]
    return {"company": "Wiesner Products, Inc.", "cust_no": "MARS125", "orders": ordenes, "warnings": []}


class FakeGmail:
    """Imita GmailReader con una lista de correos {id: (asunto, [(archivo, bytes)])}."""

    def __init__(self, correos):
        self.correos = dict(correos)
        self.consultas = []

    def buscar(self, query, max_results=100):
        self.consultas.append(query)
        return list(reversed(list(self.correos)))      # Gmail: del más reciente al más viejo

    def correo(self, mid, extension=""):
        asunto, adjuntos = self.correos[mid]
        return Correo(id=mid, thread_id=mid, subject=asunto, sender="wpireports@wpiny.com",
                      received_at=datetime(2026, 11, 11, 15, 40, tzinfo=timezone.utc),
                      adjuntos=[Adjunto(n, f"{mid}/{n}", len(b)) for n, b in adjuntos
                                if n.lower().endswith(extension.lower())])

    def descargar(self, mid, attachment_id):
        nombre = attachment_id.split("/", 1)[1]
        return dict(self.correos[mid][1])[nombre]
