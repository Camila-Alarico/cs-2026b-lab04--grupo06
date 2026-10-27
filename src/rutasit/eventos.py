"""Patrón Observer (Lab 07, E4): publicador neutral de eventos de dominio. No conoce a sus suscriptores."""
from __future__ import annotations

from abc import ABC, abstractmethod


class Suscriptor(ABC):
    """<<Observer>>: cualquier interesado en un evento implementa actualizar()."""

    @abstractmethod
    def actualizar(self, evento: str, datos: dict) -> None: ...


class PublicadorEventos:
    """<<Subject>>: los suscriptores se registran por nombre de evento y reciben los datos al publicarse."""

    def __init__(self):
        self._suscriptores: dict[str, list[Suscriptor]] = {}

    def suscribir(self, evento: str, suscriptor: Suscriptor) -> None:
        self._suscriptores.setdefault(evento, []).append(suscriptor)

    def publicar(self, evento: str, datos: dict) -> None:
        for suscriptor in self._suscriptores.get(evento, []):
            suscriptor.actualizar(evento, datos)
