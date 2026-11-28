# Issue #2: Se calcula ETA y se avisa por paraderos que el bus ya pasó

**Reportado por:** pasajeros (aplicación móvil)
**Observado:** con el bus 167 m después del Paradero 2, la app muestra ETA vigente para los Paraderos 1 y 2 y envía avisos "llega en N min" a quienes los siguen, aunque el bus ya los dejó atrás.
**Esperado:** solo los paraderos por delante tienen ETA y avisos; para los ya pasados, consultar_eta devuelve NO_DISPONIBLE y no se envía ningún aviso.
**Prueba que reproduce el error:**
tests/test_issue_02.py::test_issue_02_no_hay_eta_ni_aviso_para_paraderos_ya_pasados
