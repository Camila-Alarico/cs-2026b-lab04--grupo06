# Comparación — RutaSIT Arequipa

## 1. Vista dinámica de C4 frente al diagrama de secuencia UML (E4)
La vista dinámica muestra los 4 pasos de "consultar el ETA" entre módulos y la base de datos, numerados y con el protocolo, y sirve para que arquitectos y el equipo técnico entiendan el flujo de un vistazo. La secuencia UML del Lab 05 muestra más detalle: 10 líneas de vida con las operaciones exactas (`estaEnRuta()`, `esReciente()`), los mensajes de retorno, las ramas `alt` (sin datos, actualizado o desactualizado), el `opt` y el mensaje asíncrono de métricas. Por eso la UML sirve a los developers que implementan, y la vista C4 a quien necesita ubicar el flujo dentro de la arquitectura.

## 2. Escritura a mano frente a modelo exportado (E6)
| Aspecto | Escrito a mano (contexto-manual.puml) | Modelo exportado (workspace.dsl) |
|---------|----------------------------------------|----------------------------------|
| Tiempo invertido | 20 <minutos> para 1 vista | 180 <minutos> para el modelo completo; las 5 vistas salen del mismo archivo |
| Errores encontrados | ⚠️ <por ejemplo, diferencias de texto respecto al modelo> | ⚠️ <errores de validate, o "ninguno"> |
| Si mañana cambia el nombre de un contenedor | Hay que editar cada archivo .puml y el README | Se cambia una línea en workspace.dsl y se vuelve a exportar |
| Coherencia entre vistas | Depende de la disciplina del autor | Garantizada: todas las vistas parten del mismo modelo |

Conclusión: la escritura a mano sirve para una vista suelta, pero a medida que crece el número de vistas el modelo único evita inconsistencias.