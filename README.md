# RutaSIT Arequipa — Laboratorio 04: Fundamentos de arquitectura de software
Construcción de Software · EPIS-UNSA · 2026-B · Grupo 06
## Integrantes
| Nombre | Rol en el laboratorio |
|--------|------------------------|
| Camila | Trabajo individual: drivers, matriz de decisión, ADR, diagramas, bitácora y verificación de la IA |

## Caso
RutaSIT Arequipa permite seguir en tiempo real los buses del Sistema Integrado de Transporte. 300 buses envían su posición GPS cada 10 s; los pasajeros ven los buses en un mapa y consultan el tiempo estimado de llegada (ETA) a un paradero, y el operador recibe alertas de desvío o congestión. El atributo de calidad crítico es el rendimiento en tiempo real: el ETA debe actualizarse en ≤ 15 s (p95) desde la recepción del GPS. El MVP debe salir en 1 mes con un solo developer y un servidor de bajo costo.

## Arquitectura elegida
Monolito modular con ETA incremental, un solo despliegue y PostgreSQL.
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
## Documentos
- [Drivers y escenarios de calidad](docs/architecture/drivers.md)
- [Matriz de decisión](docs/architecture/matriz-decision.md)
- [Bitácora de uso de IA](docs/architecture/bitacora-ia.md)
- Diagrama de la alternativa descartada (PlantUML): `docs/architecture/diagramas/alternativa.puml`
- Vista de despliegue: `docs/architecture/diagramas/despliegue.puml`

## Vista de despliegue
Por falta de tiempo para instalar Graphviz, la vista de despliegue (E6) se elaboró con un diagrama de despliegue de **PlantUML** en lugar de Python Diagrams.

![Vista de despliegue](docs/architecture/diagramas/img/despliegue.png)

## Diseño UML (Lab 05)

Continuación del Laboratorio 04 sobre RutaSIT Arequipa. Historia crítica: **HU-01, consultar el ETA del bus a un paradero** ([historia.md](docs/design/historia.md)). Los diagramas se escribieron como código (PlantUML y Mermaid) y la verificación de consistencia está en [consistencia.md](docs/design/consistencia.md).

### Máquina de estados del Viaje

```mermaid
stateDiagram-v2
    [*] --> Programado : crear viaje
    Programado --> EnRuta : iniciar() [hora de salida alcanzada]
    EnRuta --> Desviado : marcarDesviado() [distancia a la ruta mayor que umbralDesvioMetros durante N lecturas]
    Desviado --> EnRuta : reanudar() [vuelve a la ruta]
    EnRuta --> Detenido : marcarDetenido() [velocidad nula durante T segundos]
    Detenido --> EnRuta : reanudar() [velocidad mayor que cero]
    EnRuta --> Finalizado : finalizar() [llegó al último paradero]
    Desviado --> Finalizado : finalizar()
    Detenido --> Finalizado : finalizar()
    Finalizado --> [*]
```

### Diagramas y documentos
- Diagrama de clases: [clases.puml](docs/design/clases.puml) · ![Clases](docs/design/img/clases.png)
- Diagrama de secuencia: [secuencia-consultar-eta.puml](docs/design/secuencia-consultar-eta.puml) · ![Secuencia](docs/design/img/secuencia-consultar-eta.png)
- Máquina de estados: [estados-viaje.mmd](docs/design/estados-viaje.mmd)
- Diagrama de actividades: [actividades-detectar-desvio.puml](docs/design/actividades-detectar-desvio.puml) · ![Actividades](docs/design/img/actividades-detectar-desvio.png)
- Diagrama de paquetes: [paquetes.puml](docs/design/paquetes.puml) · ![Paquetes](docs/design/img/paquetes.png)
- Round-trip (código generado con IA e ingeniería inversa): [round-trip.md](docs/design/round-trip.md) y [src/rutasit/dominio.py](src/rutasit/dominio.py)
- Bitácora de IA del laboratorio: [bitacora-ia.md](docs/design/bitacora-ia.md)

## Decisiones arquitectónicas
- [ADR-001: Estilo arquitectónico](docs/architecture/adr/001-estilo-arquitectonico.md)
- [ADR-002: Polling vs WebSocket](docs/architecture/adr/002-polling-vs-websocket.md)
- [ADR-003: Estado actual en PostgreSQL](docs/architecture/adr/003-estado-actual-postgresql.md)


## Arquitectura C4 (Lab 06)

Modelo C4 de RutaSIT Arequipa escrito como código con **Structurizr DSL**: un solo archivo, [workspace.dsl](docs/architecture/c4/workspace.dsl), del que se derivan las 5 vistas. Es coherente con el [ADR-001](docs/architecture/adr/001-estilo-arquitectonico.md) (monolito modular), con el [ADR-002](docs/architecture/adr/002-polling-vs-websocket.md) y el [ADR-003](docs/architecture/adr/003-estado-actual-postgresql.md) (Lab 04) y con el diagrama de paquetes y la secuencia del Lab 05.

### Contexto del sistema (nivel 1)

```mermaid
graph LR
  linkStyle default fill:#ffffff

  subgraph diagram ["System Context View: RutaSIT Arequipa"]
    style diagram fill:#ffffff,stroke:#ffffff

    1["<div style='font-weight: bold'>Pasajero</div><div style='font-size: 70%; margin-top: 0px'>[Person]</div><div style='font-size: 80%; margin-top:10px'>Consulta dÃ³nde estÃ¡ su bus<br />y cuÃ¡ndo llegarÃ¡ a su<br />paradero.</div>"]
    style 1 fill:#08427b,stroke:#052e56,color:#ffffff
    11["<div style='font-weight: bold'>Dispositivos GPS de los buses</div><div style='font-size: 70%; margin-top: 0px'>[Software System]</div><div style='font-size: 80%; margin-top:10px'>Sistema externo: rastreadores<br />de los 300 buses que reportan<br />su posiciÃ³n.</div>"]
    style 11 fill:#999999,stroke:#6b6b6b,color:#ffffff
    12["<div style='font-weight: bold'>Proveedor de mapas</div><div style='font-size: 70%; margin-top: 0px'>[Software System]</div><div style='font-size: 80%; margin-top:10px'>Sistema externo: provee los<br />mosaicos del mapa de<br />Arequipa.</div>"]
    style 12 fill:#999999,stroke:#6b6b6b,color:#ffffff
    2["<div style='font-weight: bold'>Operador</div><div style='font-size: 70%; margin-top: 0px'>[Person]</div><div style='font-size: 80%; margin-top:10px'>Gestiona rutas y paraderos y<br />atiende las alertas de<br />desvÃ­o.</div>"]
    style 2 fill:#08427b,stroke:#052e56,color:#ffffff
    3["<div style='font-weight: bold'>RutaSIT Arequipa</div><div style='font-size: 70%; margin-top: 0px'>[Software System]</div><div style='font-size: 80%; margin-top:10px'>Muestra en un mapa la<br />ubicaciÃ³n de los buses y<br />estima su tiempo de llegada a<br />cada paradero.</div>"]
    style 3 fill:#1168bd,stroke:#0b4884,color:#ffffff

    1-. "<div>Consulta la ubicaciÃ³n de los<br />buses y el ETA a su paradero</div><div style='font-size: 70%'></div>" .->3
    2-. "<div>Gestiona rutas y paraderos y<br />atiende alertas de desvÃ­o</div><div style='font-size: 70%'></div>" .->3
    11-. "<div>EnvÃ­a su posiciÃ³n cada 10 s</div><div style='font-size: 70%'>[HTTPS/JSON]</div>" .->3
    3-. "<div>Obtiene los mosaicos del mapa</div><div style='font-size: 70%'>[HTTPS]</div>" .->12

  end

```

### Vistas

| Vista | Qué muestra | Imagen |
|-------|-------------|--------|
| Contexto (nivel 1) | El sistema, sus usuarios y los sistemas externos | ![Contexto](docs/architecture/c4/img/structurizr-Contexto.png) |
| Contenedores (nivel 2) | PWA, API Django y PostgreSQL + PostGIS, con tecnología y protocolos | ![Contenedores](docs/architecture/c4/img/structurizr-Contenedores.png) |
| Componentes (nivel 3) | Los 4 módulos de la API (los mismos de `paquetes.puml` del Lab 05) | ![Componentes](docs/architecture/c4/img/structurizr-Componentes.png) |
| Dinámica | Flujo "consultar el ETA de un paradero" (HU-01) | ![Dinámica](docs/architecture/c4/img/structurizr-ConsultarEta.png) |
| Despliegue | Producción: dispositivo del usuario, bus, VPS y proveedor de mapas | ![Despliegue](docs/architecture/c4/img/structurizr-Despliegue.png) |

El nivel 4 (código) no se dibuja de nuevo: es el diagrama de clases del Lab 05, [clases.puml](docs/design/clases.puml).

### Documentos
- [inventario.md](docs/architecture/c4/inventario.md): elementos del modelo y su origen
- [comparacion.md](docs/architecture/c4/comparacion.md): vista dinámica frente a secuencia UML, y modelado frente a diagramación
- [revision-c4.md](docs/architecture/c4/revision-c4.md): lista de revisión oficial aplicada y hallazgos de la IA
- [explicacion.md](docs/architecture/c4/explicacion.md): explicación para un público no técnico
- [bitacora-ia.md](docs/architecture/c4/bitacora-ia.md): uso de IA en este laboratorio
- [contexto-manual.puml](docs/architecture/c4/contexto-manual.puml): el contexto escrito a mano con C4-PlantUML

### Cómo regenerar las vistas
```
cd docs/architecture/c4
./structurizr.sh validate -w workspace.dsl
./structurizr.sh export -w workspace.dsl -f plantuml/c4plantuml -o export
./structurizr.sh export -w workspace.dsl -f mermaid -o export
java -jar plantuml.jar -tpng -o ../img export/*.puml
```


## Reflexión sobre el uso de la IA
La IA es una herramienta muy útil al momento de hacer diversas actividades, siendo una de esas el crear alternativas y escoger las mejores, lo que pasa es que no podemos depender completamente de estas ya que estas suelen contener errores al momento de crear. Un ejemplo de esta ayuda fue en la creacion de este laboratorio donde se uso Claude y ChatGPT los cuales ayudaron a generar tres alternativas de estilo, a criticarlas y a redactar el código de los diagramas. Claude afirmó que su alternativa era la única que atacaba el atributo crítico y planteó una mitigación incoherente (reconstruir el estado desde PostgreSQL sin haber persistido antes los datos) cosa que era un error en lo que se buscaba; ambas lo reconocieron al criticarse a sí mismas. ChatGPT recomendó WebSocket sin considerar que la carga depende de los pasajeros conectados y no de los 300 buses. Al final siempre se necesita que una persona verifique lo que te manda para tener una mejor coherencia y un buen trabajo.
