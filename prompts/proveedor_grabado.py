import pathlib

RAIZ = pathlib.Path(__file__).parent


def call_api(prompt, options, context):
    carpeta = (options.get("config") or {}).get("carpeta", "criterios")
    # promptfoo compone la etiqueta como "v1: v1.txt: <texto>"; la versión es lo que va antes del primer ":"
    version = context["prompt"]["label"].split(":", 1)[0].strip()
    id_caso = context["vars"]["id"]
    ruta = RAIZ / carpeta / "grabaciones" / version / f"{id_caso}.txt"
    if not ruta.exists():
        return {"error": f"Falta la grabación: {ruta.relative_to(RAIZ)}"}
    return {"output": ruta.read_text(encoding="utf-8")}