# Issue #3: La explicación del retraso mezcla eventos de otro viaje

**Reportado por:** operación de RutaSIT
**Observado:** al explicar el retraso del viaje V1, el prompt incluye eventos del viaje V10 (por ejemplo, sin_senal:V10), y V1 sin eventos propios recibe una explicación inventada.
**Esperado:** solo cuentan los eventos cuyo identificador de viaje sea exactamente el del viaje consultado. Sin eventos propios, se responde "No hay eventos registrados para este viaje" sin llamar al LLM.
**Prueba que reproduce el error:**
tests/test_issue_03.py::test_issue_03_explicar_retraso_no_mezcla_eventos_de_otro_viaje