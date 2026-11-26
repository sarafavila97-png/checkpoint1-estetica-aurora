# Requirements traceability

Review snapshot: 26 November 2026. Implementation commit 51881e18ba4c3053648c930f97cbd597fef3ff7d was pushed and independently matched by git ls-remote on codex/aurora-modules. This is a navigation and gap register, not a blanket compliance claim. Runtime observations are labeled transcriptions where applicable. Later edits must update this register against actual exports, runs and artifacts.

Status: **evidence available** means evidence exists to review; **partial** means work/evidence remains; **pending** means implementation has not been demonstrated. No module is accepted solely because a local test passes.

## Module 1

Baseline checkpoint previously tested and published; preserve baseline and recheck final cross-module regression.

| Gate | Requirement | Current status |
| --- | --- | --- |
| M1.01 | Chat Trigger or Webhook feeds native Tools Agent with connected native chat model. | evidence available |
| M1.02 | Maximum iterations is explicitly between 5 and 10. | evidence available |
| M1.03 | Modular system prompt defines role, scope, objective, rules, escalation and prohibited actions. | evidence available |
| M1.04 | At least one working native productivity tool is connected laterally and has a detailed semantic activation description. | evidence available |
| M1.05 | Final Gmail or Slack observability notification records execution/tool outcome. | evidence available |
| M1.06 | Actual manual execution proves tool use, response and observability without expression errors. | evidence available |
| M1.07 | Named checkpoint1 JSON export is published in GitHub and matches tested configuration except documented private substitutions. | evidence available |

## Module 2

[Frozen workflows](../submissions/m02/workflows/), [runtime observations](../submissions/m02/evidence/). [Seven-page PDF](../submissions/m02/preentrega_modulo2_adan_sara.pdf) includes authentic internal-worker-error evidence. Visual and factual reviews passed; final local regression and hosted snapshot parity passed. Published on branch codex/aurora-modules.

| Gate | Requirement | Current status |
| --- | --- | --- |
| M2.01 | Manager extends Module 1 and routes a closed intent taxonomy with fallback. | evidence available |
| M2.02 | At least two independent atomic worker workflows start with Execute Workflow Trigger. | evidence available |
| M2.03 | Set/Edit Fields before delegation transfers only minimal JSON, no binary or heavy metadata. | evidence available |
| M2.04 | Each Execute Workflow waits for child completion and integrates its structured result. | evidence available |
| M2.05 | Workers return predictable success and error objects; timeout or API failure does not strand manager. | evidence available |
| M2.06 | Actual end-to-end success and worker failure runs are captured. | evidence available |
| M2.07 | Single PDF includes full manager, both workers, delegation settings, success execution, failure path, contracts and routing explanation. | evidence available |

## Module 3

[Frozen workflows](../submissions/m03/workflows/), [runtime observations](../submissions/m03/evidence/), [three-page PDF](../submissions/m03/PreEntrega_Modulo3_SaraAdan.pdf). PDF visually and factually reviewed; final local regression and hosted snapshot parity passed. Published on branch codex/aurora-modules.

| Gate | Requirement | Current status |
| --- | --- | --- |
| M3.01 | Module 2 architecture retained; Airtable lookup filters exact Session_ID before agent runs. | evidence available |
| M3.02 | IF separates new and returning users; no match is handled without blank-context errors. | evidence available |
| M3.03 | Stored memory is delimited by [INICIO DE CONTEXTO COMPARTIDO] and [FIN DEL CONTEXTO COMPARTIDO]. | evidence available |
| M3.04 | Summarization activates only after more than five messages. | evidence available |
| M3.05 | Summary schema is asunto_principal:string, puntos_clave:array, accion_requerida:string. | evidence available |
| M3.06 | Updates are idempotent; durable memory excludes entire conversations, logs and HTML. | evidence available |
| M3.07 | Two sessions demonstrably cannot read each other's memory. | evidence available |
| M3.08 | PDF shows complete canvas, exact summarization prompt and database columns/types/metadata. | evidence available |

## Module 4

[CRM sequence](../evidence/module4/crm-sequence-observation.json) records one contact ID across create/find/update. [Frozen submission](../submissions/m04/) includes inbox guards, receipt replay handling, CRM reconciliation, draft creation and Slack tests. Export parity and credential screenshots reviewed. Published on branch codex/aurora-modules; receipt reservations do not provide distributed atomic deduplication.

| Gate | Requirement | Current status |
| --- | --- | --- |
| M4.01 | Module 3 retained and three native OAuth2 connectors cover CRM, incoming email and team messaging. | evidence available |
| M4.02 | Credential connection status and scopes are evidenced, with least-privilege configuration or honest platform limitations. | evidence available |
| M4.03 | IF immediately after email trigger blocks Auto-reply, Out of office, Undeliverable and no-reply messages. | evidence available |
| M4.04 | Set/filter strips payload to validated required fields and rejects empty email before API operations. | evidence available |
| M4.05 | CRM lookup precedes create; existing contact updates and repeated input does not duplicate contacts. | evidence available |
| M4.06 | Email response uses Create Draft exclusively, preserving human approval before sending. | evidence available |
| M4.07 | Team payload excludes heavy metadata and binary content. | evidence available |
| M4.08 | Actual regression tests verify each connector and anti-loop, malformed-input and duplicate-contact guards. | evidence available |
| M4.09 | Public GitHub contains checkpoint4 export and README with three active credential connections shown; JSON imports without errors. | evidence available on codex/aurora-modules; no credentials included |

## Module 5

[Governance plan](knowledge-governance.md) and [retriever compatibility review](m5-retriever-compatibility-review.md) exist. [Nine-page report](../submissions/m05/PreEntrega_Modulo5_SaraAdan.pdf) is visually and factually reviewed. [Blind evaluation](../evidence/module5/blind-evaluation.json) records 2/5 correct (40%); this is a measured weak baseline, not a passing-quality claim. Three hosted workflow snapshots passed parity verification. Final channel adapters are integrated in M8; genuine Telegram entry and the literal native-node criterion remain unresolved.

| Gate | Requirement | Current status |
| --- | --- | --- |
| M5.01 | Module 4 extended with real organizational source of 10–30 pages including headings and a table. | partial |
| M5.02 | LlamaCloud parsing evidence visibly preserves heading hierarchy and table cells. | evidence available |
| M5.03 | Agent's lateral retrieval tool targets the correct index and has a meaningful name and business description. | partial |
| M5.04 | Top-K and Minimum Score configured and evidenced; 2–3 lines explain precision versus token-cost balance. | partial |
| M5.05 | Answers use retrieved sources, cite them and say No sé when information is absent. | evidence available |
| M5.06 | Exactly five blind synonym/informal questions produce recorded retrieval snippets, answers and verdicts, including an unknown answer case. | evidence available |
| M5.07 | Precision is calculated from actual results; failure analysis is honest. | evidence available |
| M5.08 | Governance names review cadence, responsible role and replacement/deletion rules. | evidence available |
| M5.09 | Single PDF presents parsing, retrieval settings, prompt, blind-test report and governance in specified order. | evidence available |

Additional literal check: original screenshot names **Vector Store Retrieve Tool** with visible Top-K and Minimum Score. A functional HTTP adapter is not proof of literal node equivalence. Resolve or explicitly preserve this discrepancy in the final acceptance record.

## Module 6

[Six hosted snapshots](../workflows/module6/) pass parity verification. The [15-page PDF](../submissions/m06/PreEntrega_Modulo6_SaraAdan.pdf) includes eleven authentic captures and exact native agent prompts. Synthetic transcription/synthesis ran; the original Sheets binding failure is preserved and the repaired text regression returned 180 MXN and 40 minutes. An isolated invalid-audio call now proves Whisper failure reaches the contingency without answer model, TTS or Telegram delivery. The current synthetic fixture and known local generated audio were removed and its workflow archived; historical versions/provider retention were not erased. Incoming Telegram voice still requires the user's signed-in session; component observations do not prove that full pipeline.

| Gate | Requirement | Current status |
| --- | --- | --- |
| M6.01 | Module 5 retained with an actual incoming Telegram or WhatsApp audio route. | partial |
| M6.02 | Whisper receives binary property data with language es and maps transcription into Tools Agent. | partial |
| M6.03 | Agent prompt enforces at most 200 characters without links, bullets or emoji. | partial |
| M6.04 | Native ElevenLabs output uses configured multilingual model and stability; retired-version substitution is explicitly documented. | partial |
| M6.05 | Generated binary is mapped to Send Voice or Send Audio on originating messaging channel. | partial |
| M6.06 | IF/Switch after transcription safely handles corrupt audio or empty transcription. | evidence available; isolated corrupt-audio runtime and local empty-text check |
| M6.07 | Successful and failed production executions use Do not save; no audio is persisted in external storage. | partial |
| M6.08 | Single PDF includes full canvas, Whisper/agent/TTS/contingency settings, retention settings, disposal explanation and exact agent prompt. | evidence available; runtime limits explicit |

## Module 8

[Six final snapshots](../workflows/module8/) pass hosted export parity. The [15-page PDF](../submissions/m08/Checkpoint_Modulo8_Adan_Sara.pdf) includes ten authentic captures, prompt/schema, all ten frozen A/B runs, independent 5/5 scoring in each arm and complete UI-transcribed usage of 42 model calls. Retail no-cache estimate is USD 0.14656; actual Gateway charge is unknown. A real isolated correction and a real escalation with Slack plus one-minute Wait were observed; production Wait remains 24 hours. Injected decisions separately verify malformed JSON and exhaustion. Gmail two-message regression and sequential replay passed; incoming Telegram remains unverified/inactive. Local suite: 101 passing tests. Final reviewer found no important actionable issue in a local/read-only review, not an independent runtime replay.

| Gate | Requirement | Current status |
| --- | --- | --- |
| M8.01 | Prior modules retained and supervisor implemented as sub-workflow. | partial |
| M8.02 | Structured output schema enforced and exact judge prompt reproduced in PDF. | evidence available |
| M8.03 | Switch has APROBADO, CORREGIR and ESCALAR branches; approval requires factual score at least 4. | evidence available |
| M8.04 | Correction passes judge feedback to agent and has bounded attempts ending in escalation. | evidence available |
| M8.05 | Escalation actually pauses with Wait/Wait for Webhook and notifies human channel. | evidence available |
| M8.06 | Malformed judge JSON fails safely rather than breaking routing. | evidence available |
| M8.07 | Exactly five runs of architecture A and five of B record actual precision and cost. | partial: precision and actual token usage observed; retail cost estimated, Gateway charge unknown |
| M8.08 | Simple dashboard shows mean precision, common error categories, projected cost for 1000 executions and evidence-based recommendation. | evidence available |
| M8.09 | One PDF contains supervisor/rubric, ten-run A/B matrix and dashboard/projection. | evidence available |

## Final acceptance procedure

1. Reopen all original screenshots; reconcile each row with the exact criterion and required filename/format.
2. Compare final hosted exports with public snapshots after only documented secret substitutions.
3. Inspect actual success and failure results, external effects and safe recovery for each implemented path.
4. Open every final PDF and inspect every rendered page; confirm required screenshots, prompts, schemas, metrics and source references.
5. Verify GitHub contains the intended final commit and files. Do not treat a local commit as publication.
6. Record every remaining mismatch explicitly. Do not mark the overall assignment complete while a required gate is pending, partial, indirect or missing.

## Auditoría acotada posterior a publicación

[Registro del 26 de noviembre](../evidence/remaining-gap-audit.json): conector instalado 6.7.2 Latest, sin Minimum Score ni salida Vector Store; búsqueda Llama sin resultados en el puerto vectorial nativo. Telegram continúa sin sesión en Chrome/Firefox. Gateway presenta USD 0.16 agregados del workflow M8, contaminados por desarrollo previo y redondeados; el costo real de las diez corridas sigue desconocido. No hubo reejecuciones, notificaciones ni cambios en los workflows finales.
