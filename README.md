# RutaSIT Arequipa — Laboratorio 04: Fundamentos de arquitectura de software
Construcción de Software · EPIS-UNSA · 2026-B · Grupo 06
## Integrantes
| Nombre       | Rol en el laboratorio                           |
|Camila Alarico| Redactor de ADR, diagramador y verificador de IA|
## Caso
<Descripción de 4–6 líneas y atributo de calidad crítico>
## Arquitectura elegida
```mermaid
flowchart TB
    BUS["Bus (GPS)"]
    PAS["Pasajero"]
    OPE["Operador"]
    subgraph APP["RutaSIT — Monolito modular (un solo despliegue)"]
        API["Capa de presentación: API REST<br/>(ingesta GPS con token por bus y consultas)"]
        M1["Ubicaciones<br/>(última posición y frescura)"]
        M2["ETA<br/>(cálculo incremental)"]
        M3["Alertas<br/>(desvío y congestión)"]
        M4["Rutas y paraderos"]
        INF["Capa de infraestructura: repositorios y adaptadores"]
    end
    DB[("PostgreSQL + PostGIS<br/>(un esquema por módulo)")]
    MAP["Proveedor de mapas"]
    BUS --> API
    PAS --> API
    OPE --> API
    API --> M1 & M2 & M3 & M4
    M2 -->|"consulta posición"| M1
    M2 -->|"consulta ruta"| M4
    M3 -->|"consulta posición"| M1
    M3 -->|"consulta ruta"| M4
    M1 & M2 & M3 & M4 --> INF
    INF --> DB
    PAS -.->|"tiles del mapa"| MAP
    classDef mod fill:#E8F5E9,stroke:#2E7D32,color:#000
    classDef ext fill:#F2F2F2,stroke:#7F7F7F,color:#000,stroke-dasharray: 4 3
    classDef usr fill:#FDEDEC,stroke:#C8310E,color:#000
    class M1,M2,M3,M4 mod
    class MAP ext
    class BUS,PAS,OPE usr
```
## Decisiones arquitectónicas
- [ADR-001: Estilo arquitectónico](docs/architecture/adr/001-estilo-arquitectonico.md)
- [ADR-002: ...](docs/architecture/adr/002-....md)
- [ADR-003: ...](docs/architecture/adr/003-....md)
## Reflexión sobre el uso de la IA (5–8 líneas)
<¿En qué ayudó? ¿Qué errores cometió? ¿Qué aprendimos a verificar?>
