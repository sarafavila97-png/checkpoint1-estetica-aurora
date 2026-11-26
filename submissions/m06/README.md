# Módulo 6 — validación parcial

Los seis workflows están importados, inactivos y cotejados con sus exports alojados. El informe de 15 páginas incluye once capturas auténticas de n8n y los prompts exactos.

Pruebas reales: componentes Whisper/ElevenLabs con una pregunta sintética (fallo factual original conservado) y regresión textual correcta después de reparar la referencia de Sheets y su extracción de evidencia. La respuesta reparada contiene 180 MXN y 40 minutos, con 175 caracteres.

Whisper rechazó audio inválido en una prueba aislada y activó la contingencia sin modelo de respuesta, TTS ni Telegram. Se retiraron los bytes del fixture actual y los archivos de audio temporales conocidos; el workflow se archivó. No se afirma eliminación de versiones históricas o retención del proveedor.

Pendiente: llegada real de nota de voz y respuesta Telegram (no hay sesión iniciada en los navegadores ni Telegram nativo disponible). No se declara cumplimiento completo ni coste medido.

`workflows/` y `evidence/` son copias de los artefactos revisados de M6. `report.md` es la fuente del PDF. No activar la entrada antes de completar el control operativo del bot y configurar el modo autorizado. La versión integrada M8 se entrega por separado; este checkpoint conserva la lógica M6.

Auditoría adicional del 26 de noviembre: véase [registro de pendientes](../../evidence/remaining-gap-audit.json). Reconfirma la limitación nativa de M5 y el inicio de sesión pendiente de Telegram. Gateway muestra USD 0.16 agregados para el workflow M8, incluidos desarrollo y corridas oficiales; no permite imputarlos a las diez corridas ni separar A/B. La estimación minorista y los resultados congelados permanecen intactos.
