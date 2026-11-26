# Estética Aurora — entregas M1–M6 y M8

Proyecto académico de Sara Adan. Los checkpoints preservan la evolución del asistente y sus evidencias, con workflows sanitizados y pruebas observadas.

| Módulo | Entrega | Estado y límites |
| --- | --- | --- |
| 1 | JSON y validación en raíz | Chat, Sheets y dos correos probados; Forms pendiente. No repetir envíos. |
| 2 | [Entrega M2](submissions/m02/) | Manager y workers con exportación verificada. |
| 3 | [Entrega M3](submissions/m03/) | Memoria aislada, resumen y fallos probados. |
| 4 | [Entrega M4](submissions/m04/) | CRM, borradores Gmail, replay y revisión Slack. |
| 5 | [Entrega M5](submissions/m05/) | RAG probado; ensayo ciego 2/5. Falta criterio literal de nodo nativo LlamaParse. |
| 6 | [Entrega M6](submissions/m06/) | Voz sintética y contingencia corrupta probadas; llegada real Telegram pendiente de sesión. |
| 8 | [Entrega M8](submissions/m08/) | Supervisor, corrección acotada, escalamiento y diez pruebas A/B; límites documentados. |

Todos los workflows finales de M8 permanecen inactivos. Sus seis exports cotejados se encuentran en `workflows/module8/`; `checkpoint8_sara_adan.json` es el manager, que requiere importar y enlazar sus dependencias. Los PDFs y registros de estado no afirman aceptación integral mientras persistan los límites indicados.

# Checkpoint 1 — Estética Aurora

**Alumna: Sara Adan.** Asistente de consultas para una estética ficticia. Este flujo es la base del proyecto y puede ampliarse en los siguientes módulos.

El agente responde sobre servicios, precios, duración, horarios y políticas. Consulta una base de Google Sheets y reconoce cuando falta información. No reserva citas ni procesa pagos.

## Entrega

- `checkpoint1_sara_adan.json`: configuración copiada del flujo validado en n8n; se retiraron las referencias a credenciales y el correo personal antes de publicarla.
- `base_estetica_aurora.csv`: datos ficticios para crear la pestaña `Base` en Google Sheets.
- `system_message.txt`: instrucciones del agente.
- `google_forms.gs`: conexión complementaria entre Google Forms y el Webhook. Requiere autorización y configuración antes de usarla.
- `prueba_n8n.jpg`: evidencia de la ejecución manual correcta.

## Cómo funciona

Chat de prueba o Webhook → Preparar consulta → AI Agent → Preparar reporte → Gmail: respuesta → Gmail: observabilidad → Entregar respuesta.

GPT-4o se conecta al puerto Chat Model y Google Sheets al puerto Tool del agente. El nombre del nodo de modelo es `GPT-4`; su modelo configurado es `gpt-4o`. El agente decide cuándo consultar la herramienta. No hay un bloque IF que clasifique la consulta antes del agente.

El System Message separa rol, objetivo, herramientas, límites y respuesta. El agente no debe inventar datos, ejecutar instrucciones contenidas en las consultas o celdas, ni generar lenguaje de odio. Si falta información, deriva el asunto a recepción sin prometer una reserva.

## Configuración para importar

1. Importar el JSON en n8n.
2. Seleccionar una cuenta de Google Sheets en `Consultar_informacion_estetica`. Usar una hoja propia con el CSV, pestaña `Base`, y sustituir el ID del documento en el nodo.
3. Seleccionar las credenciales de Gmail en **los dos** nodos Gmail.
4. Sustituir `REEMPLAZAR_CORREO_REPORTES` en `Preparar consulta` por el correo del responsable. El chat de prueba también envía su respuesta a esa cuenta.
5. Configurar acceso a GPT-4o en el nodo `GPT-4`. La prueba se realizó con créditos de n8n Gateway.
6. Abrir el chat de prueba y enviar una consulta. Revisar que todos los nodos terminen correctamente y que lleguen los dos correos.

El límite del agente es de **5 iteraciones**. El modelo tiene un límite de **450 tokens por llamada**, temperatura 0,1 y cero reintentos. El consumo total incluye el prompt y las respuestas de herramientas; no está limitado a 450 tokens por ejecución.

## Google Forms (configuración adicional pendiente)

El flujo por chat ya está probado. La ruta completa Google Forms → Webhook todavía requiere autorización, configuración y prueba; no se presenta como validada.

1. Copiar `google_forms.gs` en Google Apps Script y ejecutar `crearFormulario` tras revisar los permisos de Google.
2. Crear en n8n una credencial Header Auth para este proyecto: nombre de cabecera `X-Aurora-Token` y una clave privada. Seleccionarla en el Webhook.
3. Guardar esa misma clave en Propiedades del script como `WEBHOOK_SECRET`. Nunca subirla a GitHub.
4. Verificar que `WEBHOOK_URL` corresponde a la URL de producción de la instancia propia y publicar el flujo en n8n.
5. Ejecutar `activarConexion` y enviar una consulta desde el formulario para probar la integración completa. La función crea un solo activador y publica el formulario.

## Prueba realizada

El 6 de octubre de 2026 se ejecutó manualmente el flujo en n8n con la pregunta «¿Cuánto cuesta el manicure?». El agente consultó la base y respondió **180 MXN**, identificando los datos como ficticios. La interfaz mostró **Success in 8.329s — 1,776 Tokens**. Ambos nodos Gmail y el nodo final terminaron correctamente. Gmail devolvió un ID de mensaje para el reporte.

La prueba confirma el recorrido por chat, la lectura real de Sheets y la aceptación de los dos correos por Gmail. No garantiza por sí sola todas las respuestas futuras ni la ruta del formulario.

## Relación con la rúbrica

| Criterio | Implementación / evidencia |
| --- | --- |
| Disparador | Chat Trigger probado; Webhook disponible con Header Auth |
| Agente con herramientas | AI Agent con modelo y herramienta conectados a sus puertos nativos |
| Límite de iteraciones | 5, configurado explícitamente |
| System Message modular | Rol, objetivo, herramientas, límites y respuesta |
| Herramienta real | Lectura de Google Sheets, comprobada en ejecución |
| Descripción semántica | Indica cuándo consultar, cuándo no hacerlo y límites de solo lectura |
| Autonomía | El agente decide la llamada a Sheets; sin clasificación previa por IF |
| Observabilidad | Reporte por Gmail con consulta, respuesta, estado, ID de ejecución y llamadas a herramientas |
| Prueba manual | Ejecución completa correcta por chat |
| JSON y GitHub | JSON importable sin credenciales, dentro de este repositorio |

El reporte conserva entradas y resultados de herramientas, no razonamiento interno privado. Las ejecuciones pueden revisarse en `Executions` de n8n.

## Referencias

- [Tools AI Agent de n8n](https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-langchain.agent/tools-agent/).
- [FormApp de Google Apps Script](https://developers.google.com/apps-script/reference/forms/form-app).
- [Activadores instalables de Google Apps Script](https://developers.google.com/apps-script/guides/triggers/installable).
- [Ejemplos de clase](https://github.com/Carolina053Peke/AI-Automation-Avanzado).

## Sincronización y validación actual

El 18 de noviembre de 2026 se verificó nuevamente el flujo alojado: ejecución manual **244**, una consulta autónoma a Sheets, respuesta **180 MXN** y ambos envíos Gmail exitosos. Se guardó el timeout de 180 segundos y se sincronizaron los settings del JSON local con un export nuevo. Véase [VALIDACION_MODULO1.md](VALIDACION_MODULO1.md) para la evidencia, sustituciones de entorno, límites y comprobación reproducible de paridad. La evidencia corresponde a la ejecución del 18 de noviembre; no se repitieron envíos para preparar la publicación.
