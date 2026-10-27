"""<<Factory>> (registro): crea la variante adecuada por nombre. Aquí se ensamblan las variantes por defecto."""
from __future__ import annotations

from typing import Callable

from rutasit.algoritmos_eta import DistanciaDirecta, VelocidadPromedio
from rutasit.gps import ConReintentos, OperadorAAdapter, OperadorBAdapter
from rutasit.ia import ConCache, LocalAdapter, NubeAdapter


class Fabrica:
    """Registro de creadores. Agregar una variante = registrar un creador (abierto/cerrado)."""

    def __init__(self, descripcion: str):
        self._descripcion = descripcion
        self._creadores: dict[str, Callable[[], object]] = {}

    def registrar(self, nombre: str, creador: Callable[[], object]) -> None:
        self._creadores[nombre] = creador

    def crear(self, nombre: str):
        if nombre not in self._creadores:
            raise ValueError(f"{self._descripcion} no soportado: {nombre}")
        return self._creadores[nombre]()


def fabrica_gps_por_defecto(gps_a=None, gps_b=None) -> Fabrica:
    fabrica = Fabrica("Operador GPS")
    fabrica.registrar("OPERADOR_A", lambda: ConReintentos(OperadorAAdapter(gps_a)))
    fabrica.registrar("OPERADOR_B", lambda: ConReintentos(OperadorBAdapter(gps_b)))
    return fabrica


def fabrica_algoritmos_por_defecto(velocidad_promedio_kmh: float = 20.0) -> Fabrica:
    fabrica = Fabrica("Algoritmo de ETA")
    fabrica.registrar("DIRECTO", DistanciaDirecta)
    fabrica.registrar("PROMEDIO", lambda: VelocidadPromedio(velocidad_promedio_kmh))
    return fabrica


def fabrica_llm_por_defecto(llm_nube=None, llm_local=None) -> Fabrica:
    """Cada proveedor se crea UNA vez envuelto en su caché, para que la caché viva entre consultas."""
    nube = ConCache(NubeAdapter(llm_nube))
    local = ConCache(LocalAdapter(llm_local))
    fabrica = Fabrica("Proveedor de IA")
    fabrica.registrar("NUBE", lambda: nube)
    fabrica.registrar("LOCAL", lambda: local)
    return fabrica
