"""Issue 02: el servicio calcula ETA y avisa por paraderos que el bus ya pasó (ISSUE-02.md)."""
from datetime import datetime, timedelta

from rutasit.dominio import Bus, EstadoEta, Paradero, ParaderoDeRuta, Ruta
from rutasit.externos import GpsOperadorA
from rutasit.servicio import ServicioRutaSIT, Viaje

AHORA = datetime(2026, 11, 20, 8, 0, 0)


def test_issue_02_no_hay_eta_ni_aviso_para_paraderos_ya_pasados():
    # Paraderos en línea recta, ~1,1 km entre cada uno. El bus va a 36 km/h, 167 m después de P2.
    ruta = Ruta("R1", "Ruta 1", [ParaderoDeRuta(1, Paradero("P1", "Paradero 1", -16.400, -71.530)),
                                 ParaderoDeRuta(2, Paradero("P2", "Paradero 2", -16.410, -71.530)),
                                 ParaderoDeRuta(3, Paradero("P3", "Paradero 3", -16.420, -71.530))])
    gps = GpsOperadorA()
    gps.lectura = {"lat": -16.4115, "lng": -71.530, "vel_kmh": 36.0,
                   "ts": (AHORA - timedelta(seconds=5)).isoformat()}
    s = ServicioRutaSIT(gps_a=gps, reloj=lambda: AHORA)
    s.registrar_viaje(Viaje("V1", ruta, Bus("ABC-123")))
    s.iniciar_viaje("V1")
    for paradero in ("P1", "P2", "P3"):
        s.suscribir(paradero, f"tok{paradero}")

    s.actualizar_bus("V1", "OPERADOR_A")

    assert s.consultar_eta("V1", "P1").estado == EstadoEta.NO_DISPONIBLE   # ya pasó
    assert s.consultar_eta("V1", "P2").estado == EstadoEta.NO_DISPONIBLE   # ya pasó
    assert s.consultar_eta("V1", "P3").estado == EstadoEta.ACTUALIZADO     # falta llegar
    avisos = [e for e in s.eventos if e.startswith("push:")]
    assert avisos == ["push:tokP3:Bus ABC-123 llega a Paradero 3 en 2 min"]
