# Validación y sincronización — 18 de noviembre de 2026

## Resultado

Se probó el workflow alojado **Checkpoint 1 - Estética Aurora - Sara Adan**, ID `fM6BrbEZI0ia7pq3`. Ejecución manual **244**, iniciada el 18 de noviembre de 2026 a las 18:04:18, America/Denver. La lista de Executions conserva el resultado **Succeeded in 7.472s**. El panel de chat indicó **Success in 8.34s — 1,778 Tokens**; son las dos mediciones mostradas por interfaces distintas.

Entrada efectiva: `¿Cunto cuesta el manicure?` (la entrada del navegador omitió la letra acentuada). El agente respondió que el manicure clásico cuesta **180 MXN**, identificó el negocio como ficticio y remitió a recepción para más información. No fue necesario repetir la prueba.

Evidencia inspeccionada directamente en los resultados de n8n:

- El agente invocó `Consultar_informacion_estetica` una vez, con `{}` como entrada. El tool devolvió 12 registros de la base ficticia.
- Hubo dos llamadas al modelo: selección de herramienta y respuesta final. El modelo reportado fue `gpt-4o-2024-08-06`.
- `Preparar reporte` terminó correctamente y produjo `respuesta_generada`, ejecución `244`, una llamada registrada, consulta, respuesta, límite de cinco iteraciones y observación de la herramienta.
- `Gmail - Respuesta`: Success in 619ms, ID de mensaje no vacío y etiqueta `SENT`.
- `Gmail - Observabilidad`: Success in 444ms, ID de mensaje no vacío y etiqueta `SENT`.
- Ambos correos se enviaron a la cuenta de reportes existente y autorizada. Se omiten dirección e IDs de correo del documento público.
- `Entregar respuesta` completó el recorrido y devolvió la respuesta al chat.

Esto verifica aceptación de los mensajes por Gmail, no lectura humana. La evidencia es una transcripción de resultados inspeccionados; no se presenta como un archivo de ejecución exportado ni como una captura nueva. La ejecución retenida puede consultarse en la instancia autenticada, sujeto a su política de retención.

## Paridad del JSON

Se descargó un export nuevo después de guardar el timeout de **180 segundos** en el workflow alojado. No se modificaron nodos, conexiones, prompts, herramientas, modelo ni destinatarios. El workflow sigue sin publicar; la prueba manual no requirió activarlo.

El JSON público conserva exactamente los nodos, conexiones y settings de ese export, salvo estas sustituciones deliberadas:

1. Se eliminan `credentials` de Webhook, GPT-4, Sheets y ambos nodos Gmail. Al importar, seleccionar las credenciales propias correspondientes; los secretos nunca se publican.
2. En `Preparar consulta`, el valor de `const correo_reportes` se sustituye por `REEMPLAZAR_CORREO_REPORTES`. Reemplazarlo por una cuenta autorizada antes de ejecutar. La ruta de chat usa esa misma cuenta para ambos envíos.
3. Se omiten los campos superiores `id`, `versionId`, `meta`, `nodeGroups` y `tags`, propios de la instancia (los dos últimos estaban vacíos).

Se conserva el ID de hoja ya existente en la entrega; usar una hoja accesible y reasignarlo al importar en otra cuenta. Esa reasignación es una adaptación de entorno, no parte de la comparación con la instancia actual.

Settings sincronizados: `executionOrder: v1`, `binaryMode: separate`, `timeSavedMode: fixed`, `callerPolicy: workflowsFromSameOwner`, `executionTimeout: 180`, `availableInMCP: false`. Se eliminaron del JSON público las opciones explícitas de guardar ejecuciones que no estaban serializadas en el export alojado. La interfaz confirmó **Default - Save** para ejecuciones fallidas, exitosas y manuales; el resultado 244 retenido confirma que se guardó esta prueba manual. Otra instancia debe revisar sus propios valores predeterminados. No se afirma identidad byte a byte ni igualdad de credenciales entre entornos.

Para comprobar nuevamente la paridad, descargar el export privado fuera del repositorio y ejecutar:

```sh
python3 scripts/verify_parity.py /ruta/privada/export-n8n.json
```

La comparación recursiva admite exclusivamente las sustituciones enumeradas, no ignora settings ni lógica. No subir el export privado a GitHub.

## Comprobación de la consigna original del Módulo 1

| Requisito | Resultado y evidencia |
|---|---|
| Chat Trigger o Webhook | Chat Trigger ejecutado; Webhook adicional conservado. |
| AI Agent/Tools Agent y modelo nativo | Agente con modelo conectado al puerto nativo; GPT-4o ejecutado. |
| Entre 5 y 10 iteraciones | Límite explícito de 5; se conserva en el export y reporte. |
| System Message modular y límites | Rol, objetivo, herramientas, límites, respuesta y derivación; coincide con `system_message.txt`. |
| Herramienta nativa lateral con descripción semántica | Google Sheets conectado a `ai_tool`; descripción define casos de uso y solo lectura. |
| Decisión autónoma de uso | Llamada real elegida por el agente, sin IF previo ni lectura incondicional de Sheets. |
| Gmail/Slack final con actividad y resultados | Gmail de observabilidad exitoso; reporte con nombre, entrada y observación del tool. |
| Prueba manual completa antes de exportar | Ejecución 244 exitosa; configuración exportada y probada sin cambios de lógica posteriores. |
| `checkpoint1_nombre_apellido.json` en GitHub | Nombre correcto: `checkpoint1_sara_adan.json`. Esta revisión incluye el export sincronizado y la evidencia de la prueba del 18 de noviembre. |

El repositorio ya tiene una entrega histórica pública y una captura anterior. Esta revisión no altera ni sustituye esa evidencia histórica. La fecha de la prueba y la fecha de publicación pueden ser distintas; esta revisión no afirma una nueva ejecución en la fecha de publicación.

## Alcance y límites

Google Forms sigue siendo opcional y no se probó. No se añadieron componentes de módulos posteriores. Los dos Gmail permanecen en serie: si el primero falla, el segundo no se ejecuta. El reporte existente puede mostrar cero llamadas cuando falta evidencia intermedia y recorta observaciones largas. Son límites de robustez conocidos; no se produjo ninguno durante la prueba exitosa. No se ejecutaron casos adicionales de saludo, error o reservas, ni se afirma cobertura de todas las consultas.
