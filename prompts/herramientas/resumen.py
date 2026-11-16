"""Resume resultados.json de promptfoo: tasa de aprobación por versión y por aserción, y casos que fallan.

Uso:  python prompts/herramientas/resumen.py prompts/criterios/resultados.json
"""
import collections
import json
import re
import sys


def main(ruta: str) -> None:
    datos = json.load(open(ruta, encoding="utf-8"))["results"]["results"]
    por_version = collections.defaultdict(list)
    por_asercion = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
    fallos = collections.defaultdict(dict)
    for r in datos:
        version = r["prompt"]["label"].split(":", 1)[0].strip()
        caso = r["vars"]["id"]
        por_version[version].append(r["success"])
        malas = []
        for c in r["gradingResult"]["componentResults"]:
            metrica = c["assertion"].get("metric", c["assertion"]["type"])
            por_asercion[metrica][version][1] += 1
            if c["pass"]:
                por_asercion[metrica][version][0] += 1
            else:
                malas.append(metrica.split("_")[0])
        if malas:
            fallos[version][caso] = malas
    versiones = sorted(por_version)
    print("| Versión | Casos aprobados | Tasa |\n|---|---:|---:|")
    for v in versiones:
        ok, n = sum(por_version[v]), len(por_version[v])
        print(f"| {v} | {ok}/{n} | {100 * ok / n:.1f} % |")
    print("\n| Aserción | " + " | ".join(versiones) + " |\n|---|" + "---:|" * len(versiones))
    for m in sorted(por_asercion):
        celdas = []
        for v in versiones:
            ok, n = por_asercion[m][v]
            celdas.append(f"{ok}/{n}" if n else "-")
        print(f"| {m} | " + " | ".join(celdas) + " |")
    print("\nDiagnóstico (no cuenta para la aprobación): respuestas que son JSON válido al quitar los bloques de código")
    for v in versiones:
        validas = 0
        for r in datos:
            if r["prompt"]["label"].split(":", 1)[0].strip() != v:
                continue
            texto = (r.get("response") or {}).get("output", "").strip()
            texto = re.sub(r"^```[a-z]*\n|\n```$", "", texto)
            try:
                json.loads(texto)
                validas += 1
            except ValueError:
                pass
        print(f"  {v}: {validas}/{len(por_version[v])}")
    print("\nCasos que fallan (aserciones):")
    for v in versiones:
        print(f"  {v}: " + (", ".join(f"{c} {m}" for c, m in sorted(fallos[v].items())) or "ninguno"))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "prompts/criterios/resultados.json")