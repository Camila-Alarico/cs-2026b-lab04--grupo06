"""Patrón State para el ciclo de vida del Viaje (Lab 07, E3). Implementa estados-viaje.mmd del Lab 05.

La clase base prohíbe TODAS las transiciones; cada estado redefine SOLO las permitidas por el diagrama.
No usa el nombre de otros estados en condicionales: cada estado decide a cuál pasa.
"""
from __future__ import annotations

from enum import Enum


class EstadoViaje(Enum):
    """Enumeración del Lab 05 (C2): los 5 estados del diagrama. Es el valor que ve el resto del sistema."""
    PROGRAMADO = "Programado"
    EN_RUTA = "EnRuta"
    DESVIADO = "Desviado"
    DETENIDO = "Detenido"
    FINALIZADO = "Finalizado"


class EstadoDeViaje:
    """<<State>>: comportamiento del viaje según su estado. Por defecto toda transición es inválida."""
    estado: EstadoViaje

    def _prohibido(self, accion: str):
        raise ValueError(f"No se puede {accion} un viaje {self.estado.value}")

    # --- transiciones del diagrama (una operación de Viaje cada una, regla C2) ---
    def iniciar(self, viaje) -> None:
        self._prohibido("iniciar")

    def marcar_desviado(self, viaje) -> None:
        self._prohibido("marcar como desviado")

    def marcar_detenido(self, viaje) -> None:
        self._prohibido("marcar como detenido")

    def reanudar(self, viaje) -> None:
        self._prohibido("reanudar")

    def finalizar(self, viaje) -> None:
        self._prohibido("finalizar")

    # --- consultas y comportamiento que dependen del estado ---
    def esta_en_ruta(self) -> bool:
        return False

    def en_curso(self) -> bool:
        """True si el viaje acepta posiciones GPS (EnRuta, Desviado, Detenido)."""
        return False

    def procesar_lectura(self, viaje, lectura, fuera_de_ruta: bool,
                         lecturas_para_desvio: int, segundos_para_detencion: int) -> list[str]:
        """Reacciona a una lectura GPS. Devuelve los tipos de alerta generados ('DESVIO', 'DETENCION')."""
        return []


class Programado(EstadoDeViaje):
    estado = EstadoViaje.PROGRAMADO

    def iniciar(self, viaje) -> None:
        viaje.cambiar_a(EnRuta())


class EnRuta(EstadoDeViaje):
    estado = EstadoViaje.EN_RUTA

    def marcar_desviado(self, viaje) -> None:
        viaje.cambiar_a(Desviado())

    def marcar_detenido(self, viaje) -> None:
        viaje.cambiar_a(Detenido())

    def finalizar(self, viaje) -> None:
        viaje.cambiar_a(Finalizado())

    def esta_en_ruta(self) -> bool:
        return True

    def en_curso(self) -> bool:
        return True

    def procesar_lectura(self, viaje, lectura, fuera_de_ruta, lecturas_para_desvio, segundos_para_detencion):
        if viaje.lecturas_fuera_de_ruta >= lecturas_para_desvio:
            viaje.marcar_desviado()
            return ["DESVIO"]
        if lectura.velocidad == 0:
            if viaje.detenido_desde is None:
                viaje.detenido_desde = lectura.marca_tiempo
            elif (lectura.marca_tiempo - viaje.detenido_desde).total_seconds() >= segundos_para_detencion:
                viaje.marcar_detenido()
                return ["DETENCION"]
        else:
            viaje.detenido_desde = None
        return []


class Desviado(EstadoDeViaje):
    estado = EstadoViaje.DESVIADO

    def reanudar(self, viaje) -> None:
        viaje.lecturas_fuera_de_ruta = 0
        viaje.cambiar_a(EnRuta())

    def finalizar(self, viaje) -> None:
        viaje.cambiar_a(Finalizado())

    def en_curso(self) -> bool:
        return True

    def procesar_lectura(self, viaje, lectura, fuera_de_ruta, lecturas_para_desvio, segundos_para_detencion):
        if not fuera_de_ruta:
            viaje.reanudar()
        return []


class Detenido(EstadoDeViaje):
    estado = EstadoViaje.DETENIDO

    def reanudar(self, viaje) -> None:
        viaje.detenido_desde = None
        viaje.cambiar_a(EnRuta())

    def finalizar(self, viaje) -> None:
        viaje.cambiar_a(Finalizado())

    def en_curso(self) -> bool:
        return True

    def procesar_lectura(self, viaje, lectura, fuera_de_ruta, lecturas_para_desvio, segundos_para_detencion):
        if lectura.velocidad > 0:
            viaje.reanudar()
        return []


class Finalizado(EstadoDeViaje):
    """Estado final: no permite ninguna transición."""
    estado = EstadoViaje.FINALIZADO
