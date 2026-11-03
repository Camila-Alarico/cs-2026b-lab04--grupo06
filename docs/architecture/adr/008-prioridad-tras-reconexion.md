# ADR-008: Priorizar la posición más reciente de cada bus tras una caída del servidor

- Estado: Aceptado
- Fecha: 2026-11-02
- Decisores: Dai (trabajo individual)

## Contexto
QA-05: tras reiniciar el servidor en hora punta, el ETA de todos los buses debe estar al día en ≤ 30 s después de reanudarse la ingesta. Si los buses acumulan las posiciones no enviadas (R-04) y las reenvían al reconectarse, llegan hasta 14 400 posiciones de golpe con una ingesta de utilización 0,93. Esta decisión mitiga el riesgo R2 del ATAM-lite. QA-02 (bus sin señal) se cubre por diseño.

## Alternativas consideradas
1. Procesar en orden de llegada (FIFO): 112 s sin tácticas y 93 s con lotes.
2. Escalar a 8 workers: 56 s, no cumple y duplica el costo.
3. Cola persistente de pendientes (Redis o Kafka): un componente más; contradice ADR-001 y ADR-003.
4. Procesar primero la posición más reciente de cada bus; las anteriores solo van al histórico por lotes con baja prioridad: 11,7 s.

## Decisión
La API de ingesta aceptará un lote de posiciones por bus: la más reciente actualiza estado y ETA con prioridad; las anteriores van solo al histórico por lotes, con baja prioridad.

## Evidencia
Simulación de `fitness/recuperacion.py` (iteración 3): caída de 120 s con 12 posiciones acumuladas por bus. Solo la variante 4 cumple QA-05 y se mantiene en ≈ 12 s para caídas de 30 a 300 s. QA-02 está probado en el código y por FF-07.

## Consecuencias
- Positivas: la recuperación no depende del tamaño de la ráfaga; no hay componentes nuevos.
- Negativas / riesgos (trade-off aceptado): el histórico se completa con retraso tras una caída; depende de que los buses acumulen posiciones (supuesto de hardware ⚠️); el código del Lab 07 aún no tiene `recibir_lote`; la medida de QA-02 es del servidor y el pasajero puede verla hasta 45 s después (caché y polling).