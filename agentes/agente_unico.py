"""E2: un solo agente ReAct sobre un issue, sin clave de API.

Uso (desde la raíz del repositorio):
    python agentes/agente_unico.py 1                  # modo interactivo: usted pega las respuestas de su asistente
    python agentes/agente_unico.py 1 --modo grabado   # reproduce la trayectoria ya grabada
El agente trabaja en una COPIA (agentes/_copia). Nunca fusiona su cambio: usted lo aprueba al final.
"""
import argparse
import pathlib
import shutil
import sys

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(AQUI))

from agente.herramientas import Herramientas  # noqa: E402
from agente.modelo import ModeloGrabado, ModeloInteractivo  # noqa: E402
from agente.nucleo import Agente  # noqa: E402
from agente.politica import Politica  # noqa: E402
from agente.traza import generar  # noqa: E402

COPIA = AQUI / "_copia"


def preparar_copia() -> None:
    shutil.rmtree(COPIA, ignore_errors=True)
    COPIA.mkdir()
    ignorar = shutil.ignore_patterns("__pycache__", ".pytest_cache", "*.pyc")
    for nombre in ("src", "tests", "issues"):
        if (RAIZ / nombre).exists():
            shutil.copytree(RAIZ / nombre, COPIA / nombre, ignore=ignorar)
    for archivo in ("pytest.ini", "pyproject.toml", "setup.cfg", "requirements.txt", "conftest.py"):
        if (RAIZ / archivo).exists():
            shutil.copy2(RAIZ / archivo, COPIA / archivo)


def confirmar(pregunta: str) -> bool:
    while True:
        respuesta = input(f"{pregunta} (s/n): ").strip().lower()
        if respuesta in ("s", "n"):
            return respuesta == "s"
        print("Responda solo 's' o 'n'.")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("issue", type=int)
    ap.add_argument("--modo", choices=["interactivo", "grabado"], default="interactivo")
    ap.add_argument("--max-pasos", type=int, default=12)
    a = ap.parse_args()
    n = f"{a.issue:02d}"
    trayectoria = AQUI / "trayectorias" / f"issue{n}_agente_unico.json"
    traza = AQUI / "trazas" / f"issue{n}_agente_unico.jsonl"
    if a.modo == "grabado":
        modelo = ModeloGrabado.desde_archivo(trayectoria)
    else:
        if trayectoria.exists():
            trayectoria.replace(trayectoria.with_suffix(".json.anterior"))
        modelo = ModeloInteractivo(trayectoria, AQUI / "contexto_actual.txt")
    preparar_copia()
    objetivo = (f"Resuelve el issue descrito en issues/ISSUE-{n}.md. La prueba que lo reproduce está en "
                f"tests/test_issue_{n}.py y hoy falla: debe pasar. Las demás pruebas que hoy pasan deben seguir "
                "pasando (python -m pytest -q tests); los otros test_issue_* seguirán fallando y no son tu tarea. "
                "No modifiques archivos de tests/. Usa mapa_repo para ubicar el código y anotar/leer_notas para dejar "
                "constancia de hipótesis y archivos revisados.")
    herramientas = Herramientas(COPIA, original=RAIZ)
    agente = Agente("ejecutor", modelo, herramientas, Politica(max_pasos=a.max_pasos), objetivo, traza)
    print("\nRESULTADO DEL AGENTE:", agente.ejecutar())
    if (COPIA / "notas.md").exists():
        shutil.copy2(COPIA / "notas.md", AQUI / "trazas" / f"issue{n}_notas.md")
    print("\n=== CAMBIOS PROPUESTOS ===\n" + herramientas.ver_cambios())
    print("\n=== MÉTRICAS ===")
    for clave, valor in generar(traza).items():
        print(f"  {clave}: {valor}")
    cambiados = herramientas.archivos_modificados()
    if cambiados and a.modo == "interactivo" and confirmar("¿Aplicar estos cambios a su rama actual?"):
        for rel in cambiados:
            shutil.copy2(COPIA / rel, RAIZ / rel)
        print("Aplicado. Revise con git diff y haga commit usted: el agente no fusiona nada.")


if __name__ == "__main__":
    main()
