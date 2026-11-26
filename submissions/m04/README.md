# Checkpoint 4 — Sara Adan

Gmail filtra mensajes automáticos, limpia el contenido y procesa cada correo en su propia ejecución. El procesador consulta un registro de recibos antes de tocar HubSpot o el modelo. Busca el contacto por email antes del upsert y crea exclusivamente un borrador Gmail con el destinatario y el hilo originales. Los casos que requieren revisión notifican al usuario privado verificado de Sara por Slack.

## Archivos e importación

`checkpoint4_sara_adan.json` es la entrada Gmail. Sus dependencias están en `workflows/`: `gmail_message.json`, `crm_contact.json` y `slack_review.json`. Son snapshots sanitizados de las versiones alojadas, no una promesa de funcionamiento sin configurar.

1. Importar el manager y workers congelados de `../m03/workflows/`, siguiendo su documentación. Importar CRM y Slack, después el procesador, y finalmente el checkpoint de entrada.
2. Asignar credenciales OAuth2 Gmail, HubSpot y Slack en sus nodos nativos. Las credenciales y tokens no están en los JSON.
3. Crear una tabla nativa `Aurora_Request_Receipts` con seis columnas de texto: `request_id`, `status`, `contact_id`, `draft_id`, `delivery_id`, `updated_at`. Los campos del sistema `id`, `createdAt`, `updatedAt` son adicionales.
4. Sustituir los marcadores `REPLACE_RECEIPT_TABLE_ID`, `REPLACE_CRM_WORKFLOW_ID`, `REPLACE_MANAGER_WORKFLOW_ID`, `REPLACE_GMAIL_MESSAGE_WORKFLOW_ID`, `REPLACE_SLACK_REVIEW_WORKFLOW_ID` y `REPLACE_SLACK_REVIEW_USER_ID` según corresponda. El destino Slack se configura en el nodo; el correo no puede elegirlo.
5. Conservar Wait For Sub-Workflow Completion y el modo `each` en la entrada. El procesador usa referencias `.first()` únicamente dentro de una ejecución de un solo correo. Configurar ejecución serial para esta práctica.
6. Mantener todos los flujos inactivos hasta revisar credenciales y IDs. La entrada escucha únicamente `label:AURORA_TEST -in:drafts`, no descarga adjuntos y no se activó durante las pruebas. Las pruebas usaron entradas sintéticas manuales.

## Guardas y contratos

El IF inmediatamente posterior a Gmail bloquea Auto-Submitted, X-Autoreply/X-Autorespond, Precedence bulk/list/junk, remitentes no-reply/mailer-daemon y asuntos out-of-office/undeliverable. Set/Edit Fields conserva solo From, Subject, BodyText, message_id, thread_id y display_name; descarta binarios/HTML sobrante y limita el cuerpo a 4000 caracteres Unicode.

HubSpot busca el email exacto (máximo dos resultados para detectar ambigüedad). Un contacto existente con nombre vacío entrante no pierde su nombre. Tras un error de escritura hay una sola lectura de reconciliación, sin segundo intento de escritura. Esto permite recuperar un contacto existente tras conflictos o respuestas inciertas, sin atribuir confirmación a una actualización no demostrada.

El manager M3 recibe RequestV1 y calcula en dry_run. Este adaptador posee los efectos externos y utiliza `output`, el campo real de respuesta del manager. Solo status=success con texto no vacío llega a Create Draft; no existe nodo Gmail Send.

Slack recibe cinco campos: request_id, domain, status, reason (máximo 200 caracteres) y record_reference. Su IF exige needs_human, aurora_demo e ID Gmail válido. No recibe cuerpo, email, adjuntos ni URL de reanudación. Los recibos completed se devuelven por una rama separada que no vuelve a notificar.

## Evidencia observada

| Prueba | Resultado |
|---|---|
| HubSpot crear / encontrar / actualizar | Mismo contacto en las tres operaciones. |
| Siete filtros | Todos bloqueados antes del LLM; revalidados tras separar el procesador. |
| Lote de dos mensajes | Dos borradores reales, destinatarios e hilos distintos correctos; respuestas 180 MXN y 40 minutos. |
| Replay del lote | Mismos dos IDs de borrador y borrador_existente; regresión posterior a Slack también pasó. |
| Identidad Slack | Usuario activo sara favila, no bot, workspace de prácticas. |
| Aviso privado Slack | Aceptado por el proveedor. El primer arnés buscó ts en el lugar incorrecto; la evidencia conserva ese fallo de aserción, sin ocultarlo ni reenviar. |
| Recibo incompleto + Slack | needs_human, sin borrador, notificación aceptada; aserción integrada PASS. |

Se crearon dos borradores de entrada sin destinatario y dos borradores de respuesta para probar hilos reales. Ningún correo fue enviado. Se enviaron dos avisos educativos a la cuenta privada verificada de Sara: uno directo y uno por la ruta integrada de revisión. No se afirma lectura humana del aviso.

Las capturas `evidence/screenshots/{gmail,hubspot,slack}-connected.png` muestran conexiones OAuth reales sin secretos. `replay-result.png` muestra el resultado de la regresión. Las observaciones JSON son transcripciones de UI explícitamente etiquetadas; no son exports crudos de ejecución. El manifiesto contiene hashes de los cuatro snapshots. `scripts/verify_module4_exports.py` verifica paridad contra los exports privados originales y documenta la normalización de defaults de n8n.

## Límites operativos

La deduplicación demostrada es secuencial. La tabla no ofrece una reserva atómica distribuida en este diseño. Un recibo processing o delivery_unknown nunca dispara automáticamente otro borrador: requiere reconciliación humana. Repetir un recibo incompleto puede repetir el aviso Slack; no hay garantía exactamente-una-vez de notificaciones. No hay reintentos automáticos de envío.

La prueba integrada de recibo incompleto no simula una caída real de Gmail/HubSpot. Los caminos de error y reconciliación están implementados y cubiertos localmente; no se afirma haber provocado HTTP 409/429 ni timeout en proveedores reales. Los flujos guardados tienen timeout 180s, historial fallido/exitoso/manual desactivado, invocación restringida al mismo propietario y MCP desactivado. Los arneses sintéticos de prueba no son despliegues de producción.

Estado: implementación y evidencias locales congeladas; publicación GitHub pendiente junto al paquete final. M5, M6 y M8 continúan por separado.
