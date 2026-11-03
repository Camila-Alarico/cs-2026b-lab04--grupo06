# ADR-007: Indexar la consulta del ETA por paradero y mantener la caché del proxy

- Estado: Aceptado
- Fecha: 2026-11-02
- Decisores: Dai (trabajo individual)

## Contexto
QA-04: 50 000 consultas de ETA en la hora punta (13,9 por segundo) con p95 ≤ 1 s, mientras la ingesta de 1200 buses usa los mismos workers. ADR-002 ya fijó polling de 5 a 10 s con caché de 3 a 5 s en el proxy.

## Alternativas consideradas
1. Sin tácticas: p95 de 147 ms, margen de 1,12x.
2. Índice en la consulta por paradero: 46 ms, margen de 1,31x.
3. Solo caché del proxy (70 % de aciertos supuesto): 81 ms, margen de 1,28x.
4. Índice y caché: 27 ms, margen de 1,35x.
5. WebSocket: contradice ADR-002 y no hace falta.
6. Segundo VPS o réplica de lectura: duplica el costo (R-03).

## Decisión
Crear un índice sobre el ETA por paradero y mantener la caché de ADR-002. No se adopta WebSocket. El segundo VPS queda como plan B.

## Evidencia
Simulación de `fitness/consultas.py` (iteración 2): QA-04 se cumple en todas las variantes. El índice es la táctica dominante; la curva de aciertos de la caché es casi plana hasta el 90 %, así que su tasa no es un punto de sensibilidad en este modelo.

## Consecuencias
- Positivas: consultas más rápidas con un costo casi nulo; la caché ya estaba decidida.
- Negativas / riesgos (trade-off aceptado): la caché agrega hasta 5 s de antigüedad percibida; el índice vuelve algo más lentas las escrituras y ocupa espacio (no está en el modelo, ⚠️ por medir); el índice debe usar una columna que no cambie al actualizar para no impedir las actualizaciones HOT de PostgreSQL.