# Round-trip — RutaSIT Arequipa

| Diferencia observada | Causa | Acción |
|----------------------|-------|--------|
| Las composiciones (Ruta–ParaderoDeRuta, Viaje–PosicionGPS) aparecen como atributos list[...] y no como relación | pyreverse no infiere composición desde colecciones tipadas | Ninguna: limitación de la herramienta; se mantiene el diagrama de diseño |
| No hay multiplicidades | El código no expresa multiplicidades | Documentar; se podría validar en el servicio que una ruta tenga al menos 2 paraderos (C3) |
| Los puertos aparecen como clases abstractas y sin el estereotipo <<puerto>> | Python implementa interfaces con ABC | Aceptable en Python; se documenta |
| Nombres en snake_case y miembros de la enumeración en mayúsculas frente a camelCase en el diagrama (esta_en_ruta vs estaEnRuta, EN_RUTA vs EnRuta) | Convención de Python | Aceptable; se documenta la equivalencia (C5) |