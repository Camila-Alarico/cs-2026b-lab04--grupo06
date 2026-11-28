"""E5: sistema multiagente. Gestor (planificador) + actor-crítico (ejecutor y revisor de solo lectura) + humano.

Uso (desde la raíz del repositorio; use un chat de IA distinto para cada agente):
    python agentes/orquestador.py 2                  # modo interactivo
    python agentes/orquestador.py 2 --modo grabado   # reproduce las trayectorias grabadas
El humano decide al final: el sistema nunca fusiona su propio cambio.
"""
import argparse
import json
import pathlib
import shutil

from agente_unico import AQUI, COPIA, RAIZ, confirmar, objetivo_issue, preparar_copia
from agente.herramientas import Herramientas
from agente.modelo import ModeloGrabado, ModeloInteractivo
from agente.nucleo import Agente
from agente.politica import Politica
from agente.traza import cargar, generar, resumen

MAX_RONDAS = 2
LECTURA = {"ver_cambios", "leer_archivo", "buscar", "mapa_repo", "ejecutar_pruebas"}  # el revisor no edita


def orquestar(n, h, crear_modelo, trazas, max_rondas=MAX_RONDAS) -> dict:
    """crear_modelo(rol, ronda) devuelve el Modelo de cada agente. El estado final es APROBADO,
    CAMBIOS_PENDIENTES (se agotaron las rondas) o SIN_VEREDICTO (el revisor no respondió el formato)."""
    n = f"{n:02d}"
    issue = h.leer_archivo(f"issues/ISSUE-{n}.md")

    def traza(rol, ronda=1):
        return pathlib.Path(trazas) / f"issue{n}_ac_{rol}{'' if ronda == 1 else f'_r{ronda}'}.jsonl"

    gestor = Agente("planificador", crear_modelo("planificador", 1), h,
                    Politica(herramientas_permitidas=set(), max_pasos=2),
                    "Eres el gestor: no tienes herramientas, solo razonas. Lee el issue y entrega en 'final' un plan "
                    "de 3 a 5 pasos para el ejecutor (qué archivos mirar, qué cambiar y cómo verificarlo). "
                    f"No escribas código.\n\nISSUE:\n{issue}\n\nARCHIVOS EN src:\n{h.listar_archivos('src')}",
                    traza("planificador"))
    plan = gestor.ejecutar()
    agentes, rondas, retro, estado = [gestor], [], "", "SIN_VEREDICTO"
    for ronda in range(1, max_rondas + 1):
        ejecutor = Agente("ejecutor", crear_modelo("ejecutor", ronda), h, Politica(max_pasos=12),
                          f"{objetivo_issue(n)}\n\nPLAN DEL GESTOR:\n{plan}\n{retro}", traza("ejecutor", ronda))
        resumen_ejecutor = ejecutor.ejecutar()
        revisor = Agente("revisor", crear_modelo("revisor", ronda), h,
                         Politica(herramientas_permitidas=LECTURA, max_pasos=8),
                         "Eres el revisor (crítico): solo lees, no editas. Revisa el cambio del ejecutor para el issue: "
                         "usa ver_cambios, ejecuta python -m pytest -q tests (los otros test_issue_* pueden seguir "
                         "fallando) y verifica que resuelva el issue sin tocar tests/ ni salirse del alcance. Responde "
                         "en 'final' empezando con APROBADO o con CAMBIOS SOLICITADOS, seguido de motivos concretos "
                         f"y verificables.\n\nISSUE:\n{issue}\n\nRESUMEN DEL EJECUTOR:\n{resumen_ejecutor}",
                         traza("revisor", ronda))
        veredicto = revisor.ejecutar()
        agentes += [ejecutor, revisor]
        rondas.append({"ronda": ronda, "ejecutor": resumen_ejecutor, "veredicto": veredicto})
        v = veredicto.strip().upper()
        if v.startswith("APROBADO"):
            estado = "APROBADO"
            break
        if not v.startswith("CAMBIOS SOLICITADOS"):
            estado = "SIN_VEREDICTO"
            break
        estado = "CAMBIOS_PENDIENTES"
        retro = f"\nEl revisor solicitó cambios (ronda {ronda}):\n{veredicto}\n"
    return {"plan": plan, "rondas": rondas, "estado": estado, "agentes": agentes}


def metricas(eventos_por_agente: list[list[dict]]) -> dict:
    rs = [resumen(e) for e in eventos_por_agente]
    return {"acciones": sum(r["pasos"] for r in rs),
            "bloqueadas": sum(r["bloqueadas_por_politica"] for r in rs),
            "rechazos_contrato": sum(r["rechazadas_por_contrato"] for r in rs),
            "contexto_total": sum(r["contexto_final_chars"] for r in rs),
            "contexto_max": max(r["contexto_final_chars"] for r in rs)}


def tabla(unico: dict | None, ac: dict, rondas: int) -> str:
    filas = ["| Variante | Rondas | Acciones | Bloqueadas | Rechazos de contrato | Contexto final (caracteres) |",
             "|---|---|---|---|---|---|"]
    if unico:
        filas.append(f"| Agente único | 1 | {unico['acciones']} | {unico['bloqueadas']} | "
                     f"{unico['rechazos_contrato']} | {unico['contexto_total']} |")
    filas.append(f"| Actor-crítico | {rondas} | {ac['acciones']} | {ac['bloqueadas']} | {ac['rechazos_contrato']} | "
                 f"{ac['contexto_total']} en total (máx. {ac['contexto_max']} por agente) |")
    return "\n".join(filas)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("issue", type=int)
    ap.add_argument("--modo", choices=["interactivo", "grabado"], default="interactivo")
    ap.add_argument("--max-rondas", type=int, default=MAX_RONDAS)
    a = ap.parse_args()
    n = f"{a.issue:02d}"

    def crear_modelo(rol, ronda):
        archivo = AQUI / "trayectorias" / f"issue{n}_ac_{rol}{'' if ronda == 1 else f'_r{ronda}'}.json"
        if a.modo == "grabado":
            return ModeloGrabado.desde_archivo(archivo)
        if archivo.exists():
            archivo.replace(archivo.with_suffix(".json.anterior"))
        return ModeloInteractivo(archivo, AQUI / "contexto_actual.txt", f"{rol} (ronda {ronda}) · ")

    preparar_copia()
    h = Herramientas(COPIA, original=RAIZ)
    r = orquestar(a.issue, h, crear_modelo, AQUI / "trazas", a.max_rondas)
    for agente in r["agentes"]:
        generar(agente.traza_archivo)
    print("\nPLAN:", r["plan"])
    for x in r["rondas"]:
        print(f"\n--- RONDA {x['ronda']}\nEJECUTOR: {x['ejecutor']}\nREVISOR: {x['veredicto']}")
    print(f"\nEstado final del bucle actor-crítico: {r['estado']}. Decisión final: HUMANO.")
    ac = metricas([ag.eventos for ag in r["agentes"]])
    unica = AQUI / "trazas" / f"issue{n}_agente_unico.jsonl"
    comparacion = tabla(metricas([cargar(unica)]) if unica.exists() else None, ac, len(r["rondas"]))
    (AQUI / "trazas" / f"issue{n}_comparacion.md").write_text(comparacion + "\n", encoding="utf-8")
    print("\n=== COMPARACIÓN (también en trazas/issue%s_comparacion.md) ===\n%s" % (n, comparacion))
    if (COPIA / "notas.md").exists():
        shutil.copy2(COPIA / "notas.md", AQUI / "trazas" / f"issue{n}_ac_notas.md")
    cambios = h.ver_cambios()
    print("\n=== CAMBIOS PROPUESTOS ===\n" + cambios)
    cambiados = h.archivos_modificados()
    if cambiados and a.modo == "interactivo" and confirmar("¿Aplicar estos cambios a su rama actual?"):
        for rel in cambiados:
            shutil.copy2(COPIA / rel, RAIZ / rel)
        print("Aplicado. Revise con git diff y haga commit usted: el agente no fusiona nada.")


if __name__ == "__main__":
    main()
