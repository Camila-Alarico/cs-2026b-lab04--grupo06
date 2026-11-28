"""E6: humano en el circuito. Cada edición pasa por ESPERANDO_APROBACION y solo se acepta 's' o 'n'."""
import pytest

from agente.aprobacion import aprobar_por_consola
from agente.herramientas import Herramientas
from agente.modelo import ModeloGrabado
from agente.nucleo import Agente
from agente.politica import Politica
from agente.traza import a_mermaid, resumen

EDITAR = {"pensamiento": "arreglo", "accion": "editar_archivo",
          "args": {"ruta": "calc.py", "antes": "x + x + 1", "despues": "x + x"}}


def respuestas(*lineas):
    pendientes = iter(lineas)
    return lambda pregunta: next(pendientes)


def test_consola_solo_acepta_s_o_n_y_vuelve_a_preguntar():
    salida = []
    assert aprobar_por_consola({"ruta": "a.py"}, respuestas("si", "", "quizás", " S "), salida.append) is True
    assert salida.count("Responda solo 's' o 'n'.") == 3
    assert aprobar_por_consola({"ruta": "a.py"}, respuestas("x", "N"), lambda _: None) is False


def test_consola_muestra_la_edicion_antes_de_preguntar():
    salida = []
    aprobar_por_consola({"ruta": "src/a.py", "antes": "viejo", "despues": "nuevo"}, respuestas("s"), salida.append)
    texto = "\n".join(salida)
    assert "src/a.py" in texto and "viejo" in texto and "nuevo" in texto


@pytest.fixture
def repo(tmp_path):
    (tmp_path / "calc.py").write_text("def doble(x):\n    return x + x + 1\n", encoding="utf-8")
    return tmp_path


def _agente(repo, decisiones, aprobar):
    return Agente("ejecutor", ModeloGrabado(decisiones), Herramientas(repo), Politica(max_pasos=8, aprobar_edicion=aprobar),
                  "x", repo / "t.jsonl")


def test_edicion_aprobada_pasa_por_esperando_aprobacion_y_se_ejecuta(repo):
    a = _agente(repo, [EDITAR, {"pensamiento": "listo", "final": "ok"}], lambda args: True)
    a.ejecutar()
    assert a.recorrido[3:9] == ["EVALUANDO_POLITICA", "ESPERANDO_APROBACION", "EJECUTANDO", "OBSERVANDO",
                                 "DECIDIENDO", "VALIDANDO_CONTRATO"]
    assert "x + x\n" in (repo / "calc.py").read_text(encoding="utf-8")
    assert [e.get("humano") for e in a.eventos if e["tipo"] == "accion"] == ["aprobada"]


def test_edicion_rechazada_no_toca_el_archivo_y_vuelve_como_observacion(repo):
    a = _agente(repo, [EDITAR, {"pensamiento": "listo", "final": "ok"}], lambda args: False)
    a.ejecutar()
    assert a.recorrido[4:7] == ["ESPERANDO_APROBACION", "BLOQUEADO", "DECIDIENDO"]
    assert "x + x + 1" in (repo / "calc.py").read_text(encoding="utf-8")
    evento = [e for e in a.eventos if e["tipo"] == "accion"][0]
    assert evento["estado"] == "BLOQUEADO" and evento["humano"] == "rechazada"
    assert "El humano rechazó la edición" in a.historial[2]["content"]      # el modelo se entera
    r = resumen(a.eventos)
    assert (r["ediciones_aprobadas_por_humano"], r["ediciones_rechazadas_por_humano"]) == (0, 1)
    assert "U--xA: edición rechazada" in a_mermaid(a.eventos)


def test_el_humano_solo_se_consulta_para_ediciones_permitidas_por_la_politica(repo):
    consultas = []
    decisiones = [{"pensamiento": "miro", "accion": "listar_archivos"},                        # no es edición
                  {"pensamiento": "toco una prueba", "accion": "editar_archivo",               # ruta protegida
                   "args": {"ruta": "tests/test_x.py", "antes": "a", "despues": "b"}},
                  {"pensamiento": "listo", "final": "ok"}]
    _agente(repo, decisiones, lambda args: consultas.append(args) or True).ejecutar()
    assert consultas == []


def test_sin_aprobacion_configurada_no_hay_estado_de_espera(repo):
    a = _agente(repo, [EDITAR, {"pensamiento": "listo", "final": "ok"}], None)
    a.ejecutar()
    assert "ESPERANDO_APROBACION" not in a.recorrido
