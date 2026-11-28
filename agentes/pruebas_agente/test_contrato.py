"""E3: decisiones inválidas propias. Cada una debe ser rechazada por el contrato, nunca provocar una excepción."""
import pytest

from agente.contrato import validar_decision

H = {"listar_archivos", "leer_archivo", "buscar", "editar_archivo", "ejecutar_pruebas", "ejecutar_comando"}

INVALIDAS = [
    ({"pensamiento": "x", "accion": ["leer_archivo"]}, "acción como lista"),             # error hallado por estas pruebas
    ({"pensamiento": "x", "accion": {"nombre": "leer_archivo"}}, "acción como objeto"),   # idem
    ({"pensamiento": "x", "accion": 5}, "acción numérica"),
    ({"pensamiento": "x", "accion": ""}, "acción vacía"),
    ({"pensamiento": "x", "accion": "leer_archivo", "args": "a.py"}, "args como texto"),
    ({"pensamiento": "x", "accion": "leer_archivo", "args": None}, "args nulo"),
    ({"pensamiento": "x", "accion": "leer_archivo", "args": {}, "razon": "y"}, "campo de más"),
    ({"pensamiento": "x", "tool": "leer_archivo"}, "nombres de campo inventados"),
    ({"pensamiento": "x", "final": {"ok": True}}, "final que no es texto"),
    ({"pensamiento": 7, "final": "ok"}, "pensamiento que no es texto"),
    (None, "decisión nula"),
    (["leer_archivo"], "decisión como lista"),
    # Agregue aquí 1 o 2 respuestas inválidas reales que su asistente dio en E2 (cópielas de trayectorias/*.json)
]


@pytest.mark.parametrize("d, descripcion", INVALIDAS, ids=[x[1] for x in INVALIDAS])
def test_contrato_rechaza_sin_excepciones(d, descripcion):
    ok, motivo = validar_decision(d, H)
    assert ok is False and motivo
