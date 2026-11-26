# Checkpoint 5 — Sara Adan

El manager M5 extiende M3 y separa Aurora de Outer Agent. Aurora conserva Sheets y memoria Airtable; Outer Agent usa exclusivamente la fuente académica PDF v1 de diez páginas. La fuente no es una política institucional ratificada.

## Importación

Importar primero los workers históricos M3 y el writer M2, después `workflows/outer_agent_retrieval.json`, `outer_agent_knowledge.json` y `aurora_manager.json`. Asignar las credenciales existentes y sustituir los IDs `REPLACE_*` por los recursos propios. La llamada documental espera el resultado del sub-workflow. Mantener los tres workflows inactivos durante la configuración; los exports sanitizados no incluyen credenciales.

## Recuperación y límites

El nodo nativo instalado LlamaParse Platform permite Top K, pero su operación observada pierde scores y metadatos. Por ello este checkpoint utiliza HTTP autenticado más validación determinista y una herramienta de sub-workflow. No se presenta como Vector Store Retriever nativo: ese criterio literal sigue pendiente.

La configuración congelada antes de abrir las preguntas reservadas fue Top K 3 y Minimum Score 0.5, aplicado al `rerank_score` real. Se verifican archivo, versión, páginas e índice de chunk. El parámetro remoto `score_threshold` no se equipara al rerank score. Solo se citan páginas realmente recuperadas. Sin soporte se responde literalmente «No sé. No está documentado en la fuente disponible.»

## Evaluación observada

Cinco preguntas ciegas se ejecutaron una vez después de congelar código, prompt y configuración. T3 (respuesta frente a resolución el mismo día) y T5 (certificado no documentado) fueron correctas. T1 escaló innecesariamente; T2 y T4 devolvieron No sé pese a existir respuesta en la fuente. Resultado independiente: **2/5, 40%**. No se ajustó el umbral ni se repitió la evaluación para sustituir estos resultados.

`evidence/blind-results-raw.json` contiene las respuestas completas descargadas del arnés real, no una transcripción truncada. `blind-evaluation.json` conserva la rúbrica, fallos y hash. Duración total observada: 32.338 s; no se dispone de latencia individual ni facturación exacta y no se inventan costos. La causa interna de T2/T4 no está instrumentada; umbral y selección son hipótesis.

Las pruebas de desarrollo verificaron respuesta con citas y abstención ante consulta ajena. La regresión del manager verificó precio/duración Aurora y separación de dominios. El arnés original exigía evidencia vacía como array en fallbacks que la omiten; ese fallo del arnés queda registrado, junto a la evaluación del comportamiento, sin reenviar casos.

## Evidencia y privacidad

El PDF de entrega contiene cinco piezas: fuente, recuperación, prompt, evaluación y gobernanza. Las capturas son reales, sin secretos. `source/` contiene el PDF fuente, separado del informe. Los tres exports tienen paridad verificada contra descargas alojadas; timeout 180 s, historial fallido/exitoso/manual desactivado, mismo propietario y MCP desactivado. La fuente de las pruebas reservadas nunca se indexó.

Este es un baseline académico con cobertura parcial, no una afirmación de cumplimiento total. La política de actualización, propietario propuesto y rollback están en `docs/knowledge-governance.md` del repositorio. Los adaptadores finales M6/M8 deben enlazarse al manager evolucionado; los checkpoints históricos permanecen congelados.

Auditoría adicional del 26 de noviembre: véase [registro de pendientes](../../evidence/remaining-gap-audit.json). Reconfirma la limitación nativa de M5 y el inicio de sesión pendiente de Telegram. Gateway muestra USD 0.16 agregados para el workflow M8, incluidos desarrollo y corridas oficiales; no permite imputarlos a las diez corridas ni separar A/B. La estimación minorista y los resultados congelados permanecen intactos.
