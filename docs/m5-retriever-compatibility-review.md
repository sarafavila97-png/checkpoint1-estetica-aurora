# Revisión de compatibilidad del retriever M5

Revisión documental: 26 de noviembre de 2026. Es investigación técnica previa, no evidencia de ejecución ni aceptación del módulo.

## Requisito original

La captura 03 solicita un Vector Store Retrieve Tool conectado lateralmente al Tools Agent, dirigido al índice de LlamaCloud, con Top-K y Minimum Score visibles y configurados. No basta con renombrar un nodo HTTP para afirmar que es ese componente.

## Evidencia oficial revisada

- [Vector Store Retriever de n8n](https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.retrievervectorstore/): la documentación enumera Limit como parámetro y explica que recupera documentos de un vector store. No documenta Minimum Score en ese nodo.
- [Vector Store Question Answer Tool de n8n](https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.toolvectorstore/): describe una herramienta lateral que responde a partir de fragmentos de un vector store; documenta descripción de datos y límite de resultados. No enumera un selector de índice LlamaCloud ni Minimum Score.
- [Código del conector oficial de LlamaIndex, retrieveProperties](https://github.com/run-llama/n8n-llamacloud/blob/master/nodes/LlamaParsePlatform/resources/retrieve/index.ts): la versión consultada expone Index ID, Query y Top K. No expone un campo de umbral. Es una referencia upstream mutable; aún debe compararse con la versión instalada.

## Consecuencia para implementación

Estas fuentes muestran una discrepancia entre el control visual descrito en el enunciado y los parámetros documentados. No demuestran por sí solas que toda configuración compatible sea imposible.

Antes de cerrar M5, comprobar la versión y puertos disponibles en la instancia; buscar una conexión nativa soportada al índice existente; inspeccionar los scores y metadatos reales. Un adaptador con umbral efectivo puede satisfacer la función de recuperación, pero debe identificarse como adaptación y no como coincidencia literal del nodo solicitado. Mantener explícito cualquier requisito literal no demostrado.

No crear otro corpus ni migrar los documentos para disimular la discrepancia. No inventar scores ni aplicar 0.5 sin comprobar la escala del proveedor. Las capturas finales deben mostrar los controles que realmente gobiernan la consulta ejecutada.

## Auditoría de la instancia y paquete instalado

El 26 de noviembre de 2026 se comprobó n8n **2.49.6** y `@llamaindex/n8n-nodes-llamacloud` **6.7.2**, etiquetado Latest en el catálogo. La operación Retrieve Context From an Index muestra únicamente Index ID, Query y Top K; no hay Minimum Score. Se cotejó el archivo del paquete oficial fijado a 6.7.2 con la referencia ya inspeccionada: hash SHA-256 `97f21c5aa8799f003dbd2a451570ada4bd99dded0ab0099a9b259825fe6c42e2`.

El descriptor tiene entradas/salidas Main y `usableAsTool: true`, pero no salida `ai_vectorStore` ni implementación `supplyData`. Por tanto **sí admite uso como herramienta del agente**, pero no como proveedor del puerto Vector Store. La operación conserva sólo `content` en `{context: [...]}` y descarta scores y metadatos; no permite reconstruir un umbral verificable después de esa salida. No se debe interpretar la falta del puerto vectorial como falta absoluta de soporte de herramientas.

En el catálogo lateral del AI Agent se abrió **Vector Store Question Answer Tool**. Sus parámetros son Description of Data y Limit (`topK`); exige entradas Vector Store y Model. Al buscar Llama en el selector del puerto Vector Store, la interfaz devolvió **No results**. Se inspeccionaron los proveedores disponibles; LlamaCloud no figura. Los nodos se añadieron sólo a un workflow de inspección sin ejecutar y se archivó al terminar.

La discrepancia queda establecida para esta instancia y versión, no para cualquier implementación futura. Cambiar al conector LlamaParse nativo no cerraría Minimum Score ni conservaría evidencia de score. No se migró corpus, renombró HTTP ni relajó la rúbrica. El límite externo requiere un proveedor vectorial compatible que conserve score/umbral o una disposición explícita del docente sobre la adaptación funcional. Detalles reproducibles y alcance en [remaining-gap-audit.json](../evidence/remaining-gap-audit.json).
