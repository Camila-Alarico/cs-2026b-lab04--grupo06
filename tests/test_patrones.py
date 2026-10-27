"""E2-E5: pruebas que demuestran cada patrón sobre la versión con patrones."""
from datetime import datetime, timedelta

import pytest

from rutasit.algoritmos_eta import AlgoritmoEta, DistanciaDirecta, VelocidadPromedio
from rutasit.dominio import Bus, EstadoEta, Paradero, ParaderoDeRuta, PosicionGPS, Ruta
from rutasit.estados import EstadoViaje
from rutasit.externos import GpsOperadorA, GpsOperadorB
from rutasit.fabricas import Fabrica, fabrica_algoritmos_por_defecto, fabrica_gps_por_defecto
from rutasit.eventos import PublicadorEventos, Suscriptor
from rutasit.gps import ConReintentos, FuenteGps, OperadorAAdapter, OperadorBAdapter
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


# ---------- State ----------
OPERACIONES = {
    "iniciar": EstadoViaje.EN_RUTA,
    "marcar_desviado": EstadoViaje.DESVIADO,
    "marcar_detenido": EstadoViaje.DETENIDO,
    "reanudar": EstadoViaje.EN_RUTA,
    "finalizar": EstadoViaje.FINALIZADO,
}
# Las 8 transiciones de estados-viaje.mmd: estado -> operaciones permitidas
PERMITIDAS = {
    EstadoViaje.PROGRAMADO: {"iniciar"},
    EstadoViaje.EN_RUTA: {"marcar_desviado", "marcar_detenido", "finalizar"},
    EstadoViaje.DESVIADO: {"reanudar", "finalizar"},
    EstadoViaje.DETENIDO: {"reanudar", "finalizar"},
    EstadoViaje.FINALIZADO: set(),
}
CAMINO = {
    EstadoViaje.PROGRAMADO: [],
    EstadoViaje.EN_RUTA: ["iniciar"],
    EstadoViaje.DESVIADO: ["iniciar", "marcar_desviado"],
    EstadoViaje.DETENIDO: ["iniciar", "marcar_detenido"],
    EstadoViaje.FINALIZADO: ["iniciar", "finalizar"],
}


def viaje_en(estado):
    v = Viaje("V1", ruta(), Bus("ABC-123"))
    for operacion in CAMINO[estado]:
        getattr(v, operacion)()
    assert v.estado == estado
    return v


@pytest.mark.parametrize("operacion", list(OPERACIONES))
@pytest.mark.parametrize("estado", list(EstadoViaje))
def test_state_impide_transiciones_invalidas(estado, operacion):
    v = viaje_en(estado)
    if operacion in PERMITIDAS[estado]:
        getattr(v, operacion)()
        assert v.estado == OPERACIONES[operacion]
    else:
        with pytest.raises(ValueError):
            getattr(v, operacion)()
        assert v.estado == estado  # una transición inválida no cambia el estado


# ---------- Decorator: ConReintentos ----------
class FuenteFalsa(FuenteGps):
    def __init__(self, fallas=0, error=TimeoutError):
        self.fallas, self.error, self.llamadas = fallas, error, 0

    def leer(self, placa):
        self.llamadas += 1
        if self.llamadas <= self.fallas:
            raise self.error("falla simulada")
        return PosicionGPS(P1[0], P1[1], 20.0, AHORA)


def test_decorator_reintenta_ante_timeout_y_es_una_fuente_gps():
    interna = FuenteFalsa(fallas=2)
    fuente = ConReintentos(interna)
    assert isinstance(fuente, FuenteGps)
    assert fuente.leer("ABC-123").latitud == P1[0]
    assert interna.llamadas == 3


def test_decorator_relanza_timeout_al_agotar_los_intentos():
    interna = FuenteFalsa(fallas=5)
    with pytest.raises(TimeoutError):
        ConReintentos(interna, intentos=3).leer("ABC-123")
    assert interna.llamadas == 3


def test_decorator_no_reintenta_errores_que_no_son_timeout():
    interna = FuenteFalsa(fallas=1, error=ValueError)
    with pytest.raises(ValueError):
        ConReintentos(interna).leer("ABC-123")
    assert interna.llamadas == 1


# ---------- Observer ----------
class Auditoria(Suscriptor):
    def __init__(self):
        self.registro = []

    def actualizar(self, evento, datos):
        self.registro.append((evento, datos["id_viaje"]))


def lectura_desviada():
    return {"lat": -16.405, "lng": -71.520, "vel_kmh": 20.0, "ts": (AHORA - timedelta(seconds=5)).isoformat()}


def test_observer_el_desvio_notifica_a_operador_y_pasajeros():
    gps = GpsOperadorA()
    gps.lectura = lectura_desviada()
    s = servicio_en_ruta(gps_a=gps)
    for _ in range(3):
        s.actualizar_bus("V1", "OPERADOR_A")
    assert s.eventos == ["alerta_operador:V1:DESVIO", "alerta_pasajero:V1:DESVIO"]


def test_observer_nuevo_suscriptor_sin_tocar_el_servicio():
    auditoria = Auditoria()
    gps = GpsOperadorA()
    gps.lectura = lectura_desviada()
    s = servicio_en_ruta(gps_a=gps)
    s.publicador.suscribir("desvio_detectado", auditoria)
    for _ in range(3):
        s.actualizar_bus("V1", "OPERADOR_A")
    assert auditoria.registro == [("desvio_detectado", "V1")]


def test_observer_publicador_sin_suscriptores_no_falla_y_notifica_a_todos():
    publicador = PublicadorEventos()
    publicador.publicar("nada", {"id_viaje": "V1"})  # sin suscriptores: no pasa nada
    a, b = Auditoria(), Auditoria()
    publicador.suscribir("x", a)
    publicador.suscribir("x", b)
    publicador.publicar("x", {"id_viaje": "V1"})
    assert a.registro == b.registro == [("x", "V1")]
