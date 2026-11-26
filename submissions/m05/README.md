# Checkpoint 5 — Sara Adan

El manager M5 extiende M3 y separa Aurora de Outer Agent. Aurora conserva Sheets y memoria Airtable; Outer Agent usa exclusivamente la fuente académica PDF v1 de diez páginas.

## Importación

Importar primero los workers históricos M3 y el writer M2, después `workflows/outer_agent_retrieval.json`, `outer_agent_knowledge.json` y `aurora_manager.json`. Asignar las credenciales existentes y sustituir los IDs `REPLACE_*` por los recursos propios. La llamada documental espera el resultado del sub-workflow. Mantener los tres workflows inactivos durante la configuración; los exports sanitizados no incluyen credenciales.

## Recuperación documental

El Tools Agent consulta una herramienta lateral de sub-workflow conectada al endpoint oficial de LlamaCloud mediante HTTP autenticado. El adaptador conserva scores y metadatos y valida la evidencia de forma determinista antes de responder.

La configuración congelada antes de abrir las preguntas reservadas fue Top K 3 y Minimum Score 0.5, aplicado al `rerank_score` real. Se verifican archivo, versión, páginas e índice de chunk. El parámetro remoto `score_threshold` no se equipara al rerank score. Solo se citan páginas realmente recuperadas. Sin soporte se responde literalmente «No sé. No está documentado en la fuente disponible.»

## Evaluación observada

Cinco preguntas ciegas se ejecutaron una vez después de congelar código, prompt y configuración. T3 (respuesta frente a resolución el mismo día) y T5 (certificado no documentado) fueron correctas. T1 escaló innecesariamente; T2 y T4 devolvieron No sé pese a existir respuesta en la fuente. Resultado independiente: **2/5, 40%**. No se ajustó el umbral ni se repitió la evaluación para sustituir estos resultados.

`evidence/blind-results-raw.json` contiene las respuestas completas descargadas del arnés real, no una transcripción truncada. `blind-evaluation.json` conserva la rúbrica, fallos y hash. Duración total observada: 32.338 s; no se dispone de latencia individual ni facturación exacta y no se inventan costos. La causa interna de T2/T4 no está instrumentada; umbral y selección son hipótesis.

Las pruebas de desarrollo verificaron respuesta con citas y abstención ante consulta ajena. La regresión del manager verificó precio/duración Aurora y separación de dominios. El arnés original exigía evidencia vacía como array en fallbacks que la omiten; ese fallo del arnés queda registrado, junto a la evaluación del comportamiento, sin reenviar casos.

## Evidencia y privacidad

El PDF de entrega contiene cinco piezas: fuente, recuperación, prompt, evaluación y gobernanza. Las capturas son reales, sin secretos. `source/` contiene el PDF fuente, separado del informe. Los tres exports tienen paridad verificada contra descargas alojadas; timeout 180 s, historial fallido/exitoso/manual desactivado, mismo propietario y MCP desactivado. La fuente de las pruebas reservadas nunca se indexó.

La política de actualización, propietario propuesto y rollback están en `docs/knowledge-governance.md` del repositorio. Los adaptadores finales M8 ya enlazan el manager supervisado y sus workers de voz/documentación; los checkpoints históricos conservan cada etapa de la evolución.
