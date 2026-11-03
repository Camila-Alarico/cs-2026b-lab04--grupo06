# Fitness functions (Lab 08, E5)

| ID | Tipo | Qué verifica | Degradación que detecta |
|----|------|--------------|-------------------------|
| FF-01 | Estructural | Capas sin ciclos (ADR-001) | Un módulo de abajo importa a uno de arriba |
| FF-02 | Estructural | Solo la fábrica conoce adaptadores y servicios externos (ADR-005) | El servicio importa un adaptador concreto |
| FF-03 | Estructural | Los módulos no se invocan entre sí (ADR-001) | Dependencia entre Ubicaciones, ETA o Notificaciones |
| FF-04 | Calidad (QA-01) | p95 ≤ 15 s con 1200 buses y 20 % de margen | Quitar el histórico por lotes |
| FF-05 | Calidad (QA-04) | p95 de consulta ≤ 1 s con 20 % de margen | Quitar el índice y la caché a la vez |
| FF-06 | Calidad (QA-05) | ETA al día en ≤ 30 s tras reiniciar | Volver al procesamiento FIFO de la ráfaga |
| FF-07 | Calidad (QA-02) | Un bus sin señal no afecta a los otros 1199 | Un error de un bus que se propague a los demás |

## Violación introducida y revertida
Salida de `lint-imports` con un atajo de `servicio` hacia `gps` y de `gps` hacia `servicio`:

FF-01 Capas del monolito modular sin ciclos (ADR-001) BROKEN
FF-02 Solo la fabrica conoce los adaptadores y los servicios externos (ADR-005) BROKEN
FF-03 Los modulos no se invocan entre si (ADR-001) BROKEN
Contracts: 0 kept, 3 broken.

rutasit.gps is not allowed to import rutasit.servicio: rutasit.gps -> rutasit.servicio (l.8)
rutasit.servicio is not allowed to import rutasit.gps: rutasit.servicio -> rutasit.gps (l.2)

Después de revertir: Contracts: 3 kept, 0 broken.