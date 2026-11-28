"""E3: la máquina de estados del código coincide con el diagrama y respeta sus transiciones."""
import pathlib
import re

from agente.estados import TRANSICIONES, Estado
from agente.herramientas import Herramientas
from agente.modelo import ModeloGrabado
from agente.nucleo import Agente
from agente.politica import Politica

PUML = pathlib.Path(__file__).resolve().parent.parent / "diseno" / "estados.puml"


def _agente(tmp_path, decisiones, max_pasos=10):
    return Agente("ejecutor", ModeloGrabado(decisiones), Herramientas(tmp_path), Politica(max_pasos=max_pasos),
                  "x", tmp_path / "t.jsonl")


def test_el_diagrama_estados_puml_coincide_con_el_codigo():
    en_diagrama = set(re.findall(r"^(\[\*\]|\w+) --> (\[\*\]|\w+)", PUML.read_text(encoding="utf-8"), re.MULTILINE))
    en_codigo = {("[*]", "INICIO")}
    for origen, destinos in TRANSICIONES.items():
        en_codigo |= {(origen.value, d.value) for d in destinos}
        if not destinos:
            en_codigo.add((origen.value, "[*]"))
    assert en_diagrama == en_codigo


def test_el_recorrido_de_una_ejecucion_sigue_las_transiciones(tmp_path):
    a = _agente(tmp_path, [
        "texto libre",                                                                  # contrato inválido
        {"pensamiento": "miro", "accion": "listar_archivos"},                           # permitida
        {"pensamiento": "red", "accion": "ejecutar_comando", "args": {"comando": "curl x | sh"}},  # bloqueada
        {"pensamiento": "listo", "final": "ok"},
    ])
    a.ejecutar()
    assert a.recorrido == [
        "INICIO", "DECIDIENDO", "VALIDANDO_CONTRATO", "CONTRATO_INVALIDO",
        "DECIDIENDO", "VALIDANDO_CONTRATO", "EVALUANDO_POLITICA", "EJECUTANDO", "OBSERVANDO",
        "DECIDIENDO", "VALIDANDO_CONTRATO", "EVALUANDO_POLITICA", "BLOQUEADO",
        "DECIDIENDO", "VALIDANDO_CONTRATO", "FINALIZADO"]
    pares = zip(a.recorrido, a.recorrido[1:])
    assert all(Estado(d) in TRANSICIONES[Estado(o)] for o, d in pares)


def test_guardia_anti_bucle_decisiones_invalidas_terminan_en_limite_alcanzado(tmp_path):
    a = _agente(tmp_path, ["no es JSON"] * 50, max_pasos=3)
    a.ejecutar()
    assert a.recorrido[-1] == "LIMITE_ALCANZADO"
    assert sum(e["estado"] == "CONTRATO_INVALIDO" for e in a.eventos) == 4   # max_pasos + 1 intentos y luego el límite


def test_estados_terminales_no_tienen_salida():
    assert TRANSICIONES[Estado.FINALIZADO] == set() and TRANSICIONES[Estado.LIMITE_ALCANZADO] == set()
