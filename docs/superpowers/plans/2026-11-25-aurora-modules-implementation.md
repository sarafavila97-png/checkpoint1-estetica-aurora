# Aurora Modules Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task in the established implementation chat. Steps use checkbox (`- [ ]`) syntax for tracking. User subsequently authorized full implementation, testing and repository publication; proceed in the established chat without another plan approval.

**Goal:** Extender el mismo proyecto Estética Aurora desde el M1 validado hasta los módulos suministrados M2–M6 y M8, con pruebas reales, trazabilidad y entregables verificables.

**Architecture:** Un manager evolutivo conserva las entradas, el agente y la base de M1; delega mediante contratos JSON en workers separados. Airtable aporta memoria por sesión; HubSpot, Gmail y Slack integran operaciones; un worker documental consulta exclusivamente Outer Agent. Voz y juez se incorporan alrededor del mismo recorrido, con una única frontera de entrega y efectos externos controlados.

**Tech Stack:** n8n Cloud existente, GPT-4o mediante Gateway, Structured Output Parser, Execute Sub-workflow/Trigger, Google Sheets, Airtable OAuth, HubSpot OAuth, Gmail OAuth, Slack OAuth, LlamaCloud Index v2, Whisper `whisper-1`, ElevenLabs `eleven_multilingual_v2`, Telegram nativo. Python 3 estándar para validación de exports y métricas; herramientas PDF del entorno ya disponible para entregas. No backend nuevo ni servicios nuevos.

**Spec:** Las ocho imágenes originales en `/Users/sg/Documents/Codex/2026-11-18/realtime-voice-chat/outputs/whatsapp-images/`: `01-assignment.jpg` (M1), `07-assignment.jpeg` (M2), `06-assignment.jpeg` (M3), `05-assignment.jpeg` + `04-assignment.jpeg` (M4), `03-assignment.jpeg` (M5), `02-assignment.jpeg` (M6), `08-assignment.jpeg` (M8). Este plan contiene las decisiones de diseño y la matriz de cobertura; leer también `README.md`, `VALIDACION_MODULO1.md` y el informe privado `../realtime-voice-chat/outputs/readiness-report.md` resuelto desde la carpeta de fecha, no desde el repositorio.

## Global Constraints

- Estado: **implementación autorizada por instrucción posterior del usuario**, incluidos entregables, pruebas y publicación del repositorio. Ejecutar por etapas en el chat establecido; respetar restricciones concretas de credenciales, webhooks y comunicaciones.
- Repositorio real: `/Users/sg/Documents/Codex/2026-11-18/aurora-homework-alignment/checkpoint1-estetica-aurora`; base inspeccionada `4f1478c57fef93bdb39e08866c6dfe370a8642be`. Todas las rutas relativas siguientes pertenecen a ese repositorio.
- Un proyecto que crece; importar y extender el checkpoint anterior, nunca reconstruir cada módulo desde cero. Congelar la entrega histórica M1 y conservar trazabilidad de nodos y cambios en snapshots posteriores.
- M1: Tools Agent, herramienta lateral autónoma, **5–10 iteraciones**; conservar **5**. M2: **al menos dos workers independientes**, Execute Workflow Trigger y **Wait for child to finish**. La pausa debe producir un resultado estructurado antes de continuar.
- M3: cinco columnas: `Session_ID`, `Fecha de actualización`, `Resumen consolidado`, `Estado del caso`, `Datos clave`. Resumir cuando la conversación **supere 5 mensajes**; implementación: sexto mensaje entrante aceptado, documentando esta unidad de conteo.
- M3 resumen exacto: `asunto_principal` string, `puntos_clave` array de strings, `accion_requerida` string. Contexto entre `[INICIO DE CONTEXTO COMPARTIDO]` y `[FIN DEL CONTEXTO COMPARTIDO]`.
- M4: IF anti-auto-reply inmediatamente tras Gmail Trigger; lookup antes de Create; salida Gmail **Create Draft**, nunca Send. Payload mínimo validado antes de CRM y mensajería.
- M5: documento **10–30 páginas** con títulos y tabla; **5 preguntas ciegas**; Top-K y Minimum Score reales y justificados; citar fuente y decir literalmente **“No sé”** si no hay soporte. No introducir pruebas reservadas en el índice.
- M6: binario **`data`**, idioma Whisper **`es`**, voz en español, máximo **200 caracteres** y sin enlaces/viñetas/markdown en texto hablado. IF/Switch inmediatamente después de Whisper. Audio no guardado en n8n, Sheets, Airtable, Drive, logs ni exports.
- M8: juez devuelve exactamente `exactitud_factual` entero **1–5** y `estado_veredicto` enum **APROBADO / CORREGIR / ESCALAR**. Switch de tres rutas; corrección acotada y Wait humano. **5 corridas A + 5 B**, no sustituir por resultados simulados.
- M7 y M9–M11 no tienen consigna disponible. No inventar tareas ni certificar esos módulos. La referencia a M11 explica continuidad, no autoriza requisitos nuevos.
- Credenciales y acceso existentes listos; esto no prueba implementación de módulos. Nada de compras, suscripciones, recargas automáticas, rotación de tokens o nuevas cuentas. No repetir el test Telegram ya autorizado: esa autorización se agotó con un mensaje.
- Datos académicos sintéticos; no reservas, pagos, diagnóstico médico ni promesas comerciales no documentadas. No almacenar razonamiento privado del modelo; registrar solamente llamadas, observaciones, decisiones estructuradas y resultados.

## Review Focus

1. **Cruce de identidad/dominio:** dos sesiones o cambio Aurora→Outer Agent nunca comparten memoria ni precios. Pruebas T2/T3/T6.
2. **Entrega duplicada:** replay de Gmail/Telegram o reanudación humana no duplica CRM, draft o salida; errores ambiguos al enviar no se reintentan automáticamente. Pruebas T4/T8/T9.
3. **Datos con instrucciones maliciosas:** correo, memoria y fragmentos son datos; no cambian rutas, destinatarios o permisos. Pruebas T3/T6/T9.
4. **Respuesta/modelo inválidos y dependencias caídas:** JSON incorrecto, timeout o resumen inválido desembocan en error/fallback, nunca en éxito vacío ni bucle. Pruebas T2/T3/T6/T9.
5. **Binarios durante Wait:** un Wait persiste su estado aunque los historiales estén desactivados; el audio debe terminar antes de ese punto y nunca entrar al supervisor. Pruebas T8/T9.

## Diseño elegido y alternativas

La continuidad n8n ya está decidida por la consigna y el proyecto. Se elige manager + workers pequeños, evolucionando un conjunto de exports versionados. Un monolito no cumple M2; reconstruir proyectos por módulo contradice la consigna; mover lógica a un backend nuevo añadiría infraestructura sin necesidad. Es una decisión del plan, no una supuesta aprobación adicional del usuario.

**Límite de conocimiento concreto:** `domain` es `aurora_demo` o `outer_agent`. En chat/Telegram el manager clasifica semánticamente la intención con JSON; menciones explícitas de Outer Agent/OuterAgent.ai o preguntas de seguimiento de una sesión ya marcada documental van a `outer_agent`. Preguntas de estética van a `aurora_demo`. Una pregunta mixta o “cuánto cuesta” sin contexto suficiente produce una única aclaración y no consulta ambos corpus. No fusionar respuestas de ambos dominios en una misma ejecución. Gmail del ejercicio se configura exclusivamente como `aurora_demo`; consultas ajenas se derivan a revisión, no cambian de organización por instrucciones del remitente.

Aurora usa únicamente `base_estetica_aurora.csv`/Sheets y mantiene “negocio ficticio” y MXN. Outer Agent usa exclusivamente el PDF v1 y sus fuentes, sin convertir el signo `$` en USD/MXN ni presentar escenarios ilustrativos como resultados auditados. Su documento es una síntesis pública autorizada para indexar, **no una política institucional ratificada**. Si la evaluación exige esa ratificación, es una decisión académica pendiente; mientras tanto la entrega declara procedencia y límites. No requiere inventar moneda, SLA ni políticas.

**Frontera de efectos:** workers devuelven propuestas/evidencia. El manager realiza lectura/memoria; CRM solo escribe campos sintéticos autorizados. La respuesta final pasa por el punto de entrega: chat devuelve texto, Gmail crea borrador, Telegram genera/envía audio únicamente durante pruebas autorizadas. Desde M8 ningún candidato rechazado llega al usuario ni a TTS. Una aprobación del juez no autoriza enviar correo: Gmail sigue draft-only. Slack recibe solamente alertas operativas mínimas y únicamente cuando su envío esté autorizado.

## Situación real y límites conocidos

M1 tiene 13 nodos; ejecución 244 del 18/11 verificó Sheets y dos correos. Mantener `checkpoint1_sara_adan.json`, `system_message.txt`, `base_estetica_aurora.csv`, `google_forms.gs`, `prueba_n8n.jpg`, `VALIDACION_MODULO1.md` como baseline. No volver a ejecutar esa cadena de dos envíos al hacer regresiones. Forms permanece opcional/no probado.

Readiness verificó Airtable create/get, Gmail inbox/draft, HubSpot read/create, GPT-4o + parser, Whisper, ElevenLabs y LlamaCloud. Telegram **Telegram account** corresponde al bot **8947518377 / @Sarapractica_bot**; mensaje aprobado 89 a chat privado **8860086970**, resultado `ok: true`. No cambiar al credential “Telegram account 2”. El webhook no ha sido inspeccionado ni activado. Slack y Sheets tienen evidencia previa, no una nueva prueba de envío Slack.

LlamaCloud: proyecto `f0b7251e-a5fe-46d8-a231-181ed03fc94f`, índice `dec-inryey4amn6uqtzn002x2ybda4rx`, 10 páginas saludables, sincronización manual. Nodo instalado `@llamaindex/n8n-nodes-llamacloud` v6.7.2 (“LlamaParse Platform”) devuelve tres **strings** con Top K 3; no devuelve metadatos/score en esa operación. No confundir eso con el retriever rubricado ya completo.

## Archivos y responsabilidades

| Ruta (crear salvo que indique modificar) | Responsabilidad |
|---|---|
| `README.md` (modificar) | Índice de módulos, importación, estado real y límites; conservar historia M1. |
| `docs/architecture.md`, `docs/contracts.md` | Flujo de datos, contratos y decisiones de dominio. |
| `docs/requirements-traceability.md`, `docs/environment-substitutions.md` | Requisito→nodo/prueba/evidencia y sustituciones exactas permitidas. |
| `config/environment.example.json`, `config/cost-policy.json` | IDs simbólicos sin secretos; límites y tarifas fechadas. |
| `workflows/aurora_manager.json` | Descendiente del M1; router, llamadas síncronas, memoria, control de entrega. |
| `workflows/workers/aurora_knowledge.json` | Execute Trigger → Tools Agent con Sheets lateral → WorkerResult. |
| `workflows/workers/response_writer.json` | Execute Trigger → redacción con evidencia suministrada → WorkerResult. |
| `workflows/workers/memory_read.json`, `memory_write.json` | Búsqueda exacta Session_ID, alta, resumen validado y actualización. |
| `workflows/workers/crm_contact.json` | Lookup por email normalizado → Create/Update acotado. |
| `workflows/workers/outer_agent_retrieval.json` | Recuperación con Top-K/score y metadatos normalizados; nunca datos Aurora. |
| `workflows/workers/judge.json`, `workflows/human_review.json` | Juez JSON sin efectos; pausa/revisión y salida humana controlada. |
| `workflows/channels/gmail_inbox.json`, `telegram_voice.json` | Adaptadores hacia el mismo manager; anti-loop y circuito binario respectivamente. |
| `workflows/channels/telegram_delivery.json` | TTS y Send Audio después de aprobación; separado de entrada binaria. |
| `prompts/manager.txt`, `aurora_knowledge.txt`, `response_writer.txt`, `summarizer.txt`, `outer_agent_rag.txt`, `voice.txt`, `judge.txt` | Prompts exactos sincronizados con exports. |
| `schemas/request.schema.json`, `worker-result.schema.json`, `memory-summary.schema.json`, `judge.schema.json`, `human-review.schema.json` | Validación explícita y versión de interfaces. |
| `tests/fixtures/module{2,3,4,5,6,8}.json`, `tests/test_module{2,3,4,5,6,8}.py` | Casos sintéticos, aserciones estáticas y validación de resultados observados. Crear seis archivos por conjunto, no el nombre literal con llaves. |
| `scripts/verify_workflow_bundle.py`, `scripts/sanitize_exports.py`, `scripts/verify_bundle_parity.py`, `scripts/report_metrics.py` | Contratos/puertos/límites, sanitización, comparación recursiva, métricas medidas. Mantener `scripts/verify_parity.py` de M1. |
| `evidence/module{2,3,4,5,6,8}/results.json`, `capture-index.md` | Resultados sintéticos, IDs y lista de capturas auténticas redactadas. Ningún audio ni token. |
| `submissions/m02/` … `m06/`, `m08/` | Snapshots exportados en cada milestone y fuentes Markdown de informes; nombres finales abajo. |
| `docs/knowledge-governance.md`, `docs/deployment-checklist.md` | Vigencia/propietario/versiones del corpus, ownership del webhook y rollback. |

Exports privados y manifest real quedan **fuera del repo**, en `/Users/sg/Documents/Codex/2026-11-18/aurora-homework-alignment/work/implementation-private/`. PDFs/capturas finales se copian también a `/Users/sg/Documents/Codex/2026-11-18/realtime-voice-chat/outputs/aurora-submissions/`. No crear esos workflows ni fixtures durante esta tarea de planificación.

## Contratos compartidos (v1)

Todos los sub-workflows aceptan/devuelven **un item JSON**, sin binarios. `additionalProperties:false` en objetos de frontera; campos opcionales se declaran expresamente. Importación rechaza referencias a workers ausentes.

**RequestV1**: `{schema_version:"1", request_id:string, session_id:string, domain:"aurora_demo"|"outer_agent", channel:"chat"|"gmail"|"telegram", query:string, user:{display_name:string,email:string|null}, context:{summary:Summary|null,case_status:string,key_facts:string[]}, evidence:Evidence[], candidate:string|null, correction_attempt:integer, mode:"dry_run"|"live"}`. `query` 1–4.000 caracteres, sin HTML; no adjuntos, token, destinatario libre ni URL de reanudación. `correction_attempt` empieza en 0. El request no puede alterar credenciales ni activar `live`; el adaptador autorizado impone mode.

**Session_ID**: prefijo `domain:channel:principal`. Telegram principal es chat ID del evento validado, Gmail email de remitente normalizado (thread/message ID identifica petición), chat un UUID persistente por conversación. Request ID: `gmail:<message_id>`, `telegram:<update_id>`, `chat:<event_uuid>`. El dominio se decide antes de buscar memoria, pero no antes de la decisión semántica del manager. Falta de session/principal → aclarar/rechazar; jamás usar una clave global por defecto.

**Evidence**: `{source_id:string,source_kind:"aurora_sheet"|"outer_agent_pdf",text:string,section:string|null,page_start:integer|null,page_end:integer|null,score:number|null,source_version:string}`. Solo citar páginas realmente devueltas; `null` no se transforma en un número inventado.

**WorkerResultV1**: `{schema_version:"1",request_id:string,status:"success"|"error"|"needs_human",domain:enum,result:{answer:string,evidence:Evidence[],proposed_action:"none"|"draft_email"|"review"},error:null|{code:string,message:string,retryable:boolean}}`. Error tipado con answer vacío no se convierte en éxito. Normalizar errores de nodo, schema y timeout a este contrato. El padre valida request_id/domain antes de usarlo.

**Summary**: exactamente `{asunto_principal:string,puntos_clave:string[],accion_requerida:string}`. Límites de diseño: 200/5×200/200 caracteres. No dirección de correo ni audio; `Datos clave` almacena JSON `{display_name,accepted_message_count,last_request_ids,key_facts}` con máximo 20 IDs y 5 hechos breves. `Estado del caso`: `nuevo|en_curso|requiere_revision|cerrado`. Resumen consolidado almacena solo Summary JSON válido.

**JudgeOutput**: exactamente dos propiedades requeridas: `exactitud_factual:{type:integer,minimum:1,maximum:5}`, `estado_veredicto:{enum:[APROBADO,CORREGIR,ESCALAR]}`. No añadir explicación a este JSON. Entrada del juez: query original + contexto Airtable + evidencia factual + respuesta propuesta, sin herramientas de escritura. Crítica de reintento se construye fuera del juez: puntuación, reglas incumplidas detectadas y evidencia permitida; no fingir una explicación que el juez no devolvió.

**HumanReview**: `{request_id:string,decision:"approve"|"reject"|"edit",edited_answer:string|null}`; autenticar reanudación con Header Auth de credencial n8n, verificar request_id y limitar a una resolución. No publicar el resume URL ni el secreto. `edit` requiere texto no vacío y validación del canal. `reject`/expiración cierran sin envío. Una aprobación humana no habilita Gmail Send.

**Deduplicación y concurrencia:** un registro de recibos en Data Table n8n `Aurora_Request_Receipts` (`request_id,status,contact_id,draft_id,delivery_id,updated_at`) evita replays completados. El estado `processing`/`delivery_unknown` no se reintenta ciegamente. No afirmar atomicidad que Airtable/Data Tables no garantizan: pruebas académicas con un único productor serial; si aparecen dos registros de sesión/recibo, fallar a revisión. Antes de despliegue concurrente exigir mecanismo de exclusión verificado; no introducir Redis u otro gasto en este alcance.

## Secuencia ejecutable y trazabilidad

| Requisito original | Tarea | Prueba/evidencia de cierre |
|---|---|---|
| M1 agente, tool autónoma, límites, observabilidad, JSON GitHub | T1 | Baseline 244 + parity existente; no reenvíos. |
| M2 manager, dos workers, trigger, wait, payload limpio, router, error | T2 | Dos éxitos, ambigüedad, error controlado y timeout con JSON; capturas PDF. |
| M3 cinco columnas, búsqueda Session_ID, IF alta/existente, delimitadores, >5, resumen JSON | T3 | Sesiones A/B aisladas; mensajes 5/6; error resumen no sobrescribe; PDF 3 páginas. |
| M4 tres OAuth, IF anti-loop, lookup/create/update, draft-only, Set limpio | T4/T5 | Casos tabla M4, capturas credenciales y JSON importable; cero Gmail Send. |
| M5 10–30 páginas, títulos/tabla, retriever Top-K/score, fuentes/No sé, cinco pruebas, gobernanza | T6/T7 | Adaptador verificado + 5 ciegas con precisión real + PDF de cinco piezas. |
| M6 trigger, data/es, agent, TTS, 200 caracteres, contingencia, privacidad | T8 | Circuito sintético y fallos; capturas settings/config + PDF único. |
| M8 juez exacto, 3 rutas, retries/Wait, 5+5, métricas/proyección | T9/T10 | Branch tests + 10 corridas medidas + PDF tres bloques. |
| Continuidad, export alojado, reproducibilidad y sustituciones | T1–T10 | Bundle parity y snapshot por hito, README y manifests. |

### T1 — Baseline y contrato de entrega (M1, sin reenviar correos)

**Files:** leer baseline listado arriba; crear docs/architecture.md, docs/contracts.md, docs/requirements-traceability.md, config/environment.example.json, scripts/verify_workflow_bundle.py; modificar README.md. Test inicial en `tests/test_module2.py`.

**Interfaces:** consume JSON M1; produce inventario de nombres/IDs, RequestV1/WorkerResultV1 y política de `mode`. Preservar nodo `Agente de consultas`, modelo GPT-4o y conocimiento Sheets en su worker descendiente.

- [ ] Registrar hashes del baseline y comprobar `git status`; aislar trabajo al ejecutar con la skill de worktrees si hay cambios ajenos, sin modificar esos cambios.
- [ ] Añadir test `test_baseline_preserved`: hashes de archivos M1 intactos; 13 nodos y puertos model/tool existentes. Test `test_bundle_rejects_missing_worker`: referencia ausente falla, no se considera importable.
- [ ] Ejecutar `python3 -m unittest discover -s tests -p 'test_module2.py' -v`; primero demostrar la comprobación que falta y después implementar `validate_bundle(paths:list[Path])->list[str]` en el script. Errores no imprimen credenciales.
- [ ] Importar copia del M1 como manager de desarrollo **inactivo**; preservar historia original. En la copia sustituir ambas ramas Gmail Send por entrega dry-run hasta M4. Anotar la diferencia semántica intencional; no editar la evidencia M1.
- [ ] Ejecutar `python3 scripts/verify_parity.py /ruta/privada/export-m1.json` contra export fresco sin ejecutar M1; PASS debe corresponder a la lógica original. Si hay deriva, documentarla antes de continuar, no normalizarla en silencio.
- [ ] Guardar baseline/contratos y commit `docs: establish evolving Aurora contracts and baseline`.

### T2 — Manager y dos workers reales (M2)

**Files:** workflows/aurora_manager.json; workflows/workers/aurora_knowledge.json, response_writer.json; prompts/manager.txt, aurora_knowledge.txt, response_writer.txt; schemas/request.schema.json, worker-result.schema.json; tests/fixtures/module2.json, tests/test_module2.py; evidence/module2/*; submissions/m02/report.md.

**Interfaces:** RequestV1 → WorkerResultV1. Knowledge usa tool Sheets autónoma; Writer recibe solo query/evidencia y redacta, sin inventar hechos ni llamadas externas. Ambos empiezan en Execute Workflow Trigger con entrada declarada.

- [ ] Añadir aserciones: `test_worker_contract_rejects_wrong_domain`, `test_wait_enabled_for_both_workers`, `test_no_binary_handoff`, `test_worker_failure_routes_to_human`, `test_unknown_route_no_worker`. Verificador falla antes de existir los workers.
- [ ] Evolucionar el manager con Tools Agent/router semántico de categorías `AURORA_INFO`, `OUTER_AGENT_INFO` (reservada hasta T6), `CLARIFY`, `HUMAN`. Switch solo ejecuta la ruta JSON del router; no reemplaza al agente por clasificación rígida de palabras.
- [ ] Implementar Set de payload antes de **cada** Execute Sub-workflow. Activar Wait for child to finish, timeout worker 60 s/manager 180 s, sin retries automáticos. Conectar dos canvases independientes; ambos retornan contrato success/error incluso ante error de proveedor capturable. Si el hijo falla antes de retornar, el padre normaliza ese error.
- [ ] Pruebas alojadas dry-run: manicure → Sheets 180 MXN y Writer; saludo → sin tool de negocio; ambigüedad → aclaración; worker con fallo inyectado → error estructurado/fallback; worker con demora forzada → límite y revisión. Dos request_id distintos no intercambian resultados. Inyectar fallos con fixtures, no credenciales reales rotas.
- [ ] Registrar resultado, ruta, calls y tiempos reales; no chain-of-thought. Capturar manager completo, dos workers, configuración wait/contrato, éxito y fallo en ejecución.
- [ ] Ejecutar verificador y pruebas M2; exportar bundle exacto tras pruebas. PDF `submissions/m02/preentrega_modulo2_adan_sara.pdf`: arquitectura, payload, routing, ejecución, error. JSONs opcionales se conservan para continuidad.
- [ ] Commit `feat: add synchronous Aurora manager and workers`; hito M2 cerrado solo con prueba real y PDF revisado visualmente.

### T3 — Memoria híbrida por sesión (M3)

**Files:** workflows/workers/memory_read.json, memory_write.json; modificar manager; prompts/summarizer.txt, manager.txt; schemas/memory-summary.schema.json; tests/fixtures/module3.json, tests/test_module3.py; evidence/module3/*; submissions/m03/report.md.

**Interfaces:** RequestV1.session_id → Summary/context; escritura acepta solo Summary validado + campos mínimos. Tabla nueva `Memoria_Aurora` en base autorizada `Aurora - Prácticas`; no reutilizar tabla `Prueba de conexión`.

- [ ] Añadir casos `test_two_session_isolation`, `test_new_existing_branches`, `test_summary_only_after_sixth_message`, `test_invalid_summary_preserves_previous`, `test_memory_injection_is_data`, `test_duplicate_rows_fail_closed`. Ejecutar antes de conectar persistencia para confirmar fallos esperados.
- [ ] Crear cinco columnas exactas: Session_ID texto clave, Fecha de actualización fecha/hora ISO, Resumen consolidado texto largo JSON, Estado del caso selección, Datos clave texto largo JSON. Buscar igualdad exacta Session_ID antes de llamar workers; escapar el filtro, nunca interpolar entrada como fórmula arbitraria. Cero filas → IF alta; una → inyectar; >1 → revisión.
- [ ] Conectar memoria corta nativa con ventana de seis intercambios y clave Session_ID para la conversación activa; no depender de ella como memoria duradera. Airtable conserva resumen/hechos, no historial completo. Tras reinicio, reconstruir contexto desde resumen y hechos disponibles, no fingir recuperación de texto perdido.
- [ ] Incrementar contador solo para request_id nuevo. Al sexto mensaje aceptado enviar el buffer disponible más resumen previo al summarizer; validar JSON exacto y límites; solo entonces actualizar Summary y reiniciar contador. Si memoria corta falta, resumir únicamente contexto disponible y marcar cobertura parcial en la evidencia; ningún dato inventado.
- [ ] Inyectar Summary/nombre/estado entre delimitadores explícitos y advertencia de datos no confiables. Mantener domain dentro de Session_ID para que un cambio de organización abra memoria separada.
- [ ] Test alojado: A y B intercalados, nuevo/existente, 5 vs 6 mensajes, duplicado de request, resumen malformado, Airtable caído. Verificar valores leídos/escritos por record_id, no solo nodo verde. No sobrescribir resumen válido con JSON roto.
- [ ] Capturar tabla/tipos con registros sintéticos, arquitectura y prompt. Crear **3 páginas** `submissions/m03/PreEntrega_Modulo3_SaraAdan.pdf`: canvas, prompt de resumen, esquema/metadata. Exportar snapshot acumulativo y commit `feat: add isolated Airtable memory and summaries`.

### T4 — Entrada Gmail y CRM seguros (M4, parte 1)

**Files:** workflows/channels/gmail_inbox.json, workflows/workers/crm_contact.json; modificar manager; tests/fixtures/module4.json, tests/test_module4.py; config/environment.example.json; docs/contracts.md.

**Interfaces:** Gmail Trigger → IF → Set `{From,Subject,BodyText,message_id,thread_id}` → RequestV1. CRM consume `{request_id,email,display_name,mode}`, devuelve `{status,contact_id,action:"found"|"created"|"updated"|"skipped"}` sin contacto completo.

- [ ] Añadir tests `test_auto_reply_stops_before_agent`, `test_invalid_from_stops_before_crm`, `test_lookup_precedes_create`, `test_replay_no_second_contact`, `test_crm_409_rereads_once`, `test_payload_drops_html_binary`. Correr pruebas con fixtures del proveedor, no correo privado.
- [ ] Gmail Trigger limitado a etiqueta de prueba `AURORA_TEST` durante implementación. IF inmediato: bloquear Auto-Submitted distinto de no, X-Autoreply/X-Autorespond, precedencia bulk/list/junk, remitentes no-reply/noreply/mailer-daemon y asuntos Auto-reply/Out of office/Undeliverable (sin distinguir mayúsculas). Los casos bloqueados terminan sin LLM/CRM/draft.
- [ ] Set limpia HTML a texto, limita body a 4.000 caracteres, valida un remitente de email; no mandar headers/cuerpos/adjuntos enteros a workers. Remitente inválido o faltante → revisión, no email vacío al CRM.
- [ ] Lookup HubSpot por email normalizado. Existe → actualizar solo nombre explícito/sintético autorizado, nunca sobrescribir valores con vacíos. No existe → Create. Conflicto 409 → un lookup de reconciliación; fallo/429/timeout → error sin bucle ni alta repetida.
- [ ] Crear ledger de recibos definido arriba; replay finalizado retorna artefacto existente. Si una creación tiene resultado incierto, reconciliar por email/request antes de otra escritura; no confundir reintento de lectura con autorización de envío.
- [ ] Demostrar por ejecución manual cada rama con contactos `example.com`, mensajes sintéticos y triggers inactivos. Limpiar fixtures solo mediante acción reversible/autorizada. Guardar resultados y commit `feat: guard inbound Gmail and CRM contact writes`.

### T5 — Borrador, equipo y entrega M4 (parte 2)

**Files:** modificar manager y gmail_inbox; crear `workflows/channels/slack_review.json`; tests/test_module4.py; evidence/module4/*; submissions/m04/README.md; README.md; docs/environment-substitutions.md.

**Interfaces:** candidate validado + remitente/thread original → Gmail Create Draft; Slack consume solo `{request_id,domain,status,reason,record_reference}`. Ningún worker elige destinatario/channel.

- [ ] Añadir `test_no_gmail_send_in_evolved_bundle`, `test_draft_once_per_message`, `test_slack_payload_allowlist` y `test_draft_failure_does_not_claim_success`; esperar fallos antes de modificar salida.
- [ ] Sustituir en descendiente M4 las dos salidas Gmail heredadas por draft-only y observabilidad mínima. No dejar un Send heredado alcanzable por error. Mantener el baseline M1 intacto y documentar esta evolución.
- [ ] Crear draft en el hilo entrante al remitente validado. Guardar draft_id en recibo y devolver `borrador_creado`, nunca “correo enviado”. No Auto-send después de aprobar/reintentar. Fallo de draft → revisión, sin éxito fabricado.
- [ ] Slack OAuth existente, canal `all-sara-practicas`. Set excluye body, email, audio, contacto completo y contexto privado; limitar reason a 200 caracteres. Preparar alerta y probar shaping sin envío; pedir autorización para una alerta sintética solo cuando se necesite evidencia de envío. Readiness de canal no se presenta como envío probado.
- [ ] Capturar estado conectado de CRM/Gmail/Slack sin secretos y revisar permisos existentes; no ampliar scopes por comodidad. Probar todos los casos M4, incluido fallo de CRM y fallo de draft; exportar acumulativo `submissions/m04/checkpoint4_sara_adan.json` más workers dependientes en carpeta `workers/`.
- [ ] README M4 incluye captura credenciales, importación workers primero y rebind IDs, cuatro nodos rubricados claramente localizables, resultados y límites. JSON del manager debe importar sin nodos desconocidos; no prometer ejecución sin credenciales/rebind. Commit `feat: add draft-only delivery and scoped team reporting`.

### T6 — Retriever documental con score y frontera de dominio (M5, parte 1)

**Files:** workflows/workers/outer_agent_retrieval.json; modificar manager/response_writer; prompts/outer_agent_rag.txt; tests/fixtures/module5.json, tests/test_module5.py; docs/knowledge-governance.md; config/environment.example.json.

**Interfaces:** RequestV1(domain=outer_agent) → Evidence[] de PDF + WorkerResultV1. Nunca invocar Sheets para datos Outer Agent. No reemplazar la fuente Aurora por el PDF.

- [ ] Tests iniciales: `test_aurora_never_uses_outer_agent_facts`, `test_outer_agent_never_uses_aurora_prices`, `test_empty_retrieval_returns_no_se`, `test_score_filter_is_real`, `test_citation_only_uses_returned_metadata`, `test_chunk_injection_ignored`. No usar las cinco preguntas reservadas para ajustar prompts o umbrales.
- [ ] Reusar índice aprobado y comprobar checksum/version del PDF. No reindexar por rutina ni subir README, evidencia, preguntas o expectativas. Registrar fecha/10 páginas y que headings/tablas se conservaron; corregir notas históricas de despliegue en documentación local, sin alterar hechos de la fuente.
- [ ] Resolver incompatibilidad observable: el nodo probado no expone Minimum Score ni metadata. Usar un tool de sub-workflow denominado `Consultar_documentacion_Outer_Agent` conectado al puerto ai_tool; dentro, HTTP Request autenticado con **credencial LlamaParse existente** al endpoint oficial `POST /api/v1/retrieval/retrieve`, project_id como query, JSON `index_id`, `query`, `top_k:3`, `score_threshold:0.5`. Verificar primero en respuesta real la escala/sentido de score y campos de fuente. No poner API key en URL/código. Si la credencial no admite HTTP, detener esta rama y documentar la necesidad de adaptación soportada; no extraer el secreto.
- [ ] Configurar Top-K 3 y umbral inicial 0,5 como **decisión de partida**, no óptimo demostrado. Calibrar con tres consultas de desarrollo distintas de las ciegas: servicio conocido, tabla de precios, tema ausente. Comparar scores reales y ajustar una vez al menor umbral que excluya el caso ausente conservando evidencia conocida; guardar tabla y valor final antes de evaluación. No trasladar umbrales de otro proveedor ni inventar score si falta.
- [ ] El adaptador normaliza texto, source_id/versión, sección y páginas reales. Ausencia de metadatos conserva null; si no permite fuente comprobable, no cerrar M5. Prompts: responder solo con evidencia, citar documento/sección y página si existe; dato ausente → “No sé. No está documentado en la fuente disponible.” No afirmar propiedad institucional ratificada.
- [ ] Documentar que esta es una adaptación funcional del **Vector Store Retriever Tool** rubricado, no ese nodo nativo. Capturar conexión lateral y controles verdaderos. Si el docente exige literalmente el nodo nombrado, dejar aceptación académica pendiente; jamás renombrar un HTTP node para simular equivalencia. No migrar a otra base/vector DB sin autorización.
- [ ] Pruebas reales: timeout, 401/429 simulado, score bajo, metadatos ausentes, pregunta mixta, moneda no especificada y texto malicioso. Ejecutar tests/bundle, exportar y commit `feat: add source-isolated Outer Agent retrieval`.

### T7 — Evaluación ciega y entrega documental M5

**Files:** evidence/module5/results.json, capture-index.md; submissions/m05/report.md; docs/knowledge-governance.md; scripts/report_metrics.py.

**Interfaces:** cinco entradas del archivo privado `outer-agent-source/pruebas_reservadas_NO_INDEXAR.json`; el agente solo recibe query, nunca expected_answer. Resultados `{case_id,query,retrieved_evidence,answer,correct:boolean,error_category,latency_ms,cost}`; `cost:null` si no se puede medir, nunca 0 por ausencia.

- [ ] Congelar export/hash, PDF version, Top-K, umbral y prompts antes de abrir expectativas. Solo el evaluador lee expectativas; no copiarlas al tool, memoria, índice ni prompt.
- [ ] Ejecutar exactamente las cinco preguntas ciegas con sesión nueva, sin efectos externos; incluir la pregunta sin respuesta. Guardar fragmento recuperado, respuesta y veredicto humano basado en fuente. Reportar todas las fallas; si se corrige luego, mantener ronda original y etiquetar el retest como no ciego.
- [ ] Implementar `summarize_runs(rows:list[dict])->dict` y test con 4 correctas/5 → 80%, evitando división por cero y costos desconocidos. No atribuir la precisión del juez al modelo evaluado.
- [ ] Gobernanza: responsable propuesto Sara para actualización documental, ratificación comercial por propietario; revisar cada 30 días y ante cambio público, versionar PDF, mantener historial y retirar versión reemplazada solo tras prueba y aprobación de eliminación si procede. Sync manual, no schedule creado por este plan.
- [ ] Crear `submissions/m05/PreEntrega_Modulo5_SaraAdan.pdf` con cinco piezas en orden: Data Source/tabla+limpieza; retriever con Top-K/score y 2–3 líneas de justificación; prompt con cita/No sé; cinco pruebas+precisión+análisis; gobernanza. No confundir el PDF fuente de 10 páginas con este informe.
- [ ] Renderizar/revisar todas las páginas y legibilidad de capturas; export acumulativo M5 y commit `docs: record blind RAG evaluation and governance`.

### T8 — Voz integrada y privacidad (M6)

**Files:** workflows/channels/telegram_voice.json, telegram_delivery.json; modificar manager; prompts/voice.txt; tests/fixtures/module6.json, tests/test_module6.py; evidence/module6/*; docs/deployment-checklist.md; submissions/m06/report.md.

**Interfaces:** entrada Telegram validada → Get File (download) binary.data → Whisper → RequestV1 texto. Salida validada ≤200 caracteres → ElevenLabs binary.data → Send Audio al chat de entrada permitido. Nunca pasar binary a un sub-workflow de texto.

- [ ] Tests: `test_missing_or_corrupt_audio_safe_exit`, `test_whisper_data_es`, `test_empty_transcript_stops_before_agent`, `test_voice_text_200_unicode_chars`, `test_no_audio_in_persistence`, `test_duplicate_update_no_resend`, `test_unauthorized_chat_no_processing`. Ejecutar fallos con fixtures sin registrar voz real.
- [ ] **Antes de escuchar/publicar**, inventariar workflows que usan Telegram account y comprobar webhook vigente mediante superficie soportada de getWebhookInfo o revisión asistida del propietario. No usar Listen for test event como “consulta”: puede registrar/reemplazar hook. No publicar mientras ownership sea desconocido. Si hay hook ajeno, documentar propietario y conseguir autorización de transferencia; no borrar hooks ni crear otro bot como atajo. Registrar URL/destino privadamente y rollback, nunca token.
- [ ] Configurar Telegram Trigger de mensajes de voz, allowlist de chat académico en manifest privado y dedupe update_id. El paso Get File es obligatorio para transformar file_id en binario; Whisper recibe `data`, idioma `es`, modelo whisper-1. Límite local de demo 30 s/5 MB antes de descarga/procesamiento; tamaño/duración desconocidos → revisión. Son límites del plan, no límites oficiales del proveedor.
- [ ] Nodo IF/Switch inmediatamente tras Whisper (error output conectado): transcripción vacía, error o audio corrupto → salida segura de texto preparada, sin agente/TTS. No reintentar audio inválido. Falla TTS → fallback de texto únicamente autorizado, sin afirmar audio enviado.
- [ ] Voice prompt y guard final: español, máximo 200 caracteres Unicode, sin URL/markdown/viñetas. Si excede, una redacción compacta con evidencia y máximo 120 tokens; volver a validar; si aún falla, frase breve de revisión, no cortar una cifra o cita a mitad. Outer Agent puede citar sección corta; metadatos completos quedan en evidencia textual controlada.
- [ ] ElevenLabs: voz existente Isabela, `eleven_multilingual_v2`, stability 0,5 y similarity 0,75 si esos controles existen en nodo/API; capturar valores efectivos, no asumir. La consigna dice v1, retirado el 09/07/2026: declarar sustitución por v2 con fuente oficial. No gastar en clones/modelos nuevos. Usar Send Audio porque el MP3 verificado es compatible; no fingir conversión a OGG/Send Voice.
- [ ] Guardar explícitamente **Do not save** para failed/successful production y manual executions, progress off en todo workflow que toque audio. No pinData, binary en Code outputs, adjuntos Slack, dump de errores, datos en memoria o export con audio. Terminar el workflow de ingesta tras pasar texto al manager; TTS se genera solo al entregar. El supervisor/Wait posterior vive en otra ejecución solo de texto, porque Wait persiste datos al pausar.
- [ ] Cuando ownership y autorización de prueba estén resueltos, ejecutar una voz sintética en español end-to-end y los fallos controlados. Confirmar entrada/salida, texto ≤200, reproducción, y ausencia de historial binario después de finalizar. No usar grabación de cliente; no retener archivos de usuario como evidencia. Capturar solo configuración/contadores y texto sintético.
- [ ] PDF único `submissions/m06/Checkpoint_Modulo6_SaraAdan.pdf` (nombre descriptivo del plan; screenshot no fija nombre obligatorio): canvas, Whisper data/es, agente/prompt exacto, ElevenLabs, contingencia, settings privacidad y frase sobre descarte. Export acumulativo y commit `feat: add privacy-bounded Spanish voice channel`.

### T9 — Juez, corrección acotada y pausa humana (M8, parte 1)

**Files:** workflows/workers/judge.json, workflows/human_review.json; modificar manager y telegram_delivery; prompts/judge.txt; schemas/judge.schema.json, human-review.schema.json; tests/fixtures/module8.json, tests/test_module8.py; evidence/module8/*.

**Interfaces:** query+context+evidence+candidate → JudgeOutput exacto. Manager controla correction_attempt y delivery; juez no llama herramientas ni envía nada. HumanReview solo puede resolver la petición asociada.

- [ ] Tests: `test_judge_exact_schema`, `test_three_switch_routes`, `test_third_correction_escalates`, `test_malformed_judge_escalates`, `test_score_verdict_conflict_escalates`, `test_wait_never_contains_audio`, `test_review_resume_authenticated_once`, `test_gmail_approved_still_draft`. Probar primero con outputs inyectados sin costo de LLM.
- [ ] Juez con Structured Output Parser, GPT-4o, temperatura 0, máximo 150 tokens, retries 0. Rúbrica: 5 totalmente respaldada y adecuada; 4 correcta con omisión no crítica; 3 incompleta/ambigua corregible; 2 afirmación sustancial no respaldada corregible; 1 contradicción grave, mezcla de dominios o falta crítica de contexto → revisión. Puntuación no mide si es agradable.
- [ ] Switch `estado_veredicto`: APROBADO solo si score ≥4 y validadores de canal pasan; CORREGIR solo scores 2–3 y attempt <2; ESCALAR para score1, conflicto, JSON inválido, error, o límite agotado. El contador lo incrementa el manager, no el LLM. Máximo **3 candidatos y 3 evaluaciones** (original + 2 correcciones). No reiniciar contador en sub-workflows.
- [ ] Corrección devuelve al Writer los mismos hechos, query y crítica determinista; no repetir CRM/draft, no releer corpus para perseguir un veredicto. Al agotar límite, ESCALAR aunque el LLM siga pidiendo CORREGIR. Error de modelo → ESCALAR sin retry de proveedor.
- [ ] ESCALAR: payload mínimo solo texto → workflow human_review → Wait On Webhook Call con Header Auth, expiración 24 h, notificación Slack mínima a persona autorizada. Credencial de aprobación/resume requiere configuración segura en ejecución; si aún no existe, preparar interfaz y solicitar handoff solo para esa credencial. No distribuir enlace autenticado en repo/capturas. Demo puede reanudarse manualmente autenticada sin envío Slack si no está autorizado.
- [ ] Validar approve/edit/reject, request_id, no replay, expiración; approve/edit vuelve al único punto de entrega. No confiar en un webhook que diga “approved” sin autenticación. Telegram TTS ocurre después del Wait en ejecución nueva sin audio retenido; Gmail solo crea draft. Prueba de supervisor puede usar fixtures de texto sin activar Telegram.
- [ ] Capturar sub-workflow juez/parser, tres ramas, contador y ejecución pausada/reanudada; transcribir prompt/schema literal en fuente del PDF. Export y commit `feat: add bounded judge and authenticated human review`.

### T10 — A/B de diez corridas, dashboard y paquete final (M8, parte 2)

**Files:** scripts/report_metrics.py; tests/test_module8.py; evidence/module8/ab-runs.json; submissions/m08/report.md; docs/requirements-traceability.md; scripts/sanitize_exports.py, verify_bundle_parity.py; README.md.

**Interfaces:** RunMetric `{architecture:"A"|"B",case_id,run_id,correct:boolean,judge_score,verdict,corrections,latency_ms,input_tokens,output_tokens,provider_cost|null,error_category}` → resumen comparativo. Costos en una moneda/tarifa fechada, sin inventar unidades.

- [ ] Congelar cinco casos sintéticos nuevos, separados de las ciegas M5: dato Aurora, memoria previa, conocimiento Outer Agent, pregunta sin soporte, solicitud ambigua/prompt injection. Igual query/context/evidence para ambas arquitecturas. A = pipeline M6 + mismo juez sin autocorrección (CORREGIR escala); B = mismo pipeline con hasta 2 correcciones. Misma versión/modelo/temperatura y presupuesto; única variable estructural es corrección acotada. No quitar guardrails ni enviar candidatos malos en A.
- [ ] `mode=dry_run` en ambas: CRM/draft/Slack/Telegram no mutan; memoria precargada sintética en sesiones aisladas. Ejecutar **5 A + 5 B**, una vez cada caso, sin descartar fallos ni elegir mejores intentos. Registrar costos de todas las llamadas incluidas correcciones; no incluir preparación en costo por corrida, pero declararla aparte.
- [ ] Evaluador humano puntúa exactitud contra fuente/contexto sin usar el score del juez como ground truth. Test de métricas: 4/5=80%; media de 5 scores correcta; costo medio suma/5; proyección a 1.000 = costo medio×1.000; si falta costo de una llamada, total marcado parcial/no disponible, no cero.
- [ ] Dashboard estático/tablas (no app nueva): precisión y score medio por arquitectura, costo, latencia, distribución de fallas, correcciones, proyección a 1.000 y recomendación con límites n=5. Separar cargos variables de suscripciones y consumo de créditos de dinero. Incluir estimación de audio aparte si pruebas A/B solo texto; no presentarla como costo end-to-end medido de voz.
- [ ] Crear `submissions/m08/Checkpoint_Modulo8_Adan_Sara.pdf` con tres bloques: supervisor+rúbrica/JSON (60%), matriz diez corridas (20%), dashboard/proyección/recomendación (20%). No añadir UI compleja, auditoría externa o botones Slack opcionales para inflar alcance.
- [ ] Descargar export fresco **después** de cada último cambio probado. Sanitizar y comparar recursivamente con allowlist por JSON path; no ignorar prompts/settings/connections ni renombrar nodos arbitrariamente. Rebind de IDs de worker debe estar documentado. Export privado nunca se commitea.
- [ ] Correr `python3 -m unittest discover -s tests -v`, `python3 scripts/verify_workflow_bundle.py workflows`, `python3 scripts/verify_bundle_parity.py --private-dir /ruta/privada --public-dir workflows --manifest /ruta/privada/substitutions.json`; exigir PASS explícito. Comprobaciones estáticas no sustituyen ejecución hospedada; tabla evidencia distingue ambas.
- [ ] Revisar/renderizar todos los PDFs, abrir cada página y verificar textos/capturas legibles, sin datos personales ni secretos. Capturas son reales; no dibujar nodos o resultados para simular evidencia. Actualizar README con links, import order, versiones, cambios y límites.
- [ ] Commit `docs: package measured Aurora module checkpoints`; publicar/push o activar solo cuando el alcance de ejecución lo autorice. No subir a plataforma académica ni enviar entregas sin solicitud. Final: inventario de artefactos y estado real por módulo.

## Export alojado, privacidad y paridad

M1 mantiene su comparación actual. Para bundle evolucionado, `sanitize_exports(private_bundle, manifest)` realiza únicamente: eliminar `credentials`; reemplazar IDs de recursos (sheet/base/table/index/channel/chat/workflow), direcciones y URLs de instancia por símbolos `REPLACE_*` del manifest; eliminar metadata superior de instancia (`id`, `versionId`, `meta`) y `pinData` siempre vacío. Para IDs de nodos y conexiones conservar identidad; si la importación los cambia, actualizar manifest explícito, no ignorarlos globalmente. Tags/nodeGroups solo pueden omitirse si se documenta que no afectan lógica. Conservar settings, prompt, resource, operation, retry, wait y filtros.

El manifest contiene rutas JSON exactas y antes/después; permanece privado. Publicar `docs/environment-substitutions.md` con símbolos y pasos de configuración, sin valores personales. Un placeholder no funcional es sustitución de entorno documentada, no permiso para omitir lógica. Importar workers primero, anotar IDs asignados, enlazarlos al manager y validar un ciclo dry-run antes de canal activo. Public export debe coincidir exactamente con la transformación permitida del export probado; si se modifica tras la prueba, repetir únicamente las pruebas afectadas y exportar de nuevo.

`.gitignore` futura debe excluir `work/`, `*-private.json`, `.env*` salvo example, audio, binaries, raw executions y screenshots sin redactar. Evidencia pública usa nombres sintéticos y chat/email/IDs personales redactados. El bot público puede nombrarse; no publicar chat ID de Sara. El reporte readiness con IDs operativos permanece fuera del repo.

## Costos y límites operativos propuestos

No hacer más pruebas de conexión ya aprobadas. Registrar saldos al iniciar cada milestone, sin comprar: Gateway mostraba $1,98; OpenAI audio tenía financiación existente con auto-reload off; ElevenLabs key tiene cap 1.000 créditos; LlamaCloud está pagado y no requiere nueva compra. Son observaciones históricas, no saldo garantizado.

Durante ejecución, `config/cost-policy.json` fija por milestone máximo estimado equivalente a **$0,25 de Gateway** y como máximo **50 llamadas de texto de pago**, lo primero que se alcance; superar requiere revisión antes de más llamadas. No es cargo autorizado adicional ni presupuesto suficiente garantizado. Modelo router/juez 150 tokens, respuesta 450, resumen 300, temperatura 0–0,1, retries proveedor 0. Conservar 5 iteraciones del Tools Agent; no confundir maxTokens por llamada con costo total. Medir prompt+tool+completion.

M5: sin reparse si corpus idéntico; 3 consultas de calibración + 5 ciegas. M6: máximo 3 muestras sintéticas cortas y 200 caracteres por TTS; fallos se inyectan localmente cuando sea posible. M8: exactamente 10 corridas oficiales; pruebas de ramas por fixtures, no docenas de llamadas de juez. Si las tarifas actuales no están disponibles, reportar tokens/créditos y proyección condicionada, no dinero inventado. No cachear la respuesta esperada de un test para aparentar precisión.

## Entregables y cierre por milestone

| Hito | Artefacto obligatorio de la consigna | Apoyo / evidencia |
|---|---|---|
| M1 | `checkpoint1_sara_adan.json` en GitHub | Histórico actual + VALIDACION_MODULO1, sin reenvíos. |
| M2 | `preentrega_modulo2_adan_sara.pdf` | Manager, dos workers, contratos/wait, éxito/error; exports opcionales conservados. |
| M3 | `PreEntrega_Modulo3_SaraAdan.pdf` | Tres páginas: canvas, prompt, esquema/tipos. |
| M4 | `checkpoint4_sara_adan.json` + README/captura credenciales en GitHub | Bundle de workers, instrucciones de rebind, pruebas de los cuatro controles. |
| M5 | `PreEntrega_Modulo5_SaraAdan.pdf` | Cinco piezas; fuente PDF separada de diez páginas; cinco ciegas. |
| M6 | Un PDF con canvas/config/settings/prompt | `Checkpoint_Modulo6_SaraAdan.pdf`, privacidad y modelo v2 declarado. |
| M8 | `Checkpoint_Modulo8_Adan_Sara.pdf` | Tres bloques, exactamente 5+5, errores y costo/proyección. |

No se considera cerrado un hito con solo nodos verdes: se verifica contenido, fallos, archivo exportado, paridad, capturas y formato de entrega. Los PDF se generan durante ejecución usando la skill PDF, con render y revisión visual; no hay PDFs finales de módulos todavía.

## Decisiones pendientes, sin nuevas preguntas para redactar el plan

1. **Aprobación recibida posteriormente:** ejecutar todos los entregables suministrados sin nueva aprobación del plan; mismo chat y método.
2. **Aceptación académica:** M5 adaptador de retriever y fuente pública sintetizada; M6 v2 por retiro de v1. Implementar y documentar equivalencia honestamente; si se exige literalidad, conseguir criterio docente antes de declarar cumplimiento total.
3. **Activación Telegram:** ownership y autorización de registrar/transferir hook y de pruebas de voz. La identidad del credential ya está resuelta y no se vuelve a pedir token/username.
4. **Notificaciones/revisión:** autorización concreta de envíos Slack/Telegram de pruebas y configuración de credencial segura de Wait si no existe. No usar el permiso del único mensaje de readiness para cubrir mensajes futuros.
5. **Fuente Outer Agent:** moneda/impuestos/SLA/políticas no documentadas continúan desconocidas; ratificación institucional pendiente no bloquea pruebas técnicas de RAG con esa limitación declarada.
6. **Módulos no suministrados:** requieren sus enunciados cuando el usuario quiera incorporarlos. No bloquean el plan de los módulos disponibles.

## Self-review de cobertura (25/11/2026)

Releídas las ocho imágenes originales y el baseline real. Cada requisito obligatorio tiene tarea en la matriz; M4 usa ambas capturas y no pierde el README/captura de credenciales. Se corrigieron expresamente los riesgos siguientes en este plan: mantener sends M1 por herencia (T1/T5); confundir Gateway con key de audio (límites); llamar al retriever actual “Minimum Score configurado” (T6); tratar el PDF fuente como informe M5 (T7); olvidar Get File/binary.data (T8); introducir audio en Wait pese a settings de no guardado (T8/T9); añadir crítica fuera del schema exacto del juez (contrato/T9); medir precisión con el propio juez o fabricar costo (T10).

Tipos y nombres coherentes: RequestV1/WorkerResultV1 en workers; Summary con tres claves; JudgeOutput exactamente dos; correction_attempt 0→1→2 y luego ESCALAR; domain en Session_ID. Las cinco clases de Review Focus tienen pruebas asignadas. No se afirma cobertura M7/M9–M11, webhook libre, políticas comerciales ratificadas ni compatibilidad literal que aún no existe. No se ejecutó ninguna prueba nueva ni se modificó workflow externo para escribir este plan.

## Referencias técnicas verificadas

- [LlamaCloud Index v2 retrieval](https://developers.llamaindex.ai/llamaparse/cloud-index-v2/retrieval/): endpoint de recuperación con top_k y score_threshold; validar valores/metadatos reales en T6.
- [API Retrieve](https://developers.llamaindex.ai/reference/typescript/resources/retrieval/methods/retrieve/): contrato oficial para adaptador autenticado.
- [ElevenLabs, 8 junio 2026](https://elevenlabs.io/docs/es/changelog/2026/6/8): retiro de modelos v1 el 9 de julio de 2026; sustitución v2 documentada.
- [n8n Wait](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.wait/): pausa persiste ejecución, resume webhook y autenticación; base de la separación de audio y aprobación.
