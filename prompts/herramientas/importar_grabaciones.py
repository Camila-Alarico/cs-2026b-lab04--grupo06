import pathlib
import re
import sys


def main(carpeta: str, archivo: str, version: str) -> None:
    texto = pathlib.Path(archivo).read_text(encoding="utf-8")
    partes = re.split(r"(?m)^=== (\S+) ===\n", texto)
    destino = pathlib.Path(carpeta) / "grabaciones" / version
    destino.mkdir(parents=True, exist_ok=True)
    for id_caso, cuerpo in zip(partes[1::2], partes[2::2]):
        # solo se quita el salto de línea que separa una respuesta de la siguiente marca
        (destino / f"{id_caso}.txt").write_text(cuerpo.rstrip("\n") + "\n", encoding="utf-8")
        print(f"{destino / (id_caso + '.txt')}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])