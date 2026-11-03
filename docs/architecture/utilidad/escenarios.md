# Escenarios de calidad de RutaSIT 2.0 (Lab 08, E1)

**Escenario de crecimiento (Tabla 11 de la guía):** de 300 a 1200 buses y 50 000 consultas de tiempo de llegada en hora punta.
**Restricciones vigentes:** R-01 a R-05 (Lab 04) y ADR-001 (monolito modular), ADR-002 (polling con caché corta) y ADR-003 (PostgreSQL + PostGIS, sin Redis).

Cálculos del crecimiento: 1200 buses × 1 posición cada 10 s = **120 mensajes/s** (≈ 10 368 000 posiciones al día, 4 veces las 2 592 000 de 300 buses).
50 000 consultas en una hora = **≈ 13,9 consultas/s en promedio**.

## Escenarios de seis partes

| ID | Fuente | Estímulo | Entorno | Artefacto | Respuesta | Medida |
|----|--------|----------|---------|-----------|-----------|--------|
| QA-01 | Flota de 1200 buses | Cada bus envía su posición cada 10 s (120 msg/s) | Hora punta, operación normal | Módulos Ubicaciones y ETA (ingesta) | El ETA afectado se recalcula y queda disponible para lectura | p95 ≤ 15 s desde la recepción en el servidor hasta estar disponible (buses sin señal excluidos) |
| QA-04 | Pasajeros | 50 000 consultas de ETA durante la hora punta | Hora punta, con la ingesta a 120 msg/s | API de consulta y proxy inverso con caché de 3 a 5 s (ADR-002) | Devuelve el ETA con "actualizado hace X s" | p95 de respuesta ≤ 1 s y menos de 0,1 % de errores 5xx |
| QA-02 | Un bus | Deja de enviar posición | Operación normal | Módulo ETA (consulta) | Muestra "dato desactualizado" sin afectar a los demás buses | ≤ 30 s hasta marcar el bus y 0 errores para los otros 1199 buses |
| QA-05 | Operador de infraestructura | Reinicio del servidor | Hora punta, un solo VPS (R-03) | Servidor de aplicación y base de datos | Se restablecen la ingesta y la consulta | Consulta disponible en ≤ 2 min; ETA vuelve a "Actualizado" en ≤ 30 s tras reanudarse la ingesta |
| QA-06 | Cliente no autorizado | Envía posiciones sin token de bus válido | Operación normal | API REST de ingesta | Rechaza la petición sin tocar el estado de ningún bus | 1000 posiciones por minuto, 0 aceptadas |
| QA-03 | Operador | Agrega una ruta o cambia el algoritmo de ETA | Desarrollo | Módulos Rutas y paraderos y ETA | El cambio se integra sin afectar otros módulos | ≤ 2 días-persona |
| QA-07 | Desarrollador | Incorpora un operador de GPS con otro formato | Desarrollo | Puerto `FuenteGps` y fábrica (Lab 07) | Se agrega un adaptador sin modificar el servicio | ≤ 1 día-persona |

## Calificación (importancia, dificultad)

| ID | Calificación inicial de la IA | Calificación final del equipo | Justificación |
|----|-------------------------------|-------------------------------|---------------|
| QA-01 | (H,H) | (H,H) | Es el atributo crítico del caso; cada bus recalcula ETA y el volumen se cuadruplica |
| QA-04 | (H,M) | (H,M) | Es la otra mitad del atributo crítico; la caché de ADR-002 acota la carga |
| QA-02 | (H,M) | (H,L) | Corrección: el estado "desactualizado" se deriva de la marca de tiempo de la última posición al consultar; ya existe y está probado en `test_posicion_de_mas_de_30_segundos_da_eta_desactualizado` |
| QA-05 | (M,M) | (M,M) | R-03 (un solo VPS) ya aceptó el riesgo; la mitigación es operativa, no estructural |
| QA-06 | (M,L) | (M,L) | El token por bus ya está en el diseño (Lab 04) |
| QA-03 | (M,L) | (M,L) | Strategy y Factory del Lab 07 ya cubren el cambio de algoritmo |
| QA-07 | (M,L) | (M,L) | El Adapter del Lab 07 ya lo permite (`test_open_closed_nuevo_operador_gps_sin_modificar_el_servicio`) |

## Supuestos que debe confirmar el equipo (⚠️)
1. "50 000 consultas" se interpretó **por hora punta** (13,9 consultas/s). Si fueran por minuto serían ≈ 833/s y cambiaría QA-04.
2. Las medidas de QA-04 (p95 ≤ 1 s), QA-05 (2 min y 30 s), QA-06 (1000/min) y QA-07 (1 día-persona) son propuestas de la IA; no están en `drivers.md`.
3. Los números de buses de QA-01 y QA-02 (1200 y 1199) reemplazan a los de Lab 04 (300 y 299) solo para el Lab 08; `drivers.md` no se modifica.
