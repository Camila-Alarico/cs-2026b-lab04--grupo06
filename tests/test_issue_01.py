"""Issue 01: un GPS sin datos hace fallar actualizar_bus (ISSUE-01.md)."""
from datetime import datetime

import pytest

from rutasit.dominio import Bus, Paradero, ParaderoDeRuta, Ruta
from rutasit.estados import EstadoViaje
from rutasit.externos import GpsOperadorA, GpsOperadorB
from rutasit.servicio import ServicioRutaSIT, Viaje

AHORA = datetime(2026, 11, 20, 8, 0, 0)


def servicio_en_ruta(**kw):
    ruta = Ruta("R1", "Ruta 1", [ParaderoDeRuta(1, Paradero("P1", "Paradero 1", -16.400, -71.530)),
                                 ParaderoDeRuta(2, Paradero("P2", "Paradero 2", -16.410, -71.530))])
    s = ServicioRutaSIT(reloj=lambda: AHORA, **kw)
    s.registrar_viaje(Viaje("V1", ruta, Bus("ABC-123")))
    s.iniciar_viaje("V1")
    return s


@pytest.mark.parametrize("operador, kw", [("OPERADOR_A", {"gps_a": GpsOperadorA()}),
                                          ("OPERADOR_B", {"gps_b": GpsOperadorB()})])
def test_issue_01_gps_sin_datos_publica_sin_senal_y_no_falla(operador, kw):
    s = servicio_en_ruta(**kw)  # el SDK simulado responde None: el operador no tiene lectura
    assert s.actualizar_bus("V1", operador) == EstadoViaje.EN_RUTA
    assert s.eventos == ["sin_senal:V1"]
