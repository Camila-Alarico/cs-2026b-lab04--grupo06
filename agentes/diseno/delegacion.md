# Delegación progresiva — RutaSIT Arequipa

Regla: el agente propone; el contrato y la política filtran; el humano aprueba. Ningún agente fusiona su propio cambio, en ninguna etapa.

## Hoja de ruta: ejecutor → revisor → colaborador → gobernador

| Rol del humano | Qué hace el humano | Permisos del agente | Evidencia de las trazas para pasar a la siguiente etapa |
|---|---|---|---|
| **1. Ejecutor** | Hace el cambio él mismo; usa el agente como consulta. | Solo lectura: `listar_archivos`, `leer_archivo`, `buscar`, `mapa_repo`, `leer_notas`. Sin `editar_archivo` ni `ejecutar_comando`. | 3 issues explicados correctamente por el agente (la causa que indica coincide con la corrección humana) y 0 respuestas fuera del contrato en esas sesiones. |
| **2. Revisor** ← *hoy* | Aprueba o rechaza **cada edición** (`ESPERANDO_APROBACION`, respuesta `s`/`n`) y revisa el Pull Request. | Todas las herramientas del ejecutor sobre una copia del repo; `tests/` protegido; máx. 12 pasos; comandos de la lista permitida. | Racha de **5 issues seguidos** donde: la prueba del issue pasa a la primera propuesta, 0 ediciones rechazadas por el humano, 0 acciones bloqueadas por la política y 0 aprobaciones del revisor-agente revertidas por la compuerta de pruebas. |
| **3. Colaborador** | Aprueba solo las ediciones en rutas críticas (`servicio.py`, `gps.py`, `estados.py`); revisa el PR completo. | Edita sin aprobación en rutas de bajo riesgo (documentación, utilidades); mantiene `tests/` protegido; actor-crítico solo si el issue toca más de un módulo. | **10 issues** con tasa de rechazo humano ≤ 10 %, 0 incidentes de política (intentos de salir del sandbox o de ejecutar comandos prohibidos que no sean bloqueados) y contexto por agente estable (< 20 000 caracteres). |
| **4. Gobernador** | Define la política, los límites de pasos y el presupuesto; audita las trazas por muestreo; aprueba el PR sin revisión línea a línea. | Agente completo con compuerta determinista de pruebas y revisor-agente; la fusión sigue siendo humana. | Revisión trimestral de trazas sin hallazgos graves; cualquier incidente (cambio no pedido, prueba tocada, comando bloqueado repetido) devuelve al rol anterior. |

## Evidencia actual (trazas reales del grupo)

| Ejercicio | Qué se midió | Resultado |
|---|---|---|
| E2 — issue 1, agente único sin mapa ni notas | pasos / bloqueos / rechazos de contrato / contexto | 7 / 0 / 0 / 17 504 caracteres. Herramientas: `leer_archivo`, `editar_archivo`, `ejecutar_pruebas`. |
| E4 — issue 3, agente único con `mapa_repo` y notas | pasos | 11, con `mapa_repo`, `buscar`, `anotar`, `leer_notas`. Otro issue y más herramientas: no prueba por sí solo que el mapa ahorre pasos. |
| E5 — issue 2, agente único | acciones / contexto | 6 / 12 084 caracteres. |
| E5 — issue 2, actor-crítico | acciones / contexto | 8 / 27 468 caracteres en total (máx. 17 120 por agente). El revisor **aprobó** un diff que lanzaba `AttributeError` en `obtener_paraderos_ordenados()`; lo detectó el humano. |

## Decisión: hoy el agente queda en el rol 2 (Revisor)

- **A favor de avanzar:** 0 bloqueos y 0 rechazos de contrato en E2 y E5; el agente único resolvió el issue 2 en pocas acciones.
- **En contra:** en E5 el revisor-agente aprobó un cambio roto. Por eso el revisor LLM **no es una compuerta de calidad**: el orquestador ahora ejecuta la prueba del issue después de cada `APROBADO` y lo revierte si falla.
- **Para llegar al rol 3** faltan datos: la racha de 5 issues sin ediciones rechazadas y sin aprobaciones revertidas todavía no existe (hay 3 issues y un hallazgo negativo).
