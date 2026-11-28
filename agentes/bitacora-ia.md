# Bitácora de IA — Lab 10 (sistemas agénticos)

| # | Etapa | Asistente | Prompt (resumen) | Propuesta de la IA | Verificación | Decisión |
|---|---|---|---|---|---|---|
| 1 | E2 | Asistente de IA del grupo (vía `ModeloInteractivo`) | Contexto del agente con el objetivo del issue 1: un GPS sin datos hace fallar `actualizar_bus`. | Cuando el SDK responde `None`, tratarlo como bus sin señal: el adapter devuelve `None` y el servicio publica `sin_senal` (cambio en `gps.py` y `servicio.py`). | El agente ejecutó `pytest` y `test_issue_01.py` pasa para el operador A y el B; 7 pasos, 0 rechazos de contrato, 0 bloqueos. | Aceptada tras aprobar el diff |
| 2 | E3 | Claude (framework del agente) | Construir el mini framework de agentes con un contrato JSON por decisión. | `validar_decision` buscaba `d["accion"]` en un conjunto de herramientas sin comprobar su tipo. | `test_contrato.py` (acción como lista y como objeto) falló con `TypeError: unhashable type`; reproducido antes de corregir. | **Corregida:** se exige `isinstance(d["accion"], str)` antes de buscar; ahora rechaza sin excepción |
| 3 | E4 | Claude (herramienta `mapa_repo`) | Agregar `mapa_repo()` con `ast` documentada en el catálogo. | `_firma` pedía `ast.get_docstring()` de cualquier nodo del módulo. | `test_herramientas.py` falló con `TypeError: 'Expr' can't have docstrings`. | **Corregida:** se filtran solo `ClassDef` y `FunctionDef` antes de pedir el docstring |
| 4 | E5 | Asistente de IA del grupo (ejecutor y revisor) | Resolver el issue 2 con actor-crítico: el ejecutor sigue el plan del planificador y el revisor de solo lectura valida. | Ejecutor: diff en `servicio.py` con `paraderos_ord[i].paradero`. Revisor: `APROBADO`. | `pytest` completo, ejecutado por el humano: `AttributeError`, porque `obtener_paraderos_ordenados()` ya devuelve `Paradero`. La traza del revisor muestra 2 acciones (`ejecutar_pruebas`, `ver_cambios`): confirmar en `trazas/issue02_ac_revisor.jsonl` qué pruebas corrió y qué salida vio. | **Rechazada y corregida a mano.** Motivó la compuerta determinista de pruebas en E6 |
| 5 | E6 | Claude (humano en el circuito) | Activar `aprobar_edicion`, el estado `ESPERANDO_APROBACION` y redactar `delegacion.md`. | Mover la aprobación al núcleo con validación estricta `s`/`n`; además, una compuerta de pruebas tras cada `APROBADO` (adición no pedida). | 59 pruebas en verde; ensayo con un rechazo, una respuesta inválida y una aprobación; una prueba comprueba que `estados.puml` coincide con el código. | Aceptada, incluida la compuerta por el hallazgo de la entrada 4 |

## Clasificación de los errores

| Entrada | Quién se equivocó | Quién lo detectó |
|---|---|---|
| 2 y 3 | La IA, al escribir el código del framework | Las pruebas unitarias del propio framework |
| 4 | El agente ejecutor (el diff) y el revisor LLM (la aprobación) | El humano, con `pytest` completo |

**Regla de la guía cumplida:** la IA propone, el equipo decide y verifica. Las entradas 2, 3 y 4 son correcciones detectadas por pruebas.
