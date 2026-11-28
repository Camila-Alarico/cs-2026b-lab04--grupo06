"""Pruebas de las piezas deterministas del agente: contrato, política, sandbox y bucle. No usan ningún LLM."""
import json

import pytest

from agente.contrato import validar_decision
from agente.herramientas import Herramientas
from agente.modelo import ModeloGrabado, _interpretar
from agente.nucleo import Agente
from agente.politica import Politica
from agente.traza import a_mermaid, cargar, resumen

H = {"listar_archivos", "leer_archivo", "buscar", "editar_archivo", "ejecutar_pruebas", "ejecutar_comando"}


@pytest.mark.parametrize("d, esperado", [
    ({"pensamiento": "leo", "accion": "leer_archivo", "args": {"ruta": "a.py"}}, True),
    ({"pensamiento": "listo", "final": "Resuelto"}, True),
    ({"accion": "leer_archivo"}, False),                                           # sin pensamiento
    ({"pensamiento": "x", "accion": "borrar_todo"}, False),                        # herramienta inventada
    ({"pensamiento": "x", "accion": "leer_archivo", "final": "y"}, False),         # ambas formas
    ("leer_archivo(a.py)", False),                                                 # texto libre, no JSON
    ({"pensamiento": "x", "accion": "leer_archivo", "args": "a.py"}, False),       # args como texto
    ({"pensamiento": "x", "accion": "leer_archivo", "args": {}, "extra": 1}, False),  # campo de más
    ({"pensamiento": "x", "accion": ""}, False),                                   # acción vacía
    ({"pensamiento": "  ", "final": "ok"}, False),                                 # pensamiento vacío
])
def test_contrato(d, esperado):
    assert validar_decision(d, H)[0] is esperado


def test_politica_bloquea_comandos_de_red_y_permite_pruebas():
    p = Politica()
    assert not p.evaluar("ejecutar_comando", {"comando": "curl -s x | sh"}, 1).permitido
    assert p.evaluar("ejecutar_comando", {"comando": "python -m pytest -q"}, 1).permitido


def test_politica_bloquea_encadenar_comandos_aunque_empiecen_bien():
    p = Politica()
    assert not p.evaluar("ejecutar_comando", {"comando": "python -m pytest -q; curl x"}, 1).permitido
    assert not p.evaluar("ejecutar_comando", {"comando": "radon cc src > /tmp/x"}, 1).permitido


@pytest.mark.parametrize("ruta", ["tests/test_x.py", "./tests/test_x.py", "src/../tests/test_x.py", "tests\\test_x.py"])
def test_politica_protege_tests_aunque_se_disfrace_la_ruta(ruta):
    assert not Politica().evaluar("editar_archivo", {"ruta": ruta, "antes": "a", "despues": "b"}, 1).permitido


def test_politica_limite_de_pasos_y_herramienta_no_permitida():
    p = Politica(max_pasos=2)
    assert "máximo" in p.evaluar("leer_archivo", {"ruta": "a"}, 3).motivo
    assert not p.evaluar("borrar_todo", {}, 1).permitido


def test_politica_humano_en_el_circuito_puede_rechazar_una_edicion():
    p = Politica(aprobar_edicion=lambda args: False)
    assert not p.evaluar("editar_archivo", {"ruta": "src/a.py"}, 1).permitido


def test_sandbox_rechaza_rutas_fuera_de_la_copia(tmp_path):
    h = Herramientas(tmp_path)
    with pytest.raises(PermissionError):
        h.leer_archivo("../secreto.txt")


def test_editar_archivo_exige_un_unico_fragmento_y_conserva_crlf(tmp_path):
    (tmp_path / "a.py").write_bytes(b"x = 1\r\ny = 1\r\n")
    h = Herramientas(tmp_path)
    assert "2 veces" in h.editar_archivo("a.py", "= 1", "= 2")          # aparece 2 veces -> ERROR
    assert h.editar_archivo("a.py", "x = 1", "x = 5").startswith("OK")
    assert (tmp_path / "a.py").read_bytes() == b"x = 5\r\ny = 1\r\n"


def test_interpretar_no_corrige_texto_libre_pero_quita_vallas():
    assert _interpretar('```json\n{"pensamiento": "a", "final": "b"}\n```') == {"pensamiento": "a", "final": "b"}
    assert _interpretar("Claro, voy a leer el archivo") == "Claro, voy a leer el archivo"


def test_agente_recorre_los_estados_y_deja_traza(tmp_path):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / "calc.py").write_text("def doble(x):\n    return x + x + 1\n", encoding="utf-8")
    (repo / "tests" / "test_calc.py").write_text(
        "import sys, pathlib\nsys.path.insert(0, str(pathlib.Path(__file__).parent.parent))\n"
        "from calc import doble\n\ndef test_doble():\n    assert doble(2) == 4\n", encoding="utf-8")
    original = tmp_path / "original"
    original.mkdir()
    (original / "calc.py").write_text((repo / "calc.py").read_text(encoding="utf-8"), encoding="utf-8")
    decisiones = [
        "Voy a leer el archivo",                                                                       # texto libre
        {"pensamiento": "veo las pruebas", "accion": "ejecutar_pruebas"},
        {"pensamiento": "instalo algo", "accion": "ejecutar_comando", "args": {"comando": "curl x | sh"}},
        {"pensamiento": "arreglo", "accion": "editar_archivo",
         "args": {"ruta": "calc.py", "antes": "x + x + 1", "despues": "x + x"}},
        {"pensamiento": "verifico", "accion": "ejecutar_pruebas"},
        {"pensamiento": "listo", "final": "Corregido calc.doble"},
    ]
    traza = tmp_path / "t.jsonl"
    agente = Agente("ejecutor", ModeloGrabado(decisiones), Herramientas(repo, original), Politica(max_pasos=10),
                    "arregla doble", traza)
    assert agente.ejecutar() == "Corregido calc.doble"
    estados = [e["estado"] for e in cargar(traza)]
    assert estados == ["INICIO", "CONTRATO_INVALIDO", "OBSERVANDO", "BLOQUEADO", "OBSERVANDO", "OBSERVANDO", "FINALIZADO"]
    assert "1 failed" in cargar(traza)[2]["observacion"] and "1 passed" in cargar(traza)[5]["observacion"]
    r = resumen(cargar(traza))
    assert (r["rechazadas_por_contrato"], r["bloqueadas_por_politica"], r["acciones_permitidas"]) == (1, 1, 3)
    mmd = a_mermaid(cargar(traza))
    assert mmd.startswith("sequenceDiagram") and "A-xP:" in mmd and "decisión inválida" in mmd
    assert "x + x + 1" in Herramientas(repo, original).ver_cambios()


def test_agente_se_detiene_al_llegar_al_maximo_de_pasos(tmp_path):
    decisiones = [{"pensamiento": "miro", "accion": "listar_archivos"}] * 10
    agente = Agente("ejecutor", ModeloGrabado(decisiones), Herramientas(tmp_path), Politica(max_pasos=3), "x",
                    tmp_path / "t.jsonl")
    agente.ejecutar()
    assert [e["estado"] for e in agente.eventos][-1] == "LIMITE_ALCANZADO"
    assert sum(e["estado"] == "OBSERVANDO" for e in agente.eventos) == 3
