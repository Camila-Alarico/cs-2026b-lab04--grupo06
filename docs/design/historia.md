# Historia de usuario — RutaSIT Arequipa

HU-01: Como pasajero, quiero consultar el tiempo estimado de llegada (ETA) del bus
       a mi paradero para decidir cuándo salir.

Criterios de aceptación
- Dado un viaje EnRuta cuya última posición GPS tiene 30 s o menos de antigüedad,
  cuando consulto el ETA de un paradero de su ruta, entonces el sistema muestra el ETA
  actualizado en 15 s o menos desde la recepción de esa posición.
- Dado un viaje EnRuta cuya última posición tiene más de 30 s de antigüedad,
  cuando consulto el ETA, entonces el sistema muestra el último ETA calculado
  marcado como "dato desactualizado" junto con la hora de su última actualización.
- Dado un viaje que no está EnRuta (Programado o Finalizado), cuando consulto el ETA,
  entonces el sistema informa que no hay ETA disponible para ese viaje.