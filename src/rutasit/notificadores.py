"""Suscriptores concretos (Lab 07, E4). Reciben datos simples (dict): no dependen de otros módulos.

Traza a RF-04 (alertas de desvío al pasajero), RF-05 (alertas al operador) y QA-02 (bus sin señal).
R-05: los pasajeros se identifican solo con un token anónimo; los buses, por su placa.
"""
from __future__ import annotations

from rutasit.eventos import PublicadorEventos, Suscriptor

# Nombres de eventos (los publica el servicio y los estados del viaje)
DESVIO_DETECTADO = "desvio_detectado"
DETENCION_DETECTADA = "detencion_detectada"
SIN_SENAL = "sin_senal"


def evento_eta_cercano(codigo_paradero: str) -> str:
    """Un tema por paradero: así un pasajero se suscribe a SU paradero."""
    return f"eta_cercano:{codigo_paradero}"


class NotificadorOperador(Suscriptor):
    _MENSAJES = {
        DESVIO_DETECTADO: "alerta_operador:{id}:DESVIO",
        DETENCION_DETECTADA: "alerta_operador:{id}:DETENCION",
        SIN_SENAL: "sin_senal:{id}",
    }

    def __init__(self, bandeja: list[str]):
        self._bandeja = bandeja

    def actualizar(self, evento: str, datos: dict) -> None:
        self._bandeja.append(self._MENSAJES[evento].format(id=datos["id_viaje"]))


class AvisoDesvioPasajeros(Suscriptor):
    def __init__(self, bandeja: list[str]):
        self._bandeja = bandeja

    def actualizar(self, evento: str, datos: dict) -> None:
        self._bandeja.append(f"alerta_pasajero:{datos['id_viaje']}:DESVIO")


class AvisoLlegadaPasajero(Suscriptor):
    """Un pasajero (token anónimo) suscrito a un paradero."""

    def __init__(self, token: str, bandeja: list[str]):
        self._token = token
        self._bandeja = bandeja

    def actualizar(self, evento: str, datos: dict) -> None:
        self._bandeja.append(
            f"push:{self._token}:Bus {datos['placa']} llega a {datos['nombre_paradero']} en {datos['minutos']} min")


def publicador_por_defecto(bandeja: list[str]) -> PublicadorEventos:
    publicador = PublicadorEventos()
    operador = NotificadorOperador(bandeja)
    for evento in (DESVIO_DETECTADO, DETENCION_DETECTADA, SIN_SENAL):
        publicador.suscribir(evento, operador)
    publicador.suscribir(DESVIO_DETECTADO, AvisoDesvioPasajeros(bandeja))
    return publicador
