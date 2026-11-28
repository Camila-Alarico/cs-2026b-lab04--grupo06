# Observación del sistema agéntico — RutaSIT Arequipa (Lab 10, E7)

Fuente: `python agentes/agente/traza.py` sobre las trazas de `agentes/trazas/`. "Pasos" son las acciones registradas por `traza.py` (sin contar la respuesta final).

## Métricas de las trazas de los 3 issues

| Issue | Ejercicio / variante | Rondas | Pasos | Bloqueadas por la política | Rechazadas por el contrato | Herramientas usadas | Contexto final (caracteres) |
|---|---|---|---|---|---|---|---|
| 1 | E2 · agente único (sin mapa ni notas) | 1 | 7 | 0 | 0 | `editar_archivo`, `ejecutar_pruebas`, `leer_archivo` | 17 504 |
| 3 | E4 · agente único con `mapa_repo` y notas | 1 | 10 | 0 | 0 | `anotar`, `buscar`, `editar_archivo`, `ejecutar_pruebas`, `leer_archivo`, `leer_notas`, `mapa_repo` | 17 596 |
| 2 | E5 · agente único | 1 | 6 | 0 | 0 | `anotar`, `editar_archivo`, `ejecutar_pruebas`, `leer_archivo` | 12 084 |
| 2 | E5 · actor-crítico (total) | 1 | 8 | 0 | 0 | `anotar`, `editar_archivo`, `ejecutar_pruebas`, `leer_archivo`, `ver_cambios` | 27 468 en total |

Detalle del actor-crítico (issue 2):

| Agente | Pasos | Herramientas usadas | Contexto final (caracteres) |
|---|---|---|---|
| Planificador | 0 | (ninguna: solo razona) | 2 652 |
| Ejecutor | 6 | `anotar`, `editar_archivo`, `ejecutar_pruebas`, `leer_archivo` | 17 120 |
| Revisor (solo lectura) | 2 | `ejecutar_pruebas`, `ver_cambios` | 7 696 |

## Trayectoria de una ejecución (issue 1, E2)

<!--DIAGRAMA-->

## Lectura de las trazas

| Pregunta | Respuesta según las trazas |
|---|---|
| ¿Se resolvieron los issues? | Sí, los tres: sus pruebas `test_issue_0N` pasan y la suite completa está en verde. El issue 2 requirió una corrección manual del humano (ver bitácora, entrada 4). |
| ¿El contrato rechazó algo? | No: 0 rechazos en las 4 ejecuciones reales. El asistente respetó siempre el protocolo JSON; el contrato solo se ejerció con pruebas unitarias (12 decisiones inválidas propias en `test_contrato.py`). |
| ¿La política bloqueó algo? | No: 0 acciones bloqueadas. Ninguna traza intentó salir del sandbox ni ejecutar comandos prohibidos; esa capa está verificada por pruebas, no por incidentes reales. |
| ¿`mapa_repo` y las notas redujeron pasos o contexto? (E4 frente a E2) | No: 10 pasos frente a 7 (+3) y 17 596 caracteres frente a 17 504 (+0,5 %). Limitación: son issues distintos. En el issue 2, el agente único resolvió con 6 pasos y 12 084 caracteres sin usar `mapa_repo`. |
| ¿Compensó el actor-crítico? (E5) | No en este caso: 8 acciones frente a 6 (+33 %) y 27 468 caracteres frente a 12 084 (×2,3). Además, el revisor aprobó un diff con `AttributeError`; lo detectó el humano con `pytest` completo. |
| ¿Qué intervención humana hizo falta? | Corregir a mano el diff del issue 2 (E5); desde E6, aprobar cada edición (`s`/`n`) y fusionar el Pull Request. |

**Conclusión:** para este caso el agente único con aprobación humana por edición y una compuerta determinista de pruebas es la opción más simple que funciona (parsimonia). Con 3 issues y 4 ejecuciones la muestra es pequeña: estas métricas orientan la decisión, no la demuestran.
