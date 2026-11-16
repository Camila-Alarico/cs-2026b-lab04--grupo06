"""Ejecuta las ocho grabaciones v3 contra el módulo ETA real."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GRABACIONES = Path(__file__).parent / "grabaciones" / "v3"


def main() -> int:
    codigos = []
    for archivo in sorted(GRABACIONES.glob("ETA-*.txt")):
        salida = json.loads(archivo.read_text(encoding="utf-8"))
        codigo = salida["codigo"]
        compile(codigo, archivo.name, "exec")
        codigos.append(f"# {archivo.stem}\n{codigo}")
    if len(codigos) != 8:
        raise SystemExit(f"Se esperaban 8 grabaciones v3; se encontraron {len(codigos)}")

    with tempfile.TemporaryDirectory() as temporal:
        destino = Path(temporal) / "test_eta_generado.py"
        destino.write_text("\n\n".join(codigos), encoding="utf-8")
        entorno = os.environ.copy()
        entorno["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + entorno.get("PYTHONPATH", "")
        resultado = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", str(destino)],
            cwd=ROOT,
            env=entorno,
            check=False,
        )
        return resultado.returncode


if __name__ == "__main__":
    raise SystemExit(main())
