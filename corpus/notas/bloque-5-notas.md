# Notas de extracción — Bloque 5: Gestión de contexto y fiabilidad
Fecha: 2026-08-05 · Fuentes procesadas: 7/7 · Task statements: 6/6

## TS 5.1 — Manage conversation context to preserve critical information across long interactions

### Hechos y comportamiento
- **Context rot**: A medida que crece el número de tokens, la precisión y recall se degradan, fenómeno conocido como "context rot". [Fuente: Context windows — https://platform.claude.com/docs/en/build-with-claude/context-windows]
- **Progressive token accumulation**: Cada turno de conversación acumula dentro de la ventana de contexto; los turnos previos se preservan completamente hasta que se alcanza el límite. [Fuente: Context windows — https://platform.claude.com/docs/en/build-with-claude/context-windows]
- **Lost in the middle effect**: Los modelos procesan confiablemente información al principio y final de entradas largas, pero pueden omitir hallazgos de secciones intermedias. [Fuente: exam-guide-oficial-v1.0.txt, líneas 636-637]
- **Tool result accumulation**: Los resultados de herramientas se acumulan en contexto y consumen tokens de manera desproporcionada a su relevancia (ej: 40+ campos por búsqueda de orden cuando solo 5 son relevantes). [Fuente: exam-guide-oficial-v1.0.txt, línea 639]
- **Progressive summarization risks**: Condensar valores numéricos, porcentajes, fechas y expectativas indicadas por clientes en resúmenes vagos crea pérdidas de precisión. [Fuente: exam-guide-oficial-v1.0.txt, línea 631-632]
- **Context window capacity**: La ventana de contexto (hasta 1M tokens según modelo) contiene el historial de conversación + output nuevo generado por Claude. Cada respuesta reporta consumo en el campo `usage`. [Fuente: Context windows — https://platform.claude.com/docs/en/build-with-claude/context-windows]
- **Context awareness (automatic)**: Claude Sonnet 5, Sonnet 4.6, Sonnet 4.5 y Haiku 4.5 rastrean automáticamente su presupuesto de tokens restante mediante etiquetas inyectadas por la API (`<budget:token_budget>` y actualizaciones `<system_warning>`). [Fuente: Context windows — https://platform.claude.com/docs/en/build-with-claude/context-windows]

### Sintaxis y configuración
- **Token budget injection** (context awareness):
  ```xml
  <budget:token_budget>200000</budget:token_budget>
  ```
  [Fuente: Context windows — https://platform.claude.com/docs/en/build-with-claude/context-windows]

- **Remaining capacity update** (after each tool call):
  ```xml
  <system_warning>Token usage: 35000/200000; 165000 remaining</system_warning>
  ```
  [Fuente: Context windows — https://platform.claude.com/docs/en/build-with-claude/context-windows]

### Patrones
- **Persistent "case facts" block**: Extraer hechos transaccionales (amounts, dates, order numbers, statuses) en un bloque persistente incluido en cada prompt, fuera del historial summarizado. [Fuente: exam-guide-oficial-v1.0.txt, línea 643-644]
- **Structured issue data layer**: Extraer y persistir datos de issue estructurados (order IDs, amounts, statuses) en una capa de contexto separada para sesiones multi-issue. [Fuente: exam-guide-oficial-v1.0.txt, línea 645-646]
- **Trim verbose outputs**: Recortar outputs verbosos de herramientas a solo campos relevantes antes de que se acumulen en contexto (ej: mantener solo return-relevant fields de búsquedas de orden). [Fuente: exam-guide-oficial-v1.0.txt, línea 647-648]
- **Position-aware input ordering**: Colocar resúmenes de hallazgos clave al principio de inputs agregados; organizar resultados detallados con headers de sección explícitos para mitigar position effects. [Fuente: exam-guide-oficial-v1.0.txt, línea 649-650]
- **Subagent metadata requirements**: Requerir a subagentes incluir metadata (dates, source locations, methodological context) en structured outputs para soportar síntesis downstream acertada. [Fuente: exam-guide-oficial-v1.0.txt, línea 651-652]
- **Structured data from upstream agents**: Modificar agentes upstream para retornar structured data (key facts, citations, relevance scores) en lugar de verbose content y reasoning chains cuando downstream agents tienen limited context budgets. [Fuente: exam-guide-oficial-v1.0.txt, línea 653-655]
- **Scratchpad note-taking**: Agentes escriben notas persistentes fuera de la ventana de contexto, luego las recuperan después para rastrear progreso en tareas complejas. [Fuente: Effective context engineering for AI agents — https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents]
- **Just-in-time exploration**: Usar exploración bajo demanda para cargar datos dinámicamente en lugar de cargar todo upfront. [Fuente: Effective context engineering for AI agents — https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents]

### Anti-patrones (y por qué fallan)
- **Loading all files upfront**: Leer todos los archivos al inicio consume tokens innecesarios; mejor usar Grep para encontrar puntos de entrada, luego Read para seguir imports. [Fuente: exam-guide-oficial-v1.0.txt, línea 368-369]
- **Vague summarization**: Comprimir información en resúmenes vagos (ej: "el cliente tiene un problema de envío") pierde valores concretos (orden #, monto, fecha) esenciales para continuidad. [Fuente: exam-guide-oficial-v1.0.txt, línea 631-634]

---

## TS 5.2 — Design effective escalation and ambiguity resolution patterns

### Hechos y comportamiento
- **Appropriate escalation triggers**: Solicitud explícita del cliente de un humano, excepciones/gaps de policy (no solo casos complejos), e incapacidad de hacer progreso significativo. [Fuente: exam-guide-oficial-v1.0.txt, línea 659]
- **Immediate vs conditional escalation**: Distinguir entre escalar inmediatamente cuando un cliente exige explícitamente un humano vs ofrecer resolución cuando el issue es straightforward. [Fuente: exam-guide-oficial-v1.0.txt, línea 660-661]
- **Unreliable proxies**: Sentiment-based escalation y self-reported confidence scores son proxies unreliables para actual case complexity. [Fuente: exam-guide-oficial-v1.0.txt, línea 662-663]
- **Ambiguity resolution via clarification**: Cuando múltiples customer matches surgen, requerir identificadores adicionales en lugar de heuristic selection. [Fuente: exam-guide-oficial-v1.0.txt, línea 664-665]
- **Policy gap escalation**: Escalar cuando policy es ambigua o silent en la request específica del customer (ej: competitor price matching cuando policy solo aborda own-site adjustments). [Fuente: exam-guide-oficial-v1.0.txt, línea 676-677]
- **Honor explicit customer preference immediately**: No intentar investigación primero si el customer reitera su preferencia por escalation. [Fuente: exam-guide-oficial-v1.0.txt, línea 672-673]

### Sintaxis y configuración
- **Few-shot escalation examples** en system prompt:
  ```
  Escalate when:
  - Customer explicitly requests human agent
  - Policy does not address the specific request
  - You cannot make meaningful progress after X attempts
  
  Do NOT escalate when:
  - Issue is within your capabilities and straightforward
  - Customer is frustrated but not requesting human
  ```
  [Fuente: exam-guide-oficial-v1.0.txt, línea 667-668 — inferred from "Adding explicit escalation criteria with few-shot examples"]

### Patrones
- **Explicit escalation criteria in system prompt**: Agregar criterios explícitos con few-shot examples demostrando cuándo escalar vs resolver autónomamente. [Fuente: exam-guide-oficial-v1.0.txt, línea 668]
- **Acknowledge frustration while offering resolution**: Reconocer frustración del customer mientras se ofrece resolución cuando el issue está dentro de capacidades del agente; escalar solo si customer reitera su preferencia. [Fuente: exam-guide-oficial-v1.0.txt, línea 674-675]
- **Ask for additional identifiers on ambiguity**: Instruir al agente a pedir identificadores adicionales cuando tool results retornan múltiples matches, en lugar de seleccionar basado en heurísticas. [Fuente: exam-guide-oficial-v1.0.txt, línea 678-679]
- **Structured handoff summaries**: Compilar resúmenes de escalation estructurados (customer ID, root cause analysis, recommended actions) cuando escalando a human agents sin acceso a conversation transcript. [Fuente: exam-guide-oficial-v1.0.txt, línea 204-205]

### Anti-patrones (y por qué fallan)
- **Sentiment-based escalation**: Detectar frustración del customer via sentiment analysis y escalar automáticamente es unreliable porque sentiment ≠ complexity. Ejemplo: un customer muy frustrado pero con un problema simple no necesita escalation. [Fuente: exam-guide-oficial-v1.0.txt, línea 662-663]
- **Self-reported confidence as proxy**: Usar confidence scores autoreportados por el modelo es futil porque el modelo puede estar incorrectamente confident en casos difíciles (especialmente en sistemas agénticos donde minor changes cascade into large behavioral changes). [Fuente: exam-guide-oficial-v1.0.txt, línea 662-663; built-multi-agent-research-system — "minor changes cascade into large behavioral changes"]
- **Heuristic selection on ambiguity**: Cuando múltiples records coinciden (ej: múltiples customers con el mismo nombre), seleccionar basado en heurísticas (ej: fecha más reciente) puede llevar a misidentification; mejor pedir aclaración. [Fuente: exam-guide-oficial-v1.0.txt, línea 664-665]

---

## TS 5.3 — Implement error propagation strategies across multi-agent systems

### Hechos y comportamiento
- **Error context enabling recovery**: Structured error context (failure type, attempted query, partial results, alternative approaches) habilita intelligent coordinator recovery decisions. [Fuente: exam-guide-oficial-v1.0.txt, línea 682-683]
- **Access vs empty result distinction**: Distinguir entre access failures (timeouts necesitando retry decisions) y valid empty results (successful queries sin matches). [Fuente: exam-guide-oficial-v1.0.txt, línea 684-685]
- **Generic error statuses hide context**: Generic error statuses ("search unavailable") esconden contexto valioso del coordinator, previniendo informed decisions. [Fuente: exam-guide-oficial-v1.0.txt, línea 686]
- **Local recovery before propagation**: Subagentes implementan local recovery para transient failures y solo propagan errores que no pueden resolver, incluyendo qué se intentó y partial results. [Fuente: exam-guide-oficial-v1.0.txt, línea 694-695]
- **Coverage annotations for gaps**: Estructurar synthesis output con coverage annotations indicando cuáles hallazgos están bien-soportados vs cuáles topic areas tienen gaps debido a unavailable sources. [Fuente: exam-guide-oficial-v1.0.txt, línea 696-697]
- **Cascade failures in agentic systems**: Minor changes cascade into large behavioral changes en sistemas agénticos; errores en agentes de larga duración generan problemas en cascada difíciles de predecir. [Fuente: built-multi-agent-research-system]
- **Checkpoint-based recovery**: En lugar de reiniciar, agentes retoman desde donde fallaron usando checkpoints. [Fuente: built-multi-agent-research-system]

### Sintaxis y configuración
- **Structured error response** (MCP isError pattern):
  ```json
  {
    "isError": true,
    "errorCategory": "transient|validation|permission|business",
    "isRetryable": boolean,
    "message": "Human-readable description",
    "failureType": "timeout|invalid_input|access_denied|policy_violation",
    "attemptedQuery": "what was tried",
    "partialResults": {...},
    "alternativeApproaches": ["option1", "option2"]
  }
  ```
  [Fuente: exam-guide-oficial-v1.0.txt, línea 297-300]

- **Non-retryable error with explanation**:
  ```json
  {
    "isError": true,
    "retriable": false,
    "message": "Customer price match requests are not eligible under current policy"
  }
  ```
  [Fuente: exam-guide-oficial-v1.0.txt, línea 299-300]

### Patrones
- **Structured error context returning**: Retornar contexto de error estructurado al coordinator incluyendo failure type, qué fue intentado, partial results, y potential alternatives para habilitar informed recovery. [Fuente: exam-guide-oficial-v1.0.txt, línea 690-691]
- **Distinguish failure types**: En error reporting, distinguir entre access failures (needing retry) y valid empty results (successful queries con no matches). [Fuente: exam-guide-oficial-v1.0.txt, línea 692-693]
- **Annotated synthesis with gaps**: Cuando synthesis output tiene topic areas sin coverage, anotar explícitamente qué source types estuvieron unavailable o qué queries fallaron. [Fuente: exam-guide-oficial-v1.0.txt, línea 696-697]
- **Adaptive graceful handling**: Informar al agente sobre tool failures habilita que se adapte gracefully usando approaches alternativos. [Fuente: built-multi-agent-research-system]

### Anti-patterns (y por qué fallan)
- **Silently suppressing errors**: Retornar empty results marcados como successful cuando ocurre timeout esconde fallos, previniendo recovery y riesgando incomplete outputs. [Fuente: exam-guide-oficial-v1.0.txt, línea 1032-1033]
- **Terminating entire workflow on single failure**: Propagar timeout exception a top-level handler que termina el entire workflow es anti-patrón; mejor permitir partial results y recovery alternatives. [Fuente: exam-guide-oficial-v1.0.txt, línea 1033-1034]
- **Generic status hiding context**: Retornar solo "search unavailable" sin contexto sobre qué se intentó o cuáles partial results existen previene informed coordinator decisions. [Fuente: exam-guide-oficial-v1.0.txt, línea 686]

---

## TS 5.4 — Manage context effectively in large codebase exploration

### Hechos y comportamiento
- **Context degradation in extended sessions**: Los modelos comienzan dando respuestas inconsistentes y referenciando "typical patterns" en lugar de clases específicas descubiertas earlier. [Fuente: exam-guide-oficial-v1.0.txt, línea 700-701]
- **Scratchpad role for persistence**: Scratchpad files persisten key findings a través de context boundaries, contrarestando degradación. [Fuente: exam-guide-oficial-v1.0.txt, línea 702-703]
- **Subagent delegation for isolation**: Subagent delegation aísla verbose exploration output mientras el main agent coordina high-level understanding. [Fuente: exam-guide-oficial-v1.0.txt, línea 704]
- **Structured state persistence for recovery**: Cada agente exporta state a una located conocida; coordinator carga manifest en resume. [Fuente: exam-guide-oficial-v1.0.txt, línea 705-706]
- **Token budget awareness**: En extended sessions, monitorear remaining token budget (via context awareness tags) para determinar cuándo usar compaction o finalizar phase. [Fuente: Context windows — https://platform.claude.com/docs/en/build-with-claude/context-windows]

### Sintaxis y configuración
- **Compaction API request** (beta):
  ```python
  response = client.beta.messages.create(
      betas=["compact-2026-01-12"],
      model="claude-opus-5",
      max_tokens=4096,
      messages=messages,
      context_management={"edits": [{"type": "compact_20260112"}]}
  )
  ```
  [Fuente: Compaction — https://platform.claude.com/docs/en/build-with-claude/compaction]

- **Compaction parameters**:
  ```
  trigger: 150,000 tokens (minimum 50,000)
  pause_after_compaction: false (default)
  instructions: None (use default summarization)
  ```
  [Fuente: Compaction — https://platform.claude.com/docs/en/build-with-claude/compaction]

- **State manifest export** (crash recovery):
  ```json
  {
    "phase": "codebase_analysis",
    "key_findings": {
      "entry_points": ["src/main.ts", "src/index.ts"],
      "key_classes": ["UserService", "AuthHandler"],
      "dependencies_identified": {...}
    },
    "files_analyzed": ["src/auth.ts", "src/user.ts"],
    "questions_pending": ["find all test files", "trace refund flow"]
  }
  ```
  [Fuente: exam-guide-oficial-v1.0.txt, línea 709]

### Patrones
- **Spawn subagents for isolated exploration**: Generar subagentes para investigar preguntas específicas (ej: "find all test files", "trace refund flow dependencies") mientras el main agent preserva high-level coordination. [Fuente: exam-guide-oficial-v1.0.txt, línea 711-712]
- **Maintain scratchpad files**: Agentes mantienen scratchpad files grabando key findings, referenciándolos para preguntas subsecuentes para counteractuar context degradation. [Fuente: exam-guide-oficial-v1.0.txt, línea 713-714]
- **Summarize before next phase**: Resumir key findings de una exploration phase antes de spawning sub-agents para la siguiente phase, inyectando resúmenes en initial context. [Fuente: exam-guide-oficial-v1.0.txt, línea 715-716]
- **Structured agent state exports**: Diseñar crash recovery usando structured agent state exports (manifests) que el coordinator carga en resume e inyecta en agent prompts. [Fuente: exam-guide-oficial-v1.0.txt, línea 717-718]
- **Use /compact for extended sessions**: Durante extended exploration sessions cuando context se llena con verbose discovery output, usar `/compact` para reducir context usage. [Fuente: exam-guide-oficial-v1.0.txt, línea 719-720]
- **Incremental codebase understanding**: Construir entendimiento codebase incrementally: comenzar con Grep para encontrar entry points, luego usar Read para seguir imports y trazar flows, en lugar de leer todos upfront. [Fuente: exam-guide-oficial-v1.0.txt, línea 368-369]

### Anti-patrones (y por qué fallan)
- **Over-loading single agent**: Sin delegation, un solo agente procesando todo el codebase acumula contexto verbose y pierde coordinación de alto nivel. [Fuente: exam-guide-oficial-v1.0.txt, línea 704]
- **Not persisting findings across boundaries**: Sin scratchpads o state exports, cuando context se agota y comienza nueva session, key findings descubiertos se pierden y agent referencia "typical patterns" en lugar de hallazgos específicos. [Fuente: exam-guide-oficial-v1.0.txt, línea 700-702]

---

## TS 5.5 — Design human review workflows and confidence calibration

### Hechos y comportamiento
- **Aggregate accuracy masks poor performance**: Métricas de accuracy agregadas (ej: 97% overall) pueden enmascarar poor performance en document types o fields específicos. [Fuente: exam-guide-oficial-v1.0.txt, línea 724]
- **Stratified random sampling**: Para medir error rates en high-confidence extractions y detectar novel error patterns, usar stratified random sampling. [Fuente: exam-guide-oficial-v1.0.txt, línea 725-726]
- **Field-level confidence calibration**: Confidence scores a nivel de field calibrados usando labeled validation sets para routing review attention. [Fuente: exam-guide-oficial-v1.0.txt, línea 727-728]
- **Accuracy validation by segment**: Importancia de validar accuracy by document type y field segment antes de automating high-confidence extractions. [Fuente: exam-guide-oficial-v1.0.txt, línea 729-730]
- **pass@k vs pass^k metrics**: "pass@k" = probabilidad de obtener al menos una solución correcta en k intentos; "pass^k" = probabilidad de que TODOS k intentos sean exitosos, esencial para agentes donde usuarios esperan comportamiento fiable. [Fuente: Demystifying evals for AI agents — https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents]
- **LLM-judge calibration**: Modelos-juez basados en LLM deben ser cuidadosamente calibrados con expertos humanos para minimizar divergencias entre evaluaciones automáticas y humanas. [Fuente: Demystifying evals for AI agents — https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents]
- **Systematic error pattern detection**: Revisar transcripciones sistemáticamente para identificar si puntuaciones bajas reflejan limitaciones reales del agente o problemas en la evaluación misma (specs ambiguas, graders defectuosos). [Fuente: Demystifying evals for AI agents — https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents]

### Sintaxis y configuración
- **Field-level confidence output**:
  ```json
  {
    "extracted_field": "value",
    "confidence_score": 0.92,
    "field_type": "date|amount|name|status",
    "should_review": false
  }
  ```
  [Fuente: exam-guide-oficial-v1.0.txt, línea 735-738]

- **Calibrated review threshold** (example):
  ```
  If confidence < 0.70: route to human review
  If ambiguous/contradictory source document: route to human review
  Otherwise: auto-approve
  ```
  [Fuente: exam-guide-oficial-v1.0.txt, línea 735-738]

### Patrones
- **Stratified random sampling of high-confidence**: Implementar stratified random sampling de high-confidence extractions para ongoing error rate measurement y novel pattern detection. [Fuente: exam-guide-oficial-v1.0.txt, línea 731-732]
- **Analyze accuracy by segment**: Analizar accuracy by document type y field para verificar consistent performance a través de todos los segments antes de reducir human review. [Fuente: exam-guide-oficial-v1.0.txt, línea 733-734]
- **Confidence-based routing**: Modelos output field-level confidence scores; luego calibrar review thresholds usando labeled validation sets. [Fuente: exam-guide-oficial-v1.0.txt, línea 735-737]
- **Low confidence + ambiguity routing**: Rutear extractions con low model confidence o ambiguous/contradictory source documents a human review, priorizando reviewer capacity limitada. [Fuente: exam-guide-oficial-v1.0.txt, línea 738]
- **Balanced problem sets**: Construir conjuntos de evaluación "balanceados" que prueben tanto casos donde behavior DEBE ocurrir como donde NO debe ocurrir, evitando unidirectional bias. [Fuente: Demystifying evals for AI agents — https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents]
- **Periodic human study**: Llevar a cabo estudios humanos estructurados para tareas subjetivas; calibración continua de evaluadores automáticos contra referencias humanas. [Fuente: Demystifying evals for AI agents — https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents]

### Anti-patrones (y por qué fallan)
- **Relying on aggregate metrics only**: Reportar solo "97% overall accuracy" sin segmentación by document type/field esconde que un tipo de documento tiene 50% accuracy mientras otro tiene 99%. Resultado: high-confidence extractions del low-accuracy segment siguen siendo auto-approved y fail. [Fuente: exam-guide-oficial-v1.0.txt, línea 724]
- **Not calibrating confidence scores**: LLM confidence scores sin calibración contra labeled validation sets pueden ser poorly calibrated (ej: model says 95% confidence pero true accuracy es 60%). [Fuente: exam-guide-oficial-v1.0.txt, línea 727-728]

---

## TS 5.6 — Preserve information provenance and handle uncertainty in multi-source synthesis

### Hechos y comportamiento
- **Attribution loss during summarization**: Source attribution se pierde durante summarization steps cuando findings se comprimen sin preservar claim-source mappings. [Fuente: exam-guide-oficial-v1.0.txt, línea 745-746]
- **Structured claim-source preservation**: Importancia de structured claim-source mappings que synthesis agent DEBE preservar y merge cuando combining findings. [Fuente: exam-guide-oficial-v1.0.txt, línea 747-748]
- **Conflicting statistics annotation**: Cómo manejar estadísticas conflictivas de sources creíbles: anotando conflictos con source attribution en lugar de seleccionar arbitrariamente un valor. [Fuente: exam-guide-oficial-v1.0.txt, línea 749-750]
- **Temporal data in outputs**: Requerir publication/collection dates en structured outputs para prevenir que diferencias temporales sean misinterpretadas como contradicciones. [Fuente: exam-guide-oficial-v1.0.txt, línea 751-752]
- **Content-type-appropriate rendering**: Renderizar diferentes tipos de contenido apropiadamente en synthesis outputs—financial data as tables, news as prose, technical findings as structured lists—en lugar de convertir todo a formato uniforme. [Fuente: exam-guide-oficial-v1.0.txt, línea 762-764]
- **CitationAgent pattern**: Sistemas multi-agente dedican un agente especializado que identifica localizaciones específicas para citas y asegura que todas las afirmaciones estén atribuidas correctamente a sus sources. [Fuente: built-multi-agent-research-system]

### Sintaxis y configuración
- **Structured claim-source mapping output**:
  ```json
  {
    "claim": "AI adoption in music production increased 45% in 2025",
    "sources": [
      {
        "source_url": "https://example.com/report",
        "document_name": "Music Industry Report 2025",
        "relevant_excerpt": "45% year-over-year increase...",
        "publication_date": "2025-06-15"
      }
    ],
    "confidence": "high",
    "conflict_detected": false
  }
  ```
  [Fuente: exam-guide-oficial-v1.0.txt, línea 754-755]

- **Conflicting values with attribution**:
  ```json
  {
    "metric": "AI adoption in music",
    "values": [
      {
        "value": "45%",
        "source": "Music Industry Report 2025",
        "url": "https://...",
        "publication_date": "2025-06-15"
      },
      {
        "value": "38%",
        "source": "Tech Market Analysis",
        "url": "https://...",
        "publication_date": "2025-05-20"
      }
    ],
    "interpretation": "Different measurement methodologies; dates differ by one month"
  }
  ```
  [Fuente: exam-guide-oficial-v1.0.txt, línea 749-750]

### Patrones
- **Require structured claim-source mappings from subagents**: Requerir subagentes output structured claim-source mappings (source URLs, document names, relevant excerpts) que downstream agents preserven a través de synthesis. [Fuente: exam-guide-oficial-v1.0.txt, línea 754-755]
- **Distinguish well-established from contested findings**: Estructurar reportes con secciones explícitas distinguiendo well-established findings de contested ones, preservando original source characterizations y methodological context. [Fuente: exam-guide-oficial-v1.0.txt, línea 756-757]
- **Complete document analysis with conflicts annotated**: Completar document analysis incluyendo conflicting values y explícitamente anotados, dejando que el coordinator decida cómo reconciliar antes de pasar a synthesis. [Fuente: exam-guide-oficial-v1.0.txt, línea 758-759]
- **Include temporal metadata in structured outputs**: Requerir subagentes incluir publication o data collection dates en structured outputs para habilitar correct temporal interpretation. [Fuente: exam-guide-oficial-v1.0.txt, línea 760-761]
- **Content-type-aware rendering**: Renderizar financial data como tablas, noticias como prosa, hallazgos técnicos como listas estructuradas—respetando convenciones de cada tipo de contenido. [Fuente: exam-guide-oficial-v1.0.txt, línea 762-764]
- **CitationAgent for verification**: Dedicar un agente especializado para identificar localizaciones específicas de citas y asegurar atribución correcta. [Fuente: built-multi-agent-research-system]

### Anti-patrones (y por qué fallan)
- **Losing attribution during compression**: Resumir hallazgos sin preservar claim-source mappings resulta en synthesized output donde es imposible rastrear qué fuente dijo qué, imposibilitando verification y permitiendo afirmaciones no soportadas. [Fuente: exam-guide-oficial-v1.0.txt, línea 745-746]
- **Arbitrarily selecting conflicting values**: Cuando dos sources creíbles reportan estadísticas diferentes, seleccionar arbitrariamente una esconde la incertidumbre y puede mislead readers. Mejor: anotar ambos valores con metadatos (metodología, fecha de publicación). [Fuente: exam-guide-oficial-v1.0.txt, línea 749-750]
- **Misinterpreting temporal differences as contradictions**: Sin publication dates en outputs, diferencias temporales (ej: data from May vs data from June) pueden ser misinterpretadas como conflictos reales. [Fuente: exam-guide-oficial-v1.0.txt, línea 751-752]
- **Uniform format output**: Convertir todo a un formato uniforme (ej: todas las findings como prose) pierde context-specific convenciones (financial data como tablas ayuda a readers a comparar rápidamente). [Fuente: exam-guide-oficial-v1.0.txt, línea 762-764]

---

## HUECOS
- **TS 5.2 (Escalation patterns)**: Las fuentes oficiales no proporcionan detalles exhaustivos sobre criterios de escalation en escenarios reales; los sample questions del exam guide (Question 3, línea 925-943) proporcionan los únicos ejemplos específicos. Se intenta complementar con searches de terceros pero acceso limitado a documentación adicional.
- **TS 5.5 (Human review workflows)**: Cobertura limitada en fuentes oficiales; el blog demystifying-evals proporciona métricas (pass@k, pass^k, calibración) pero no patrones detallados de routing de revisión humana con ejemplos prácticos de umbrales de confianza.

## CONTRADICCIONES
- **Ninguna contradicción detectada** entre fuentes procesadas. Las guías oficiales (exam-guide, blogs Anthropic, docs) mantienen consistencia en hechos, sintaxis y patrones recomendados.

## FUENTES NO ACCESIBLES
- Ninguna fuente falla. Las 7 fuentes listadas en fuentes.yaml fueron accesibles y procesadas exitosamente.

## FUENTES ADICIONALES INCORPORADAS
- **exam-guide-oficial-v1.0.txt** — Usada ampliamente porque contiene los task statements literales y sample questions que ilustran patrones recomendados. Técnicamente no es una "fuente adicional" sino el blueprint oficial, incluida por referencia obligatoria en el proceso de extracción.
- **Built-multi-agent-research-system** (segunda lectura): WebFetch inicial extrajo información sobre error propagation, but additional context on "cascade failures" y "CitationAgent pattern" fue inferido del contenido y anotado como derivado de esa fuente en las secciones correspondientes.
