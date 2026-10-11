from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class EstadoViaje(Enum):
    PROGRAMADO = "Programado"
    EN_RUTA = "EnRuta"
    DESVIADO = "Desviado"
    DETENIDO = "Detenido"
    FINALIZADO = "Finalizado"


class EstadoEta(Enum):
    ACTUALIZADO = "Actualizado"
    DESACTUALIZADO = "Desactualizado"
    NO_DISPONIBLE = "NoDisponible"


@dataclass
class Paradero:
    codigo: str
    nombre: str
    latitud: float
    longitud: float


@dataclass
class ParaderoDeRuta:
    orden: int
    paradero: Paradero


@dataclass
class Ruta:
    codigo: str
    nombre: str
    paraderos: list[ParaderoDeRuta] = field(default_factory=list)

    def obtener_paraderos_ordenados(self) -> list[Paradero]:
        ordenados = sorted(self.paraderos, key=lambda p: p.orden)
        return [p.paradero for p in ordenados]


@dataclass
class Bus:
    placa: str


@dataclass
class PosicionGPS:
    latitud: float
    longitud: float
    velocidad: float
    marca_tiempo: datetime

    def antiguedad_segundos(self, ahora: datetime) -> int:
        return int((ahora - self.marca_tiempo).total_seconds())

    def es_reciente(self, ahora: datetime, umbral_antiguedad_segundos: int) -> bool:
        return self.antiguedad_segundos(ahora) <= umbral_antiguedad_segundos

@dataclass
class Viaje:
    id: str
    ruta: Ruta
    bus: Bus
    estado: EstadoViaje = EstadoViaje.PROGRAMADO
    posiciones: list[PosicionGPS] = field(default_factory=list)

    def esta_en_ruta(self) -> bool:
        return self.estado == EstadoViaje.EN_RUTA

    def iniciar(self) -> None:
        self.estado = EstadoViaje.EN_RUTA

    def marcar_desviado(self) -> None:
        self.estado = EstadoViaje.DESVIADO

    def marcar_detenido(self) -> None:
        self.estado = EstadoViaje.DETENIDO

    def reanudar(self) -> None:
        self.estado = EstadoViaje.EN_RUTA

    def finalizar(self) -> None:
        self.estado = EstadoViaje.FINALIZADO


@dataclass
class Eta:
    minutos_estimados: int
    hora_calculo: datetime


@dataclass
class ResultadoEta:
    estado: EstadoEta
    mensaje: str
    eta: Eta | None = None


class RepositorioViajes(ABC):
    @abstractmethod
    def buscar_por_id(self, id_viaje: str) -> Viaje | None: ...


class RepositorioPosiciones(ABC):
    @abstractmethod
    def guardar_posicion(self, id_viaje: str, posicion: PosicionGPS) -> None: ...

    @abstractmethod
    def obtener_ultima_posicion(self, id_viaje: str) -> PosicionGPS | None: ...


class RepositorioEta(ABC):
    @abstractmethod
    def guardar_eta(self, id_viaje: str, codigo_paradero: str, eta: Eta) -> None: ...

    @abstractmethod
    def obtener_ultimo_eta(self, id_viaje: str, codigo_paradero: str) -> Eta | None: ...


class RegistroMetricas(ABC):
    @abstractmethod
    def registrar(self, nombre: str, valor: int) -> None: ...


class RepositorioPosicionesPostgres(RepositorioPosiciones):
    def guardar_posicion(self, id_viaje: str, posicion: PosicionGPS) -> None:
        raise NotImplementedError("Integrar con PostgreSQL")

    def obtener_ultima_posicion(self, id_viaje: str) -> PosicionGPS | None:
        raise NotImplementedError("Integrar con PostgreSQL")


class ServicioEta:
    def __init__(
        self,
        repositorio_viajes: RepositorioViajes,
        repositorio_posiciones: RepositorioPosiciones,
        repositorio_eta: RepositorioEta,
        registro_metricas: RegistroMetricas,
        umbral_antiguedad_segundos: int = 30,
    ) -> None:
        self.repositorio_viajes = repositorio_viajes
        self.repositorio_posiciones = repositorio_posiciones
        self.repositorio_eta = repositorio_eta
        self.registro_metricas = registro_metricas
        self.umbral_antiguedad_segundos = umbral_antiguedad_segundos

    def consultar_eta(self, id_viaje: str, codigo_paradero: str) -> ResultadoEta:
        viaje = self.repositorio_viajes.buscar_por_id(id_viaje)
        if viaje is None or not viaje.esta_en_ruta():
            return ResultadoEta(EstadoEta.NO_DISPONIBLE, "No hay ETA disponible para este viaje")
        posicion = self.repositorio_posiciones.obtener_ultima_posicion(id_viaje)
        eta = self.repositorio_eta.obtener_ultimo_eta(id_viaje, codigo_paradero)
        if posicion is None or eta is None:
            return ResultadoEta(EstadoEta.NO_DISPONIBLE, "Aún no hay datos para este paradero")
        ahora = datetime.now()
        antiguedad = posicion.antiguedad_segundos(ahora)
        self.registro_metricas.registrar("antiguedad_posicion_s", antiguedad)
        if posicion.es_reciente(ahora, self.umbral_antiguedad_segundos):
            return ResultadoEta(EstadoEta.ACTUALIZADO, "ETA vigente", eta)
        return ResultadoEta(EstadoEta.DESACTUALIZADO, "Dato desactualizado", eta)

    def recalcular_eta(self, id_viaje: str, posicion: PosicionGPS) -> None:
        raise NotImplementedError("Algoritmo de ETA pendiente (proyección sobre la ruta)")

@dataclass
class Alerta:
    id_viaje: str
    tipo: str
    hora_generacion: datetime


class RepositorioAlertas(ABC):
    @abstractmethod
    def guardar(self, alerta: Alerta) -> None: ...


class ServicioAlertas:
    def __init__(
        self,
        repositorio_alertas: RepositorioAlertas,
        umbral_desvio_metros: float,
        lecturas_para_desvio: int,
        segundos_para_detencion: int,
    ) -> None:
        self.repositorio_alertas = repositorio_alertas
        self.umbral_desvio_metros = umbral_desvio_metros
        self.lecturas_para_desvio = lecturas_para_desvio
        self.segundos_para_detencion = segundos_para_detencion

    def evaluar_posicion(self, viaje: Viaje, posicion: PosicionGPS) -> None:
        raise NotImplementedError("Cálculo de distancia a la ruta pendiente")

    def registrar_alerta(self, id_viaje: str, tipo: str) -> Alerta:
        alerta = Alerta(id_viaje, tipo, datetime.now())
        self.repositorio_alertas.guardar(alerta)
        return alerta