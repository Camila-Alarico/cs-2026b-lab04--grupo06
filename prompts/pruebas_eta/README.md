# E4 — Tarea B: generar pruebas pytest para ETA (RutaSIT Arequipa)

## 1. Alcance

El código de producción utilizado como referencia es `src/rutasit/algoritmos_eta.py`. Contiene:

- `DistanciaDirecta.segundos(distancia_m, velocidad_kmh)`: usa la velocidad actual, con un mínimo de `5.0 km/h`.
- `VelocidadPromedio(velocidad_promedio_kmh=20.0).segundos(...)`: usa la velocidad configurada en el constructor; el parámetro `velocidad_kmh` del método no cambia esa velocidad.
- La conversión de km/h a m/s divide entre `3.6`.


## 2. Contrato y dataset (E1)

`esquema.json` exige una salida JSON con exactamente cuatro campos: `caso_id`, `archivo`, `codigo` y `objetivo`. El código debe ser una cadena Python ejecutable.

`casos.yaml` contiene ocho casos definidos antes de la evaluación: cinco de cálculo/velocidad, dos bordes adicionales (incluyendo cero y velocidad mínima) y un caso adversario con una instrucción incrustada en el requisito.

## 3. Aserciones

| ID | Aserción | Propósito |
|---|---|---|
| A1 | `is-json` + `esquema.json` | Cumplir el contrato de salida |
| A2 | Tres o más `assert` y una función `test_...` | Aserción clave sugerida por la guía, reforzada con estructura pytest |
| A3 | Importar `DistanciaDirecta` o `VelocidadPromedio` desde `rutasit.algoritmos_eta` y llamar a `segundos` | Probar el código real, no clases inventadas |
| A4 | Función de prueba compatible con pytest | Evitar código que solo ejecute aserciones al importarse |
| A5 | JSON sin bloques Markdown ni texto externo | Mantener salida parseable automáticamente |

La compilación y ejecución real del código se comprueba aparte de las aserciones estáticas de Promptfoo; no se afirma que una expresión regular equivalga a ejecutar Python.

## 4. Iteraciones de prompt (E2–E3 aplicadas a E4)

- **v1:** solicitud breve. No fija formato de salida ni contrato; se espera que falle el JSON y que produzca pruebas incompletas.
- **v2:** incorpora contexto del módulo y exige JSON, pero todavía no fija un mínimo de aserciones ni una función de prueba por caso.
- **v3:** incorpora rol, contexto, tarea, restricciones, formato y ejemplo (*few-shot*); añade una verificación interna tipo *Cognitive Verifier*. También trata el requisito como dato para resistir la instrucción adversaria.

Los archivos de `grabaciones/` son fixtures provisionales preparados para comprobar el flujo de evaluación; no son transcripciones literales de ejecuciones independientes de cada prompt. Antes de presentar la evidencia final de la práctica, ejecuta cada versión en el asistente elegido y sustituye cada archivo por la respuesta literal, sin editarla, tal como exige la guía.

## 5. Ejecución

Desde la raíz del repositorio:

```bash
npx promptfoo eval -c prompts/pruebas_eta/promptfooconfig.yaml
```

Para validar que los fragmentos v3 compilan y ejecutan contra el módulo real:

```bash
python prompts/pruebas_eta/validar_v3.py
```


## 6. Evidencia y límites

Las fixtures v1 y v2 son deliberadamente débiles para mostrar por qué se endureció el prompt; v3 es la versión candidata. 