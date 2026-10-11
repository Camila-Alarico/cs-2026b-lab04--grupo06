# Consistencia (C1–C5) — RutaSIT Arequipa

Herramienta: Claude (Prompt IA 3). Los hallazgos se verificaron contra los cinco diagramas.
Resumen: 26 hallazgos; 17 aceptados, 2 parciales, 5 falsos positivos y 2 rechazados por decisión de diseño.

| # | Regla | Hallazgo de la IA | Verificación del equipo | Decisión |
|---|-------|-------------------|-------------------------|----------|
| 1 | C1 | EtaController no existe en el diagrama de clases | Es de la capa de presentación, fuera de los módulos modelados; la guía hace lo mismo con PedidoController | Falso positivo |
| 2 | C1 | Los puertos devuelven Optional pero la secuencia no muestra el caso vacío | Correcto: faltaba la rama | Aceptado: se agregó el alt "sin posición o sin ETA registrado" |
| 3 | C1 | `antiguedad` no se calcula en ningún mensaje | Correcto | Aceptado: se agregó `antiguedadSegundos(ahora)` en PosicionGPS y el mensaje en la secuencia |
| 4 | C1 | Validar token, calcular distancia y registrar alerta (diagrama de actividades) no son operaciones del diagrama de clases | C1 aplica solo a mensajes de secuencia, no a acciones de actividades | Falso positivo |
| 5 | C1 | iniciar, marcarDetenido, reanudar, finalizar, guardarEta y obtenerParaderosOrdenados no aparecen en S ni en A | C1 exige que cada mensaje sea una operación, no que cada operación aparezca en una secuencia; esas operaciones se cubren en E3 y E6 | Falso positivo |
| 6 | C2 | Las guardas de E no tienen dueño; N, T y el umbral no existen en las clases | Correcto | Aceptado: ServicioAlertas con umbralDesvioMetros, lecturasParaDesvio (N) y segundosParaDetencion (T) |
| 7 | C2 | A marca Desviado en cada lectura y no cubre reanudar, marcarDetenido ni finalizar | Parcial: faltaban la guarda "EnRuta" y el reanudar; A modela solo la detección de desvío, no todo el ciclo de vida | Parcial: se agregó la guarda y la acción de reanudar |
| 8 | C2 | A recalcula el ETA de un viaje Desviado, pero estaEnRuta() es falso y devuelve NoDisponible | Correcto: inconsistencia real | Aceptado: A deja el ETA NoDisponible mientras el viaje esté Desviado |
| 9 | C2 | [*] → Programado no tiene operación | La transición inicial corresponde a la creación del Viaje | Parcial: se etiquetó "crear viaje" |
| 10 | C2 | EstadoEta no cambia por ninguna operación | EstadoEta no es una máquina de estados; clasifica el resultado de una consulta | Falso positivo |
| 11 | C3 | La guarda "hay bus asignado" es siempre verdadera (Bus 1 – 0..* Viaje) | Correcto | Aceptado: guarda cambiada a [hora de salida alcanzada] |
| 12 | C3 | Dos asociaciones no expresan un solo ETA por (viaje, paradero) | Correcto | Aceptado: nota con el invariante en Eta |
| 13 | C3 | La composición Viaje–PosicionGPS es abierta porque las posiciones viven en el repositorio | El ADR-003 guarda el histórico de posiciones por viaje y una posición no existe sin su viaje; el repositorio es un detalle de persistencia | Falso positivo |
| 14 | C3 | estado está duplicado como atributo y como asociación al enum | Se mantiene como en el ejemplo de la guía (Pedido --> EstadoPedido más el atributo estado) | Rechazado (decisión de diseño) |
| 15 | C3 | 0..1 Eta no impone los invariantes de ResultadoEta | Parcial: el invariante sí faltaba; la construcción del resultado es interna de ServicioEta | Aceptado: nota de invariante en ResultadoEta |
| 16 | C4 | Las asociaciones sin dirección implican ciclos UBI↔ETA y RUT↔ETA | Correcto: ciclo real | Aceptado: Eta → Viaje y Eta → Paradero son direccionales |
| 17 | C4 | A encadena desvío, alerta y ETA entre paquetes sin orquestador | Correcto en parte | Aceptado: la nota de P indica que la capa de presentación orquesta; A ya no invoca a ETA |
| 18 | C4 | Los enums no pertenecen a ningún paquete | Correcto | Aceptado: EstadoViaje en Ubicaciones y EstadoEta en ETA |
| 19 | C4 | La nota "solo por interfaces públicas" contradice el uso de clases concretas | Correcto | Aceptado: nota reescrita |
| 20 | C4 | Alertas no existe en el diagrama de clases | Correcto | Aceptado: paquete Alertas agregado |
| 21 | C5 | umbralSegundos vs umbralAntiguedadSegundos | Correcto | Aceptado: se unificó el nombre |
| 22 | C5 | "umbral" designa a la vez una distancia y un tiempo | Correcto | Aceptado: umbralDesvioMetros y umbralAntiguedadSegundos |
| 23 | C5 | "30 s" está escrito a mano en la secuencia | Correcto | Aceptado: la secuencia usa el atributo |
| 24 | C5 | "ETA vigente" no coincide con Actualizado | Correcto | Aceptado |
| 25 | C5 | La URL usa {id} y {codigo}, el modelo idViaje y codigoParadero | Correcto | Aceptado: URL renombrada |
| 26 | C5 | El paquete se llama ETA y las clases Eta, EstadoEta, ResultadoEta | El paquete conserva el nombre del módulo del ADR-001 | Rechazado (decisión de diseño) |

## Falsos positivos y qué habría pasado si se aceptaban sin verificar
- **#1 y #4:** habríamos llenado el diagrama de clases con controladores y acciones de proceso que no son clases del dominio.
- **#5:** habríamos obligado a que todas las operaciones aparezcan en una secuencia, inflando un diagrama pensado para un solo flujo.
- **#10:** habríamos creado una máquina de estados innecesaria para EstadoEta.
- **#13:** habríamos quitado la composición y perdido la regla de que el histórico de posiciones depende del viaje (ADR-003).