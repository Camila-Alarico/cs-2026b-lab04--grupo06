# Bitácora de uso de IA — RutaSIT Arequipa

| # | Fecha | Herramienta | Prompt (resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|---|-------|-------------|------------------|-------------------|------------------------------|----------|
| 1 | 01/10 | Claude | Prompt 1 adaptado: 3 alternativas para RutaSIT (300 buses, 1 dev, 1 mes, 1 servidor) | A: monolito Django síncrono. B: monolito modular con pipeline (Redis + workers). C: microservicios + Kafka. Recomendó B. | Cálculo: 300/10 s = 30 mensajes/s, cabe en un servidor. C excede R-01, R-02 y R-03. Se corrigió el requisito de ETA ≤ 15 s, mal definido con reporte cada 10 s: se mide desde la recepción en el servidor. | Corregida |
| 2 | 01/10 | Claude | Prompt 2: crítica adversarial a la alternativa B | 5 riesgos: supuestos de hardware y reloj, cola de Redis, ETA correcto vs rápido, aislamiento solo lógico, costo de operar. Retractó que B fuera "la única" que ataca el atributo crítico y propuso una B reducida sin Redis. | Se detectó la incoherencia "si Redis cae se reconstruye desde PostgreSQL" (solo vale si el crudo se persiste antes de encolar). Se verificó que 2,6 M posiciones/día × ~100 B ≈ 260 MB/día, coherente con "cientos de MB". | Aceptada (B reducida) |
| 3 | 02/10 | ChatGPT | Prompt 1 adaptado: el mismo contexto y restricciones | 1: monolito modular + polling. 2: monolito modular + WebSocket. 3: event-driven/microservicios. Recomendó la 2. | WebSocket depende de los pasajeros conectados, no de los buses; añade reconexiones y estado; R-02 limita a 1 developer. La alternativa 3 coincide con el descarte de Claude. | Rechazada (WebSocket en el MVP) |
| 4 | 02/10 | ChatGPT | Prompt 2: crítica adversarial a la alternativa 2 | 5 riesgos: WebSocket como cuello de botella, servidor único, cortes de red, ETA más complejo de lo previsto, complejidad operativa. Señaló que se puede cumplir el p95 y dar un ETA obsoleto. | Se acepta separar latencia de frescura: guardar timestamp GPS y de recepción, y marcar "dato desactualizado". La propia IA recomendó empezar con polling. | Aceptada |
| 5 | 03/10 | Claude | Generar el Mermaid de la alternativa B a partir de matriz-decision.md | Diagrama con 3 actores, 4 módulos, capa de presentación e infraestructura, PostgreSQL y proveedor de mapas | Se validó en mermaid.live y GitHub; se comprobó que cada módulo cubre RF-01 a RF-06 y que ETA y Alertas dependen de Ubicaciones y Rutas solo por interfaz pública | Aceptada |
| 6 | 01/11 | Claude | E1: escenarios de calidad de seis partes con (importancia, dificultad) para el crecimiento de RutaSIT a 1200 buses y 50 000 consultas | 7 escenarios (4 atributos) y calificaciones; QA-02 propuesto como (H,M) | Se contrastó QA-02 con la prueba existente de ETA desactualizado: se corrigió a (H,L). Se recalcularon las cifras de carga (120 msg/s y 13,9 consultas/s) | Corregida |
| 7 | 02/11 | Claude | E2: iteración 1 de ADD para QA-01 con 1200 buses; tácticas candidatas y simulación con evidencia antes/después | 5 conceptos (microservicios + Kafka, Redis, histórico por lotes, 8 workers, control), simulación M/G/c y medición de CPU del código del Lab 07 | Se ejecutó la simulación con 5 semillas y se midió la CPU real; los supuestos de tiempo de servicio no están medidos. Se rechazaron Redis y microservicios | Aceptada |
| 8 | 02/11 | Claude | E3: evaluador adversario ATAM-lite sobre el árbol, los ADR 001 a 003 y 005 y la iteración 1 | 12 hallazgos: 2 sensibilidades, 2 trade-offs, 5 riesgos y 3 no riesgos o falsos positivos | Se verificó cada hallazgo contra la evidencia. Refutados: S2 (la caché no es sensible; iteración 2) y FP1 (ETA en Python no escala; medición de 0,08 ms) | Corregida |
| 9 | 02/11 | Claude | E4: iteración 2 y 3 (QA-05 y QA-02) con simulación de recuperación tras reinicio | Variantes R0 a R3 y script `fitness/recuperacion.py` | Se ejecutó la simulación: solo la priorización de la última posición cumple. Se rechazaron 8 workers y una cola persistente | Aceptada |
| 10 | 02/11 | Claude | E5: contratos de import-linter y fitness functions de calidad para los escenarios | 3 contratos estructurales, 4 pruebas de calidad y el workflow de Actions | Se ejecutó lint-imports (3 kept), se introdujeron dos violaciones (3 broken, exit 1) y se revirtieron. Corrección: la IA afirmó que quitar solo el índice rompe FF-05; al probar las variantes, solo la rompe quitar índice y caché a la vez (C2 conserva 1,28x). Se corrigió el docstring | Corregida |
| 11 | 02/11 | Claude | E6: ADR-006 a ADR-008 y escenarios [QA-xx] en workspace.dsl | Tres ADR con evidencia y trade-off, y 15 elementos del DSL con su escenario | `structurizr validate` pasó (exit 0) antes y después de editar; se comprobó que no cambian nombres, relaciones ni vistas | Aceptada |

## Anexo: prompts

### Prompt 1 (usado en Claude y en ChatGPT)
```
Actúa como arquitecto de software senior con experiencia en sistemas de transporte y sistemas en tiempo real para presupuestos bajos.
Contexto: plataforma "RutaSIT Arequipa" para seguimiento en tiempo real de los buses del Sistema Integrado de Transporte. 300 buses envían su posición GPS cada 10 s; los pasajeros ven los buses en un mapa y consultan el tiempo estimado de llegada (ETA) a un paradero; el operador recibe alertas de desvío o congestión.
Restricciones: 1 solo developer con experiencia en Python, Java, Django y SQL; MVP en producción en 1 mes; presupuesto bajo (un solo servidor en la nube); los buses envían por red móvil con cortes posibles; no se almacenan datos personales del pasajero (Ley 29733).
Atributo crítico: el ETA debe actualizarse en ≤ 15 s (p95).
Tarea: propón 3 alternativas de estilo arquitectónico. Para cada una indica fortalezas, debilidades, riesgos y qué atributos de calidad favorece o penaliza.
Formato: tabla comparativa en Markdown y, al final, tu recomendación justificada.
No inventes APIs ni capacidades de servicios; si no estás seguro, indícalo.
```

### Prompt 2 (usado en Claude y en ChatGPT)
```
Ahora actúa como "abogado del diablo". Critica duramente la alternativa que
recomendaste: ¿qué supuestos no se cumplen con nuestras restricciones?, ¿qué podría
fallar en producción?, ¿qué costo oculto tiene? Enumera los 5 riesgos más graves y,
para cada uno, una táctica arquitectónica de mitigación.
```
