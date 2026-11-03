# ATAM-lite de RutaSIT 2.0 (Lab 08, E3 y E7)

> **Nota de método:** no hubo grupo evaluador (el docente revisa al final). Una IA actuó como evaluador adversario (Prompt IA 3) sobre el árbol de utilidad, los ADR-001 a 003 y 005 y la iteración 1; cada hallazgo se verificó después contra la evidencia del repositorio. Es una autoevaluación asistida por IA, no una evaluación cruzada.

## Hallazgos
| ID | Tipo | Hallazgo | Evidencia | Respuesta del equipo |
|----|------|----------|-----------|----------------------|
| S1 | Sensibilidad | QA-01 depende del tiempo de servicio por posición: con 4 workers deja de cumplirse si la mediana supera ≈ 28 ms | Iteración 1: margen de 1,08x sin tácticas | Aceptado. Se adopta el histórico por lotes (margen 1,30x) y se medirá el tiempo real en un prototipo |
| S2 | Sensibilidad | QA-04 depende de la tasa de aciertos de la caché del proxy | Iteración 2: el p95 de lectura apenas cambia entre 0 % y 90 % de aciertos (46 a 34 ms con índice) | **Refutado en parte (falso positivo):** la sensibilidad real es la utilización del pool de workers compartido con la ingesta |
| T1 | Trade-off | Histórico por lotes: mejora la ingesta, pero una caída puede perder un lote del histórico | Iteración 1 (V2) | Aceptado: el estado actual se escribe de forma síncrona y el histórico no está en el camino del ETA |
| T2 | Trade-off | Caché de 3 a 5 s y polling de 5 a 10 s reducen la carga, pero el ETA que ve el pasajero puede tener hasta 15 s más de antigüedad que el medido en el servidor | ADR-002 y cálculo: 15 s + 5 s + 10 s | Aceptado: QA-01 y QA-02 se miden en el servidor y la app muestra "actualizado hace X s" |
| R1 | Riesgo (P=3, I=5) | Un solo VPS es punto único de falla | R-03 | Aceptado para el MVP; respaldo diario y plan de recuperación. La iteración 3 acota el tiempo de reinicio |
| R2 | Riesgo (P=3, I=4) | Tras una caída, los buses reenvían posiciones acumuladas y la ingesta casi no tiene capacidad ociosa (utilización de 0,93 sin tácticas) | Iteración 1; confirmado en la iteración 3 (112 s para recuperarse) | **Mitigado en la iteración 3:** 11,7 s |
| R3 | Riesgo (P=4, I=3) | El histórico crece 10,4 millones de filas al día sin retención ni particionado | ADR-003 ya lo advertía; 1200 × 8640 | Aceptado con plan: particionar por día y definir retención (⚠️ N días por decidir) |
| R4 | Riesgo (P=3, I=3) | Actualizar 120 veces por segundo las mismas 1200 filas del estado actual genera filas muertas y carga de autovacuum | Sin medición | Aceptado con mitigación: fillfactor bajo en esa tabla y autovacuum agresivo (⚠️ no medido) |
| R5 | Riesgo (P=2, I=3) | Un token de bus robado permite enviar posiciones falsas | QA-06 | Mitigación: token revocable por bus y límite de tasa; fuera de la zona crítica |
| NR1 | No riesgo | El monolito modular soporta 1200 buses | Simulación: p95 de 60 a 150 ms frente a 15 s | Aceptado, condicionado a que la mediana medida sea ≤ 22 ms |
| NR2 | No riesgo | La lógica de ETA en Python no limita la ingesta | Medición: 0,08 ms por posición con 40 paraderos | Aceptado |
| FP1 | Falso positivo | "El cálculo de ETA en Python no escala a 120 mensajes/s" | `fitness/medir_logica.py`: 120 × 0,08 ms ≈ 10 ms de CPU por segundo, cerca del 1 % de un núcleo | **Refutado con evidencia** |

## Matriz de probabilidad e impacto
