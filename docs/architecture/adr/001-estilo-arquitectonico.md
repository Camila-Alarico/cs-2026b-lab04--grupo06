# ADR-001: Adoptar un monolito modular con ETA incremental para el MVP de RutaSIT

- Estado: Aceptado
- Fecha: 2026-10-03
- Decisores: Dai (trabajo individual)

## Contexto
RutaSIT debe mostrar la ubicación de 300 buses y actualizar el ETA en ≤ 15 s (QA-01), con posiciones GPS cada 10 s (RF-01, RF-02, RF-03), unos 30 mensajes por segundo. El MVP debe salir en 1 mes (R-01) con un solo developer que domina Python, Java, Django y SQL (R-02), en un solo servidor de bajo costo (R-03). Los buses envían por red móvil con cortes posibles (R-04, QA-02) y se debe poder agregar rutas o cambiar el algoritmo de ETA en ≤ 2 días-persona (QA-03).

## Alternativas consideradas
1. Monolito en capas síncrono (3,90): el más simple, pero el ETA se calcula al consultar y la base de datos queda en el camino de lectura; modificabilidad baja.
2. Monolito modular con ETA incremental (4,15): elegido.
3. Microservicios orientados a eventos (3,30): mejor rendimiento y aislamiento, pero exige operar un broker y varios servicios; excede R-01, R-02 y R-03.

## Decisión
Usaremos un monolito modular en Django con cuatro módulos (Ubicaciones, ETA, Alertas, Rutas y paraderos) que se comunican solo mediante interfaces públicas. Al recibir cada posición se recalculará únicamente el ETA afectado y se guardará el estado actual del bus con su marca de tiempo. Los datos se almacenarán en PostgreSQL con PostGIS, con un esquema por módulo, y los pasajeros consultarán el estado con polling. No usaremos Redis ni WebSocket en el MVP.

## Consecuencias
- Positivas: un solo despliegue y un solo servidor (R-03); el ETA se precalcula, así que su latencia no depende de cuántos pasajeros consulten (QA-01); entrega viable en 1 mes por un solo developer (R-01, R-02); los módulos pueden separarse más adelante si la carga lo exige (QA-03).
- Negativas / riesgos: un fallo del servidor afecta a todo el sistema; hay que respetar los límites entre módulos (se usará import-linter en la CI); el polling genera más peticiones y un dato puede verse con hasta unos segundos extra de antigüedad; la calidad del ETA depende de asociar bien la posición a la ruta, lo que debe medirse con llegadas reales.