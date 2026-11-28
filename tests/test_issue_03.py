"""Issue 03: explicar_retraso mezcla los eventos de otro viaje (ISSUE-03.md)."""
from datetime import datetime

from rutasit.dominio import Bus, Paradero, ParaderoDeRuta, Ruta
from rutasit.servicio import ServicioRutaSIT, Viaje

AHORA = datetime(2026, 11, 20, 8, 0, 0)


class LlmEspia:
    """LLM simulado: guarda los prompts que recibe."""

    def __init__(self):
        self.prompts = []

    def predict(self, prompt):
        self.prompts.append(prompt)
        return "El bus se desvió de su ruta habitual."


def test_issue_03_explicar_retraso_no_mezcla_eventos_de_otro_viaje():
    ruta = Ruta("R1", "Ruta 1", [ParaderoDeRuta(1, Paradero("P1", "Paradero 1", -16.400, -71.530))])
    llm = LlmEspia()
    s = ServicioRutaSIT(llm_local=llm, reloj=lambda: AHORA)
    s.registrar_viaje(Viaje("V1", ruta, Bus("ABC-123")))
    s.registrar_viaje(Viaje("V10", ruta, Bus("XYZ-999")))

    s.eventos.append("sin_senal:V10")  # solo el viaje V10 tiene eventos
    assert s.explicar_retraso("V1", "LOCAL") == "No hay eventos registrados para este viaje"
    assert llm.prompts == []

    s.eventos.append("alerta_operador:V1:DESVIO")  # ahora V1 también tiene un evento propio
    assert s.explicar_retraso("V1", "LOCAL") == "El bus se desvió de su ruta habitual."
    assert "V10" not in llm.prompts[0]
