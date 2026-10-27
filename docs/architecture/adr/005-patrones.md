# ADR-005: Patrones de diseño adoptados y rechazados

- **Estado:** Aceptado
- **Fecha:** 2026-10-24
- **Contexto:** El servicio original de RutaSIT concentra decisiones de selección de proveedores, procesamiento GPS, cálculo de ETA, gestión del estado de los viajes y notificaciones. Esto dificulta extender el sistema y probar sus componentes por separado.

## Decisión

Se adoptan los siguientes patrones:

1. **Strategy:** permite intercambiar algoritmos de cálculo de ETA.
2. **Adapter:** normaliza las interfaces y unidades de los operadores GPS y de los proveedores de IA.
3. **Factory:** centraliza la creación y selección de implementaciones.
4. **State:** encapsula las reglas y transiciones del ciclo de vida de los viajes.
5. **Observer:** desacopla la publicación de eventos de las notificaciones.
6. **Decorator:** incorpora reintentos de lectura GPS y funcionalidades adicionales sin modificar el adaptador interno.
7. **Chain of Responsibility:** organiza las validaciones de las respuestas de IA mediante guardrails encadenados.

## Alternativas consideradas

- Mantener condicionales en el servicio original: es más sencillo inicialmente, pero dificulta añadir variantes.
- Introducir un Singleton para el servicio: se rechaza porque no se necesita una instancia global y se desea mantener la facilidad de pruebas.
- Añadir patrones adicionales sin una necesidad identificada: se rechaza para evitar abstracciones innecesarias.

## Consecuencias positivas

- Mayor separación de responsabilidades.
- Menor acoplamiento entre el servicio y las implementaciones concretas.
- Facilidad para sustituir algoritmos, proveedores y suscriptores.
- Mejor capacidad de probar los componentes individualmente.

## Consecuencias negativas

- Mayor número de clases y archivos.
- Más relaciones que comprender y documentar.
- Necesidad de mantener sincronizados el código, las pruebas y los diagramas.

## Verificación

La decisión se valida mediante las pruebas de comportamiento y las pruebas específicas de patrones. La comparación de complejidad ciclomática y SLOC se documenta en `metricas.md`.
