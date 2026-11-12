"""
Patrones de capa para un mismo tipo de caja.

Problema 2D ("pallet loading"): ¿cuántos rectángulos p x q caben en la huella
W x D del pallet? Se resuelve con programación dinámica guillotina sobre
"raster points" (combinaciones i*p + j*q), que da patrones ordenados en
bloques alineados y casi óptimos para este tipo de cajas.

Luego se elige qué dimensión de la caja va vertical (hasta 3 opciones) y se
apilan capas idénticas hasta la altura útil. Todas las capas comparten huella,
por lo que el apoyo es del 100 % y el dibujo queda alineado.
"""
from bisect import bisect_right
from dataclasses import dataclass
from functools import lru_cache
from typing import List, Optional, Tuple

TOL = 1e-6

Rect = Tuple[float, float, float, float]  # x, z, ancho (eje x), profundidad (eje z)


@dataclass(frozen=True)
class Capa:
    alto: float
    rects: Tuple[Rect, ...]     # huellas de la capa, ordenadas por (z, x)
    de_pie: bool                # True si la dimensión vertical es el alto declarado


@dataclass(frozen=True)
class Patron:
    capas: Tuple[Capa, ...]     # de abajo hacia arriba

    @property
    def capacidad(self) -> int:
        return sum(len(c.rects) for c in self.capas)

    @property
    def alto_total(self) -> float:
        return sum(c.alto for c in self.capas)

    def posiciones(self, n: Optional[int] = None) -> List[Tuple[float, float, float, float, float, float]]:
        """Primeras n cajas (capa por capa, de abajo hacia arriba):
        tuplas (x, y, z, w, h, d)."""
        limite = self.capacidad if n is None else min(n, self.capacidad)
        out: List[Tuple[float, float, float, float, float, float]] = []
        y = 0.0
        for capa in self.capas:
            for (x, z, w, d) in capa.rects:
                if len(out) >= limite:
                    return out
                out.append((x, round(y, 3), z, w, capa.alto, d))
            y += capa.alto
        return out


def _area_solape(a: Rect, b: Rect) -> float:
    ix = min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])
    iz = min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
    return ix * iz if ix > 0 and iz > 0 else 0.0


def _apilado_valido(capas: Tuple[Capa, ...], soporte_min: float) -> bool:
    """Cada caja de una capa debe apoyarse >= soporte_min sobre la capa inferior."""
    for k in range(1, len(capas)):
        for r in capas[k].rects:
            apoyo = sum(_area_solape(r, o) for o in capas[k - 1].rects)
            if apoyo < soporte_min * r[2] * r[3] - TOL:
                return False
    return True


def _raster(limite: float, p: float, q: float) -> List[float]:
    pts = set()
    i = 0
    while i * p <= limite + TOL:
        j = 0
        while i * p + j * q <= limite + TOL:
            pts.add(round(i * p + j * q, 4))
            j += 1
        i += 1
    return sorted(pts)


def mejor_patron_2d(W: float, D: float, p: float, q: float) -> List[Rect]:
    """Mejor disposición guillotina de rectángulos p x q (rotables 90°) en W x D."""
    X = _raster(W, p, q)
    Z = _raster(D, p, q)

    def reducir(v: float, pts: List[float]) -> float:
        i = bisect_right(pts, v + TOL) - 1
        return pts[i] if i >= 0 else 0.0

    @lru_cache(maxsize=None)
    def best(w: float, d: float):
        mejor = (0, ("vacio",))
        for bw, bd in ((p, q), (q, p)):
            nx, nz = int((w + TOL) // bw), int((d + TOL) // bd)
            if nx * nz > mejor[0]:
                mejor = (nx * nz, ("grid", bw, bd, nx, nz))
        for c in X:
            if c <= TOL or c >= w - TOL:
                continue
            w2 = reducir(w - c, X)
            if w2 > 0:
                total = best(c, d)[0] + best(w2, d)[0]
                if total > mejor[0]:
                    mejor = (total, ("cut_x", c, w2))
        for c in Z:
            if c <= TOL or c >= d - TOL:
                continue
            d2 = reducir(d - c, Z)
            if d2 > 0:
                total = best(w, c)[0] + best(w, d2)[0]
                if total > mejor[0]:
                    mejor = (total, ("cut_z", c, d2))
        return mejor

    def construir(w: float, d: float, ox: float, oz: float) -> List[Rect]:
        _, plan = best(w, d)
        if plan[0] == "grid":
            _, bw, bd, nx, nz = plan
            return [(ox + i * bw, oz + j * bd, bw, bd) for j in range(nz) for i in range(nx)]
        if plan[0] == "cut_x":
            _, c, w2 = plan
            return construir(c, d, ox, oz) + construir(w2, d, ox + c, oz)
        if plan[0] == "cut_z":
            _, c, d2 = plan
            return construir(w, c, ox, oz) + construir(w, d2, ox, oz + c)
        return []

    wr, dr = reducir(W, X), reducir(D, Z)
    return construir(wr, dr, 0.0, 0.0)


def mejor_patron_caja(
    dims: Tuple[float, float, float],
    alto_original: float,
    W: float,
    D: float,
    H: float,
    soporte_min: float = 0.65,
    solo_de_pie: bool = False,
) -> Optional[Patron]:
    """Patrón de pallet completo para un tipo de caja.

    Cada capa elige qué dimensión de la caja va vertical. Se combinan capas de
    distinta orientación cuando eso permite más cajas (p. ej. 4 capas de 11.8"
    + 3 de 10.6" en 79.5"), verificando que el apilado conserve el soporte.
    Desempates: más capas "de pie", menos tipos de capa distintos.
    """
    a, b, c = dims
    verticales = {(a, b, c), (b, c, a), (c, a, b)}  # (p, q, vertical)
    opciones: List[Capa] = []
    for p, q, hv in sorted(verticales):
        de_pie = abs(hv - alto_original) < TOL
        if solo_de_pie and not de_pie:
            continue
        if hv > H + TOL:
            continue
        rects = mejor_patron_2d(W, D, p, q)
        if not rects:
            continue
        rects_ord = tuple(sorted(((round(x, 3), round(z, 3), w, d) for x, z, w, d in rects),
                                 key=lambda r: (r[1], r[0])))
        opciones.append(Capa(alto=hv, rects=rects_ord, de_pie=de_pie))
    if not opciones:
        return None

    # Mochila sobre la altura: n_i capas de cada opción (cantidades pequeñas).
    candidatos: List[Tuple[Tuple, Tuple[int, ...]]] = []

    def enumerar(i: int, restante: float, cuentas: Tuple[int, ...]) -> None:
        if i == len(opciones):
            if sum(cuentas) == 0:
                return
            cap = sum(n * len(o.rects) for n, o in zip(cuentas, opciones))
            de_pie_n = sum(n for n, o in zip(cuentas, opciones) if o.de_pie)
            tipos = sum(1 for n in cuentas if n)
            candidatos.append(((cap, de_pie_n, -tipos), cuentas))
            return
        max_n = int((restante + TOL) // opciones[i].alto)
        for n in range(max_n + 1):
            enumerar(i + 1, restante - n * opciones[i].alto, cuentas + (n,))

    enumerar(0, H, ())
    candidatos.sort(key=lambda t: t[0], reverse=True)

    from itertools import permutations
    for _, cuentas in candidatos:
        grupos = [o for n, o in zip(cuentas, opciones) for _ in [0] if n]
        conteos = [n for n in cuentas if n]
        idx = list(range(len(grupos)))
        for orden in permutations(idx):
            capas = tuple(grupos[g] for g in orden for _ in range(conteos[g]))
            if _apilado_valido(capas, soporte_min):
                return Patron(capas=capas)
    return None
