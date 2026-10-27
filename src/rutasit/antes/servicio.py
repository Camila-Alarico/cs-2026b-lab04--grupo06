"""VERSIÓN ANTES (ingenua): flujo crítico de RutaSIT con condicionales. Se conserva para comparar (Lab 07, E1)."""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime

from rutasit.dominio import (Bus, Eta, EstadoEta, EstadoViaje, Paradero, ParaderoDeRuta,  # noqa: F401
                             PosicionGPS, ResultadoEta, Ruta)
from rutasit.geo import distancia_a_ruta_m, distancia_m


@dataclass
class Viaje:
    id: str
    ruta: Ruta
    bus: Bus
    estado: EstadoViaje = EstadoViaje.PROGRAMADO
    ultima_posicion: PosicionGPS | None = None
    lecturas_fuera_de_ruta: int = 0
    detenido_desde: datetime | None = None


class ServicioRutaSIT:
    def __init__(self, gps_a=None, gps_b=None, llm_nube=None, llm_local=None, algoritmo="DIRECTO",
                 reloj=datetime.now, umbral_antiguedad_segundos=30, umbral_desvio_metros=100.0,
                 lecturas_para_desvio=3, segundos_para_detencion=60, velocidad_promedio_kmh=20.0,
                 minutos_aviso=3):
        self.gps_a, self.gps_b = gps_a, gps_b
        self.llm_nube, self.llm_local = llm_nube, llm_local
        self.algoritmo = algoritmo
        self.reloj = reloj
        self.umbral_antiguedad_segundos = umbral_antiguedad_segundos
        self.umbral_desvio_metros = umbral_desvio_metros
        self.lecturas_para_desvio = lecturas_para_desvio
        self.segundos_para_detencion = segundos_para_detencion
        self.velocidad_promedio_kmh = velocidad_promedio_kmh
        self.minutos_aviso = minutos_aviso
        self.viajes: dict[str, Viaje] = {}
        self.etas: dict[tuple[str, str], Eta] = {}
        self.suscripciones: dict[str, list[str]] = {}
        self.eventos: list[str] = []
        self.metricas: list[tuple[str, int]] = []

    def registrar_viaje(self, viaje: Viaje) -> None:
        self.viajes[viaje.id] = viaje

    def suscribir(self, codigo_paradero: str, token: str) -> None:
        self.suscripciones.setdefault(codigo_paradero, []).append(token)

    def iniciar_viaje(self, id_viaje: str) -> None:
        viaje = self.viajes[id_viaje]
        if viaje.estado != EstadoViaje.PROGRAMADO:
            if viaje.estado == EstadoViaje.FINALIZADO:
                raise ValueError("El viaje ya finalizó")
            else:
                raise ValueError("El viaje ya está iniciado")
        viaje.estado = EstadoViaje.EN_RUTA

    def finalizar_viaje(self, id_viaje: str) -> None:
        viaje = self.viajes[id_viaje]
        if viaje.estado == EstadoViaje.PROGRAMADO:
            raise ValueError("No se puede finalizar un viaje programado")
        elif viaje.estado == EstadoViaje.FINALIZADO:
            raise ValueError("El viaje ya finalizó")
        viaje.estado = EstadoViaje.FINALIZADO

    def actualizar_bus(self, id_viaje: str, operador: str) -> EstadoViaje:
        viaje = self.viajes.get(id_viaje)
        if viaje is None:
            raise ValueError(f"El viaje no existe: {id_viaje}")
        if viaje.estado == EstadoViaje.PROGRAMADO or viaje.estado == EstadoViaje.FINALIZADO:
            raise ValueError("El viaje no está en curso")
        lectura = None
        if operador == "OPERADOR_A":
            for intento in range(3):
                try:
                    crudo = self.gps_a.ultima_lectura(viaje.bus.placa)
                    lectura = PosicionGPS(crudo["lat"], crudo["lng"], crudo["vel_kmh"],
                                          datetime.fromisoformat(crudo["ts"]))
                    break
                except TimeoutError:
                    if intento == 2:
                        lectura = None
        elif operador == "OPERADOR_B":
            for intento in range(3):
                try:
                    lat_e6, lon_e6, vel_ms, epoch = self.gps_b.leer(viaje.bus.placa)
                    lectura = PosicionGPS(lat_e6 / 1e6, lon_e6 / 1e6, vel_ms * 3.6,
                                          datetime.fromtimestamp(epoch))
                    break
                except TimeoutError:
                    if intento == 2:
                        lectura = None
        else:
            raise ValueError(f"Operador GPS no soportado: {operador}")
        if lectura is None:
            self.eventos.append(f"sin_senal:{viaje.id}")
            return viaje.estado
        viaje.ultima_posicion = lectura
        puntos = [(p.paradero.latitud, p.paradero.longitud) for p in viaje.ruta.paraderos]
        fuera = distancia_a_ruta_m(lectura.latitud, lectura.longitud, puntos) > self.umbral_desvio_metros
        viaje.lecturas_fuera_de_ruta = viaje.lecturas_fuera_de_ruta + 1 if fuera else 0
        if viaje.estado == EstadoViaje.EN_RUTA:
            if viaje.lecturas_fuera_de_ruta >= self.lecturas_para_desvio:
                viaje.estado = EstadoViaje.DESVIADO
                self.eventos.append(f"alerta_operador:{viaje.id}:DESVIO")
                self.eventos.append(f"alerta_pasajero:{viaje.id}:DESVIO")
            elif lectura.velocidad == 0:
                if viaje.detenido_desde is None:
                    viaje.detenido_desde = lectura.marca_tiempo
                elif (lectura.marca_tiempo - viaje.detenido_desde).total_seconds() >= self.segundos_para_detencion:
                    viaje.estado = EstadoViaje.DETENIDO
                    self.eventos.append(f"alerta_operador:{viaje.id}:DETENCION")
            else:
                viaje.detenido_desde = None
        elif viaje.estado == EstadoViaje.DESVIADO:
            if not fuera:
                viaje.estado = EstadoViaje.EN_RUTA
                viaje.lecturas_fuera_de_ruta = 0
        elif viaje.estado == EstadoViaje.DETENIDO:
            if lectura.velocidad > 0:
                viaje.estado = EstadoViaje.EN_RUTA
                viaje.detenido_desde = None
        if viaje.estado == EstadoViaje.EN_RUTA:
            for pr in viaje.ruta.paraderos:
                p = pr.paradero
                d = distancia_m(lectura.latitud, lectura.longitud, p.latitud, p.longitud)
                if self.algoritmo == "DIRECTO":
                    segundos = d / (max(lectura.velocidad, 5.0) / 3.6)
                elif self.algoritmo == "PROMEDIO":
                    segundos = d / (self.velocidad_promedio_kmh / 3.6)
                else:
                    raise ValueError(f"Algoritmo de ETA no soportado: {self.algoritmo}")
                minutos = int(round(segundos / 60))
                self.etas[(viaje.id, p.codigo)] = Eta(minutos, self.reloj())
                if minutos <= self.minutos_aviso:
                    for token in self.suscripciones.get(p.codigo, []):
                        self.eventos.append(f"push:{token}:Bus {viaje.bus.placa} llega a {p.nombre} en {minutos} min")
        return viaje.estado

    def consultar_eta(self, id_viaje: str, codigo_paradero: str) -> ResultadoEta:
        viaje = self.viajes.get(id_viaje)
        if viaje is None or viaje.estado != EstadoViaje.EN_RUTA:
            return ResultadoEta(EstadoEta.NO_DISPONIBLE, "No hay ETA disponible para este viaje")
        eta = self.etas.get((id_viaje, codigo_paradero))
        if viaje.ultima_posicion is None or eta is None:
            return ResultadoEta(EstadoEta.NO_DISPONIBLE, "Aún no hay datos para este paradero")
        antiguedad = viaje.ultima_posicion.antiguedad_segundos(self.reloj())
        self.metricas.append(("antiguedad_posicion_s", antiguedad))
        if antiguedad <= self.umbral_antiguedad_segundos:
            return ResultadoEta(EstadoEta.ACTUALIZADO, "ETA vigente", eta)
        return ResultadoEta(EstadoEta.DESACTUALIZADO, "Dato desactualizado", eta)

    def explicar_retraso(self, id_viaje: str, proveedor: str) -> str:
        viaje = self.viajes[id_viaje]
        eventos = [e for e in self.eventos if f":{id_viaje}" in e]
        if not eventos:
            return "No hay eventos registrados para este viaje"
        prompt = f"Explica en una frase el retraso del bus {viaje.bus.placa} según estos eventos: {eventos}"
        if proveedor == "NUBE":
            texto = self.llm_nube.generate(prompt)["texto"]
        elif proveedor == "LOCAL":
            texto = self.llm_local.predict(prompt)
        else:
            raise ValueError(f"Proveedor de IA no soportado: {proveedor}")
        if re.search(r"\d{1,2}:\d{2}", texto):
            raise ValueError("Guardrail: la IA inventó una hora")
        for palabra in ["conductor", "chofer", "culpa"]:
            if palabra in texto.lower():
                raise ValueError(f"Guardrail: atribución no permitida '{palabra}'")
        if len(texto) > 280:
            raise ValueError("Guardrail: respuesta demasiado larga")
        return texto