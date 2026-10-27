"""E1: pruebas de caracterización. Describen lo que el sistema hace hoy (comportamiento observable)."""
import importlib
from datetime import datetime, timedelta

import pytest

from rutasit.externos import GpsOperadorA, GpsOperadorB, LlmLocalSDK, LlmNubeSDK

AHORA = datetime(2026, 10, 20, 8, 0, 0)
# Ruta de 3 paraderos alineados sobre un meridiano (~1,1 km entre paraderos)
P1, P2, P3 = (-16.400, -71.530), (-16.410, -71.530), (-16.420, -71.530)


@pytest.fixture(params=["rutasit.antes.servicio", "rutasit.servicio"])
def m(request):
    return importlib.import_module(request.param)


def ruta(m):
    paraderos = [m.ParaderoDeRuta(i + 1, m.Paradero(f"P{i + 1}", f"Paradero {i + 1}", lat, lon))
                 for i, (lat, lon) in enumerate([P1, P2, P3])]
    return m.Ruta("R1", "Ruta 1", paraderos)


def servicio(m, **kw):
    return m.ServicioRutaSIT(reloj=lambda: AHORA, **kw)


def viaje_en_ruta(m, s):
    v = m.Viaje("V1", ruta(m), m.Bus("ABC-123"))
    s.registrar_viaje(v)
    s.iniciar_viaje("V1")
    return v


def lectura_a(lat, lon, vel_kmh=20.0, antiguedad_s=5):
    ts = AHORA - timedelta(seconds=antiguedad_s)
    return {"lat": lat, "lng": lon, "vel_kmh": vel_kmh, "ts": ts.isoformat()}


def lectura_b(lat, lon, vel_kmh=20.0, antiguedad_s=5):
    ts = AHORA - timedelta(seconds=antiguedad_s)
    return (round(lat * 1e6), round(lon * 1e6), vel_kmh / 3.6, ts.timestamp())


def servicio_con_gps_a(m, gps=None, **kw):
    gps = gps or GpsOperadorA()
    return servicio(m, gps_a=gps, **kw), gps


# ---------- ciclo de vida del viaje ----------
def test_iniciar_viaje_programado_pasa_a_en_ruta(m):
    s = servicio(m)
    v = m.Viaje("V1", ruta(m), m.Bus("ABC-123"))
    s.registrar_viaje(v)
    s.iniciar_viaje("V1")
    assert v.estado == m.EstadoViaje.EN_RUTA


def test_no_se_puede_iniciar_un_viaje_ya_iniciado(m):
    s = servicio(m)
    viaje_en_ruta(m, s)
    with pytest.raises(ValueError):
        s.iniciar_viaje("V1")


def test_finalizar_viaje_en_ruta_y_no_dos_veces(m):
    s = servicio(m)
    v = viaje_en_ruta(m, s)
    s.finalizar_viaje("V1")
    assert v.estado == m.EstadoViaje.FINALIZADO
    with pytest.raises(ValueError):
        s.finalizar_viaje("V1")


# ---------- ingesta GPS de dos operadores y ETA (HU-01) ----------
def test_posicion_del_operador_a_genera_eta_actualizado(m):
    s, gps = servicio_con_gps_a(m)
    viaje_en_ruta(m, s)
    gps.lectura = lectura_a(*P1)
    s.actualizar_bus("V1", "OPERADOR_A")
    r = s.consultar_eta("V1", "P2")
    assert r.estado == m.EstadoEta.ACTUALIZADO
    assert r.eta.minutos_estimados == 3  # 1,1 km a 20 km/h


def test_operador_b_con_otras_unidades_da_el_mismo_eta(m):
    sa, gps_a = servicio_con_gps_a(m)
    sb = servicio(m, gps_b=GpsOperadorB())
    viaje_en_ruta(m, sa)
    viaje_en_ruta(m, sb)
    gps_a.lectura = lectura_a(*P1)
    sb.gps_b.lectura = lectura_b(*P1)
    sa.actualizar_bus("V1", "OPERADOR_A")
    sb.actualizar_bus("V1", "OPERADOR_B")
    assert sb.consultar_eta("V1", "P2").eta.minutos_estimados == sa.consultar_eta("V1", "P2").eta.minutos_estimados


def test_reintenta_tras_dos_timeouts(m):
    s, gps = servicio_con_gps_a(m, GpsOperadorA(fallas=2))
    viaje_en_ruta(m, s)
    gps.lectura = lectura_a(*P1)
    s.actualizar_bus("V1", "OPERADOR_A")
    assert gps.llamadas == 3
    assert s.consultar_eta("V1", "P2").estado == m.EstadoEta.ACTUALIZADO


def test_tres_timeouts_registran_sin_senal_y_no_hay_eta(m):
    s, gps = servicio_con_gps_a(m, GpsOperadorA(fallas=3))
    viaje_en_ruta(m, s)
    gps.lectura = lectura_a(*P1)
    s.actualizar_bus("V1", "OPERADOR_A")
    assert gps.llamadas == 3
    assert "sin_senal:V1" in s.eventos
    assert s.consultar_eta("V1", "P2").estado == m.EstadoEta.NO_DISPONIBLE


def test_operador_no_soportado_lanza_error(m):
    s = servicio(m)
    viaje_en_ruta(m, s)
    with pytest.raises(ValueError):
        s.actualizar_bus("V1", "OPERADOR_X")


def test_posicion_de_mas_de_30_segundos_da_eta_desactualizado(m):
    s, gps = servicio_con_gps_a(m)
    viaje_en_ruta(m, s)
    gps.lectura = lectura_a(*P1, antiguedad_s=45)
    s.actualizar_bus("V1", "OPERADOR_A")
    assert s.consultar_eta("V1", "P2").estado == m.EstadoEta.DESACTUALIZADO


def test_viaje_no_en_ruta_no_muestra_eta(m):
    s, gps = servicio_con_gps_a(m)
    v = viaje_en_ruta(m, s)
    gps.lectura = lectura_a(*P1)
    s.actualizar_bus("V1", "OPERADOR_A")
    s.finalizar_viaje("V1")
    assert v.estado == m.EstadoViaje.FINALIZADO
    assert s.consultar_eta("V1", "P2").estado == m.EstadoEta.NO_DISPONIBLE


def test_algoritmo_promedio_y_algoritmo_desconocido(m):
    s, gps = servicio_con_gps_a(m, algoritmo="PROMEDIO", velocidad_promedio_kmh=10.0)
    viaje_en_ruta(m, s)
    gps.lectura = lectura_a(*P1, vel_kmh=40.0)
    s.actualizar_bus("V1", "OPERADOR_A")
    assert s.consultar_eta("V1", "P2").eta.minutos_estimados == 7  # 1,1 km a 10 km/h
    malo, gps2 = servicio_con_gps_a(m, algoritmo="MAGICO")
    viaje_en_ruta(m, malo)
    gps2.lectura = lectura_a(*P1)
    with pytest.raises(ValueError):
        malo.actualizar_bus("V1", "OPERADOR_A")


def test_algoritmo_desconocido_no_altera_el_viaje(m, request):
    if m.__name__.endswith("antes.servicio"):
        request.applymarker(pytest.mark.xfail(
            strict=True, reason="Bug de la versión antes: guarda la posición y recién después falla"))
    s, gps = servicio_con_gps_a(m, algoritmo="MAGICO")
    v = viaje_en_ruta(m, s)
    gps.lectura = lectura_a(*P1)
    with pytest.raises(ValueError):
        s.actualizar_bus("V1", "OPERADOR_A")
    assert v.ultima_posicion is None


# ---------- desvío, detención y reanudación (RF-05, RF-04) ----------
def test_tres_lecturas_fuera_de_ruta_marcan_desviado_y_alertan(m):
    s, gps = servicio_con_gps_a(m)
    v = viaje_en_ruta(m, s)
    gps.lectura = lectura_a(-16.405, -71.520)  # ~1 km al este de la ruta
    for _ in range(3):
        s.actualizar_bus("V1", "OPERADOR_A")
    assert v.estado == m.EstadoViaje.DESVIADO
    assert "alerta_operador:V1:DESVIO" in s.eventos
    assert "alerta_pasajero:V1:DESVIO" in s.eventos
    assert s.consultar_eta("V1", "P2").estado == m.EstadoEta.NO_DISPONIBLE


def test_desviado_vuelve_a_en_ruta_al_regresar_a_la_ruta(m):
    s, gps = servicio_con_gps_a(m)
    v = viaje_en_ruta(m, s)
    gps.lectura = lectura_a(-16.405, -71.520)
    for _ in range(3):
        s.actualizar_bus("V1", "OPERADOR_A")
    gps.lectura = lectura_a(*P2)
    s.actualizar_bus("V1", "OPERADOR_A")
    assert v.estado == m.EstadoViaje.EN_RUTA


def test_detenido_tras_60_segundos_sin_moverse_y_reanuda(m):
    s, gps = servicio_con_gps_a(m)
    v = viaje_en_ruta(m, s)
    gps.lectura = lectura_a(*P2, vel_kmh=0.0, antiguedad_s=90)
    s.actualizar_bus("V1", "OPERADOR_A")
    assert v.estado == m.EstadoViaje.EN_RUTA
    gps.lectura = lectura_a(*P2, vel_kmh=0.0, antiguedad_s=20)
    s.actualizar_bus("V1", "OPERADOR_A")
    assert v.estado == m.EstadoViaje.DETENIDO
    assert "alerta_operador:V1:DETENCION" in s.eventos
    gps.lectura = lectura_a(*P2, vel_kmh=15.0, antiguedad_s=5)
    s.actualizar_bus("V1", "OPERADOR_A")
    assert v.estado == m.EstadoViaje.EN_RUTA


def test_suscriptor_recibe_aviso_cuando_el_eta_es_cercano(m):
    s, gps = servicio_con_gps_a(m)
    viaje_en_ruta(m, s)
    s.suscribir("P2", "tok-anonimo-1")
    gps.lectura = lectura_a(-16.408, -71.530)  # ~220 m de P2
    s.actualizar_bus("V1", "OPERADOR_A")
    assert s.eventos == ["push:tok-anonimo-1:Bus ABC-123 llega a Paradero 2 en 1 min"]


# ---------- IA: explicar el motivo de un retraso ----------
def servicio_con_eventos(m, **kw):
    s = servicio(m, **kw)
    viaje_en_ruta(m, s)
    s.eventos.append("alerta_operador:V1:DESVIO")
    return s


def test_explicacion_valida_con_cualquier_proveedor(m):
    texto = "El bus se desvió de su ruta habitual."
    assert servicio_con_eventos(m, llm_nube=LlmNubeSDK(texto)).explicar_retraso("V1", "NUBE") == texto
    assert servicio_con_eventos(m, llm_local=LlmLocalSDK(texto)).explicar_retraso("V1", "LOCAL") == texto


@pytest.mark.parametrize("texto", [
    "El bus llegará a las 08:15 sin falta.",
    "Se retrasó por culpa del conductor.",
    "x" * 281,
])
def test_guardrails_bloquean_respuestas_invalidas(m, texto):
    s = servicio_con_eventos(m, llm_local=LlmLocalSDK(texto))
    with pytest.raises(ValueError):
        s.explicar_retraso("V1", "LOCAL")


def test_proveedor_ia_no_soportado_lanza_error(m):
    with pytest.raises(ValueError):
        servicio_con_eventos(m).explicar_retraso("V1", "OTRO")
