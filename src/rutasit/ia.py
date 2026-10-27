"""Componente de IA aislado (Lab 07, E5): Strategy + Adapter + Decorator (caché) + Chain of Responsibility.

La respuesta del LLM es un dato NO confiable: se valida con guardrails antes de llegar al usuario.
Nada de este módulo necesita red ni claves: en las pruebas se inyecta un SDK simulado.
"""
from __future__ import annotations

import re
from abc import ABC, abstractmethod

LONGITUD_MAXIMA = 280


class ProveedorLLM(ABC):
    """Puerto <<Strategy>>: todos los proveedores de IA se usan igual."""

    @abstractmethod
    def completar(self, prompt: str) -> str:
        """Devuelve el texto generado para el prompt."""


# ---------- ADAPTER: traduce cada SDK a la interfaz ProveedorLLM ----------
class NubeAdapter(ProveedorLLM):
    """<<Adapter>>: el SDK en la nube responde con un dict {'texto': ...}."""

    def __init__(self, sdk):
        self._sdk = sdk

    def completar(self, prompt: str) -> str:
        return self._sdk.generate(prompt)["texto"]


class LocalAdapter(ProveedorLLM):
    """<<Adapter>>: el modelo local responde directamente con el texto."""

    def __init__(self, sdk):
        self._sdk = sdk

    def completar(self, prompt: str) -> str:
        return self._sdk.predict(prompt)


# ---------- DECORATOR: caché ----------
class ConCache(ProveedorLLM):
    """<<Decorator>>: evita pagar dos veces por el mismo prompt (reduce costo y latencia)."""

    def __init__(self, interno: ProveedorLLM):
        self._interno = interno
        self._cache: dict[str, str] = {}

    def completar(self, prompt: str) -> str:
        if prompt not in self._cache:
            self._cache[prompt] = self._interno.completar(prompt)
        return self._cache[prompt]


# ---------- CHAIN OF RESPONSIBILITY: guardrails de salida ----------
class Guardrail(ABC):
    """<<Handler>>: valida el texto y lo pasa al siguiente eslabón. Si es inválido, lanza ValueError."""

    def __init__(self, siguiente: Guardrail | None = None):
        self._siguiente = siguiente

    def validar(self, texto: str) -> str:
        texto = self._aplicar(texto)
        return self._siguiente.validar(texto) if self._siguiente else texto

    @abstractmethod
    def _aplicar(self, texto: str) -> str: ...


class SinHoraInventada(Guardrail):
    """La IA no conoce la hora real de llegada: cualquier hora (08:15) es inventada."""

    def _aplicar(self, texto: str) -> str:
        if re.search(r"\d{1,2}:\d{2}", texto):
            raise ValueError("Guardrail: la IA inventó una hora")
        return texto


class SinCulparAlConductor(Guardrail):
    PROHIBIDAS = ["conductor", "chofer", "culpa"]

    def _aplicar(self, texto: str) -> str:
        for palabra in self.PROHIBIDAS:
            if palabra in texto.lower():
                raise ValueError(f"Guardrail: atribución no permitida '{palabra}'")
        return texto


class LongitudMaxima(Guardrail):
    def _aplicar(self, texto: str) -> str:
        if len(texto) > LONGITUD_MAXIMA:
            raise ValueError("Guardrail: respuesta demasiado larga")
        return texto


def cadena_guardrails_por_defecto() -> Guardrail:
    """SinHoraInventada -> SinCulparAlConductor -> LongitudMaxima."""
    return SinHoraInventada(SinCulparAlConductor(LongitudMaxima()))
