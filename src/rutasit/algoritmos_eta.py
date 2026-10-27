"""Módulo ETA: puerto del algoritmo de tiempo de llegada y sus estrategias (Lab 07, E2). Traza a QA-03."""
from __future__ import annotations

from abc import ABC, abstractmethod

VELOCIDAD_MINIMA_KMH = 5.0


class AlgoritmoEta(ABC):
    """<<Strategy>>: algoritmos intercambiables para estimar el tiempo de llegada."""

    @abstractmethod
    def segundos(self, distancia_m: float, velocidad_kmh: float) -> float:
        """Segundos estimados para recorrer distancia_m dado el estado actual del bus."""


class DistanciaDirecta(AlgoritmoEta):
    """Distancia dividida por la velocidad actual (con un mínimo para no dividir por cero)."""

    def segundos(self, distancia_m: float, velocidad_kmh: float) -> float:
        return distancia_m / (max(velocidad_kmh, VELOCIDAD_MINIMA_KMH) / 3.6)


class VelocidadPromedio(AlgoritmoEta):
    """Distancia dividida por una velocidad promedio configurada para la ruta."""

    def __init__(self, velocidad_promedio_kmh: float = 20.0):
        self._velocidad_promedio_kmh = velocidad_promedio_kmh

    def segundos(self, distancia_m: float, velocidad_kmh: float) -> float:
        return distancia_m / (self._velocidad_promedio_kmh / 3.6)
