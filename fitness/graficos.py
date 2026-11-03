"""Genera la figura de la iteración 1 (ADD): p95 por variante y sensibilidad al tiempo de servicio."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from fitness.rendimiento import PRESUPUESTO_P95_MS, VARIANTES, simular


def main(salida="docs/architecture/add/img/iteracion-1.png"):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.8))
    nombres = list(VARIANTES)
    p95 = [simular(**v)["p95"] for v in VARIANTES.values()]
    colores = ["#888888", "#c8301a", "#2e7d32", "#e0a030", "#4a78c2"]
    ax1.bar(range(len(nombres)), p95, color=colores)
    for i, v in enumerate(p95):
        ax1.text(i, v * 1.15, f"{v:.0f} ms", ha="center", fontsize=8)
    ax1.axhline(PRESUPUESTO_P95_MS, ls="--", color="k", lw=1)
    ax1.text(len(nombres) - 0.5, PRESUPUESTO_P95_MS * 1.1, "QA-01: p95 ≤ 15 s", ha="right", fontsize=8)
    ax1.set_yscale("log"); ax1.set_ylim(10, 60000)
    ax1.set_xticks(range(len(nombres)))
    ax1.set_xticklabels([n.split(" ", 1)[0] for n in nombres])
    ax1.set_ylabel("p95 recepción → ETA disponible (ms, log)")
    ax1.set_title("Supuestos centrales (mediana 26 ms por posición)", fontsize=10)

    factores = [1 + 0.05 * i for i in range(0, 31)]
    for clave, color in (("V1", "#c8301a"), ("V2", "#2e7d32"), ("V3", "#e0a030")):
        nombre = next(n for n in VARIANTES if n.startswith(clave))
        ys = [simular(**VARIANTES[nombre], factor=f)["p95"] for f in factores]
        ax2.plot(factores, ys, marker="o", ms=3, color=color, label=nombre)
    ax2.axhline(PRESUPUESTO_P95_MS, ls="--", color="k", lw=1)
    ax2.set_yscale("log"); ax2.set_ylim(20, 200000)
    ax2.set_xlabel("Factor sobre el tiempo de servicio supuesto (1,0 = supuesto central)")
    ax2.set_ylabel("p95 (ms, log)")
    ax2.set_title("Punto de sensibilidad: tiempo de servicio por posición", fontsize=10)
    ax2.legend(fontsize=8)
    fig.suptitle("Iteración 1 de ADD, QA-01 con 1200 buses (simulación M/G/c, 30 min de hora punta)", fontsize=11)
    fig.tight_layout()
    fig.savefig(salida, dpi=130)


if __name__ == "__main__":
    main()
