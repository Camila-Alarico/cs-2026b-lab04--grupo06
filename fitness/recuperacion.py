"""Iteración 3 de ADD (QA-05 y QA-02): recuperación tras reiniciar el servidor.

Escenario: el servidor está caído D segundos; los buses guardan las posiciones que no pudieron enviar (R-04) y las
reenvían al reconectarse, mientras siguen llegando las posiciones normales y las consultas de los pasajeros.
Medida (QA-05): segundos desde que el servidor vuelve hasta que el ETA de cada bus está al día, es decir, hasta que
se procesó su posición más reciente. Se reporta el p95 y el máximo entre los 1200 buses.

SUPUESTOS NUEVOS (no medidos):
  R1. Los buses acumulan las posiciones no enviadas y las reenvían al reconectarse (si no las acumularan, no hay ráfaga).
  R2. Caída de D = 120 s (el límite de disponibilidad de QA-05), es decir 12 posiciones acumuladas por bus.
  R3. Cada bus se reconecta con un retraso aleatorio de 0 a 10 s y envía su ráfaga de la más antigua a la más nueva.
  R4. Con la táctica, la posición más reciente de cada bus se procesa con prioridad (estado y ETA, 21,5 ms) y las
      anteriores van solo al histórico en lote con baja prioridad (0,5 ms cada una).
  R5. Se mantienen los demás supuestos de fitness/rendimiento.py (4 workers, lognormal sigma 0,5, 13,9 lecturas/s).
"""
from __future__ import annotations

import heapq
import random

from fitness.rendimiento import COMPONENTES_MS, LECTURA_MEDIANA_MS, LECTURAS_POR_S, _lognormal

PRESUPUESTO_RECUPERACION_S = 30  # QA-05: ETA al día en ≤ 30 s tras reanudarse la ingesta
SIN_LOTES_MS = sum(COMPONENTES_MS.values())                      # 26 ms
CON_LOTES_MS = sum({**COMPONENTES_MS, "historico": 0.5}.values())  # 21,5 ms
HISTORICO_LOTE_MS = 0.5

VARIANTES = {
    "R0 FIFO, sin tácticas":                dict(workers=4, estado_ms=SIN_LOTES_MS, prioridad=False),
    "R1 FIFO + histórico por lotes":        dict(workers=4, estado_ms=CON_LOTES_MS, prioridad=False),
    "R2 FIFO con 8 workers":                dict(workers=8, estado_ms=SIN_LOTES_MS, prioridad=False),
    "R3 última posición primero + lotes":   dict(workers=4, estado_ms=CON_LOTES_MS, prioridad=True),
}


def simular(workers: int, estado_ms: float, prioridad: bool, buses: int = 1200, caida_s: int = 120,
            horizonte_s: int = 900, factor: float = 1.0, semilla: int = 7) -> dict:
    rnd = random.Random(semilla)
    acumuladas = caida_s // 10
    trabajos = []  # (llegada, tipo, bus, es_ultima)   tipo: 'E' estado+ETA, 'H' solo histórico, 'L' lectura
    for bus in range(buses):
        reconexion = rnd.uniform(0, 10)
        for j in range(acumuladas):
            ultima = j == acumuladas - 1
            if prioridad and not ultima:
                trabajos.append((reconexion + 0.001 * j, "H", bus, False))
            else:
                trabajos.append((reconexion + 0.001 * j, "E", bus, ultima))
        t = reconexion + rnd.uniform(0, 10)          # posiciones normales después de reconectarse
        while t < horizonte_s:
            trabajos.append((t, "E", bus, False))
            t += 10
    t = 0.0
    while t < horizonte_s:
        t += rnd.expovariate(LECTURAS_POR_S)
        trabajos.append((t, "L", -1, False))
    trabajos.sort()
    libres = [0.0] * workers
    heapq.heapify(libres)
    alta, baja, i, n = [], [], 0, len(trabajos)
    al_dia = {}
    while i < n or alta or baja:
        t_libre = libres[0]
        t = t_libre if (alta or baja) else max(t_libre, trabajos[i][0])
        while i < n and trabajos[i][0] <= t:
            llegada, tipo, bus, ultima = trabajos[i]
            (baja if tipo == "H" else alta).append((llegada, tipo, bus, ultima))
            i += 1
        cola = alta if alta else baja
        if not cola:
            continue
        # FIFO dentro de cada clase de prioridad (las listas se llenan en orden de llegada)
        llegada, tipo, bus, ultima = cola.pop(0)
        heapq.heappop(libres)
        mediana = {"E": estado_ms, "H": HISTORICO_LOTE_MS, "L": LECTURA_MEDIANA_MS}[tipo] * factor
        fin = t + _lognormal(rnd, mediana)
        heapq.heappush(libres, fin)
        if ultima:
            al_dia[bus] = fin
    tiempos = sorted(al_dia.values())
    return {"p95": tiempos[int(0.95 * (len(tiempos) - 1))], "max": tiempos[-1], "trabajos": n}


def grafico(salida="docs/architecture/add/img/iteracion-3.png"):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, (a, b) = plt.subplots(1, 2, figsize=(13, 4.8))
    nombres = list(VARIANTES)
    maxs = [simular(**v)["max"] for v in VARIANTES.values()]
    a.bar(range(len(nombres)), maxs, color=["#c8301a", "#e0a030", "#4a78c2", "#2e7d32"])
    for k, v in enumerate(maxs):
        a.text(k, v * 1.1, f"{v:.0f} s", ha="center", fontsize=8)
    a.axhline(PRESUPUESTO_RECUPERACION_S, ls="--", color="k", lw=1)
    a.text(len(nombres) - 0.5, PRESUPUESTO_RECUPERACION_S * 1.15, "QA-05: ≤ 30 s", ha="right", fontsize=8)
    a.set_yscale("log"); a.set_ylim(1, 5000)
    a.set_xticks(range(len(nombres))); a.set_xticklabels([n.split(" ", 1)[0] for n in nombres])
    a.set_ylabel("Segundos hasta que TODOS los buses tienen ETA al día (log)")
    a.set_title("Caída de 120 s con 12 posiciones acumuladas por bus", fontsize=10)
    caidas = [30, 60, 90, 120, 180, 240, 300]
    for nombre, color in (("R0 FIFO, sin tácticas", "#c8301a"), ("R1 FIFO + histórico por lotes", "#e0a030"),
                          ("R3 última posición primero + lotes", "#2e7d32")):
        b.plot(caidas, [simular(**VARIANTES[nombre], caida_s=c)["max"] for c in caidas], marker="o", ms=3, color=color, label=nombre.split(" ", 1)[0])
    b.axhline(PRESUPUESTO_RECUPERACION_S, ls="--", color="k", lw=1)
    b.set_yscale("log"); b.set_xlabel("Duración de la caída (s)"); b.set_ylabel("Máximo (s, log)")
    b.set_title("Sensibilidad a la duración de la caída", fontsize=10); b.legend(fontsize=8)
    fig.suptitle("Iteración 3 de ADD: QA-05 (recuperación tras reiniciar el servidor)", fontsize=11)
    fig.tight_layout(); fig.savefig(salida, dpi=130)


if __name__ == "__main__":
    print(f"{'variante':38} {'p95 s':>8} {'máximo s':>9} {'cumple QA-05':>13}")
    for nombre, v in VARIANTES.items():
        r = simular(**v)
        print(f"{nombre:38} {r['p95']:8.1f} {r['max']:9.1f} {'sí' if r['max'] <= PRESUPUESTO_RECUPERACION_S else 'NO':>13}")
    grafico()