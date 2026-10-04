# Bitácora de uso de IA — <Nombre del caso>
| # | Fecha | Herramienta | Prompt (resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión
|
|01|01/10/2026|Claude|Actúa como arquitecto de software senior. Contexto: plataforma "RutaSIT Arequipa" para seguimiento en tiempo real de los buses del Sistema Integrado de Transporte. 
Restricciones: 1 solo developer con experiencia en Python, Java, Django y SQL; MVP en producción en 1 mes; presupuesto bajo. Tarea: propón 3 alternativas de estilo arquitectónico.||||
| 1 | 29/09 | Claude | Prompt 1 adaptado: 3 alternativas para ... | Microservicios + Kubernetes |
Excede R-01 (1 mes) y R-03 (presupuesto) | Rechazada |
| 2 | ... | ... | ... | ... | ... | Aceptada
/ Corregida / Rechazada |

# Bitácora de uso de IA — RutaSIT Arequipa

| # | Fecha | Herramienta | Prompt (resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|---|-------|-------------|------------------|-------------------|------------------------------|----------|
| 1 | 01/10 | Claude | Prompt 1 adaptado: 3 alternativas para RutaSIT (300 buses, 1 dev, 1 mes, 1 servidor) | A: monolito Django síncrono. B: monolito modular con pipeline (Redis + workers). C: microservicios + Kafka. Recomendó B. | Cálculo: 300/10 s = 30 mensajes/s, cabe en un servidor. C excede R-01, R-02 y R-03. Se corrigió el requisito de ETA ≤ 15 s, mal definido con reporte cada 10 s: se mide desde la recepción en el servidor. | Corregida |
| 2 | 01/10 | Claude | Prompt 2: crítica adversarial a la alternativa B | 5 riesgos: supuestos de hardware y reloj, cola de Redis, ETA correcto vs rápido, aislamiento solo lógico, costo de operar. Retractó que B fuera "la única" que ataca el atributo crítico y propuso una B reducida sin Redis. | Se detectó la incoherencia "si Redis cae se reconstruye desde PostgreSQL" (solo vale si el crudo se persiste antes de encolar). Se verificó que 2,6 M posiciones/día × ~100 B ≈ 260 MB/día, coherente con "cientos de MB". | Aceptada (B reducida) |
| 3 | 02/10 | ChatGPT | Prompt 1 adaptado: el mismo contexto y restricciones | 1: monolito modular + polling. 2: monolito modular + WebSocket. 3: event-driven/microservicios. Recomendó la 2. | WebSocket depende de los pasajeros conectados, no de los buses; añade reconexiones y estado; R-02 limita a 1 developer. La alternativa 3 coincide con el descarte de Claude. | Rechazada (WebSocket en el MVP) |
| 4 | 02/10 | ChatGPT | Prompt 2: crítica adversarial a la alternativa 2 | 5 riesgos: WebSocket como cuello de botella, servidor único, cortes de red, ETA más complejo de lo previsto, complejidad operativa. Señaló que se puede cumplir el p95 y dar un ETA obsoleto. | Se acepta separar latencia de frescura: guardar timestamp GPS y de recepción, y marcar "dato desactualizado". La propia IA recomendó empezar con polling. | Aceptada |
| 5 | 03/10 | Claude | Generar el Mermaid de la alternativa B a partir de matriz-decision.md | Diagrama con 3 actores, 4 módulos, capa de presentación e infraestructura, PostgreSQL y proveedor de mapas | Se validó en mermaid.live y GitHub; se comprobó que cada módulo cubre RF-01 a RF-06 y que ETA y Alertas dependen de Ubicaciones y Rutas solo por interfaz pública | Aceptada |

> Faltan entradas para llegar a 5: la siguiente será la generación del diagrama Mermaid (E3), revisada línea por línea.

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