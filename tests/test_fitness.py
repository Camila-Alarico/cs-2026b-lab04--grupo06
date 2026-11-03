"""Fitness functions de calidad (Lab 08, E5): convierten los escenarios de calidad en pruebas.

FF-04 a FF-06 ejecutan las simulaciones de fitness/ con el margen de seguridad del 20 % exigido a cada táctica.
FF-07 usa el código real (Lab 07). Los supuestos de las simulaciones están escritos en cada módulo de fitness/.
"""
from datetime import datetime, timedelta

from fitness import consultas, recuperacion, rendimiento
from rutasit.dominio import Bus, EstadoEta, Paradero, ParaderoDeRuta, Ruta
from rutasit.servicio import ServicioRutaSIT, Viaje

MARGEN = 1.2  # los tiempos de servicio pueden empeorar un 20 % y el escenario debe seguir cumpliéndose


def test_ff04_qa01_eta_en_15_s_con_1200_buses():
    """QA-01: si alguien quita el histórico por lotes (V1), el margen cae a 1,08x y esta prueba falla."""
    variante = rendimiento.VARIANTES["V2 + histórico por lotes"]
    r = rendimiento.simular(**variante, factor=MARGEN)
    assert r["p95"] <= rendimiento.PRESUPUESTO_P95_MS, f"p95={r['p95']:.0f} ms excede el presupuesto de QA-01"


def test_ff05_qa04_consulta_en_1_s_con_50000_consultas_por_hora():
    """QA-04: si alguien quita a la vez el índice y la caché (C0), el margen baja a 1,12x y esta prueba falla.
    Quitar solo uno de los dos no la rompe (C1 y C2 tienen margen de 1,31x y 1,28x)."""
    variante = consultas.VARIANTES["C3 índice + caché (70 %)"]
    r = consultas.simular(**variante, factor=MARGEN)
    assert r["lectura_p95"] <= consultas.PRESUPUESTO_LECTURA_P95_MS, f"p95={r['lectura_p95']:.0f} ms"


def test_ff06_qa05_eta_al_dia_en_30_s_tras_reiniciar_el_servidor():
    """QA-05: si alguien vuelve al procesamiento FIFO de la ráfaga (R1), tarda 93 s y esta prueba falla."""
    variante = recuperacion.VARIANTES["R3 última posición primero + lotes"]
    r = recuperacion.simular(**variante)
    assert r["max"] <= recuperacion.PRESUPUESTO_RECUPERACION_S, f"máximo={r['max']:.0f} s"


class GpsPorPlaca:
    """GPS simulado: el bus BUS-0 no responde (timeout); los demás reportan con la hora indicada."""

    def __init__(self, reloj):
        self.reloj = reloj
        self.sin_senal = False

    def ultima_lectura(self, placa):
        if placa == "BUS-0" and self.sin_senal:
            raise TimeoutError("sin señal")
        return {"lat": -16.405, "lng": -71.530, "vel_kmh": 20.0,
                "ts": (self.reloj() - timedelta(seconds=5)).isoformat()}


def test_ff07_qa02_un_bus_sin_senal_no_afecta_a_los_otros_1199():
    """QA-02: el bus sin señal queda 'desactualizado' y los otros 1199 siguen 'actualizados', sin errores."""
    ahora = [datetime(2026, 11, 2, 8, 0, 0)]
    reloj = lambda: ahora[0]
    gps = GpsPorPlaca(reloj)
    ruta = Ruta("R1", "Ruta 1", [ParaderoDeRuta(1, Paradero("P1", "Paradero 1", -16.400, -71.530)),
                                 ParaderoDeRuta(2, Paradero("P2", "Paradero 2", -16.410, -71.530))])
    s = ServicioRutaSIT(gps_a=gps, reloj=reloj)
    for i in range(1200):
        s.registrar_viaje(Viaje(f"V{i}", ruta, Bus(f"BUS-{i}")))
        s.iniciar_viaje(f"V{i}")
        s.actualizar_bus(f"V{i}", "OPERADOR_A")
    ahora[0] += timedelta(seconds=40)          # pasan 40 s y BUS-0 deja de reportar
    gps.sin_senal = True
    for i in range(1200):
        s.actualizar_bus(f"V{i}", "OPERADOR_A")  # no debe lanzar excepciones
    assert s.consultar_eta("V0", "P2").estado == EstadoEta.DESACTUALIZADO
    estados = {s.consultar_eta(f"V{i}", "P2").estado for i in range(1, 1200)}
    assert estados == {EstadoEta.ACTUALIZADO}
    assert "sin_senal:V0" in s.eventos