# M3: implementación en verificación, no entrega final

Los archivos de esta carpeta son borradores generados y sanitizados, no exports certificados. En n8n están guardados los workers de lectura/escritura, conocimiento con memoria corta y manager con resumen automático y consulta de preferencias desde memoria persistente.

Verificado: diez casos reales de persistencia; seis turnos con resumen generado por el modelo, contador reiniciado y conservación de la preferencia del primer turno; recuerdo desde una sesión nueva con solo resumen restaurado; fallo controlado de tabla Airtable sin modificar memoria previa. Las observaciones distinguen transcripción de UI de export nativo.

La prueba de seis turnos detectó ausencia de evidencia actual en una respuesta. El worker de negocio ya contiene un error estructurado para esa condición; la ruta separada de recuerdo usa contexto persistente validado. Falta cerrar regresión de consultas de negocio tras esa corrección, exports frescos/paridad de todo M3, capturas y PDF de tres páginas. Los workflows de pruebas sintéticas aún necesitan archivar o ajustar retención.
