# Olores detectados en `src/rutasit/antes/servicio.py` (Lab 07, E1)

Medición base: `radon cc -s -a src/` → ⚠️ pega aquí tu salida.

| # | Olor detectado | Líneas | Patrón propuesto | Principio SOLID | Costo | Decisión |
|---|----------------|--------|------------------|-----------------|-------|----------|
| 1 | if/elif por operador GPS; el servicio conoce dict/tupla, grados/micro-grados, km/h y m/s | 75-96 | Adapter | D (inversión de dependencias) | 1 clase por operador y un puerto | Aceptado |
| 2 | Bloque de reintentos duplicado para los operadores A y B (R-04: red móvil con cortes) | 76-84, 86-95 | Decorator (`ConReintentos`) | S (responsabilidad única) | 1 clase; reintentar solo ante `TimeoutError` | Aceptado |
| 3 | if/elif por algoritmo de ETA dentro de un bucle (QA-03: cambiar el algoritmo en ≤ 2 días-persona) | 129-134 | Strategy + Factory (registro) | O (abierto/cerrado) | 1 clase por algoritmo y un registro | Aceptado |
| 4 | Condicionales sobre `viaje.estado` repartidos en 4 métodos | 54, 62-66, 72, 104-123 | State | O y L | 1 clase base y 5 estados | Aceptado: coincide con `estados-viaje.mmd` (Lab 05) |
| 5 | El servicio arma a mano las alertas y los avisos push mientras detecta | 107-108, 114, 139 | Observer | S y O | Publicador y suscriptores | Aceptado |
| 6 | if/elif por proveedor de LLM y validaciones de salida mezcladas | 161-174 | Strategy + Adapter + Chain of Responsibility | S, O y D | Puerto `ProveedorLLM` y un eslabón por regla | Aceptado |
| 7 | "Hacer `FabricaAlgoritmos` / `FabricaOperadores` Singleton" | n/a | Singleton | n/a | Estado global | **Rechazado:** impide inyectar GPS y LLM simulados en las pruebas; se inyecta la dependencia |
| 8 | "Usar Abstract Factory para crear familias (GPS + LLM + algoritmo)" | n/a | Abstract Factory | n/a | Jerarquía de fábricas | **Rechazado:** no hay familias de productos relacionados; sería sobreingeniería |