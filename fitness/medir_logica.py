"""Medición REAL (solo CPU, sin base de datos) del costo de procesar una posición con el código del Lab 07.

Sirve para calibrar el componente "eta" de la simulación: cuánto cuesta en Python recalcular los ETA de una ruta.
Ejecutar desde la raíz del repo:  python -m fitness.medir_logica
"""
import statistics
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from rutasit.dominio import Bus, Paradero, ParaderoDeRuta, Ruta  # noqa: E402
from rutasit.externos import GpsOperadorA  # noqa: E402
from rutasit.servicio import ServicioRutaSIT, Viaje  # noqa: E402

AHORA = datetime(2026, 10, 20, 8, 0, 0)


def medir(paraderos: int, repeticiones: int = 2000) -> tuple[float, float]:
    ruta = Ruta("R1", "Ruta 1", [ParaderoDeRuta(i + 1, Paradero(f"P{i}", f"Paradero {i}", -16.40 - i * 0.002, -71.53))
                                 for i in range(paraderos)])
    gps = GpsOperadorA()
    s = ServicioRutaSIT(gps_a=gps, reloj=lambda: AHORA)
    s.registrar_viaje(Viaje("V1", ruta, Bus("ABC-123")))
    s.iniciar_viaje("V1")
    tiempos = []
    for i in range(repeticiones):
        gps.lectura = {"lat": -16.40 - (i % 20) * 0.001, "lng": -71.53, "vel_kmh": 20.0,
                       "ts": (AHORA - timedelta(seconds=5)).isoformat()}
        t0 = time.perf_counter()
        s.actualizar_bus("V1", "OPERADOR_A")
        tiempos.append((time.perf_counter() - t0) * 1000)
    tiempos.sort()
    return statistics.median(tiempos), tiempos[int(0.95 * (len(tiempos) - 1))]


if __name__ == "__main__":
    print("paraderos por ruta | mediana ms | p95 ms   (solo lógica en memoria, sin base de datos)")
    for n in (20, 40, 80):
        mediana, p95 = medir(n)
        print(f"{n:18d} | {mediana:10.3f} | {p95:7.3f}")
