| Propuesta de la IA | Decisión | Justificación |
|--------------------|----------|---------------|
| 12 componentes (controladores, repositorios, servicios) | Corregida | El nivel 3 son los 4 módulos de paquetes.puml (Lab 05); repositorios y servicios son nivel 4 (clases) |
| Un solo sistema externo (GPS) | Corregida | Faltaba el proveedor de mapas del Lab 04 (arquitectura.mmd y despliegue.puml) |
| Servidor de aplicación y de base de datos separados y sin anidar | Corregida | R-03 y ADR-001: un solo VPS; se anidaron los nodos y se puso una instancia de cada contenedor |
| Relaciones con "HTTP" y "HTTP POST" | Corregida | El Lab 04 usa HTTPS; se cambió a HTTPS/JSON |
| Métricas guardadas en PostgreSQL | Corregida | No hay decisión de guardarlas en la BD; el monitoreo va en el VPS (Lab 04) |