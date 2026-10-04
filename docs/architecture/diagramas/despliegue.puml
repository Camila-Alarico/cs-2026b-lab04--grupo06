@startuml
skinparam dpi 220
skinparam defaultFontName Arial
skinparam backgroundColor white
title RutaSIT Arequipa - Vista de despliegue
actor "Pasajero" as P
actor "Operador" as O
node "Bus con GPS\n(300 unidades)" as B
node "Celular / navegador" as CEL
cloud "Red móvil" as NET
cloud "Proveedor de mapas\n(servicio externo)" as MAP
node "Servidor en la nube (VPS)" {
  node "Proxy inverso Nginx\n(HTTPS y caché de 3 a 5 s)" as NGX
  node "Django\nMonolito modular (4 módulos)" as APP
  database "PostgreSQL + PostGIS" as DB
  node "Monitoreo\n(logs y métricas)" as MON
}
P --> CEL
O --> CEL
B --> NET : POST posición cada 10 s (token por bus)
CEL --> NET : polling cada 5 a 10 s
NET --> NGX : HTTPS
NGX --> APP
APP --> DB
APP ..> MON : métricas
CEL ..> MAP : tiles del mapa
@enduml