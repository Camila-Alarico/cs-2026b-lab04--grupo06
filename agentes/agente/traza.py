"""Convierte una traza JSONL en un diagrama de secuencia Mermaid y un resumen de métricas.

Uso:  python agentes/agente/traza.py [trazas/archivo.jsonl ...]   (sin argumentos: todas las de agentes/trazas)
"""
import json
import pathlib
import re
import sys

ESTADOS_BLOQUEO = {"BLOQUEADO", "LIMITE_ALCANZADO"}


def cargar(archivo) -> list[dict]:
    lineas = pathlib.Path(archivo).read_text(encoding="utf-8").splitlines()
    return [json.loads(x) for x in lineas if x.strip()]


def _limpio(texto, largo=48) -> str:
    texto = re.sub(r"[;#\"\n\r]", " ", str(texto)).strip()
    return texto if len(texto) <= largo else texto[:largo - 1] + "…"


def _llamada(e) -> str:
    args = ", ".join(f"{k}={_limpio(v, 22)}" for k, v in e["args"].items())
    return f"{e['accion']}({args})"


def _observacion(e) -> str:
    """Para pytest y comandos, lo útil es la última línea (ej. '4 failed, 89 passed'); para el resto, la primera."""
    lineas = [x for x in str(e["observacion"]).splitlines() if x.strip()] or [""]
    return lineas[-1] if e["accion"] in ("ejecutar_pruebas", "ejecutar_comando") else lineas[0]


def a_mermaid(eventos: list[dict]) -> str:
    agente = _limpio(eventos[0]["agente"].capitalize(), 20)
    lineas = ["sequenceDiagram", "    autonumber", "    participant U as Humano", f"    participant A as {agente}",
              "    participant P as Política", "    participant H as Herramientas"]
    for e in eventos:
        estado = e["estado"]
        if estado == "INICIO":
            lineas.append("    U->>A: objetivo")
        elif estado == "OBSERVANDO":
            if e.get("humano"):
                lineas += [f"    A->>U: {_limpio(_llamada(e), 60)}", "    U-->>A: edición aprobada"]
            lineas += [f"    A->>H: {_limpio(_llamada(e), 60)}", f"    H-->>A: {_limpio(_observacion(e))}"]
        elif estado in ESTADOS_BLOQUEO:
            accion = "límite de pasos" if e["accion"] == "(ninguna)" else _limpio(_llamada(e), 60)
            if e.get("humano"):
                lineas += [f"    A->>U: {_limpio(_llamada(e), 60)}", "    U--xA: edición rechazada"]
            else:
                lineas += [f"    A-xP: {accion}", f"    P-->>A: {estado}"]
        elif estado == "CONTRATO_INVALIDO":
            lineas += ["    A-xA: decisión inválida", f"    Note over A: {_limpio(e['observacion'], 70)}"]
        elif estado == "FINALIZADO":
            lineas.append(f"    A-->>U: {_limpio(e['texto'])}")
    return "\n".join(lineas) + "\n"


def resumen(eventos: list[dict]) -> dict:
    acciones = [e for e in eventos if e["tipo"] == "accion"]
    return {"agente": eventos[0]["agente"],
            "pasos": len(acciones),
            "acciones_permitidas": sum(1 for e in acciones if e["estado"] == "OBSERVANDO"),
            "bloqueadas_por_politica": sum(1 for e in acciones if e["estado"] in ESTADOS_BLOQUEO),
            "rechazadas_por_contrato": sum(1 for e in acciones if e["estado"] == "CONTRATO_INVALIDO"),
            "ediciones_aprobadas_por_humano": sum(1 for e in acciones if e.get("humano") == "aprobada"),
            "ediciones_rechazadas_por_humano": sum(1 for e in acciones if e.get("humano") == "rechazada"),
            "herramientas": sorted({e["accion"] for e in acciones if e["estado"] == "OBSERVANDO"}),
            "contexto_final_chars": max(e["contexto_chars"] for e in eventos),
            "termino_con": eventos[-1]["estado"]}


def generar(archivo) -> dict:
    archivo = pathlib.Path(archivo)
    eventos = cargar(archivo)
    archivo.with_suffix(".mmd").write_text(a_mermaid(eventos), encoding="utf-8")
    return resumen(eventos)


if __name__ == "__main__":
    carpeta = pathlib.Path(__file__).resolve().parent.parent / "trazas"
    for ruta in map(pathlib.Path, sys.argv[1:] or sorted(carpeta.glob("*.jsonl"))):
        print(f"{ruta.name} -> {ruta.with_suffix('.mmd').name}")
        for clave, valor in generar(ruta).items():
            print(f"  {clave}: {valor}")
