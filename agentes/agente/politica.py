"""Política por rol: lo que cada agente NO puede hacer (mínimo privilegio)."""
import posixpath
import re
from dataclasses import dataclass, field

METACARACTERES = re.compile(r"[;&|`$<>\n]")  # encadenar comandos o redirigir está prohibido


@dataclass
class Decision:
    permitido: bool
    motivo: str = ""


def normalizar(ruta: str) -> str:
    """'./tests/x.py', 'src/../tests/x.py' y 'tests\\x.py' son la misma ruta protegida."""
    return posixpath.normpath(str(ruta).replace("\\", "/"))


@dataclass
class Politica:
    herramientas_permitidas: set = field(default_factory=lambda: {
        "listar_archivos", "leer_archivo", "buscar", "mapa_repo", "ejecutar_pruebas", "editar_archivo",
        "ejecutar_comando", "anotar", "leer_notas"})
    comandos_permitidos: tuple = (r"^python -m pytest\b", r"^radon cc\b", r"^lint-imports\b", r"^git (status|diff)\b")
    rutas_protegidas: tuple = ("tests/",)  # el agente no puede "arreglar" las pruebas para que pasen
    max_pasos: int = 15
    aprobar_edicion: object = None  # función opcional: humano en el circuito (E6)

    def evaluar(self, accion: str, args: dict, paso: int) -> Decision:
        if paso > self.max_pasos:
            return Decision(False, f"Se alcanzó el máximo de {self.max_pasos} pasos")
        if accion not in self.herramientas_permitidas:
            return Decision(False, f"Herramienta no permitida: {accion}")
        if accion == "ejecutar_comando":
            cmd = str(args.get("comando", ""))
            if METACARACTERES.search(cmd):
                return Decision(False, f"Comando con caracteres no permitidos: {cmd!r}")
            if not any(re.search(p, cmd) for p in self.comandos_permitidos):
                return Decision(False, f"Comando fuera de la lista permitida: {cmd!r}")
        if accion == "editar_archivo":
            ruta = normalizar(args.get("ruta", ""))
            if ruta.startswith(self.rutas_protegidas):
                return Decision(False, f"Ruta protegida: {ruta}")
            if self.aprobar_edicion and not self.aprobar_edicion(args):
                return Decision(False, "El revisor humano rechazó la edición")
        return Decision(True)
