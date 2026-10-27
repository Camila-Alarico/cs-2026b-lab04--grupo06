"""E2-E5: pruebas que demuestran cada patrón sobre la versión con patrones."""
from datetime import datetime, timedelta

import pytest

from rutasit.algoritmos_eta import AlgoritmoEta, DistanciaDirecta, VelocidadPromedio
from rutasit.dominio import Bus, EstadoEta, Paradero, ParaderoDeRuta, PosicionGPS, Ruta
from rutasit.externos import GpsOperadorA, GpsOperadorB
from rutasit.fabricas import Fabrica, fabrica_algoritmos_por_defecto, fabrica_gps_por_defecto
from rutasit.gps import FuenteGps, OperadorAAdapter, OperadorBAdapter
from rutasit.servicio import ServicioRutaSIT, Viaje

AHORA = datetime(2026, 10, 20, 8, 0, 0)
P1, P2 = (-16.400, -71.530), (-16.410, -71.530)


def ruta():
    return Ruta("R1", "Ruta 1", [ParaderoDeRuta(1, Paradero("P1", "Paradero 1", *P1)),
                                 ParaderoDeRuta(2, Paradero("P2", "Paradero 2", *P2))])


def servicio_en_ruta(**kw):
    s = ServicioRutaSIT(reloj=lambda: AHORA, **kw)
    s.registrar_viaje(Viaje("V1", ruta(), Bus("ABC-123")))
    s.iniciar_viaje("V1")
    return s


# ---------- Adapter ----------
def test_adapters_traducen_cada_sdk_a_la_misma_posicion():
    ts = AHORA - timedelta(seconds=5)
    a = GpsOperadorA()
    a.lectura = {"lat": -16.4, "lng": -71.53, "vel_kmh": 36.0, "ts": ts.isoformat()}
    b = GpsOperadorB()
    b.lectura = (-16_400_000, -71_530_000, 10.0, ts.timestamp())  # 10 m/s = 36 km/h
    pa, pb = OperadorAAdapter(a).leer("ABC-123"), OperadorBAdapter(b).leer("ABC-123")
    assert isinstance(pa, PosicionGPS)
    assert (pa.latitud, pa.longitud, round(pa.velocidad, 6), pa.marca_tiempo) == \
           (pb.latitud, pb.longitud, round(pb.velocidad, 6), pb.marca_tiempo)


# ---------- Factory (registro) ----------
def test_fabrica_rechaza_un_nombre_no_registrado():
    with pytest.raises(ValueError, match="OPERADOR_X"):
        fabrica_gps_por_defecto().crear("OPERADOR_X")
    with pytest.raises(ValueError, match="MAGICO"):
        fabrica_algoritmos_por_defecto().crear("MAGICO")


# ---------- Strategy ----------
@pytest.mark.parametrize("estrategia", [DistanciaDirecta(), VelocidadPromedio(20.0)])
def test_las_estrategias_son_sustituibles(estrategia):
    assert isinstance(estrategia, AlgoritmoEta)
    assert estrategia.segundos(1000.0, 0.0) > 0  # sin división por cero con el bus detenido


# ---------- Abierto/cerrado: variantes nuevas sin tocar el servicio ----------
class SdkOperadorC:
    """Un tercer operador con otra interfaz: posicion() -> (lat, lon, kph, hora ISO)."""

    def posicion(self, placa):
        return (P1[0], P1[1], 20.0, (AHORA - timedelta(seconds=5)).isoformat())


class OperadorCAdapter(FuenteGps):
    def __init__(self, sdk):
        self._sdk = sdk

    def leer(self, placa):
        lat, lon, kph, hora = self._sdk.posicion(placa)
        return PosicionGPS(lat, lon, kph, datetime.fromisoformat(hora))


class CincoMinutosFijos(AlgoritmoEta):
    def segundos(self, distancia_m, velocidad_kmh):
        return 300.0


def test_open_closed_nuevo_operador_gps_sin_modificar_el_servicio():
    fabrica = fabrica_gps_por_defecto()
    fabrica.registrar("OPERADOR_C", lambda: OperadorCAdapter(SdkOperadorC()))
    s = servicio_en_ruta(fabrica_gps=fabrica)
    s.actualizar_bus("V1", "OPERADOR_C")
    assert s.consultar_eta("V1", "P2").estado == EstadoEta.ACTUALIZADO


def test_open_closed_nuevo_algoritmo_eta_sin_modificar_el_servicio():
    fabrica = fabrica_algoritmos_por_defecto()
    fabrica.registrar("FIJO_5_MIN", CincoMinutosFijos)
    gps = GpsOperadorA()
    gps.lectura = {"lat": P1[0], "lng": P1[1], "vel_kmh": 20.0,
                   "ts": (AHORA - timedelta(seconds=5)).isoformat()}
    s = servicio_en_ruta(gps_a=gps, algoritmo="FIJO_5_MIN", fabrica_algoritmos=fabrica)
    s.actualizar_bus("V1", "OPERADOR_A")
    assert s.consultar_eta("V1", "P2").eta.minutos_estimados == 5