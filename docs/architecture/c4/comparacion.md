# Comparación — RutaSIT Arequipa

## 1. Vista dinámica de C4 frente al diagrama de secuencia UML (E4)
La vista dinámica muestra los 4 pasos de "consultar el ETA" entre módulos y la base de datos, numerados y con su protocolo, y sirve para que arquitectos y el equipo técnico ubiquen el flujo dentro de la arquitectura. La secuencia UML del Lab 05 muestra más detalle: 10 líneas de vida con las operaciones exactas (`estaEnRuta()`, `esReciente()`), los mensajes de retorno, las ramas `alt` (sin datos, actualizado o desactualizado), el `opt` y el mensaje asíncrono de métricas. Por eso la secuencia UML sirve a los developers que implementan, y la vista dinámica a quien necesita entender el flujo sin entrar al código.

## 2. Escritura a mano frente a modelo exportado (E6)
| Aspecto | Escrito a mano (contexto-manual.puml) | Modelo exportado (workspace.dsl) |
|---------|----------------------------------------|----------------------------------|
| Tiempo invertido | Unos 15 minutos para 1 vista | Unos 40 minutos para el modelo completo; las 5 vistas salen del mismo archivo |
| Errores encontrados | Ninguno de sintaxis, pero hay que verificar a ojo que nombres, descripciones y protocolos coincidan con el modelo | `validate` sin errores. El borrador de otra IA tenía 5 errores de diseño (un solo sistema externo, 12 componentes a nivel de clases, dos servidores sin anidar, HTTP en vez de HTTPS y métricas en la base de datos), corregidos antes de validar |
| Si mañana cambia el nombre de un contenedor | Hay que editar cada archivo .puml y el README | Se cambia una línea en workspace.dsl y se vuelve a exportar |
| Coherencia entre vistas | Depende de la disciplina del autor | Garantizada: todas las vistas parten del mismo modelo |

Conclusión: escribir a mano sirve para una vista suelta, pero al crecer el número de vistas el modelo único evita inconsistencias.