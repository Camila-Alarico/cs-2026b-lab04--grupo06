# E6. Métricas y trade-off

## 1. Complejidad ciclomática con Radon

Se comparan la implementación original de RutaSIT (`src/rutasit/antes/servicio.py`) y la implementación refactorizada (`src/rutasit/servicio.py`). La complejidad ciclomática permite estimar la cantidad de caminos independientes de ejecución de cada método.

### Complejidad antes y después

| Método | Complejidad antes | Complejidad después | Variación |
|---|---:|---:|---:|
| `iniciar_viaje` | Por medir | Por medir | Por calcular |
| `finalizar_viaje` | Por medir | Por medir | Por calcular |
| `actualizar_bus` | Por medir | Por medir | Por calcular |
| `consultar_eta` | Por medir | Por medir | Por calcular |
| `explicar_retraso` | Por medir | Por medir | Por calcular |
| **Promedio** | **Por medir** | **Por medir** | **Por calcular** |

Los valores deben obtenerse ejecutando Radon sobre ambas versiones. La variación se calcula como complejidad después menos complejidad antes.

### Líneas de código (SLOC)

| Versión | Archivo principal | SLOC |
|---|---|---:|
| Antes | `src/rutasit/antes/servicio.py` | Por medir |
| Después | `src/rutasit/servicio.py` | Por medir |

SLOC representa las líneas de código fuente, excluyendo comentarios y líneas en blanco según el análisis de la herramienta.

## 2. Análisis del trade-off

La refactorización mejoró la separación de responsabilidades al aplicar patrones de diseño en RutaSIT.  
Strategy permite cambiar el algoritmo de ETA sin modificar el servicio principal.  
Adapter normaliza los formatos de los distintos operadores GPS.  
State encapsula las transiciones y reglas del ciclo de vida de los viajes.  
Observer desacopla la publicación de eventos de los componentes que reciben las alertas.  
Factory centraliza la creación de implementaciones y Decorator añade reintentos sin modificar los adaptadores.  
El costo es un mayor número de clases, archivos y relaciones que el equipo debe comprender y mantener.  
La versión anterior habría sido suficiente para un prototipo pequeño, estable y con pocas variantes de GPS, algoritmos y notificaciones.

## 3. Patrón evaluado y no aplicado

Se decidió no introducir un patrón adicional cuando no existía una necesidad clara que justificara su complejidad. En particular, no se incorporó un Singleton para el servicio principal: las dependencias pueden inyectarse y las instancias independientes facilitan las pruebas. El patrón añadiría restricciones innecesarias al ciclo de vida de los objetos sin aportar una mejora funcional demostrable.
