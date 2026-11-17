"""Genera pruebas ETA a través del puerto ProveedorLLM y valida su salida."""
from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

from jsonschema import ValidationError, validate

from rutasit.ia import ProveedorLLM

ROOT = Path(__file__).resolve().parents[2]
PROMPT_DIR = ROOT / "prompts" / "pruebas_eta"
ESQUEMA = json.loads((PROMPT_DIR / "esquema.json").read_text(encoding="utf-8"))
IMPORTS_PERMITIDOS = {"pytest", "rutasit.algoritmos_eta"}
LLAMADAS_PROHIBIDAS = {"eval", "exec", "compile", "open", "__import__", "input", "breakpoint"}


class SalidaInvalida(ValueError):
    """La respuesta del proveedor no cumple el contrato seguro de E4."""


class GeneradorPruebasEta:
    """Usa cualquier implementación del puerto ProveedorLLM (Strategy)."""

    def __init__(self, proveedor: ProveedorLLM, version: str = "v3") -> None:
        if version not in {"v1", "v2", "v3"}:
            raise ValueError(f"Versión no soportada: {version}")
        self._proveedor = proveedor
        self.version = version
        self._plantilla = (PROMPT_DIR / f"{version}.txt").read_text(encoding="utf-8")

    def generar(self, caso_id: str, requisito: str, objetivo: str) -> dict[str, Any]:
        """Genera el artefacto JSON y lo valida antes de devolverlo."""
        if not caso_id.strip() or not requisito.strip() or not objetivo.strip():
            raise ValueError("caso_id, requisito y objetivo son obligatorios")
        prompt = (self._plantilla
                  .replace("{{id}}", caso_id)
                  .replace("{{requisito}}", requisito)
                  .replace("{{objetivo}}", objetivo))
        texto = self._proveedor.completar(prompt)
        try:
            resultado = json.loads(texto)
            validate(instance=resultado, schema=ESQUEMA)
            self._validar_codigo(resultado["codigo"])
        except (json.JSONDecodeError, ValidationError, SyntaxError, ValueError, TypeError) as exc:
            raise SalidaInvalida(f"{self.version}/{caso_id}: {exc}") from exc
        if resultado["caso_id"] != caso_id:
            raise SalidaInvalida("El caso_id de la respuesta no coincide con la solicitud")
        return resultado

    @staticmethod
    def _validar_codigo(codigo: str) -> None:
        """Valida sintaxis y limita imports/llamadas; no ejecuta el código generado."""
        arbol = ast.parse(codigo, filename="test_eta_generado.py", mode="exec")
        funciones = [n for n in ast.walk(arbol) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                     and n.name.startswith("test_")]
        asserts = [n for n in ast.walk(arbol) if isinstance(n, ast.Assert)]
        if not funciones:
            raise ValueError("Debe existir al menos una función test_...")
        if len(asserts) < 3:
            raise ValueError("Se requieren al menos tres instrucciones assert")
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.Import):
                for alias in nodo.names:
                    if alias.name not in IMPORTS_PERMITIDOS:
                        raise ValueError(f"Import no permitido: {alias.name}")
            elif isinstance(nodo, ast.ImportFrom):
                if nodo.module not in IMPORTS_PERMITIDOS or nodo.level:
                    raise ValueError(f"Import no permitido: {nodo.module}")
            elif isinstance(nodo, ast.Call):
                nombre = nodo.func.id if isinstance(nodo.func, ast.Name) else None
                if nombre in LLAMADAS_PROHIBIDAS:
                    raise ValueError(f"Llamada no permitida: {nombre}")
                if isinstance(nodo.func, ast.Attribute) and nodo.func.attr.startswith("__"):
                    raise ValueError("No se permiten accesos a atributos especiales")
