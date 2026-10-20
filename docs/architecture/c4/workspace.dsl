workspace "RutaSIT Arequipa" "Modelo C4 del seguimiento en tiempo real de los buses del Sistema Integrado de Transporte de Arequipa" {

    !identifiers hierarchical

    model {
        pasajero = person "Pasajero" "Consulta dónde está su bus y cuándo llegará a su paradero."
        operador = person "Operador" "Gestiona rutas y paraderos y atiende las alertas de desvío."

        rutasit = softwareSystem "RutaSIT Arequipa" "Muestra en un mapa la ubicación de los buses y estima su tiempo de llegada a cada paradero." {
            pwa = container "Aplicación web progresiva" "Interfaz para pasajeros y operadores: mapa, ETA y alertas." "PWA (HTML y JavaScript)" "Web Browser"
            api = container "API RutaSIT" "Monolito modular que recibe las posiciones GPS, calcula el ETA y detecta desvíos." "Python / Django" {
                ubicaciones = component "Módulo Ubicaciones" "Recibe y guarda las posiciones GPS y mantiene el estado de cada viaje." "Django app"
                rutas = component "Módulo Rutas y paraderos" "Gestiona las rutas, los paraderos y su orden." "Django app"
                eta = component "Módulo ETA" "Calcula y sirve el tiempo estimado de llegada; marca el dato desactualizado." "Django app"
                alertas = component "Módulo Alertas" "Detecta desvíos y detenciones de los viajes y registra las alertas." "Django app"
            }
            db = container "Base de datos" "Rutas, paraderos, viajes, última posición e histórico, ETA y alertas (un esquema por módulo)." "PostgreSQL + PostGIS" "Database"
        }

        gps = softwareSystem "Dispositivos GPS de los buses" "Sistema externo: rastreadores de los 300 buses que reportan su posición." "Externo"
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
            deploymentNode "Bus" "Equipo GPS a bordo de cada bus" "Equipo a bordo" {
                softwareSystemInstance gps
            }
            deploymentNode "Servidor en la nube (VPS)" "Un solo servidor de bajo costo que aloja la API y la base de datos. El proxy inverso Nginx y el monitoreo no se dibujan en esta vista (ver despliegue.puml del Lab 04)." "Linux (VPS de bajo costo)" {
                deploymentNode "Servidor de aplicación" "Ejecuta el monolito modular" "Python / Django" {
                    containerInstance rutasit.api
                }
                deploymentNode "Servidor de base de datos" "Almacena los datos de todos los módulos" "PostgreSQL + PostGIS" {
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