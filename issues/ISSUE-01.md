# Issue #1: Un GPS sin datos hace fallar la actualización del bus

**Reportado por:** operación de RutaSIT
**Observado:** cuando el operador de GPS no tiene lectura para el bus (responde None), `actualizar_bus` lanza `TypeError` y se cae la actualización. Ocurre con el operador A y con el B.
**Esperado:** se trata como un bus sin señal: se publica el evento `sin_senal` (QA-02), el viaje conserva su estado y no se lanza ninguna excepción.
**Prueba que reproduce el error:**
tests/test_issue_01.py::test_issue_01_gps_sin_datos_publica_sin_senal_y_no_falla
