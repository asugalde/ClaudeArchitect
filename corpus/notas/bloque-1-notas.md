# Notas de extracción — Bloque 1: Prompt Engineering y salida estructurada
Fecha: 2026-08-05 · Fuentes procesadas: 8/9

## TS 4.1 — Diseñar prompts con criterios explícitos para mejorar precisión y reducir falsos positivos

### Hechos y comportamiento
- Los criterios explícitos mejoran significativamente la precisión frente a instrucciones vagas ("sea conservador" o "solo reportes de alta confianza"). [Fuente: exam-guide-oficial-v1.0.txt — línea 505-508]
- La tasa de falsos positivos en categorías tiene impacto directo en la confianza del desarrollador: categorías con muchos falsos positivos socavan la confianza incluso en categorías precisas. [Fuente: exam-guide-oficial-v1.0.txt — línea 509-510]
- **Enfoque recomendado**: definir criterios categóricos específicos sobre qué reportar (bugs, seguridad) vs qué omitir (estilo menor, patrones locales), en lugar de filtrado basado en confianza. [Fuente: exam-guide-oficial-v1.0.txt — línea 512-513]
- Deshabilitar temporalmente categorías de alto falso positivo mientras se mejoran los prompts permite restaurar confianza. [Fuente: exam-guide-oficial-v1.0.txt — línea 514-515]
- Definir criterios de severidad explícitos con ejemplos de código concretos para cada nivel de severidad logra clasificación consistente. [Fuente: exam-guide-oficial-v1.0.txt — línea 516-517]

### Sintaxis y configuración
- Estructura de criterios categóricos: definir explícitamente en el prompt qué tipos de problemas incluir vs excluir. [Fuente: Claude prompting best practices — "Be clear and direct"]
```
Golden rule: mostrar el prompt a un colega con contexto mínimo y preguntar si lo entiende. Si estaría confuso, Claude también lo estará.
```
[Fuente: Claude prompting best practices]

- **Separación datos/instrucciones**: envolver ejemplos en tags `<example>` o `<examples>` para que Claude distinga ejemplos de instrucciones. [Fuente: Claude prompting best practices — línea 90]
```xml
<examples>
  <example>
    <input>commented_code = true, actual_behavior = true</input>
    <classification>NO REPORT</classification>
    <reason>El comentario describe con precisión el comportamiento actual</reason>
  </example>
  <example>
    <input>commented_code = "close file", actual_behavior = "delete file"</input>
    <classification>REPORT</classification>
    <reason>El comentario contradice el comportamiento real — crítico encontrar discrepancias</reason>
  </example>
</examples>
```
[Fuente: Claude prompting best practices — ejemplo adaptado]

- Usar contexto en las instrucciones (explicar el *por qué*) para que Claude generalice mejor. [Fuente: Claude prompting best practices — línea 62-80]

### Patrones
- **Pattern 1 — Criterios categóricos vs confianza**: en lugar de "reporta solo si confianza > 0.8", usar "reporta cuando el comentario contradice demostrablemente el código". [Fuente: exam-guide-oficial-v1.0.txt — TS 4.1]
- **Pattern 2 — Ejemplos concretos de severidad**: proporcionar ejemplos de código para cada nivel de severidad (crítica, alta, media, baja) para lograr clasificación consistente. [Fuente: exam-guide-oficial-v1.0.txt — línea 516-517]
- **Pattern 3 — Mejora iterativa de categorías**: medir falsos positivos por categoría y deshabilitar temporalmente las peores mientras se refinan. [Fuente: exam-guide-oficial-v1.0.txt — línea 514-515]

### Anti-patrones (y por qué fallan)
- **Anti-patrón 1 — Instrucciones vagas ("sea conservador", "solo hallazgos de alta confianza")**: no mejoran precisión frente a criterios específicos; el modelo interpreta "confianza" arbitrariamente. [Fuente: exam-guide-oficial-v1.0.txt — línea 507-508]
- **Anti-patrón 2 — Intentar filtrar falsos positivos en post-procesamiento sin refinar el prompt**: no resuelve la raíz (criterios mal definidos). [Fuente: exam-guide-oficial-v1.0.txt — línea 512-513]

---

## TS 4.2 — Aplicar few-shot prompting para mejorar consistencia y calidad de salida

### Hechos y comportamiento
- **Few-shot examples es la técnica más efectiva** para lograr salida consistentemente formateada y accionable cuando instrucciones detalladas solos producen resultados inconsistentes. [Fuente: exam-guide-oficial-v1.0.txt — línea 521-522]
- Los ejemplos few-shot mejoran la capacidad del modelo de generalizar el juicio a patrones nuevos (no solo casos pre-especificados). [Fuente: exam-guide-oficial-v1.0.txt — línea 525-526]
- Los ejemplos few-shot reducen alucinación en tareas de extracción (p. ej. manejar medidas informales, estructuras de documento variadas). [Fuente: exam-guide-oficial-v1.0.txt — línea 527-528]
- Los ejemplos few-shot demuestran manejo de casos ambiguos (ej. selección de herramienta para requests ambiguos, brechas de cobertura de tests por rama). [Fuente: exam-guide-oficial-v1.0.txt — línea 523-524]
- **Rango recomendado: 2-4 ejemplos dirigidos** para escenarios ambiguos, mostrando razonamiento de por qué se eligió una acción sobre alternativas plausibles. [Fuente: exam-guide-oficial-v1.0.txt — línea 533-534]
- **Rango para consistencia: 3-5 ejemplos** para mejores resultados. [Fuente: Claude prompting best practices — línea 93-94]

### Sintaxis y configuración
- **Estructura de ejemplos**: envolver en tags `<examples>` (múltiples) o `<example>` (singular). [Fuente: Claude prompting best practices — línea 90]
```xml
<examples>
  <example>
    <input>var x = "hello"; console.log(x.toUpperCase())</input>
    <output_format>
      <location>line_5</location>
      <issue>potential_type_error</issue>
      <severity>medium</severity>
      <suggested_fix>ensure variable is string before calling method</suggested_fix>
    </output_format>
  </example>
  <example>
    <input>// undefined variable used
result = y + 5</input>
    <output_format>
      <location>line_2</location>
      <issue>undefined_variable</issue>
      <severity>high</severity>
      <suggested_fix>declare y with var/let/const before use</suggested_fix>
    </output_format>
  </example>
</examples>
```
[Fuente: exam-guide-oficial-v1.0.txt — TS 4.2, línea 535-536]

- **Demostrar razonamiento para casos ambiguos**: incluir en el ejemplo por qué se tomó una decisión vs alternativas. [Fuente: exam-guide-oficial-v1.0.txt — línea 533-534]
```
Caso ambiguo: request "validar usuario"
Ejemplo muestra: "Se selecciona auth_validate porque el contexto menciona permisos, no load_user"
```

- **Distinguir patrones aceptables de genuinos problemas**: proporcionar ejemplos que muestren código correcto vs incorrecto. [Fuente: exam-guide-oficial-v1.0.txt — línea 537-538]
- **Ejemplo con estructuras de documento variadas**: si la entrada varía (inline citations vs bibliographies), incluir ejemplos con cada variante. [Fuente: exam-guide-oficial-v1.0.txt — línea 539-540]
- **Evitar alucinación de campos vacíos**: añadir ejemplos mostrando extracción correcta cuando campos pueden estar ausentes (null vs hallucination). [Fuente: exam-guide-oficial-v1.0.txt — línea 541-542]

### Patrones
- **Pattern 1 — Few-shot para formato de salida**: cuando el prompt produce JSON inconsistente, añadir 2-3 ejemplos con formato exacto deseado logra consistencia. [Fuente: exam-guide-oficial-v1.0.txt — línea 535-536]
- **Pattern 2 — Few-shot para casos ambiguos**: resolver ambigüedad mostrando cómo el modelo debe razonar en escenarios grises. [Fuente: exam-guide-oficial-v1.0.txt — línea 533-534]
- **Pattern 3 — Few-shot para reducir alucinación**: mostrar ejemplo donde un campo está ausente (null) vs hallucinated generaliza mejor que instrucción sola. [Fuente: exam-guide-oficial-v1.0.txt — línea 541-542]
- **Pattern 4 — Estructura clara de ejemplos**: usar tags XML o markdown para distinguir componentes del ejemplo (input, output, reasoning). [Fuente: Claude prompting best practices — línea 90, 253]

### Anti-patrones (y por qué fallan)
- **Anti-patrón 1 — Ejemplos genéricos que no cubren casos reales**: si los ejemplos no reflejan distribución real de datos, el modelo no generaliza. [Fuente: Claude prompting best practices — línea 88 ("Relevant")]
- **Anti-patrón 2 — Demasiados ejemplos (>5) sin reducción de claridad**: incrementa context length innecesariamente. [Fuente: exam-guide-oficial-v1.0.txt — TS 4.2, rango 2-4 dirigidos]
- **Anti-patrón 3 — Few-shot sin razonamiento explícito**: mostrar solo input/output sin explicar por qué omite oportunidades de generalización. [Fuente: exam-guide-oficial-v1.0.txt — línea 533-534]

---

## TS 4.3 — Reforzar salida estructurada con tool use y JSON schemas

### Hechos y comportamiento
- **Tool use con JSON schemas es el enfoque más confiable** para garantizar salida conforme a schema, eliminando errores de sintaxis JSON. [Fuente: exam-guide-oficial-v1.0.txt — línea 545-546]
- **Strict tool use (strict: true)**: garantiza que los parámetros de herramienta coincidan con el schema JSON mediante grammar-constrained sampling; **no hay validación de sintaxis** pero sí validación de tipo y estructura. [Fuente: Strict tool use — descripción general]
- **Distinción crítica**: strict tool use elimina *errores de sintaxis JSON* pero NO previene *errores semánticos* (ej. line items que no suman total, valores en campos equivocados). [Fuente: exam-guide-oficial-v1.0.txt — línea 550-551]
- **tool_choice opciones**:
  - `"auto"`: modelo puede retornar texto en lugar de llamar herramienta (NO garantiza tool use). [Fuente: exam-guide-oficial-v1.0.txt — línea 548-549]
  - `"any"`: modelo DEBE llamar herramienta, pero puede elegir cuál (garantiza tool use cuando múltiples schemas existen y tipo de documento desconocido). [Fuente: exam-guide-oficial-v1.0.txt — línea 558]
  - Forzado específico `{"type": "tool", "name": "extract_metadata"}`: asegura que herramienta particular corre antes de pasos de enriquecimiento. [Fuente: exam-guide-oficial-v1.0.txt — línea 559-560]

### Sintaxis y configuración
- **Parámetro strict en definición de herramienta**:
```typescript
{
  name: "extract_data",
  description: "Extract structured data from document",
  strict: true,  // Enable strict mode
  input_schema: {
    type: "object",
    properties: {
      title: { type: "string" },
      amount: { type: "number" },
      date: { type: "string", format: "date" }
    },
    required: ["title", "amount"],
    additionalProperties: false  // Rechaza campos no definidos
  }
}
```
[Fuente: Strict tool use — Quick start + Structured Outputs]

- **Diseño de fields — required vs optional**:
```
Required fields: solo datos que SIEMPRE existen en documentos de origen.
Optional fields: información que PUEDE estar ausente (previene hallucination).

Incorrecto:  "author": { type: "string" }  // always required
Correcto:    required: ["title"]  // solo campos verdaderamente obligatorios
```
[Fuente: exam-guide-oficial-v1.0.txt — línea 562-563]

- **Enum con patrón "other" + detail string para extensibilidad**:
```json
{
  "category": {
    "type": "string",
    "enum": ["positive", "negative", "neutral", "other"]
  },
  "category_details": {
    "type": "string",
    "description": "Use when category is 'other'"
  }
}
```
[Fuente: exam-guide-oficial-v1.0.txt — línea 563-564]

- **Valores enum adicionales para casos ambiguos**: incluir "unclear" para situaciones donde información es genuinamente ambigua. [Fuente: exam-guide-oficial-v1.0.txt — línea 563]

- **Normalización de formato en el prompt**: aunque el schema sea estricto, incluir reglas de normalización en el prompt para manejar fuentes inconsistentes (p. ej. fechas en múltiples formatos → YYYY-MM-DD). [Fuente: exam-guide-oficial-v1.0.txt — línea 568-569]

- **JSON Schema soportado** (valid en strict mode):
  - Basic types: `object`, `array`, `string`, `integer`, `number`, `boolean`, `null`
  - `enum` (strings, numbers, bools)
  - `anyOf`, `allOf`
  - `$ref` y `definitions`
  - String formats: `date-time`, `date`, `email`, `uri`, `uuid`
  - `required` fields
  - `additionalProperties: false`
  [Fuente: Structured outputs — JSON Schema Support]

- **NO soportado en strict mode**:
  - Recursive schemas
  - Numerical constraints (`minimum`, `maximum`)
  - String constraints (`minLength`, `maxLength`)
  - `additionalProperties: true`
  [Fuente: Structured outputs — JSON Schema Support / Not Supported]

### Patrones
- **Pattern 1 — Tool use forzado para garantizar extracción**: usar `tool_choice: {"type": "tool", "name": "extract_metadata"}` cuando se debe garantizar que la herramienta se ejecuta (ej. before enrichment). [Fuente: exam-guide-oficial-v1.0.txt — línea 559-560]
- **Pattern 2 — tool_choice: "any" para múltiples schemas con tipo desconocido**: cuando el tipo de documento es incierto, "any" garantiza tool use pero permite al modelo elegir schema. [Fuente: exam-guide-oficial-v1.0.txt — línea 558]
- **Pattern 3 — Campos opcionales para prevenir hallucination**: diseñar campos como nullable cuando el documento source puede no contener información. [Fuente: exam-guide-oficial-v1.0.txt — línea 562-563]
- **Pattern 4 — Enum + "other" para extensibilidad**: permitir que el modelo reporte categorías no previstas con campo de detalle. [Fuente: exam-guide-oficial-v1.0.txt — línea 563-564]

### Anti-patrones (y por qué fallan)
- **Anti-patrón 1 — Todos los campos como required**: fuerza al modelo a alucinar datos cuando el documento fuente es incompleto. [Fuente: exam-guide-oficial-v1.0.txt — línea 562-563]
- **Anti-patrón 2 — Strict mode sin prompt de normalización**: source data variada (fechas, formatos) puede no conformarse al schema esperado. [Fuente: exam-guide-oficial-v1.0.txt — línea 568-569]
- **Anti-patrón 3 — Confundir sintaxis con semántica**: strict mode valida estructura JSON, NO lógica (ej. campos que deben sumar X). [Fuente: exam-guide-oficial-v1.0.txt — línea 550-551]
- **Anti-patrón 4 — additionalProperties: true en strict mode**: el schema debe ser explícito; rechazar campos no definidos con `additionalProperties: false`. [Fuente: Structured outputs]

---

## TS 4.4 — Implementar validación, reintentos y bucles de feedback

### Hechos y comportamiento
- **Retry with error feedback**: incluir errores de validación específicos en el reintenso para guiar al modelo hacia corrección. [Fuente: exam-guide-oficial-v1.0.txt — línea 573-574]
- **Límites de reintento**: los reintentos son INEFECTIVOS cuando la información requerida simplemente no existe en el documento source (vs errores de formato o estructura). [Fuente: exam-guide-oficial-v1.0.txt — línea 575-576]
- **Feedback loop design**: rastrear qué construcciones de código disparan hallazgos (campo detected_pattern) para análisis sistemático de patrones de descarte. [Fuente: exam-guide-oficial-v1.0.txt — línea 577-578]
- **Distinción crítica**: errores de validación *semántica* (valores no suman, campos equivocados) vs *sintaxis* (tool use elimina errores de sintaxis). [Fuente: exam-guide-oficial-v1.0.txt — línea 579-580]

### Sintaxis y configuración
- **Follow-up request con error feedback específico**:
```
Prompt inicial: "Extract invoice data as JSON"
Respuesta: { "items": [...], "total": 1500 }  ← validación falla

Follow-up: "The extraction failed validation:
- Sum of item amounts ($1000) ≠ stated total ($1500)
- Fix the discrepancy by re-examining the document.
Provide the corrected extraction."
```
[Fuente: exam-guide-oficial-v1.0.txt — línea 582-583]

- **Incluir documento original + extracción fallida + errores específicos**: el modelo necesita todo el contexto para auto-corregirse. [Fuente: exam-guide-oficial-v1.0.txt — línea 582-583]

- **detected_pattern field para análisis de falsos positivos**:
```json
{
  "finding": "potential null pointer dereference",
  "location": "line 42",
  "detected_pattern": "variable_accessed_without_null_check",
  "confidence": 0.85
}
```
[Fuente: exam-guide-oficial-v1.0.txt — línea 586]

- **Validación de conflictos en los datos source**: añadir campos de validación calculada para detectar inconsistencias:
```json
{
  "stated_total": 1500,
  "calculated_total": 1000,
  "conflict_detected": true,
  "conflict_description": "Sum of items does not match stated total"
}
```
[Fuente: exam-guide-oficial-v1.0.txt — línea 588-589]

### Patrones
- **Pattern 1 — Retry con error feedback específico**: cuando la extracción falla validación, reintentar con el error exacto (no genérico) guía corrección. [Fuente: exam-guide-oficial-v1.0.txt — línea 573-574]
- **Pattern 2 — Detectar cuándo reintentos serán inútiles**: si la información no existe en source document, reintento no mejorará; requiere cambio de fuente o aceptación del vacío. [Fuente: exam-guide-oficial-v1.0.txt — línea 575-576]
- **Pattern 3 — Track detected_pattern para análisis de false positives**: cuando developers descartan findings, rastrear qué patrón se detectó permite mejora sistemática. [Fuente: exam-guide-oficial-v1.0.txt — línea 577-578]
- **Pattern 4 — Self-correction validation flows**: incluir "calculated_total" y "stated_total" juntos para que el modelo reporte discrepancias. [Fuente: exam-guide-oficial-v1.0.txt — línea 588-589]

### Anti-patrones (y por qué fallan)
- **Anti-patrón 1 — Reintentar sin proporcionar feedback específico**: el error genérico ("try again") no ayuda; el modelo necesita saber exactamente qué falló. [Fuente: exam-guide-oficial-v1.0.txt — línea 573-574]
- **Anti-patrón 2 — Reintentar información que no existe**: si el documento source no contiene el dato, reintentos repetidos no lo generarán. [Fuente: exam-guide-oficial-v1.0.txt — línea 575-576]
- **Anti-patrón 3 — No rastrear patrones de falsos positivos**: sin detected_pattern, no se puede analizar qué categorías tienen altas tasas de descarte. [Fuente: exam-guide-oficial-v1.0.txt — línea 577-578]

---

## TS 4.5 — Diseñar estrategias eficientes de batch processing

### Hechos y comportamiento
- **Message Batches API**: ahorro del 50% de coste, ventana de procesamiento hasta 24 horas, SLA de latencia NO garantizado. [Fuente: exam-guide-oficial-v1.0.txt — línea 592-593]
- **Batch processing es apropiado para**: workloads no-bloqueantes y tolerantes de latencia (reportes overnight, auditorías semanales, generación de tests nocturnos). [Fuente: exam-guide-oficial-v1.0.txt — línea 594-596]
- **Batch processing es INAPROPIADO para**: flujos bloqueantes (pre-merge checks, feedback en tiempo real). [Fuente: exam-guide-oficial-v1.0.txt — línea 594-596]
- **Limitación crítica**: Batch API NO soporta multi-turn tool calling dentro de single request (no puedes ejecutar tools mid-request y retornar resultados). [Fuente: exam-guide-oficial-v1.0.txt — línea 597-598]

### Sintaxis y configuración
- **custom_id para correlacionar request/response**:
```python
requests = [
    {
        "custom_id": "invoice-001",
        "params": {
            "model": "claude-opus-5",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": "Extract invoice data..."}]
        }
    },
    {
        "custom_id": "invoice-002",
        "params": {
            "model": "claude-opus-5",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": "Extract invoice data..."}]
        }
    }
]

batch = client.messages.batches.create(requests=requests)
```
[Fuente: Batch processing — Message Batches API]

- **Limite de batch**: 100,000 requests o 256 MB de tamaño (lo que se alcance primero). [Fuente: Batch processing — Batch limitations]
- **Ventana de procesamiento**: la mayoría se completa en < 1 hora; máximo 24 horas (después expira). Acceso a resultados por 29 días. [Fuente: Batch processing — Batch limitations]
- **Parámetros NO soportados en batch**: `stream: true`, `speed` (fast mode), `store` / `previous_thread_event_id` (threads), `cache_hint` / `context_hint`, `max_tokens: 0`. [Fuente: Batch processing — What can be batched]

### Patrones
- **Pattern 1 — Seleccionar API según latencia requerida**: API síncrona para pre-merge checks (bloqueantes); Batch API para reportes overnight. [Fuente: exam-guide-oficial-v1.0.txt — línea 604-605]
- **Pattern 2 — Calcular frecuencia de submission por SLA**: p. ej. "para garantizar 30-hour SLA con 24-hour batch processing, enviar cada 4 horas". [Fuente: exam-guide-oficial-v1.0.txt — línea 606-607]
- **Pattern 3 — Manejar fallos de batch**: reintentar solo documentos fallidos (identificados por custom_id) con modificaciones apropiadas (ej. chunking de docs que excedieron context limit). [Fuente: exam-guide-oficial-v1.0.txt — línea 608-609]
- **Pattern 4 — Refinar prompt en muestra antes de batch masivo**: probar prompt refinement en sample set primero para maximizar éxito de primer intento y reducir resubmisiones. [Fuente: exam-guide-oficial-v1.0.txt — línea 610-611]

### Anti-patrones (y por qué fallan)
- **Anti-patrón 1 — Usar batch para workloads bloqueantes**: si necesitas respuesta en < minutos, batch (24h max) es inadecuado. [Fuente: exam-guide-oficial-v1.0.txt — línea 594-596]
- **Anti-patrón 2 — No usar custom_id para tracking**: sin correlación clara, es imposible saber cuál request corresponde a cuál respuesta. [Fuente: Batch processing — Message Batches API]
- **Anti-patrón 3 — Batch masivo sin refinamiento previo**: enviar 100,000 requests con prompt sin probar = costo/tiempo desperdiciado en fallos. [Fuente: exam-guide-oficial-v1.0.txt — línea 610-611]
- **Anti-patrón 4 — Multi-turn tool use esperado en batch**: batch procesa cada request independently; no hay estado entre requests. [Fuente: exam-guide-oficial-v1.0.txt — línea 597-598]

---

## TS 4.6 — Diseñar arquitecturas de multi-instancia y multi-pass review

### Hechos y comportamiento
- **Auto-review limitación**: el modelo retiene contexto de razonamiento de generación, lo que lo hace MENOS propenso a cuestionarse a sí mismo en la misma sesión. [Fuente: exam-guide-oficial-v1.0.txt — línea 614-615]
- **Revisión independiente es más efectiva**: instancias Claude independientes (sin contexto de razonamiento previo del generador) son MEJORES para detectar problemas sutiles que self-review. [Fuente: exam-guide-oficial-v1.0.txt — línea 616-617]
- **Multi-pass review arquitectura**: dividir reviews grandes en:
  - **Local analysis passes** (por-archivo): problemas locales, patrones directos.
  - **Cross-file integration passes**: análisis de data flow entre archivos, contradicciones.
  Esto **evita dilución de atención** y hallazgos contradictorios. [Fuente: exam-guide-oficial-v1.0.txt — línea 618-619]

### Sintaxis y configuración
- **Instancia independiente para review (pseudo-código)**:
```python
# Generator instance
generated_code = generator_claude.generate_code(prompt)

# Independent reviewer instance (different context, no knowledge of generator's reasoning)
review = reviewer_claude.review_code(
    code=generated_code,
    criteria=review_criteria
    # NO incluir razonamiento del generador
)
```
[Fuente: exam-guide-oficial-v1.0.txt — línea 621-622]

- **Multi-pass review con confidence tracking**:
```python
# Pass 1: Local file analysis
local_findings = []
for file in files:
    findings = claude.analyze_file(
        file=file,
        focus="local issues, syntax, direct patterns"
    )
    # Include confidence with each finding
    findings = [{**f, "confidence": ...} for f in findings]
    local_findings.extend(findings)

# Pass 2: Integration analysis (cross-file)
integration_findings = claude.analyze_integration(
    files=files,
    local_findings=local_findings,
    focus="data flow, dependencies, contradictions"
)
```
[Fuente: exam-guide-oficial-v1.0.txt — línea 624-626]

- **Confidence self-reporting**: el modelo reporta su propia confianza junto a cada hallazgo para habilitar **calibrated review routing** (high-confidence findings aceptar; low-confidence repasar). [Fuente: exam-guide-oficial-v1.0.txt — línea 625-626]

### Patrones
- **Pattern 1 — Segunda instancia independiente para review**: nunca usar la misma instancia que generó el código; usar contexto fresco. [Fuente: exam-guide-oficial-v1.0.txt — línea 621-622]
- **Pattern 2 — Split local vs integration passes**: para reviews de múltiples archivos, dividir en pass local (por-archivo) + pass de integración (cross-archivo). [Fuente: exam-guide-oficial-v1.0.txt — línea 624]
- **Pattern 3 — Confidence calibration**: incluir confianza en cada hallazgo para que routing pueda priorizar revisión manual en casos de baja confianza. [Fuente: exam-guide-oficial-v1.0.txt — línea 625-626]

### Anti-patrones (y por qué fallan)
- **Anti-patrón 1 — Self-review en la misma instancia**: el modelo retiene razonamiento previo y es menos propenso a cuestionarse. [Fuente: exam-guide-oficial-v1.0.txt — línea 614-615]
- **Anti-patrón 2 — Single-pass review para código multi-archivo**: intenta encontrar problemas locales Y cross-file simultáneamente = dilución de atención, hallazgos contradictorios. [Fuente: exam-guide-oficial-v1.0.txt — línea 618-619]
- **Anti-patrón 3 — No rastrear confianza en hallazgos**: sin calibración, no hay forma de priorizar qué hallazgos requieren validación manual. [Fuente: exam-guide-oficial-v1.0.txt — línea 625-626]

---

## HUECOS
- **Implementación detallada de evaluación de evals**: TS 4.1 y 4.4 mencionan évals pero carecen de detalles sobre cómo implementar graders (solo disponible en "Define success criteria" doc, que cubre métodos genéricos). Posible gap: notebooks de ejemplo específicos para evals de precisión/falsos positivos no encontrados en cookbook accessible.
- **TS 4.6 — Detalles de arquitectura**: la guía oficial es breve; implementación práctica de multi-pass y confidence routing en Agent SDK no cubierta en fuentes procesadas (probablemente en Bloque 4 "Agent SDK").

## CONTRADICCIONES
- Ninguna contradicción detectada entre fuentes. Batch processing claridad, tool use strict mode, y few-shot guidance son consistentes.

## FUENTES NO ACCESIBLES
- "Prompting 101 — Code w/ Claude" (https://www.youtube.com/watch?v=ysPbXH0LpIE) → **Video de YouTube, no transcripción extraíble**. Anotada como no accesible; se recomienda revisión manual del video si disponible.

## FUENTES ADICIONALES INCORPORADAS
- **Exam-guide-oficial-v1.0.txt** (local) → Source of truth para TS 4.1–4.6, líneas 501-626.
- **Define success criteria & evals doc** (https://platform.claude.com/docs/en/docs/test-and-evaluate/develop-tests) → Incluida porque TS 4.1 y 4.4 refieren a métricas/validación.
- **Interactive Prompt Engineering Tutorial** (GitHub) → Incluida como cobertura de técnicas intermedias (few-shot, estrutura).
- **Claude Cookbooks** (GitHub) → Incluida para referencias a patrones prácticos de JSON extraction y evals.
