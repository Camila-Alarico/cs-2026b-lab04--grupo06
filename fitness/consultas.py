"""Iteración 2 de ADD (QA-04): consultas de ETA en hora punta con ingesta concurrente.

Reutiliza los supuestos de fitness/rendimiento.py (4 workers compartidos, tiempos lognormales, 50 000 consultas/hora)
y agrega: tiempo de lectura con y sin índice y tasa de aciertos de la caché del proxy (ADR-002).

SUPUESTOS NUEVOS (no medidos):
  C1. Consulta sin índice: mediana 40 ms en el origen; con índice: 8 ms.
  C2. Una respuesta servida por la caché del proxy tarda 2 ms y no usa workers.
  C3. Tasa de aciertos central de la caché: 70 % (depende de cuántos pasajeros consultan el mismo paradero).
  C4. La ingesta usa el histórico por lotes decidido en la iteración 1 (mediana 21,5 ms por posición).
"""
from __future__ import annotations

import heapq
import random

from fitness.rendimiento import COMPONENTES_MS, LECTURAS_POR_S, SIGMA, _lognormal  # noqa: F401

PRESUPUESTO_LECTURA_P95_MS = 1000  # QA-04
INGESTA_MS = sum({**COMPONENTES_MS, "historico": 0.5}.values())  # V2 de la iteración 1
HIT_MS = 2.0

VARIANTES = {
    "C0 sin tácticas":         dict(lectura_ms=40.0, aciertos=0.0),
    "C1 solo índice":          dict(lectura_ms=8.0,  aciertos=0.0),
    "C2 solo caché (70 %)":    dict(lectura_ms=40.0, aciertos=0.7),
    "C3 índice + caché (70 %)": dict(lectura_ms=8.0,  aciertos=0.7),
}


def simular(lectura_ms: float, aciertos: float, buses: int = 1200, workers: int = 4, factor: float = 1.0,
            segundos: int = 1800, semilla: int = 7) -> dict:
    rnd = random.Random(semilla)
    eventos = []
    for _ in range(buses):
        t = rnd.uniform(0, 10)
        while t < segundos:
            eventos.append((max(0.0, t + rnd.gauss(0, 0.3)), "I"))
            t += 10
    t = 0.0
    while t < segundos:
        t += rnd.expovariate(LECTURAS_POR_S)
        eventos.append((t, "L"))
    eventos.sort()
    libres = [0.0] * workers
    heapq.heapify(libres)
    ingesta, lecturas_origen, lecturas_todas, ocupado = [], [], [], 0.0
    for llegada, tipo in eventos:
        if tipo == "L" and rnd.random() < aciertos:
            lecturas_todas.append(HIT_MS)
            continue
        servicio = _lognormal(rnd, (INGESTA_MS if tipo == "I" else lectura_ms) * factor)
        libre = heapq.heappop(libres)
        fin = max(llegada, libre) + servicio
        heapq.heappush(libres, fin)
        ocupado += servicio
        respuesta = (fin - llegada) * 1000
        if tipo == "I":
            ingesta.append(respuesta)
        else:
            lecturas_origen.append(respuesta)
            lecturas_todas.append(respuesta)
    q = lambda xs, p: sorted(xs)[int(p * (len(xs) - 1))]
    return {"lectura_p95": q(lecturas_todas, 0.95), "origen_p95": q(lecturas_origen, 0.95) if lecturas_origen else 0.0,
            "ingesta_p95": q(ingesta, 0.95), "utilizacion": ocupado / (workers * segundos)}


def margen(variante: dict, maximo=4.0, pasos=14) -> float:
    """Mayor factor sobre los tiempos de servicio que aún cumple QA-04 (p95 de lectura ≤ 1 s)."""
    if simular(**variante, factor=maximo)["lectura_p95"] <= PRESUPUESTO_LECTURA_P95_MS:
        return maximo
    lo, hi = 1.0, maximo
    for _ in range(pasos):
        medio = (lo + hi) / 2
        if simular(**variante, factor=medio)["lectura_p95"] <= PRESUPUESTO_LECTURA_P95_MS:
            lo = medio
        else:
            hi = medio
    return lo


def grafico(salida="docs/architecture/add/img/iteracion-2.png"):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, (a, b) = plt.subplots(1, 2, figsize=(13, 4.8))
    nombres = list(VARIANTES)
    p95 = [simular(**v)["lectura_p95"] for v in VARIANTES.values()]
    a.bar(range(len(nombres)), p95, color=["#c8301a", "#e0a030", "#4a78c2", "#2e7d32"])
    for i, v in enumerate(p95):
        a.text(i, v * 1.1, f"{v:.0f} ms", ha="center", fontsize=8)
    a.axhline(PRESUPUESTO_LECTURA_P95_MS, ls="--", color="k", lw=1)
    a.set_yscale("log"); a.set_ylim(1, 5000)
    a.set_xticks(range(len(nombres))); a.set_xticklabels([n.split(" ", 1)[0] for n in nombres])
    a.set_ylabel("p95 de la consulta de ETA (ms, log)")
    a.set_title("QA-04 con 50 000 consultas/hora y 1200 buses", fontsize=10)
    aciertos = [i * 5 for i in range(0, 20)]
    for etiqueta, ms, color in (("sin índice", 40.0, "#4a78c2"), ("con índice", 8.0, "#2e7d32")):
        b.plot(aciertos, [simular(ms, h / 100)["lectura_p95"] for h in aciertos], marker="o", ms=3, color=color, label=etiqueta)
    b.axhline(PRESUPUESTO_LECTURA_P95_MS, ls="--", color="k", lw=1)
    b.set_yscale("log"); b.set_xlabel("Tasa de aciertos de la caché del proxy (%)"); b.set_ylabel("p95 (ms, log)")
    b.set_title("Sensibilidad a la tasa de aciertos de la caché", fontsize=10); b.legend(fontsize=8)
    fig.suptitle("Iteración 2 de ADD: QA-04 (simulación M/G/c, 30 min de hora punta)", fontsize=11)
    fig.tight_layout(); fig.savefig(salida, dpi=130)


if __name__ == "__main__":
    print(f"{'variante':28} {'lectura p95':>12} {'origen p95':>11} {'ingesta p95':>12} {'util.':>6} {'cumple':>7} {'margen x':>9}")
    for nombre, v in VARIANTES.items():
        r = simular(**v)
        print(f"{nombre:28} {r['lectura_p95']:12.0f} {r['origen_p95']:11.0f} {r['ingesta_p95']:12.0f} "
              f"{r['utilizacion']:6.2f} {'sí' if r['lectura_p95'] <= PRESUPUESTO_LECTURA_P95_MS else 'NO':>7} {margen(v):9.2f}")
    grafico()