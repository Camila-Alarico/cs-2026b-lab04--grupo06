"""Humano en el circuito (E6): aprobación de cada edición desde la consola."""


def aprobar_por_consola(args, entrada=input, salida=print) -> bool:
    """Muestra la edición propuesta y exige 's' o 'n'. Cualquier otra respuesta se vuelve a preguntar."""
    salida(f"\n=== EDICIÓN PROPUESTA en {args.get('ruta')} ===")
    salida(f"--- antes\n{args.get('antes', '')}\n--- después\n{args.get('despues', '')}")
    while True:
        respuesta = entrada("¿Aprueba esta edición? (s/n): ").strip().lower()
        if respuesta in ("s", "n"):
            return respuesta == "s"
        salida("Responda solo 's' o 'n'.")
