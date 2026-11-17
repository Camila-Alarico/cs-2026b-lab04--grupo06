# Bitácora de IA — Laboratorio 09

> Registro de decisiones de diseño y verificación. Las pruebas locales son reproducibles; las ejecuciones reales de un modelo externo y su latencia deben añadirse con sus salidas originales. No se inventan métricas.

| # | Interacción | Hallazgo | Decisión |
|---|---|---|---|
| 1 | Revisar la consigna E4 del caso RutaSIT Arequipa. | La tarea específica es generar pruebas pytest para ETA; la aserción clave exige compilar y contener 3 o más `assert`. | Se creó `prompts/pruebas_eta/` separado de la Tarea A. |
| 2 | Analizar `src/rutasit/algoritmos_eta.py`. | `DistanciaDirecta` aplica mínimo 5 km/h; `VelocidadPromedio` usa el valor configurado. | Los prompts y casos se ajustaron a esas clases reales. |
| 3 | Revisar el contrato JSON de E4. | Una respuesta libre o Markdown no puede consumirse de forma fiable. | Se fijó JSON estricto con `additionalProperties: false`. |
| 4 | Revisar el riesgo de instrucciones dentro del requisito. | El requisito puede contener texto que intenta sustituir las reglas del prompt. | Se añadió la instrucción de tratar el requisito como dato y un caso adversario. |
| 5 | Revisar seguridad del código generado para E6. | Validar solo JSON no evita imports o llamadas peligrosas en el código. | Se añadió validación AST con lista permitida; el código generado no se ejecuta automáticamente. |
| 6 | Revisar la propuesta de usar `exec` para probar la salida. | Ejecutar directamente código de un LLM puede afectar el entorno. | Se rechazó esa sugerencia; se valida sintaxis y se limita el AST. |

## No determinismo (requisito E7)

La guía exige ejecutar la mejor versión sobre los mismos tres casos, tres veces (nueve respuestas), y describir los cambios. Este registro debe completarse con el proveedor/modelo real usado por el equipo; no se sustituyen esas ejecuciones por fixtures grabados.

| Caso | Ejecución 1 | Ejecución 2 | Ejecución 3 | ¿Cambió el JSON/código? |
|---|---|---|---|---|
| ETA-01 | Pendiente de ejecución real | Pendiente de ejecución real | Pendiente de ejecución real | Pendiente |
| ETA-02 | Pendiente de ejecución real | Pendiente de ejecución real | Pendiente de ejecución real | Pendiente |
| ETA-08 (adversario) | Pendiente de ejecución real | Pendiente de ejecución real | Pendiente de ejecución real | Pendiente |

### Análisis que debe completarse después de las nueve ejecuciones

1. Comparar si cambia la estructura JSON, los imports, el número de pruebas y los valores esperados.
2. Identificar si alguna variación rompe el esquema o el contrato de pytest.
3. Volver a ejecutar las pruebas locales con cada salida literal, sin editar las grabaciones.
4. Conservar las nueve respuestas originales y registrar modelo, fecha y configuración.
5. Si una salida cambia entre ejecuciones, mantener validación determinista en la aplicación y no asumir que un prompt produce siempre el mismo resultado.
