# ADR-003: Guardar el estado actual de los buses en PostgreSQL, sin Redis en el MVP

- Estado: Aceptado
- Fecha: 2026-10-03
- Decisores: Camila

## Contexto
El sistema recibe unos 30 mensajes por segundo (300 buses cada 10 s, RF-01) y debe servir la última posición y el ETA de cada bus (RF-02, RF-03) con el ETA actualizado en ≤ 15 s (QA-01). Los buses pueden perder señal y el sistema debe seguir funcionando con datos marcados como desactualizados (QA-02, R-04). Hay un solo developer (R-02), un solo servidor de bajo costo (R-03) y 1 mes de plazo (R-01). Claude propuso un pipeline con cola y estado en Redis, pero en su crítica detectó que reconstruir el estado desde PostgreSQL solo funciona si las posiciones crudas se guardan antes de encolarse.

## Alternativas consideradas
1. PostgreSQL con PostGIS: una tabla de estado actual (una fila por bus, actualizada en cada posición) y una tabla de histórico de posiciones con política de retención.
2. Redis para el estado actual y PostgreSQL para rutas, paraderos e histórico.

## Decisión
Usaremos PostgreSQL con PostGIS como único almacenamiento. Cada posición válida actualizará la fila del bus en la tabla de estado actual, con su marca de tiempo GPS y de recepción, y se registrará en la tabla de histórico. No usaremos Redis en el MVP; se evaluará solo si las pruebas de carga con 300 buses simulados lo exigen.

## Consecuencias
- Positivas: hay un solo componente de datos y es durable, así que un reinicio no pierde el estado y no hay que reconstruirlo (QA-02); se reduce el número de piezas que un solo developer debe operar (R-02, R-03); el mismo SQL sirve para consultas, alertas e histórico.
- Negativas / riesgos: las escrituras de 30 posiciones por segundo y las lecturas de pasajeros comparten la misma base de datos, por lo que debe comprobarse con el simulador y con pruebas de lectura; el histórico crece unas 2,6 millones de filas al día y necesita una política de retención; si la base de datos se satura, habrá que introducir una caché y rediseñar esa parte.