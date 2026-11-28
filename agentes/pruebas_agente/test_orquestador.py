"""E5: el orquestador (gestor + actor-crítico + humano). Todo con modelos grabados, sin LLM."""
import pytest

from agente.herramientas import Herramientas
from agente.modelo import ModeloGrabado
from orquestador import LECTURA, metricas, orquestar, tabla

EDITAR = {"pensamiento": "arreglo", "accion": "editar_archivo",
          "args": {"ruta": "calc.py", "antes": "x + x + 1", "despues": "x + x"}}
PRUEBAS = {"pensamiento": "verifico", "accion": "ejecutar_pruebas"}
PLAN = [{"pensamiento": "planifico", "final": "1) leer calc.py 2) corregir doble 3) correr pruebas"}]


def final(texto):
    return {"pensamiento": "concluyo", "final": texto}


@pytest.fixture
def entorno(tmp_path):
    original = tmp_path / "original"
    (original / "tests").mkdir(parents=True)
    (original / "issues").mkdir()
    (original / "src").mkdir()
    (original / "calc.py").write_text("def doble(x):\n    return x + x + 1\n", encoding="utf-8")
    (original / "src" / "m.py").write_text("X = 1\n", encoding="utf-8")
    (original / "issues" / "ISSUE-01.md").write_text("# Issue 1: doble está mal\n", encoding="utf-8")
    (original / "tests" / "test_calc.py").write_text(
        "import sys, pathlib\nsys.path.insert(0, str(pathlib.Path(__file__).parent.parent))\n"
        "from calc import doble\n\ndef test_doble():\n    assert doble(2) == 4\n", encoding="utf-8")
    copia = tmp_path / "copia"
    import shutil
    shutil.copytree(original, copia)
    return Herramientas(copia, original), tmp_path / "trazas"


def modelos(**decisiones):
    return lambda rol, ronda: ModeloGrabado(decisiones[f"{rol}{ronda}"])


def test_dos_rondas_el_revisor_pide_cambios_y_luego_aprueba(entorno):
    h, trazas = entorno
    r = orquestar(1, h, modelos(
        planificador1=PLAN,
        ejecutor1=[EDITAR, final("Cambié doble; no corrí pruebas")],
        revisor1=[{"pensamiento": "intento editar", "accion": "editar_archivo",
                   "args": {"ruta": "calc.py", "antes": "x + x", "despues": "x * 2"}},   # el revisor NO puede editar
                  PRUEBAS, final("CAMBIOS SOLICITADOS: falta evidencia de que las pruebas pasan")],
        ejecutor2=[PRUEBAS, final("Pruebas: 1 passed")],
        revisor2=[{"pensamiento": "miro el diff", "accion": "ver_cambios"}, final("APROBADO: 1 passed")]), trazas)
    assert r["estado"] == "APROBADO" and len(r["rondas"]) == 2
    assert "CAMBIOS SOLICITADOS" in r["agentes"][3].historial[0]["content"]       # ejecutor ronda 2 recibe la crítica
    assert "1) leer calc.py" in r["agentes"][1].historial[0]["content"]           # ejecutor ronda 1 recibe el plan
    revisor1 = r["agentes"][2]
    assert [e["estado"] for e in revisor1.eventos].count("BLOQUEADO") == 1
    assert "x + x\n" in (h.raiz / "calc.py").read_text(encoding="utf-8")          # el revisor no modificó nada
    for nombre in ("planificador", "ejecutor", "revisor", "ejecutor_r2", "revisor_r2"):
        assert (trazas / f"issue01_ac_{nombre}.jsonl").exists()


def test_el_bucle_termina_al_agotar_las_rondas_y_decide_el_humano(entorno):
    h, trazas = entorno
    siempre = [final("CAMBIOS SOLICITADOS: no me convence")]
    r = orquestar(1, h, modelos(planificador1=PLAN, ejecutor1=[final("hecho")], revisor1=siempre,
                                ejecutor2=[final("hecho otra vez")], revisor2=siempre), trazas, max_rondas=2)
    assert r["estado"] == "CAMBIOS_PENDIENTES" and len(r["rondas"]) == 2


def test_un_veredicto_sin_formato_no_se_toma_como_aprobacion(entorno):
    h, trazas = entorno
    r = orquestar(1, h, modelos(planificador1=PLAN, ejecutor1=[final("hecho")],
                                revisor1=[final("Me parece bien")]), trazas)
    assert r["estado"] == "SIN_VEREDICTO" and len(r["rondas"]) == 1


def test_cada_rol_ve_solo_sus_herramientas(entorno):
    h, trazas = entorno
    r = orquestar(1, h, modelos(planificador1=PLAN, ejecutor1=[final("hecho")],
                                revisor1=[final("APROBADO")]), trazas)
    gestor, ejecutor, revisor = (a.historial[0]["content"] for a in r["agentes"])
    assert "(ninguna: solo razonas)" in gestor and "editar_archivo(" not in gestor
    assert "editar_archivo(" in ejecutor and "anotar(" in ejecutor
    assert "ver_cambios(" in revisor and "editar_archivo(" not in revisor and "anotar(" not in revisor
    assert "editar_archivo" not in LECTURA and "ejecutar_comando" not in LECTURA


def test_metricas_y_tabla_de_comparacion(entorno):
    h, trazas = entorno
    r = orquestar(1, h, modelos(planificador1=PLAN, ejecutor1=[EDITAR, PRUEBAS, final("hecho")],
                                revisor1=[final("APROBADO")]), trazas)
    ac = metricas([a.eventos for a in r["agentes"]])
    assert ac["acciones"] == 2 and ac["bloqueadas"] == 0
    assert ac["contexto_total"] >= ac["contexto_max"] > 0
    t = tabla({"acciones": 7, "bloqueadas": 0, "rechazos_contrato": 0, "contexto_total": 17504}, ac, 1)
    assert "| Agente único | 1 | 7 |" in t and "| Actor-crítico | 1 | 2 |" in t


# ---------- E6: aprobación humana y compuerta determinista ----------
def _con_prueba_del_issue(h):
    (h.raiz / "tests" / "test_issue_01.py").write_text(
        "import sys, pathlib\nsys.path.insert(0, str(pathlib.Path(__file__).parent.parent))\n"
        "from calc import doble\n\ndef test_issue_01():\n    assert doble(2) == 4\n", encoding="utf-8")


def test_la_aprobacion_humana_aplica_al_ejecutor_y_no_al_revisor(entorno):
    h, trazas = entorno
    consultas = []
    r = orquestar(1, h, modelos(planificador1=PLAN, ejecutor1=[EDITAR, final("hecho")],
                                revisor1=[final("APROBADO")]), trazas,
                  aprobar_edicion=lambda args: consultas.append(args["ruta"]) or True)
    assert consultas == ["calc.py"] and r["estado"] == "APROBADO"
    assert r["agentes"][2].politica.aprobar_edicion is None                         # el revisor no edita ni aprueba


def test_compuerta_revierte_un_aprobado_del_revisor_si_la_prueba_del_issue_falla(entorno):
    h, trazas = entorno
    _con_prueba_del_issue(h)
    r = orquestar(1, h, modelos(
        planificador1=PLAN,
        ejecutor1=[final("Dije que lo arreglé pero no toqué nada")],
        revisor1=[final("APROBADO: se ve bien")],                                   # el LLM se equivoca
        ejecutor2=[EDITAR, final("Ahora sí")],
        revisor2=[final("APROBADO: pasa")]), trazas)
    assert r["rondas"][0]["aprobado_con_pruebas_en_rojo"] is True
    assert r["rondas"][0]["veredicto"].startswith("CAMBIOS SOLICITADOS (compuerta de pruebas)")
    assert "CAMBIOS SOLICITADOS (compuerta" in r["agentes"][3].historial[0]["content"]
    assert r["estado"] == "APROBADO" and len(r["rondas"]) == 2


def test_compuerta_deja_cambios_pendientes_si_en_la_ultima_ronda_sigue_en_rojo(entorno):
    h, trazas = entorno
    _con_prueba_del_issue(h)
    r = orquestar(1, h, modelos(planificador1=PLAN, ejecutor1=[final("nada")], revisor1=[final("APROBADO")],
                                ejecutor2=[final("nada otra vez")], revisor2=[final("APROBADO")]), trazas)
    assert r["estado"] == "CAMBIOS_PENDIENTES" and len(r["rondas"]) == 2
    assert all(x["aprobado_con_pruebas_en_rojo"] for x in r["rondas"])
