"""Simulación de la iteración 1 de ADD (QA-01): ingesta de posiciones GPS y recálculo del ETA.

Modelo: cola M/G/c con un pool de workers COMPARTIDO entre la ingesta (buses) y las lecturas (pasajeros).
Medida: tiempo desde que llega la posición al servidor hasta que el ETA queda disponible (respuesta - llegada),
la misma medida de QA-01. Las lecturas que atiende el proxy con caché no entran al pool.

SUPUESTOS (NO medidos; deben reemplazarse por mediciones reales del prototipo):
  S1. 4 workers de Django sobre un solo VPS (R-03); el tamaño real del VPS no está definido.
  S2. Tiempo de servicio por posición, mediana en ms: framework + token 10, estado actual 5, ETA 6, histórico 5.
  S3. Tiempos de servicio lognormales con sigma = 0,5 (cola pesada).
  S4. Cada bus envía cada 10 s con fase aleatoria y un jitter de 0,3 s (no es Poisson).
  S5. Las lecturas (50 000 en una hora = 13,9/s) llegan por Poisson y tardan 12 ms de mediana cada una.
  S6. El histórico por lotes agrupa 10 inserciones: su costo por posición baja de 5 a 0,5 ms.
  S7. Redis para el estado actual baja ese componente de 5 a 1 ms.
"""
from __future__ import annotations

import heapq
import math
import random

PRESUPUESTO_P95_MS = 15_000  # QA-01
SIGMA = 0.5
COMPONENTES_MS = {"framework": 10.0, "estado": 5.0, "eta": 6.0, "historico": 5.0}
LECTURA_MEDIANA_MS = 12.0
LECTURAS_POR_S = 50_000 / 3600

VARIANTES = {
    "V0 control: 300 buses, sin tácticas": dict(buses=300, workers=4, componentes=dict(COMPONENTES_MS)),
    "V1 1200 buses, sin tácticas":          dict(buses=1200, workers=4, componentes=dict(COMPONENTES_MS)),
    "V2 + histórico por lotes":             dict(buses=1200, workers=4, componentes={**COMPONENTES_MS, "historico": 0.5}),
    "V3 8 workers (segundo VPS)":           dict(buses=1200, workers=8, componentes=dict(COMPONENTES_MS)),
    "V4 Redis para el estado actual":       dict(buses=1200, workers=4, componentes={**COMPONENTES_MS, "estado": 1.0}),
}


def _lognormal(rnd: random.Random, mediana_ms: float) -> float:
    return rnd.lognormvariate(math.log(mediana_ms), SIGMA) / 1000.0  # segundos


def simular(buses: int, workers: int, componentes: dict, factor: float = 1.0,
            segundos: int = 1800, semilla: int = 7) -> dict:
    """Devuelve p50, p95 y utilización de la ingesta. `factor` escala todos los tiempos de servicio."""
    rnd = random.Random(semilla)
    eventos = []  # (llegada, tipo)
    for _ in range(buses):
        fase = rnd.uniform(0, 10)
        t = fase
        while t < segundos:
            eventos.append((max(0.0, t + rnd.gauss(0, 0.3)), "I"))
            t += 10
    t = 0.0
    while t < segundos:
        t += rnd.expovariate(LECTURAS_POR_S)
        eventos.append((t, "L"))
    eventos.sort()
    mediana_ing = sum(componentes.values()) * factor
    libres = [0.0] * workers
    heapq.heapify(libres)
    respuestas, ocupado = [], 0.0
    for llegada, tipo in eventos:
        servicio = _lognormal(rnd, mediana_ing if tipo == "I" else LECTURA_MEDIANA_MS * factor)
        libre = heapq.heappop(libres)
        inicio = max(llegada, libre)
        fin = inicio + servicio
        heapq.heappush(libres, fin)
        ocupado += servicio
        if tipo == "I":
            respuestas.append((fin - llegada) * 1000)
    respuestas.sort()
    q = lambda p: respuestas[int(p * (len(respuestas) - 1))]
    return {"n": len(respuestas), "p50": q(0.50), "p95": q(0.95),
            "utilizacion": ocupado / (workers * segundos)}


def margen(variante: dict, minimo=1.0, maximo=4.0, pasos=14) -> float:
    """Mayor factor sobre los tiempos de servicio que aún cumple QA-01 (bisección). Es el margen de seguridad."""
    if simular(**variante, factor=maximo)["p95"] <= PRESUPUESTO_P95_MS:
        return maximo
    lo, hi = minimo, maximo
    for _ in range(pasos):
        medio = (lo + hi) / 2
        if simular(**variante, factor=medio)["p95"] <= PRESUPUESTO_P95_MS:
            lo = medio
        else:
            hi = medio
    return lo


if __name__ == "__main__":
    print(f"{'variante':40} {'p50 ms':>8} {'p95 ms':>9} {'util.':>6} {'cumple':>7} {'margen x':>9}")
    for nombre, v in VARIANTES.items():
        r = simular(**v)
        print(f"{nombre:40} {r['p50']:8.0f} {r['p95']:9.0f} {r['utilizacion']:6.2f} "
              f"{'sí' if r['p95'] <= PRESUPUESTO_P95_MS else 'NO':>7} {margen(v):9.2f}")
