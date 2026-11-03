# ADR-006: Escribir el histórico por lotes y mantener PostgreSQL sin Redis para 1200 buses

- Estado: Aceptado
- Fecha: 2026-11-02
- Decisores: Dai (trabajo individual)

## Contexto
El escenario de crecimiento lleva la flota de 300 a 1200 buses: 120 mensajes por segundo, unos 10,4 millones de posiciones al día. QA-01 exige el ETA disponible en ≤ 15 s (p95). ADR-003 dejó una condición: evaluar Redis solo si las pruebas de carga lo exigen. Restricciones: R-01 (1 mes), R-02 (1 developer), R-03 (un servidor).

## Alternativas consideradas
1. Sin cambios: p95 de 150 ms, pero utilización de 0,93 y margen de solo 1,08x.
2. Histórico por lotes fuera del camino crítico: margen de 1,30x, sin componentes nuevos.
3. Redis para el estado actual: margen de 1,27x, un componente más.
4. Escalar a 8 workers (segundo VPS): margen de 2,17x, duplica el costo.
5. Microservicios con Kafka: contradice ADR-001, R-01, R-02 y R-03.

## Decisión
Escribir el histórico en lotes de unas 10 posiciones, fuera del camino que deja el ETA disponible. El estado actual y el ETA se siguen escribiendo de forma síncrona. No se adopta Redis (no se cumple la condición de ADR-003) ni microservicios. El segundo VPS queda como plan B.

## Evidencia
Simulación M/G/c de 30 min de hora punta con 4 workers (`fitness/rendimiento.py`; iteración 1): QA-01 se cumple en todas las variantes (p95 de 60 a 150 ms). Margen frente al tiempo de servicio: 1,08x sin tácticas y 1,30x con lotes. Medición real de CPU del ETA: 0,08 ms por posición.

## Consecuencias
- Positivas: más margen de seguridad sin componentes nuevos; el ETA no depende del histórico.
- Negativas / riesgos (trade-off aceptado): el histórico puede retrasarse unos segundos y una caída puede perder un lote (no el estado actual); los tiempos de servicio de la simulación no están medidos, así que hay que medirlos en un prototipo; se revisa la decisión si la mediana medida supera 22 ms.