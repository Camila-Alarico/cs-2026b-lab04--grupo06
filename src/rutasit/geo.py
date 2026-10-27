"""Funciones geográficas puras (sin estado). Se comparten entre la versión antes y la versión con patrones."""
import math

RADIO_TIERRA_M = 6_371_000.0


def distancia_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distancia entre dos puntos (fórmula de Haversine), en metros."""
    f1, f2 = math.radians(lat1), math.radians(lat2)
    df, dl = f2 - f1, math.radians(lon2 - lon1)
    a = math.sin(df / 2) ** 2 + math.cos(f1) * math.cos(f2) * math.sin(dl / 2) ** 2
    return 2 * RADIO_TIERRA_M * math.asin(math.sqrt(a))


def _distancia_a_segmento_m(lat, lon, a, b) -> float:
    """Distancia del punto (lat, lon) al segmento a-b, con proyección plana local (válida a escala urbana)."""
    coseno = math.cos(math.radians(lat))

    def xy(p):
        return (math.radians(p[1] - lon) * coseno * RADIO_TIERRA_M,
                math.radians(p[0] - lat) * RADIO_TIERRA_M)

    ax, ay = xy(a)
    bx, by = xy(b)
    dx, dy = bx - ax, by - ay
    largo2 = dx * dx + dy * dy
    if largo2 == 0:
        return math.hypot(ax, ay)
    t = max(0.0, min(1.0, -(ax * dx + ay * dy) / largo2))
    return math.hypot(ax + t * dx, ay + t * dy)


def distancia_a_ruta_m(lat: float, lon: float, puntos: list[tuple[float, float]]) -> float:
    """Distancia mínima del punto a la polilínea formada por los paraderos de la ruta."""
    if len(puntos) == 1:
        return distancia_m(lat, lon, puntos[0][0], puntos[0][1])
    return min(_distancia_a_segmento_m(lat, lon, a, b) for a, b in zip(puntos, puntos[1:]))