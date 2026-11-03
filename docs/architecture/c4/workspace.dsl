workspace "RutaSIT Arequipa" "Modelo C4 del seguimiento en tiempo real de los buses del Sistema Integrado de Transporte de Arequipa" {

    !identifiers hierarchical

    model {
        pasajero = person "Pasajero" "Consulta dónde está su bus y cuándo llegará a su paradero. [QA-04]"
        operador = person "Operador" "Gestiona rutas y paraderos y atiende las alertas de desvío. [QA-03]"

        rutasit = softwareSystem "RutaSIT Arequipa" "Muestra en un mapa la ubicación de los buses y estima su tiempo de llegada a cada paradero. Atiende [QA-01, QA-02, QA-04, QA-05, QA-06]." {
            pwa = container "Aplicación web progresiva" "Interfaz para pasajeros y operadores: mapa, ETA y alertas; muestra «actualizado hace X s». [QA-04, QA-02]" "PWA (HTML y JavaScript)" "Web Browser"
            api = container "API RutaSIT" "Monolito modular que recibe las posiciones GPS con token por bus, calcula el ETA y detecta desvíos; tras una caída prioriza la posición más reciente de cada bus. [QA-01, QA-05, QA-06]" "Python / Django" {
                ubicaciones = component "Módulo Ubicaciones" "Recibe y guarda las posiciones GPS y mantiene el estado de cada viaje; escribe el histórico por lotes y tiene un adaptador por operador de GPS. [QA-01, QA-02, QA-05, QA-07]" "Django app"
                rutas = component "Módulo Rutas y paraderos" "Gestiona las rutas, los paraderos y su orden. [QA-03]" "Django app"
                eta = component "Módulo ETA" "Calcula y sirve el tiempo estimado de llegada con un algoritmo intercambiable; marca el dato desactualizado. [QA-01, QA-02, QA-03, QA-04]" "Django app"
                alertas = component "Módulo Alertas" "Detecta desvíos y detenciones de los viajes y registra las alertas. [RF-05]" "Django app"
            }
            db = container "Base de datos" "Rutas, paraderos, viajes, última posición e histórico, ETA y alertas (un esquema por módulo); índice del ETA por paradero. [QA-01, QA-04]" "PostgreSQL + PostGIS" "Database"
        }

        gps = softwareSystem "Dispositivos GPS de los buses" "Sistema externo: rastreadores de los 1200 buses que reportan su posición cada 10 s y, según el supuesto de la iteración 3, reenvían las posiciones acumuladas al reconectarse. [QA-01, QA-05, QA-06]" "Externo"
        mapas = softwareSystem "Proveedor de mapas" "Sistema externo: provee los mosaicos del mapa de Arequipa." "Externo"

        pasajero -> rutasit "Consulta la ubicación de los buses y el ETA a su paradero"
        operador -> rutasit "Gestiona rutas y paraderos y atiende alertas de desvío"
        gps -> rutasit "Envía su posición cada 10 s" "HTTPS/JSON"
        rutasit -> mapas "Obtiene los mosaicos del mapa" "HTTPS"

        pasajero -> rutasit.pwa "Consulta buses y ETA" "HTTPS"
        operador -> rutasit.pwa "Gestiona rutas y paraderos y atiende alertas" "HTTPS"
        rutasit.pwa -> rutasit.api "Consulta buses, ETA y alertas, y gestiona rutas (polling de 5 a 10 s)" "HTTPS/JSON"
        gps -> rutasit.api "Envía su posición cada 10 s con el token del bus" "HTTPS/JSON"
        rutasit.pwa -> mapas "Carga los mosaicos del mapa" "HTTPS"
        rutasit.api -> rutasit.db "Lee y escribe" "SQL/TCP"

        rutasit.pwa -> rutasit.api.ubicaciones "Consulta la ubicación de los buses" "HTTPS/JSON"
        rutasit.pwa -> rutasit.api.eta "Consulta el ETA de un paradero" "HTTPS/JSON"
        rutasit.pwa -> rutasit.api.alertas "Consulta las alertas de desvío" "HTTPS/JSON"
        rutasit.pwa -> rutasit.api.rutas "Consulta y gestiona rutas y paraderos" "HTTPS/JSON"
        gps -> rutasit.api.ubicaciones "Envía su posición cada 10 s con el token del bus" "HTTPS/JSON"
        rutasit.api.eta -> rutasit.api.ubicaciones "Obtiene el viaje y su última posición"
        rutasit.api.eta -> rutasit.api.rutas "Obtiene el paradero"
        rutasit.api.alertas -> rutasit.api.ubicaciones "Evalúa la posición y cambia el estado del viaje"
        rutasit.api.alertas -> rutasit.api.rutas "Calcula la distancia a la ruta"
        rutasit.api.ubicaciones -> rutasit.api.rutas "Referencia la ruta del viaje"
        rutasit.api.ubicaciones -> rutasit.db "Lee y escribe viajes y posiciones" "SQL"
        rutasit.api.eta -> rutasit.db "Lee y escribe los ETA" "SQL"
        rutasit.api.alertas -> rutasit.db "Registra las alertas" "SQL"
        rutasit.api.rutas -> rutasit.db "Lee y escribe rutas y paraderos" "SQL"

        produccion = deploymentEnvironment "Producción" {
            deploymentNode "Celular o PC del usuario" "Dispositivo del pasajero o del operador" "Android / navegador web" {
                containerInstance rutasit.pwa
            }
            deploymentNode "Bus" "Equipo GPS a bordo de cada bus. [QA-06]" "Equipo a bordo" {
                softwareSystemInstance gps
            }
            deploymentNode "Servidor en la nube (VPS)" "Un solo servidor de bajo costo que aloja la API y la base de datos; es un punto único de falla aceptado para el MVP (riesgo R1). [QA-05] El proxy inverso Nginx y el monitoreo no se dibujan en esta vista (ver despliegue.puml del Lab 04)." "Linux (VPS de bajo costo)" {
                deploymentNode "Servidor de aplicación" "Ejecuta el monolito modular. [QA-01, QA-04]" "Python / Django" {
                    containerInstance rutasit.api
                }
                deploymentNode "Servidor de base de datos" "Almacena los datos de todos los módulos. [QA-01, QA-04]" "PostgreSQL + PostGIS" {
                    containerInstance rutasit.db
                }
            }
            deploymentNode "Nube del proveedor de mapas" "Servicio externo" "Internet" {
                softwareSystemInstance mapas
            }
        }
    }

    views {
        systemContext rutasit "Contexto" "Nivel 1: RutaSIT y su entorno." {
            include *
            autolayout lr
        }
        container rutasit "Contenedores" "Nivel 2: contenedores de RutaSIT." {
            include *
            autolayout lr
        }
        component rutasit.api "Componentes" "Nivel 3: módulos de la API." {
            include *
            autolayout lr
        }
        dynamic rutasit.api "ConsultarEta" "Dinámico: consultar el ETA de un paradero (HU-01)." {
            rutasit.pwa -> rutasit.api.eta "GET /viajes/{idViaje}/paraderos/{codigoParadero}/eta"
            rutasit.api.eta -> rutasit.api.ubicaciones "Obtiene el viaje y su última posición"
            rutasit.api.ubicaciones -> rutasit.db "Lee y escribe viajes y posiciones" "SQL"
            rutasit.api.eta -> rutasit.db "Lee y escribe los ETA" "SQL"
            rutasit.api.alertas -> rutasit.db "Registra las alertas" "SQL"
            rutasit.api.rutas -> rutasit.db "Lee y escribe rutas y paraderos" "SQL"
            autolayout lr
        }
        deployment rutasit produccion "Despliegue" "Despliegue en producción (MVP)." {
            include *
            autolayout lr
        }
        styles {
            element "Person" {
                shape person
                background #08427B
                color #ffffff
            }
            element "Software System" {
                background #1168BD
                color #ffffff
            }
            element "Externo" {
                background #999999
            }
            element "Container" {
                background #438DD5
                color #ffffff
            }
            element "Component" {
                background #85BBF0
                color #000000
            }
            element "Database" {
                shape cylinder
            }
            element "Web Browser" {
                shape WebBrowser
            }
        }
    }
}