# Drivers arquitectónicos — 
## 1. Requisitos funcionales clave 
| ID | Requisito | Actor | Prioridad |
|-------|----------------------------------------|-----------|-----------|
| RF-01 | <El paciente reserva una cita ...> | Paciente | Alta |
| RF-02 | ... | ... | ... |
## 2. Atributos de calidad (ordenados por prioridad)
1. <Atributo crítico del caso> — <por qué es crítico>
2. <Atributo> — <por qué>
3. ...
## 3. Restricciones
| ID | Tipo | Restricción |
|------|--------------|-------------------------------------------------|
| R-01 | Plazo | MVP en producción en 1 mes |
| R-02 | Equipo | <3 developers con experiencia en ...> |
| R-03 | Presupuesto | <p. ej., un servidor en la nube de bajo costo> |
| R-04 | Normativa | <p. ej., Ley 29733 de protección de datos> |
## 4. Escenarios de atributos de calidad
| ID | Atributo | Fuente | Estímulo | Entorno | Artefacto | Respuesta | Medida |
|-------|--------------|--------|----------|---------|-----------|-----------|------------|
| QA-01 | <Rendimiento>| ... | ... | ... | ... | ... | p95 ≤ 2 s |
| QA-02 | ... | ... | ... | ... | ... | ... | <número> |
| QA-03 | ... | ... | ... | ... | ... | ... | <número> |

# Drivers arquitectónicos — RutaSIT Arequipa

## 1. Requisitos funcionales clave
| ID    | Requisito                                                        | Actor     | Prioridad |
|-------|------------------------------------------------------------------|-----------|-----------|
| RF-01 | El bus envía su posición GPS al sistema cada 10 s                | Bus (GPS) | Alta      |
| RF-02 | Ver la ubicación de los buses en un mapa                         | Pasajero  | Alta      |
| RF-03 | Consultar el tiempo estimado de llegada (ETA) a un paradero      | Pasajero  | Alta      |
| RF-04 | Recibir alertas de desvío de ruta o congestión                   | Pasajero  | Media     |
| RF-05 | Detectar desvíos y congestión y generar alertas                  | Operador  | Media     |
| RF-06 | Gestionar rutas, paraderos y buses                               | Operador  | Media     |

## 2. Atributos de calidad (ordenados por prioridad)
1. Rendimiento en tiempo real (atributo crítico): un ETA desactualizado hace inútil el servicio.
2. Disponibilidad: los buses circulan todo el día y la red móvil es intermitente. El sistema debe seguir mostrando datos aunque algunos buses pierdan señal.
3. Modificabilidad: se deben poder agregar rutas, paraderos o cambiar el algoritmo de ETA sin reescribir el sistema.
4. Seguridad: solo buses autenticados deben poder enviar posiciones, para evitar datos falsos.

## 3. Restricciones
| ID   | Tipo         | Restricción                                                                 |
|------|--------------|-----------------------------------------------------------------------------|
| R-01 | Plazo        | MVP en producción en 1 mes                                                  |
| R-02 | Equipo       | 1 developer con experiencia en Python, Java, Django y SQL                   |
| R-03 | Presupuesto  | Bajo: un solo servidor en la nube de bajo costo                             |
| R-04 | Tecnología   | Los buses envían su posición por red móvil, con cortes posibles             |
| R-05 | Normativa    | Ley 29733 de protección de datos personales: no almacenar datos personales del pasajero |

## 4. Escenarios de atributos de calidad
| ID    | Atributo        | Fuente              | Estímulo                                      | Entorno                          | Artefacto                 | Respuesta               | Medida                |
|-------|-----------------|---------------------|-----------------------------------------------|----------------------------------|---------------------------|-------------------------|-----------------------|
| QA-01 | Rendimiento     | 300 buses | Envían su posición cada 10 s                  | Operación normal, hora punta     | Módulo de ETA             | Recalcula y publica el ETA de cada paradero afectado             | ETA actualizado en ≤ 15 s (p95)        |
| QA-02 | Disponibilidad  | Un bus | Pierde señal móvil y deja de reportar   | Operación normal     | Módulo de ubicaciones     | Marca al bus como "posición desactualizada" y sigue atendiendo a los demás | Aviso en ≤ 30 s; 0 errores de consulta para los otros buses restantes |
| QA-03 | Modificabilidad | El operador | Pide agregar una nueva ruta o cambiar el algoritmo de ETA | Desarrollo | Módulos de Rutas y ETA    | Se agrega o cambia sin modificar los demás módulos  | ≤ 2 días-persona   |
