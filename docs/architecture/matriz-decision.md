# Matriz de decisión — RutaSIT Arequipa
## Alternativas
- **A. Monolito en capas síncrono:** una sola aplicación Django en capas. El bus envía su posición por POST, se guarda en PostgreSQL y el ETA se calcula al consultar con una query. Los pasajeros usan polling.
- **B. Monolito modular con ETA incremental:** una sola aplicación Django con módulos (Ubicaciones, ETA, Alertas, Rutas y paraderos) que se comunican por interfaces públicas. Al recibir cada posición se recalcula solo el ETA afectado y se guarda el estado actual del bus. La API de lectura sirve ese estado y el pasajero consulta con polling de 5–10 s. Redis y WebSocket quedan para una fase 2 si las pruebas de carga lo exigen.
- **C. Microservicios orientados a eventos:** servicios separados (ingesta, ETA, alertas, API) comunicados por un broker de mensajes, cada uno desplegado de forma independiente.

## Criterios y pesos (suman 100 %)
| Criterio                    | Peso | Justificación (driver relacionado)                                  |
|-----------------------------|------|---------------------------------------------------------------------|
| Rendimiento en tiempo real  | 25 % | QA-01: ETA en ≤ 15 s con 300 buses; es el atributo crítico         |
| Tiempo de entrega           | 20 % | R-01: el MVP debe salir en 1 mes                                    |
| Simplicidad operativa       | 20 % | R-02: un solo developer debe construir y operar todo                |
| Modificabilidad             | 20 % | QA-03: agregar rutas o cambiar el ETA en ≤ 2 días-persona           |
| Costo operativo             | 15 % | R-03: presupuesto bajo, un solo servidor                            |

## Matriz 
| Criterio (peso)                   | A    | B    | C    |
|-----------------------------------|------|------|------|
| Rendimiento en tiempo real (25 %) | 3    | 4    | 5    |
| Tiempo de entrega (20 %)          | 5    | 4    | 2    |
| Simplicidad operativa (20 %)      | 5    | 4    | 2    |
| Modificabilidad (20 %)            | 2    | 4    | 4    |
| Costo operativo (15 %)            | 5    | 5    | 3    |
| **Total ponderado**               | 3,90 | 4,15 | 3,30 |

Total ponderado = Σ (peso × puntaje). Ejemplo (B): 0,25×4 + 0,20×4 + 0,20×4 + 0,20×4 + 0,15×5 = 4,15.

## Análisis de las respuestas de la IA
Se consultó a Claude y a ChatGPT con el mismo Prompt 1 y luego con el Prompt 2 (ver [bitácora](bitacora-ia.md)). Ambas coincidieron en descartar microservicios para 1 developer, 1 mes y un servidor (30 mensajes/s no lo justifican).

La decisión final **difiere parcialmente de ambas recomendaciones**:
- **Claude** recomendó el monolito modular con cola en Redis y workers. En su crítica adversarial reconoció que esa cola podría ser complejidad innecesaria y sugirió una variante reducida. Adoptamos la variante reducida (sin cola al inicio).
- **ChatGPT** recomendó monolito modular con WebSocket. En su crítica admitió que el polling podría bastar para el MVP. Adoptamos polling y dejamos WebSocket para una fase 2.

### Afirmaciones de la IA incorrectas, exageradas o inconsistentes
| IA | Afirmación | Verificación | Resultado |
|----|-----------|--------------|-----------|
| Claude | "B es la única alternativa que ataca directamente el atributo crítico" | La propia IA la retractó en el Prompt 2. Con la última posición de cada bus guardada, calcular el ETA al leer es aritmética barata; lo que degrada A es la BD en el camino de lectura. | Exagerada |
| Claude | "Si Redis cae, el estado se reconstruye desde PostgreSQL" | Solo es cierto si cada posición cruda se persiste antes de encolarse; si no, hay pérdida de mensajes. La IA lo admitió en el Prompt 2. | Inconsistente |
| ChatGPT | Recomendó WebSocket para el MVP | La carga de WebSocket depende de los pasajeros conectados, no de los 300 buses, y R-02 limita el tiempo del único developer. La IA admitió que el polling podría ser suficiente. | No respeta R-01 y R-02 |
| Claude | "Mensajes cada 10 s con ETA ≤ 15 s (p95)" sin definir la medición | Con reporte cada 10 s, el dato puede llegar con hasta 10 s de antigüedad. Se define el p95 desde la recepción en el servidor hasta que el ETA está disponible para lectura. | Corregida en QA-01 |

## Conclusión
Elegimos el monolito modular con ETA incremental (B) porque obtiene el mayor puntaje (4,15), ataca el atributo crítico precalculando el ETA al recibir cada posición, y es construible y operable por un solo developer en 1 mes sobre un servidor. Ver [ADR-001](adr/001-estilo-arquitectonico.md).