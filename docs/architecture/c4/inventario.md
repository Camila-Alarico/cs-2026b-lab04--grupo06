# Inventario de elementos — RutaSIT Arequipa

| Elemento | Tipo C4 | Origen |
|----------|---------|--------|
| Pasajero, Operador | Persona | drivers.md (Lab 04: RF-02 a RF-06) |
| RutaSIT Arequipa | Sistema de software | Caso (matriz-decision.md, ADR-001) |
| Dispositivos GPS de los buses | Sistema externo | drivers.md (RF-01, R-04) |
| Proveedor de mapas | Sistema externo | arquitectura.mmd y despliegue.puml (Lab 04) |
| Aplicación web progresiva (PWA) | Contenedor | arquitectura.mmd y despliegue.puml (Lab 04) |
| API RutaSIT (monolito modular en Django) | Contenedor | ADR-001, despliegue.puml (Lab 04) |
| Base de datos PostgreSQL + PostGIS | Contenedor | ADR-001, ADR-003 (Lab 04) |
| Módulos Ubicaciones, Rutas y paraderos, ETA y Alertas | Componente (de la API) | paquetes.puml (Lab 05) |
| Flujo "consultar el ETA de un paradero" | Vista dinámica | secuencia-consultar-eta.puml (Lab 05) |
| Dispositivo del usuario y servidor en la nube (VPS) | Nodos de despliegue | despliegue.puml (Lab 04), R-03 |

## Elementos que no son contenedores
- Redis y WebSocket: descartados en ADR-002 y ADR-003.
- Proxy inverso (Nginx) y monitoreo: infraestructura; van en la vista de despliegue, no en la de contenedores.
- Docker: no forma parte de las decisiones de arquitectura.