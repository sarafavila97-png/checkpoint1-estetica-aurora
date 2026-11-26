# Módulo 8 — supervisión y evidencia

Seis workflows finales importados y cotejados con exportaciones alojadas, todos inactivos. El PDF incluye el prompt y esquema exactos, resultados de diez corridas congeladas, evaluación independiente, uso completo de 42 llamadas y diez capturas auténticas.

Resultados: A 5/5 y B 5/5 en esta muestra pequeña, sin correcciones oficiales. Pruebas separadas demuestran una corrección real, escalamiento con Slack y Wait de un minuto, y guardas con decisiones explícitamente inyectadas. Producción conserva Wait de 24 horas y termina en revisión pendiente, nunca en aprobación automática. No se implementó aprobación humana autenticada automatizada.

Estimación minorista sin caché: 0.14656 USD por las diez corridas; cargo real Gateway desconocido. El 100% de esta muestra no sustituye el ensayo ciego M5 de 2/5 ni demuestra una mejora general de B. M8-04 recuperó evidencia diferente entre brazos; queda documentado.

## Importación

Importar primero las dependencias M3 (lectura/escritura de memoria y workers), M5 (retrieval y agente Outer), M6 (transcripción y worker Aurora), y M4 (CRM/recibos). Importar supervisor M8, manager M8, entrega Telegram M8, procesador Gmail M8 y finalmente las dos entradas M8. Enlazar todos los marcadores REPLACE_* a los IDs de la instancia propia y asignar credenciales en n8n. Los JSON públicos no incluyen secretos. Verificar nombres y columnas de los contratos antes de probar.

Gmail usa el manager en dry_run para que el adaptador sea el único propietario del borrador/CRM; no hay envío de correo. La regresión de dos mensajes creó borradores en hilos distintos y el replay conservó sus IDs. La deduplicación probada es secuencial, no una garantía de concurrencia atómica.

Telegram permanece inactivo y dry_run. La llegada y respuesta de una nota de voz genuina requieren sesión del usuario y validación operativa del bot. No activar ni cambiar a live hasta completar esa prueba autorizada. El texto aprobado se valida y pasa intacto a TTS; no hay reescritura posterior al juez.

`workflows/` y `evidence/` son copias revisadas; `report.md` es la fuente del PDF. Los constructores, contratos y tests están en las carpetas del repositorio. La prueba de escalamiento envió una notificación real al revisor; no repetirla para regenerar evidencia. M1 ya envió sus correos y tampoco debe repetirse.

Auditoría adicional del 26 de noviembre: véase [registro de pendientes](../../evidence/remaining-gap-audit.json). Reconfirma la limitación nativa de M5 y el inicio de sesión pendiente de Telegram. Gateway muestra USD 0.16 agregados para el workflow M8, incluidos desarrollo y corridas oficiales; no permite imputarlos a las diez corridas ni separar A/B. La estimación minorista y los resultados congelados permanecen intactos.
