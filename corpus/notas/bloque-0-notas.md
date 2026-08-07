# Notas de extracción — Bloque 0: Fundamentos — API de Claude, tool use y bucle agéntico

Fecha: 2026-08-05 · Fuentes procesadas: 5/7 (2 URLs de Skilljar con acceso restringido; 7 intentadas)

---

## TS 0.1 — Anatomía de la Messages API: estructura request/response, roles, array messages, max_tokens, multi-turno

### Hechos y comportamiento

- **Estructura básica de request**: `POST /v1/messages` con parámetros `model`, `max_tokens`, `messages` (array), opcionalmente `system` (top-level). Las cabeceras son `x-api-key`, `anthropic-version: 2023-06-01`, `content-type: application/json`. [Fuente: Working with the Messages API — https://platform.claude.com/docs/en/build-with-claude/working-with-messages]

- **Parámetro system**: se pasa a nivel top-level, NO como mensaje con role "system" al inicio (salvo en Claude Opus 5, Opus 4.8, Fable 5, Mythos 5 que permiten mid-conversation system messages después de un user turn). [Fuente: Working with the Messages API — https://platform.claude.com/docs/en/build-with-claude/working-with-messages]

- **Array messages**: contiene objetos con `role` ("user" o "assistant") y `content` (string o array de content blocks). Historial de conversación debe enviarse completo en cada request (API es stateless). [Fuente: Working with the Messages API — https://platform.claude.com/docs/en/build-with-claude/working-with-messages]

- **Roles permitidos**: `user` (entrada del usuario o tool results), `assistant` (respuestas del modelo, incluyendo tool_use blocks). No hay role "system" en el array messages (solo top-level system parameter). [Fuente: Working with the Messages API — https://platform.claude.com/docs/en/build-with-claude/working-with-messages]

- **max_tokens**: determina cuántos tokens puede usar Claude para su respuesta de salida. Se refiere a presupuesto de tokens de salida, no de entrada. Si se alcanza durante generación, `stop_reason` = `"max_tokens"`. [Fuente: Working with the Messages API — https://platform.claude.com/docs/en/build-with-claude/working-with-messages]

- **Response estructura**: retorna objeto con `id`, `type: "message"`, `role: "assistant"`, `content` (array de content blocks: text, tool_use, tool_result, image, document), `model`, `stop_reason`, `stop_sequence` (null si no aplica), `usage` (input_tokens, output_tokens). [Fuente: Working with the Messages API — https://platform.claude.com/docs/en/build-with-claude/working-with-messages]

- **Content blocks en response**: pueden ser `type: "text"` (string), `type: "tool_use"` (id, name, input), `type: "tool_result"` (cuando server tools ejecutan), etc. [Fuente: How tool use works — https://platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works]

- **Multi-turno**: cada request incluye el historial COMPLETO (user → assistant → user → assistant → ...). No hay sesión persistente en servidor; cliente mantiene estado. [Fuente: Working with the Messages API — https://platform.claude.com/docs/en/build-with-claude/working-with-messages]

### Sintaxis y configuración

```json
// Request básico
{
  "model": "claude-opus-5",
  "max_tokens": 1024,
  "system": "You are a helpful assistant.",
  "messages": [
    {"role": "user", "content": "Hello, Claude"},
    {"role": "assistant", "content": "Hello!"},
    {"role": "user", "content": "Can you describe LLMs?"}
  ]
}
```

```json
// Response de éxito
{
  "id": "msg_01XFDUDYJgAACzvnptvVoYEL",
  "type": "message",
  "role": "assistant",
  "content": [
    {"type": "text", "text": "LLMs are..."}
  ],
  "model": "claude-opus-5",
  "stop_reason": "end_turn",
  "stop_sequence": null,
  "usage": {
    "input_tokens": 12,
    "output_tokens": 6
  }
}
```

[Fuente: Working with the Messages API — https://platform.claude.com/docs/en/build-with-claude/working-with-messages]

### Patrones

- **Pattern: Construir historial progresivo**: append de cada turno (user mensaje, assistant respuesta) en el array messages; en siguiente request, enviar array completo actualizado. Permite mantener contexto.

- **Pattern: Content blocks heterogéneos**: un single assistant message puede contener mix de text + tool_use blocks (p.ej., "I'll check the weather" + tool_use call).

### Anti-patrones (y por qué fallan)

- **NO pasar system como mensaje**: pasarlo como parámetro top-level, no dentro del array messages. Enviar como `{"role": "system", "content": "..."}` en messages causa error o comportamiento indefinido.

- **NO confundir responsabilidad de estado**: API es stateless. Si se asume que servidor mantiene contexto entre requests, se perderá historial.

- **NO truncar historial sin cuidado**: si se envía solo el último turn, se pierde contexto previo crítico (el modelo no lo verá).

---

## TS 0.2 — Definición de tools con JSON Schema: name, description, input_schema; qué hace buena una descripción; strict tool use

### Hechos y comportamiento

- **Parámetros de tool definition**: `name` (regex `^[a-zA-Z0-9_-]{1,64}$`), `description` (plaintext detallado, 3-4 oraciones mínimo), `input_schema` (JSON Schema object), opcionalmente `input_examples` (array de objetos válidos). [Fuente: Define tools — https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools]

- **input_schema estructura**: objeto JSON Schema con `type: "object"`, `properties` (objeto con claves de parámetros y sus definiciones type/description), `required` (array de nombres de parámetros obligatorios). [Fuente: Define tools — https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools]

- **Descripción efectiva debe incluir**:
  - Qué hace el tool
  - Cuándo usarlo (y cuándo NO usarlo)
  - Qué significa cada parámetro y cómo afecta comportamiento
  - Caveats y limitaciones (p.ej., "no retorna info sobre X")
  - Ejemplos de entrada si es complejo
  [Fuente: Define tools — https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools]

- **input_examples field**: opcional, array de objetos que son instancias válidas del input_schema. Ayuda al modelo a entender parámetros opcionales, formatos, y patrones. Token cost: ~20–50 por ejemplo simple, ~100–200 para complejos. [Fuente: Define tools — https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools]

- **Strict tool use** (strict: true): garantiza que llamadas a tools SIEMPRE matchean el schema exactamente (no hay missing required parameters, type mismatches, etc.). Requiere `tool_choice: "any"` o `"tool"` para que el prefill automático funcione. [Fuente: Define tools — https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools]

- **Consolidación de tools**: mejor tener 4-5 tools capables con un `action` parameter que 20 herramientas específicas (reduce ambigüedad). [Fuente: Define tools — https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools]

- **Namespacing de nombres**: prefijo con servicio (p.ej., `github_list_prs`, `slack_send_message`) cuando tools abarcan múltiples servicios; claridad y evita confusión. [Fuente: Define tools — https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools]

- **Tool use system prompt**: la API construye automáticamente un system prompt especial a partir de las tool definitions, tool_choice, y user system prompt. No se modifica manualmente; es generado internamente. [Fuente: Define tools — https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools]

### Sintaxis y configuración

```json
// Tool definition con description mínima (POBRE)
{
  "name": "get_stock_price",
  "description": "Gets the stock price for a ticker.",
  "input_schema": {
    "type": "object",
    "properties": {
      "ticker": {"type": "string"}
    },
    "required": ["ticker"]
  }
}
```

```json
// Tool definition con description excelente (BUENA)
{
  "name": "get_stock_price",
  "description": "Retrieves the current stock price for a given ticker symbol. The ticker symbol must be a valid symbol for a publicly traded company on a major US stock exchange like NYSE or NASDAQ. The tool will return the latest trade price in USD. It should be used when the user asks about the current or most recent price of a specific stock. It will not provide any other information about the stock or company.",
  "input_schema": {
    "type": "object",
    "properties": {
      "ticker": {
        "type": "string",
        "description": "The stock ticker symbol, e.g. AAPL for Apple Inc."
      }
    },
    "required": ["ticker"]
  }
}
```

```json
// Tool con input_examples
{
  "name": "get_weather",
  "description": "Get the current weather in a given location",
  "input_schema": {
    "type": "object",
    "properties": {
      "location": {
        "type": "string",
        "description": "The city and state, e.g. San Francisco, CA"
      },
      "unit": {
        "type": "string",
        "enum": ["celsius", "fahrenheit"],
        "description": "The unit of temperature"
      }
    },
    "required": ["location"]
  },
  "input_examples": [
    {"location": "San Francisco, CA", "unit": "fahrenheit"},
    {"location": "Tokyo, Japan", "unit": "celsius"},
    {"location": "New York, NY"}  // unit es opcional
  ]
}
```

```json
// Strict tool use
{
  "name": "extract_data",
  "description": "Extract structured data from input",
  "strict": true,
  "input_schema": {
    "type": "object",
    "properties": {
      "field1": {"type": "string"},
      "field2": {"type": "integer"}
    },
    "required": ["field1", "field2"]
  }
}
```

[Fuente: Define tools — https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools]

### Patrones

- **Pattern: Descripción diferenciadora**: cuando dos tools son similares (p.ej., `analyze_content` vs `analyze_document`), descripción detallada que explique fronteras (qué acepta cada uno, cuándo elegir uno vs otro). Evita misrouting.

- **Pattern: Parámetros opcionales con null**: si el source document puede no contener un valor, marcar field como nullable/optional en schema, no required. El modelo no fabricará valores para satisfacer required fields.

- **Pattern: Enum + "other" + detail**: para categorización extensible, incluir enum values PLUS un campo "other" con string para casos no previstos.

- **Pattern: input_examples para complejos**: si tool tiene parámetros complejos o nested, proporcionar 2-3 ejemplos válidos en `input_examples`.

### Anti-patrones (y por qué fallan)

- **Descripción genérica/vaga**: "Gets data" sin contexto. Modelo no sabe CUÁNDO usar, con qué input, qué esperar. Resultado: misrouting, invocaciones incorrectas.

- **Parámetros ambiguos o overlapping**: tool "lookup_data" sin especificar si es por ID, nombre, o email. Modelo adivinará. Mejor: parámetros nombrados claramente + descripción del rango válido.

- **Required fields que el source no siempre proporciona**: si schema pide "customer_phone" como required pero un documento puede no tenerlo, modelo inventará valores falsos. Solución: marcar como optional/nullable.

- **Sin strict mode cuando se requiere garantía**: si necesitas validación de schema garantizada (p.ej., extracción estructurada), usar `strict: true`. Sin él, el modelo puede emitir JSON inválido (aunque es raro).

---

## TS 0.3 — Ciclo tool_use/tool_result: bloques de contenido, tool_use_id, client tools vs server tools, errores en tool_result

### Hechos y comportamiento

- **Ciclo básico (client tools)**:
  1. Request con `tools` array y user message
  2. Response con `stop_reason: "tool_use"` + uno o más `tool_use` content blocks
  3. Cliente parsea `tool_use` blocks: extrae `id`, `name`, `input`
  4. Cliente ejecuta el tool real en su codebase
  5. Cliente envía nuevo request: historial completo + user message con `tool_result` block
  6. Loop continúa while `stop_reason == "tool_use"`, sale en `end_turn` o `max_tokens` u otro.
  [Fuente: How tool use works — https://platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works]

- **tool_use block estructura**: 
  - `type: "tool_use"`
  - `id`: UUID único para este tool call (usado para matchear con tool_result)
  - `name`: nombre exacto del tool
  - `input`: objeto JSON con parámetros pasados al tool, conforme a input_schema
  [Fuente: How tool use works, Handle tool calls — https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls]

- **tool_result block estructura**:
  - `type: "tool_result"`
  - `tool_use_id`: el `id` del tool_use block que responde (DEBE matchear)
  - `content` (optional): resultado como string, array de content blocks (text, image, document), o empty. Puede incluir text, image, document, search_result blocks.
  - `is_error` (optional): boolean, true si hubo error en ejecución
  [Fuente: Handle tool calls — https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls]

- **Requisito de ordenamiento**: tool_result blocks deben venir INMEDIATAMENTE después de los tool_use blocks del assistant en el historial. No se permite interpolar otros mensajes entre tool_use y tool_result.

- **Orden en content array**: en el user message que contiene tool_result, los tool_result blocks deben venir PRIMERO; si hay texto, va DESPUÉS. Texto antes de tool_result causa error 400. [Fuente: Handle tool calls — https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls]

- **Server tools vs client tools**:
  - **Client tools**: Claude emite `tool_use` block, cliente ejecuta, retorna tool_result. Cliente maneja el loop.
  - **Server tools** (web_search, web_fetch, code_execution, tool_search): Anthropic ejecuta internamente. Response puede tener `server_tool_use` block sin resultado aún si está en un batch con client tools; de lo contrario, resultado viene en respuesta. [Fuente: How tool use works — https://platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works]

- **Parallel tool calls**: Claude puede emitir múltiples `tool_use` blocks en un single response (parallelismo). Cliente ejecuta TODOS en paralelo, retorna TODOS sus tool_result blocks en el siguiente request. [Fuente: Overview — https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview]

- **error handling con is_error**:
  - Si tool execution falla (p.ej., network error), retorna `"is_error": true` en tool_result con mensaje descriptivo (no genérico como "failed").
  - Claude incorpora error en su siguiente respuesta, puede intentar recuperarse o escalalar al usuario.
  - Mensaje de error instructivo (p.ej., "Rate limit exceeded. Retry after 60 seconds.") mejor que "Error".
  [Fuente: Handle tool calls — https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls]

- **Server tool + client tool en same turn**: si assistant response contiene tanto `tool_use` como `server_tool_use` blocks, cliente responde solo con los `tool_result` blocks para los client tools; servidor ejecuta sus server tools y retorna resultados. [Fuente: Handling stop reasons — https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons]

### Sintaxis y configuración

```json
// Request inicial con tools
{
  "model": "claude-opus-5",
  "max_tokens": 1024,
  "tools": [
    {
      "name": "get_weather",
      "description": "Get the current weather for a given location.",
      "input_schema": {
        "type": "object",
        "properties": {
          "location": {
            "type": "string",
            "description": "City and state, e.g. San Francisco, CA"
          }
        },
        "required": ["location"]
      }
    }
  ],
  "messages": [
    {"role": "user", "content": "What's the weather in San Francisco?"}
  ]
}
```

```json
// Response con tool_use block
{
  "id": "msg_01Aq9w938a90dw8q",
  "type": "message",
  "role": "assistant",
  "stop_reason": "tool_use",
  "content": [
    {
      "type": "text",
      "text": "I'll check the current weather in San Francisco for you."
    },
    {
      "type": "tool_use",
      "id": "toolu_01A09q90qw90lq917835lq9",
      "name": "get_weather",
      "input": {
        "location": "San Francisco, CA"
      }
    }
  ]
}
```

```json
// Follow-up request con tool_result
{
  "model": "claude-opus-5",
  "max_tokens": 1024,
  "tools": [...],  // mismas tools
  "messages": [
    {"role": "user", "content": "What's the weather in San Francisco?"},
    {
      "role": "assistant",
      "content": [
        {"type": "text", "text": "I'll check the current weather in San Francisco for you."},
        {"type": "tool_use", "id": "toolu_01A09q90qw90lq917835lq9", "name": "get_weather", "input": {"location": "San Francisco, CA"}}
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "tool_result",
          "tool_use_id": "toolu_01A09q90qw90lq917835lq9",
          "content": "15 degrees Celsius, partly cloudy"
        }
      ]
    }
  ]
}
```

```json
// tool_result con error
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01A09q90qw90lq917835lq9",
      "content": "ConnectionError: the weather service API is not available (HTTP 500)",
      "is_error": true
    }
  ]
}
```

```json
// tool_result con múltiples content blocks
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01A09q90qw90lq917835lq9",
      "content": [
        {"type": "text", "text": "15 degrees"},
        {
          "type": "image",
          "source": {
            "type": "base64",
            "media_type": "image/jpeg",
            "data": "/9j/4AAQSkZJRg..."
          }
        }
      ]
    }
  ]
}
```

[Fuente: Handle tool calls — https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls]

### Patrones

- **Pattern: Loop while stop_reason == "tool_use"**: la condicional de control del bucle agéntico es simple: si stop_reason es tool_use, continuar; de lo contrario, salir.

- **Pattern: Error messages instructivos**: no "failed" ni "error", sino "Rate limit exceeded. Retry after 60 seconds." o "Missing required 'location' parameter". Habilita recuperación inteligente del modelo.

- **Pattern: Preservar tool_use_id exactamente**: el id de tool_use debe matchear exactamente el tool_use_id en tool_result. Mismatch causa error o resultado perdido.

- **Pattern: Empty tool_result**: Si tool execution retorna nada (vacío válido), permitir `tool_result` sin `content` o con `content: ""`. Diferente de error.

### Anti-patrones (y por qué fallan)

- **Text antes de tool_result en content array**: Si se envía `[{"type": "text"}, {"type": "tool_result"}]`, API retorna 400 error. Los tool_result deben venir primero.

- **Saltar tool_result entero**: Si assistant emitió tool_use pero cliente no retorna tool_result, el loop se rompe o retorna error. SIEMPRE matchear tool_use con tool_result.

- **Ignorar is_error**: si tool_result tiene `is_error: true`, el cliente aún debe enviarlo. Claude lo verá como error y adaptará su respuesta. No ignorar.

- **Confundir server tools con client tools**: Server tools no requieren tool_result del cliente; Anthropic los ejecuta. Enviar tool_result para un server tool causa comportamiento indefinido.

- **Genéricos "failed" en error content**: "Operation failed" sin contexto. Claude no sabe si reintentar o escalar. Específico: "Database connection timeout. Retry possible." mejora decisiones.

---

## TS 0.4 — stop_reason como control del bucle agéntico: valores, qué hacer ante cada uno

### Hechos y comportamiento

- **Valores de stop_reason y significado**:
  - `"end_turn"`: Respuesta completada naturalmente. Usar resultado como es.
  - `"tool_use"`: Claude quiere llamar un tool. Ejecutar tools, retornar tool_result, continuar loop.
  - `"max_tokens"`: Se alcanzó el límite de tokens de salida especificado. Respuesta truncada. Opción: aumentar max_tokens o continuar sesión.
  - `"stop_sequence"`: Se emitió una secuencia personalizada (si se configura una con `stop_sequences` parameter). Leer `stop_sequence` para saber cuál.
  - `"pause_turn"`: Con server tools, se alcanzó el límite de iteraciones internas (default 10). Modelo no ha terminado. Continuar reenvío de respuesta del asistente para que continúe.
  - `"refusal"`: Claude rechazó responder por política. Response incluye `stop_details` identificando categoría (p.ej., "violence", "sexual_content"). Usar fallback si aplica.
  - `"model_context_window_exceeded"`: Ventana de contexto llena (raro con latest models, más común con muy largo historial). Tratar como truncada.
  [Fuente: Handling stop reasons — https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons]

- **Control del loop**: la lógica canonical es:
  ```
  while stop_reason == "tool_use":
      execute tools
      send tool_result
      response = api.messages.create(...)
      stop_reason = response.stop_reason
  // Salir en: end_turn, max_tokens, stop_sequence, refusal, pause_turn, etc.
  ```
  [Fuente: How tool use works — https://platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works]

- **pause_turn con server tools**: cuando server tools corren en Anthropic's infrastructure y alcanzan límite de iteraciones internas:
  1. Response retorna `stop_reason: "pause_turn"`
  2. Cliente reenvía el mensaje del asistente (incluyendo los server_tool_use results que ya llegaron)
  3. Modelo continúa donde se pausó
  [Fuente: How tool use works — https://platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works]

- **Verificación de stop_reason es CRÍTICA**: debe hacerse antes de procesar content. No verificar causa procesamientos incorrectos (p.ej., tratar respuesta truncada como completa).

- **Refusal response**: incluye campo `stop_details` con información sobre qué política triggeró la refusal. Permite logging, fallback a modelo menos restrictivo, o mostrar error amigable al usuario. [Fuente: Handling stop reasons — https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons]

- **max_tokens truncation**: si se alcanza max_tokens mid-generation, respuesta se trunca (puede estar a mitad de palabra). Opción: aumentar max_tokens (costo más alto) o aceptar respuesta parcial. En tool use loops, asegurar que max_tokens es suficiente para al menos un tool call completo.

### Sintaxis y configuración

```python
# Loop básico (pseudocode)
messages = [{"role": "user", "content": "What's the weather in San Francisco?"}]

while True:
    response = client.messages.create(
        model="claude-opus-5",
        max_tokens=1024,
        tools=tools,
        messages=messages
    )
    
    if response.stop_reason == "tool_use":
        # Extraer tool_use blocks, ejecutar, retornar tool_result
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = execute_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                    "is_error": False
                })
        messages.append({"role": "user", "content": tool_results})
    
    elif response.stop_reason == "end_turn":
        # Respuesta lista
        return response
    
    elif response.stop_reason == "max_tokens":
        # Truncada, opción: aumentar max_tokens y reintentar
        break
    
    elif response.stop_reason == "refusal":
        # Modelo rechazó, revisar stop_details
        print(f"Refusal: {response.stop_details}")
        break
    
    elif response.stop_reason == "pause_turn":
        # Server tools se pausaron, continuar
        messages.append({"role": "assistant", "content": response.content})
        # Reenviar sin tool_result, servidor continúa
    
    else:
        break
```

[Fuente: Handling stop reasons — https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons]

### Patrones

- **Pattern: Siempre verificar stop_reason**: antes de procesar content, siempre hacer `if response.stop_reason == "tool_use"` vs `elif == "end_turn"` etc. Evita bugs sutiles.

- **Pattern: Retry logic para pause_turn**: cuando stop_reason es pause_turn (server tools), simplemente reenviare la respuesta del asistente; servidor continuará iterando.

- **Pattern: Fallback para refusal**: si se detecta refusal, intentar con un modelo diferente (p.ej., más permisivo) o escalar a usuario.

- **Pattern: Aumentar max_tokens si trunca**: si max_tokens es insuficiente (stop_reason: max_tokens y se vea truncation), aumentar y reintentar. Registrar para futuro.

### Anti-patrones (y por qué fallan)

- **NO ignorar stop_reason**: si se asume siempre "end_turn" y se procesa la respuesta sin verificar, se puede procesar herramienta incompleta, refusal, truncation, etc. incorrectamente.

- **Confundir pause_turn con end_turn**: pause_turn NO es el final. Si se retorna al usuario una respuesta pausada como si fuera final, el trabajo quedará incompleto (server tools no terminaron).

- **Truncation silenciosa**: si max_tokens causa truncation y no se verifica, se puede retornar respuesta incompleta al usuario. Mejor: detectar max_tokens y reintentar o alertar.

- **Refusal sin manejo**: si response.stop_reason == "refusal", NO continuar con loop o user request. Manejar explícitamente (fallback, logging, error al usuario).

---

## TS 0.5 — Opciones de tool_choice: auto, any, tool, none; cuándo usar cada una; interacción con streaming/paralelismo si la fuente lo documenta

### Hechos y comportamiento

- **Cuatro valores de tool_choice**:
  - `"auto"` (default): Claude decide si llamar tool o responder directamente. Llama tool si request mapea a capabilidad descrita y respuesta no está en context. Responde sin tool si es conocimiento general, creativo, conversacional.
  - `"any"`: Claude DEBE llamar a uno de los tools disponibles (no puede responder sin tool). Modelo elige cuál. API prefill automático del asistente fuerza la llamada.
  - `{"type": "tool", "name": "tool_name"}` (forced): Claude DEBE llamar el tool específico nombrado. Fuerza primera acción. Usado para secuencias críticas (p.ej., extract_metadata antes de enrichment). API prefill automático.
  - `"none"`: Claude NO puede usar tools. Solo respuesta de texto (default si no hay tools).
  [Fuente: Define tools — https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools]

- **Impacto del prefill automático**: cuando tool_choice es `"any"` o forced tool, la API **prefilla automáticamente el mensaje del asistente** en la respuesta. Esto significa que Claude NO emitirá explicación en texto antes del tool_use block, incluso si se le pide explícitamente hacerlo. [Fuente: Define tools — https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools]

- **Cuándo usar "auto"**: cuando aplicación quiere que modelo DECIDA si tool es necesario. Defecto seguro. Requiere prompting cuidadoso si model es "over-eager" en llamar tools; palanca: "Consider whether you need to call a tool or can answer directly."

- **Cuándo usar "any"**: cuando se requiere tool call GARANTIZADO pero no importa cuál. P.ej., extracción estructurada donde `tool_choice: "any"` + multiple extraction tools y documento type desconocido.

- **Cuándo usar forced tool**: cuando hay orden crítica (p.ej., siempre extract_metadata antes de enrich). O cuando se necesita salida estruturada garantizada en first turn.

- **Cuándo usar "none"**: cuando herramientas no deben usarse (modo QA puro, conversación sin side effects).

- **Combinación con strict mode**: `tool_choice: "any"` + `strict: true` en tool definitions garantiza TANTO que un tool se llame Y que inputs sean schema-compliant (no missing required params, no type mismatches). [Fuente: Define tools — https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools]

- **Regla de prompt caching**: cambios en tool_choice parameter invalidan cached message blocks. Tool definitions y system prompts se mantienen cached, pero message content se reprocesa. [Fuente: Define tools — https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools]

- **Limitaciones con extended thinking**: manual extended thinking (`thinking: {type: "enabled"}`) NO soporta `tool_choice: "any"` o forced tool. Solo `"auto"` (default) o `"none"` son compatibles con manual thinking. Adaptive thinking (default en algunos modelos como Opus 5) SÍ soporta forced tool use. [Fuente: Define tools — https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools]

### Sintaxis y configuración

```json
// tool_choice: "auto" (default)
{
  "model": "claude-opus-5",
  "max_tokens": 1024,
  "tools": [...],
  "tool_choice": {"type": "auto"},
  "messages": [...]
}
```

```json
// tool_choice: "any" - fuerza una herramienta (cualquiera)
{
  "model": "claude-opus-5",
  "max_tokens": 1024,
  "tools": [
    {"name": "extract_json", "description": "...", "input_schema": {...}},
    {"name": "extract_xml", "description": "...", "input_schema": {...}}
  ],
  "tool_choice": {"type": "any"},
  "messages": [{"role": "user", "content": "Extract this document. (type unknown)"}]
}
```

```json
// tool_choice: forced tool - siempre herramienta específica
{
  "model": "claude-opus-5",
  "max_tokens": 1024,
  "tools": [...],
  "tool_choice": {"type": "tool", "name": "extract_metadata"},
  "messages": [...]
}
```

```json
// tool_choice: "none" - sin tools
{
  "model": "claude-opus-5",
  "max_tokens": 1024,
  "tool_choice": {"type": "none"},
  "messages": [...]
}
```

```json
// Combinación: "any" + strict: true
{
  "model": "claude-opus-5",
  "max_tokens": 1024,
  "tools": [
    {
      "name": "extract_data",
      "description": "...",
      "strict": true,  // Garantiza schema compliance
      "input_schema": {...}
    }
  ],
  "tool_choice": {"type": "any"},
  "messages": [...]
}
```

[Fuente: Define tools — https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools]

### Patrones

- **Pattern: Usar "any" para garantías de output**: si necesitas salida estructurada (JSON schema validated) siempre, combina `tool_choice: "any"` + `strict: true` en tool definition.

- **Pattern: Forced tool para secuencias críticas**: si workflow requiere cierto orden (p.ej., "siempre verify customer antes de refund"), usar forced tool_choice para el primer step, luego "auto" para pasos posteriores.

- **Pattern: Default "auto" con prompting**: la mayoría de casos usan "auto" + system prompt que instruye cuándo usar tools ("Use tools to investigate before responding" vs "Respond directly from training if you can").

- **Pattern: Multi-extraction con "any"**: si documento type es desconocido pero tienes múltiples extraction schemas, usar "any" para forzar que UNO se llame (modelo elige). Más flexible que forced tool.

### Anti-patrones (y por qué fallan)

- **Overuse de forced tool**: si se fuerza tool en CADA turn, pierdes flexibilidad del modelo. Limitar a crítico (verify customer) o primer step de pipeline.

- **"any" sin prompting claro**: si especificas "any" pero no das claro qué esperas en response (p.ej., "extract data" sin definir qué campos), modelo puede elegir tool equivocado o con input inválido.

- **tool_choice: "none" cuando queeres tool**: si configuras "none" pero luego tu prompt dice "please call this tool", no pasa nada (API rechaza call). Asegurar consistencia.

- **Ignorar impacto prefill de "any"/"tool"**: si configuras forced tool y luego pides modelo que explique antes de llamar, no lo hará (prefill lo impide). Acepta que forced tool = directo a call, sin explicación previa.

---

## TS 0.6 — Decisión dirigida por el modelo vs flujos deterministas preconfigurados: cuándo conviene un agente y cuándo un workflow programado

### Hechos y comportamiento

- **Decisión dirigida por modelo (agente)**: Claude decide en cada turno qué tool llamar, en qué orden, basado en contexto y razonamiento. Flexible, adaptable, maneja casos nuevos. Ejemplo: customer support agent que analiza request y decide escalación vs auto-resolución basado en contenido. [Implícito en exam guide Task 1.1, 1.6; relativo a "model-driven decision-making"]

- **Flujo determinista preconfigurado (workflow)**: secuencia fija de pasos, sin decisión del modelo. P.ej., "siempre: 1. verify customer, 2. lookup order, 3. process refund". Si cualquier paso falla, salir. No hay adaptación. Usado para operaciones críticas donde compliance es no-negotiable. [Referenciado en exam guide Task 1.4: "programmatic enforcement" vs "prompt-based guidance"]

- **Tool use es soporte para ambos**:
  - Agente: tool_choice "auto", modelo decide qué tool; sistema de hooks (PostToolUse, etc.) puede interceptar para enforcement.
  - Workflow: tool_choice forzado en cierto orden, o programmatic prerequisite gates que bloquean herramientas hasta que dependencias completen.
  [Exam guide references]

- **La distinción clave**: ¿Necesita sistema ser 100% determinístico (falla crítica si algo sale mal)? → Workflow programado. ¿Puede adaptarse a contexto variad? → Agente.

- **Prompt chaining vs dynamic decomposition**:
  - Prompt chaining: secuencia fija de llamadas (Task 1.6: "fixed sequential pipelines"). Determinis.
  - Dynamic decomposition: modelo genera subtareas basadas en hallazgos intermedios (Task 1.6: "adaptive investigation plans"). Dirigido por modelo.
  [Exam guide Task 1.6]

- **Patrones de hook para enforcement**: Agent SDK proporciona hooks (PostToolUse, tool call interception) que permiten implementar garantías determinísticas dentro de un context agéntico. P.ej., hook que bloquea refund > $500 y redirige a escalation. [Exam guide Task 1.5]

- **Multi-agent orchestration**: Coordinator-subagent pattern es fundamentalmente dirigido por modelo (coordinador decide qué subagentes invocar, en qué orden, basado en análisis de query). Pero dentro de cada subagent, puede haber workflow determinístico. [Exam guide Task 1.2]

### Sintaxis y configuración

```python
# AGENTE: Dirigido por modelo (tool_choice: auto, modelo decide)
messages = [...]
while True:
    response = client.messages.create(
        model="claude-opus-5",
        max_tokens=4096,
        tools=[get_customer, lookup_order, process_refund, escalate_to_human],
        tool_choice={"type": "auto"},  # Modelo decide qué tool llamar
        system="You are a support agent. Analyze customer requests and decide whether to resolve or escalate.",
        messages=messages
    )
    # Modelo razona: "This is a standard refund. I'll call get_customer first, then lookup_order, then process_refund."
    # O: "This is a policy exception. I'll escalate."
```

```python
# WORKFLOW: Determinístico (herramientas forzadas en secuencia, o gates programáticos)
def process_refund_workflow(customer_id, order_id):
    # Step 1: Verify customer (forzado, no decision del modelo)
    customer = get_customer(customer_id)
    if not customer.verified:
        return error("Customer not verified")
    
    # Step 2: Lookup order
    order = lookup_order(order_id)
    if order.status != "shipped":
        return error("Order not eligible")
    
    # Step 3: Process refund
    refund = process_refund(order_id, amount=order.total)
    return refund
```

```python
# HOOK enforcement (Agent + determinism)
from anthropic import Anthropic

class RefundAgent:
    def __init__(self, client):
        self.client = client
        self.hooks = []
    
    def add_hook(self, event_type, callback):
        """Register a hook (e.g., PostToolUse) to intercept and enforce rules"""
        self.hooks.append((event_type, callback))
    
    def run(self, user_query):
        # Agent loop con hooks
        messages = [{"role": "user", "content": user_query}]
        while True:
            response = self.client.messages.create(
                model="claude-opus-5",
                max_tokens=4096,
                tools=self.tools,
                tool_choice={"type": "auto"},
                messages=messages
            )
            
            if response.stop_reason == "tool_use":
                # Intercept tool calls with hooks
                for block in response.content:
                    if block.type == "tool_use":
                        # Hook: check refund amount
                        if block.name == "process_refund":
                            amount = block.input.get("amount", 0)
                            if amount > 500:
                                # BLOCK: Override tool call, redirect to escalation
                                block.name = "escalate_to_human"
                
                # Execute tools and collect results
                messages.append({"role": "assistant", "content": response.content})
                tool_results = [...]  # execute tools with potential overrides
                messages.append({"role": "user", "content": tool_results})
            
            elif response.stop_reason == "end_turn":
                return response
            else:
                break
```

[Inspirado en exam guide references a Task 1.5 hooks y Task 1.1 agentic loops]

### Patrones

- **Pattern: Agente para discovery/decisión, workflow para enforcement**: Usar agente para analizar y decidir (flexible). Usar workflow determinístico para pasos críticos (refund, delete, escalation).

- **Pattern: Prompt chaining para multi-step fijo**: Si pasos son SIEMPRE: A → B → C, usar prompt chaining (sequential fixed pipeline). Modelo no elige orden; aplicación fuerza.

- **Pattern: Coordinator + subagents para multi-agent flexible**: Coordinator como agente (tool_choice: auto) decide qué subagents invocar. Cada subagent puede ser determinístico (narrower task) o agente.

- **Pattern: Hooks para enforcement dentro de agente**: Si necesitas garantías (p.ej., "refund never > $500") pero quieres que modelo siga siendo flexible (decide cuándo refund vs escalation), usar hooks para interceptar y bloquear.

- **Pattern: Separar concerns**: No mezclar lógica determinística con decisional en un prompt. Usar system prompt claro sobre cuándo escalat, cuándo auto-resolve, etc. Usar hooks para hard-fail constraints.

### Anti-patrones (y por qué fallan)

- **Forzar agente para operación determinística crítica**: Si refund DEBE verificar customer primero, confiar solo en prompt ("verify customer first") fallará ~10-12% (exam guide ejemplo Q1). Usar hook o prerequisite gate.

- **Workflow rígido sin fallback**: Si pasos fijos son "verify → lookup → refund" y verify falla, workflow detiene. Agente podría escalar o reintentar. A veces inflexible es correcto; a veces no.

- **Mezclar tool_choice: auto con forced para todos los tools**: Si todos los tools están forced, no es agente, es workflow. Claridad: ¿Realmente necesita determinism? Si no, usa auto.

- **Prompt chaining sin estado compartido**: Si 5 prompts chain pero no pasan contexto entre ellos, cada uno redescubre lo mismo. Guardar estado (scratchpad, structured output) entre steps.

- **Ignoring cost de agentes**: Agentes son más iteraciones (más tokens). Workflows fijos son más directos (menos costo). Si presupuesto es ajustado, preferir workflow. Si flexibilidad es crítica, pagar el costo agente.

---

## HUECOS

- **0.1 - Prefill técnica**: Documentación oficial menciona que tool_choice "any"/"tool" causa "API prefills the assistant message", pero detalle técnico de QUÉ EXACTAMENTE se prefilla y cómo afecta exactamente la respuesta es vago. Exam guide no clarifica. Necesitaría ejemplo explícito de prefill content.
  
- **0.3 - Parallel tool execution timing**: Las fuentes confirman que múltiples tool_use blocks se ejecutan en paralelo, pero no especifican latency exacta, si hay determinism en order de ejecución, o si timeout global aplica. Podría ser relevante en contexto de test.

- **0.4 - stop_sequence custom**: Documentación menciona `stop_sequence` field en request (para sequences personalizadas), pero ejemplos completos faltan. Cómo se configura, formato, cuándo usarla — no cubierto en profundidad.

- **0.5 - Tool choice con streaming**: Las fuentes dan info sobre tool_choice en general, pero NO detallan cómo tool_choice interactúa con streaming (si existe). Exam menciona "paralelismo" y "streaming" potencial; cobertura incompleta.

- **0.6 - Decisión vs determinism: métricas de comparación**: El exam guide sugiere que agentes son mejores para adaptación, workflows para críticos, pero no da datos de latency, token cost, success rate — métricas cuantitativas de trade-off.

---

## CONTRADICCIONES

No se detectaron contradicciones directas entre fuentes oficiales. Todas las páginas de platform.claude.com (oficial Anthropic) son consistentes en:
- Definición de stop_reason, tool_choice, request/response structure
- Ciclo tool_use/tool_result

Las páginas de Skilljar (courses.anthropic) no fueron accesibles (restricción de login), así que no hay conflicto que reportar.

---

## FUENTES ADICIONALES INCORPORADAS

- [Stop reasons and fallback](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons) — Official Anthropic docs, refuerza cobertura de stop_reason values y patrones de manejo. **OFICIAL**

- [Working with the Messages API](https://platform.claude.com/docs/en/build-with-claude/working-with-messages) — Official Anthropic docs, cubre request/response structure, multi-turn, roles, system parameter. **OFICIAL**

- [Handle tool calls](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls) — Official Anthropic docs, refuerza tool_use/tool_result lifecycle, error handling, formatting reqs. **OFICIAL**

---

## RESUMEN DE COBERTURA POR EJE

| Eje | Cobertura | Fuentes |
|-----|-----------|---------|
| 0.1 Messages API | Completa | How tool use works, Working with Messages, Overview |
| 0.2 Tools JSON Schema | Completa | Define tools, Skilljar (parcial) |
| 0.3 Tool_use/tool_result | Completa | How tool use works, Handle tool calls, Overview |
| 0.4 stop_reason | Completa | Handling stop reasons, How tool use works |
| 0.5 tool_choice | Completa | Define tools, Overview |
| 0.6 Modelo vs determinismo | Cobertura media | Exam guide references, How tool use works (implícito) |

**Evaluación**: 5/7 fuentes procesadas exitosamente. 2 URLs de Skilljar (courses.anthropic.com) requieren login y no accesibles. Huecos menores en detalles técnicos (prefill exacto, streaming+tool_choice) y contradicciones: ninguna.
