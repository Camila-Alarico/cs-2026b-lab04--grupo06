# Revisión con la lista oficial del modelo C4 — RutaSIT Arequipa

Método: se aplicó la lista de revisión (Tabla 3 de la guía) a las 5 vistas con un auditor de IA (Prompt IA 2) sobre los PNG exportados. Cada hallazgo se verificó contra workspace.dsl, los Labs 04 y 05 y las figuras de ejemplo de la guía.
Resumen: 20 hallazgos: 7 aceptados, 3 aceptados en parte, 5 falsos positivos y 5 rechazados.

| Vista | Hallazgo de la IA | Verificación del equipo | Decisión |
|-------|-------------------|-------------------------|----------|
| Contexto | Los sistemas externos tienen el mismo color que el sistema y no indican su tipo (2 hallazgos) | Correcto en el PNG: el exportador no los distingue visualmente | Aceptado: la descripción de cada sistema externo empieza con "Sistema externo:" |
| Contexto | La etiqueta "cada 10 / s" deja la "s" suelta | Correcto: defecto de render | Aceptado: etiqueta acortada a "Envía su posición cada 10 s" |
| Contexto | Hay protocolo en 2 de 4 líneas | En el nivel 1 la guía no exige tecnologías; la Figura 5 de la guía también pone protocolo solo en las líneas hacia sistemas externos | Rechazado |
| Contenedores, Componentes, Dinámico y Despliegue | El tipo de elemento se distingue solo por color y leyenda (4 hallazgos) | La leyenda de cada vista explica color y forma, que es lo que pide la lista; los ejemplos de la guía son iguales | Rechazado |
| Contenedores, Componentes, Dinámico y Despliegue | El glifo "▯" en la leyenda (límite del sistema, del contenedor o nodo) parece un error (4 hallazgos) | Falso positivo: la leyenda de las Figuras 6 a 9 de la guía muestra el mismo glifo; es una limitación de la fuente del exportador, no un error del modelo | Falso positivo |
| Contenedores | Las relaciones Pasajero y Operador dicen solo "Usa" | Correcto: es genérico y la lista pide la intención | Aceptado: "Consulta buses y ETA" y "Gestiona rutas y paraderos y atiende alertas" |
| Contenedores | La etiqueta PWA a API no incluye la gestión de rutas que muestra Componentes, y el protocolo de la BD es SQL/TCP aquí y SQL allá | Correcto: inconsistencia entre vistas | Aceptado: etiqueta completada y protocolo unificado a SQL/TCP |
| Componentes y Dinámico | Hay etiquetas cruzadas por líneas o por el borde del límite (2 hallazgos) | Correcto en el PNG: viene del autolayout | Aceptado en parte: se probó otro layout que mejoro en algo minimo al proyecto |
| Dinámico | No aparece el paso ETA a Rutas que sí muestra Componentes | Falso positivo: una vista dinámica muestra un solo escenario, no todas las relaciones; replica la secuencia del Lab 05, que lee el ETA ya calculado y no consulta Rutas | Falso positivo |
| Despliegue | R-03 y ADR-002 no se entienden en el diagrama | Correcto: son códigos internos | Aceptado: se reemplazaron por texto en la descripción |
| Despliegue | La descripción menciona Nginx y monitoreo pero no se dibujan | Correcto: el texto contradice el dibujo | Aceptado: se aclara que no se dibujan y se remite a despliegue.puml (Lab 04) |
| Despliegue | No aparecen GPS ni mapas, aunque sí están en Contenedores | Correcto: el tráfico GPS es el principal en producción | Aceptado: se agregaron los nodos Bus y Nube del proveedor de mapas |

Resultado final: General, Elementos y Relaciones cumplen en las 5 vistas.