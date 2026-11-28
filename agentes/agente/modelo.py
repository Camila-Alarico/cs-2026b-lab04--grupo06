"""El 'cerebro' intercambiable (Strategy, Lab 07): el agente no sabe qué modelo hay detrás."""
import json
import pathlib
import platform
import re
import subprocess
from abc import ABC, abstractmethod


class Modelo(ABC):
    @abstractmethod
    def decidir(self, historial: list[dict]):
        """Devuelve la siguiente decisión (dict). Si el modelo responde mal, puede devolver cualquier cosa:
        el contrato la rechaza."""


class ModeloGrabado(Modelo):
    """Reproduce una trayectoria ya grabada (clase, pruebas, integración continua)."""

    def __init__(self, decisiones: list):
        self._decisiones = iter(decisiones)

    @classmethod
    def desde_archivo(cls, archivo):
        return cls(json.loads(pathlib.Path(archivo).read_text(encoding="utf-8")))

    def decidir(self, historial):
        return next(self._decisiones, {"pensamiento": "se acabó la trayectoria grabada", "final": "(sin más decisiones)"})


def _copiar_al_portapapeles(texto: str) -> bool:
    comando = {"Windows": ["clip"], "Darwin": ["pbcopy"]}.get(platform.system())
    if not comando:
        return False
    try:
        subprocess.run(comando, input=texto.encode("utf-16" if platform.system() == "Windows" else "utf-8"),
                       check=True)
        return True
    except (OSError, subprocess.CalledProcessError):
        return False


def _interpretar(texto: str):
    """Quita las vallas ```json ... ``` y convierte a JSON. Si no es JSON, devuelve el texto tal cual (sin corregirlo)."""
    m = re.search(r"```(?:json)?\s*(.*?)```", texto, re.DOTALL)
    candidato = (m.group(1) if m else texto).strip()
    try:
        return json.loads(candidato)
    except json.JSONDecodeError:
        return texto.strip()


class ModeloInteractivo(Modelo):
    """Practicar sin clave de API: se copia el contexto a un asistente de IA, se pega su respuesta y la
    decisión queda grabada en 'archivo_trayectoria' (se guarda también si es inválida)."""

    def __init__(self, archivo_trayectoria, archivo_contexto):
        self._trayectoria = pathlib.Path(archivo_trayectoria)
        self._contexto = pathlib.Path(archivo_contexto)
        self._decisiones: list = []

    def decidir(self, historial):
        etiquetas = {"user": "[ENTRADA]", "assistant": "[TU DECISIÓN ANTERIOR]"}
        texto = "\n\n".join(f"{etiquetas[m['role']]}\n{m['content']}" for m in historial)
        texto += "\n\n[AHORA] Responde SOLO con el JSON de tu siguiente decisión."
        self._contexto.write_text(texto, encoding="utf-8")
        copiado = _copiar_al_portapapeles(texto)
        print(f"\n--- Paso {len(self._decisiones) + 1} ---")
        print(f"Contexto ({len(texto)} caracteres) guardado en {self._contexto}"
              + (" y copiado al portapapeles." if copiado else ". Cópielo a su asistente."))
        print("Pegue la respuesta del asistente (si no es JSON válido, termine con una línea que diga FIN):")
        lineas = []
        while True:
            linea = input()
            if linea.strip() == "FIN":
                break
            lineas.append(linea)
            if isinstance(_interpretar("\n".join(lineas)), dict):
                break
        decision = _interpretar("\n".join(lineas))
        self._decisiones.append(decision)
        self._trayectoria.write_text(json.dumps(self._decisiones, ensure_ascii=False, indent=1), encoding="utf-8")
        return decision
