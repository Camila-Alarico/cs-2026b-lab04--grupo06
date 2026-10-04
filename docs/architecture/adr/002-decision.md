# ADR-002: Entregar el ETA al pasajero con polling HTTP en el MVP

- Estado: Aceptado
- Fecha: 2026-10-03
- Decisores: Camila

## Contexto
El pasajero debe ver los buses en un mapa y consultar el ETA de un paradero (RF-02, RF-03), con el ETA actualizado en ≤ 15 s desde la recepción del GPS (QA-01). El MVP debe salir en 1 mes (R-01) con un solo developer (R-02) y un solo servidor de bajo costo (R-03). La carga de un canal persistente depende de cuántos pasajeros estén conectados a la vez, y ese número es desconocido. Las IAs consultadas recomendaron WebSocket, pero en su crítica reconocieron que el polling podría ser suficiente para un MVP.

## Alternativas consideradas
1. Polling HTTP: el cliente consulta la API cada 5–10 s, con peticiones condicionales (ETag) y una caché corta de 3–5 s en el proxy.
2. WebSocket: el servidor envía las actualizaciones a los clientes conectados apenas se recalcula el ETA.

## Decisión
Usaremos polling HTTP cada 5–10 s sobre la API de lectura, con caché corta en el proxy inverso. La app mostrará "actualizado hace X s" para que el pasajero sepa la antigüedad del dato. No usaremos WebSocket en el MVP; se reevaluará solo si las pruebas de carga con pasajeros simulados muestran que el polling no alcanza.

## Consecuencias
- Positivas: es la opción más simple de construir y operar (R-01, R-02); no hay conexiones persistentes ni reconexiones que manejar; la caché corta hace que el costo de lectura no crezca con el número de pasajeros (R-03).
- Negativas / riesgos: genera más peticiones HTTP que un canal persistente; el pasajero puede ver un dato con hasta el intervalo de polling de antigüedad adicional, por lo que el ETA percibido puede superar los 15 s aunque el servidor cumpla QA-01; hay que medir esa frescura y mostrarla en la interfaz.