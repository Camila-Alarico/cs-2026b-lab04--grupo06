"""Módulo Ubicaciones: puerto de lectura GPS y un Adapter por operador (Lab 07, E2)."""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from rutasit.dominio import PosicionGPS


class FuenteGps(ABC):
    """Puerto (interfaz) común <<Strategy>>: todas las fuentes de GPS se usan igual."""

    @abstractmethod
    def leer(self, placa: str) -> PosicionGPS:
        """Devuelve la última posición normalizada (grados, km/h). Puede lanzar TimeoutError."""


class OperadorAAdapter(FuenteGps):
    """<<Adapter>>: traduce el dict del operador A (grados, km/h, fecha ISO)."""

    def __init__(self, sdk):
        self._sdk = sdk

    def leer(self, placa: str) -> PosicionGPS:
        crudo = self._sdk.ultima_lectura(placa)
        return PosicionGPS(crudo["lat"], crudo["lng"], crudo["vel_kmh"],
                           datetime.fromisoformat(crudo["ts"]))


class OperadorBAdapter(FuenteGps):
    """<<Adapter>>: traduce la tupla del operador B (micro-grados, m/s, epoch)."""

    def __init__(self, sdk):
        self._sdk = sdk

    def leer(self, placa: str) -> PosicionGPS:
        lat_e6, lon_e6, vel_ms, epoch = self._sdk.leer(placa)
        return PosicionGPS(lat_e6 / 1e6, lon_e6 / 1e6, vel_ms * 3.6, datetime.fromtimestamp(epoch))
