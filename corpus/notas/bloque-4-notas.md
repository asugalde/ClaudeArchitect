# Notas de extracción — Bloque 4: Agent SDK: arquitectura agéntica y orquestación
Fecha: 2026-08-05 · Fuentes procesadas: 8/10

---

## TS 1.1 — Design and implement agentic loops for autonomous task execution

### Hechos y comportamiento

- El agentic loop es el ciclo fundamental del Agent SDK que ejecuta iterativamente: Claude evalúa el estado → responde con tool calls o texto final → el SDK ejecuta herramientas → devuelve resultados a Claude → repite hasta que no hay tool calls.
  [Fuente: How the agent loop works — https://code.claude.com/docs/en/agent-sdk/agent-loop]

- **Lifecycle de cinco pasos:**
  1. Recibir prompt (Claude recibe prompt, system prompt, tool definitions, conversation history; SDK emite `SystemMessage` con subtype `"init"`)
  2. Evaluar y responder (Claude determina cómo proceder: puede devolver texto, solicitar tool calls, o ambos; SDK emite `AssistantMessage`)
  3. Ejecutar herramientas (SDK ejecuta cada tool solicitado; los resultados alimentan el siguiente turno a Claude)
  4. Repetir (pasos 2 y 3 continúan hasta que Claude produce respuesta sin tool calls)
  5. Retornar resultado (SDK emite `AssistantMessage` final + `ResultMessage` con texto, uso de tokens, costo, session ID)
  [Fuente: How the agent loop works — https://code.claude.com/docs/en/agent-sdk/agent-loop]

- Un **turn** es una ronda completa: Claude produce salida con tool calls, el SDK ejecuta esas herramientas, los resultados se devuelven a Claude automáticamente (todo sin ceder control al código). Los turns continúan hasta que Claude produce output sin tool calls.
  [Fuente: How the agent loop works — https://code.claude.com/docs/en/agent-sdk/agent-loop]

- **Message types en el loop:**
  - `SystemMessage`: eventos de ciclo de vida de sesión (subtype `"init"`, `"compact_boundary"`, `"informational"`, `"worker_shutting_down"`)
  - `AssistantMessage`: emitido después de cada respuesta de Claude, incluye bloques de texto y tool calls
  - `UserMessage`: emitido después de cada ejecución de tool con el resultado devuelto a Claude
  - `StreamEvent`: solo cuando partial messages están habilitados; contiene raw API streaming events
  - `ResultMessage`: marca el fin del loop; contiene texto final, token usage, costo, session ID, y `subtype` (success, error_max_turns, error_max_budget_usd, error_during_execution, error_max_structured_output_retries)
  [Fuente: How the agent loop works — https://code.claude.com/docs/en/agent-sdk/agent-loop]

- **stop_reason handling:** El loop continúa mientras Claude produzca tool calls. La decisión de continuar o parar se basa en la respuesta de Claude (si incluye tool calls → continúa; si es solo texto → para). No se debe analizar natural language signals ni checking for assistant text content.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 140-142]

- Cada ciclo (turn) con tool calls cuenta hacia `max_turns` / `maxTurns`. Un límite de `max_turns=2` detiene antes de ciertos pasos. Sin límites, el loop continúa hasta que Claude termina.
  [Fuente: How the agent loop works — https://code.claude.com/docs/en/agent-sdk/agent-loop]

- **Anti-patrón:** Parsing natural language signals para determinar terminación del loop, usar arbitrary iteration caps como mecanismo principal de stopping, o checking for assistant text content como indicador de completion. Estos fallan porque la decisión correcta la toma Claude basándose en stop_reason de su respuesta.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 140-142]

- **Tool execution flow:** Cuando Claude solicita múltiples tool calls en un single turn, el SDK puede ejecutarlos concurrentemente o secuencialmente según el tool. Tools de solo lectura (Read, Glob, Grep, MCP read-only) se ejecutan concurrentemente. Tools que modifican estado (Edit, Write, Bash) se ejecutan secuencialmente para evitar conflictos.
  [Fuente: How the agent loop works — https://code.claude.com/docs/en/agent-sdk/agent-loop]

- El **context window** acumula a lo largo de turns (nunca se resetea dentro de una sesión). Todo se acumula: system prompt, tool definitions, conversation history, tool inputs, tool outputs. El contenido estático se cachea automáticamente (prompt cache).
  [Fuente: How the agent loop works — https://code.claude.com/docs/en/agent-sdk/agent-loop]

### Sintaxis y configuración

```python
# Python: Estructura básica de query() con opciones de loop control
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

async def main():
    try:
        async for message in query(
            prompt="Find and fix bugs in auth module",
            options=ClaudeAgentOptions(
                allowed_tools=["Read", "Edit", "Bash", "Glob", "Grep"],  # auto-approve
                setting_sources=["project"],  # Load CLAUDE.md, skills
                max_turns=30,  # Maximum tool-use round trips
                effort="high",  # "low", "medium", "high", "xhigh", "max"
            ),
        ):
            if isinstance(message, ResultMessage):
                if message.subtype == "success":
                    print(message.result)
                elif message.subtype == "error_max_turns":
                    print(f"Hit turn limit. Resume session {message.session_id}")
                print(f"Cost: ${message.total_cost_usd:.4f}")
    except Exception as error:
        print(f"Session ended: {error}")

asyncio.run(main())
```
[Fuente: How the agent loop works — https://code.claude.com/docs/en/agent-sdk/agent-loop]

```typescript
// TypeScript: Estructura de query()
import { query } from "@anthropic-ai/claude-agent-sdk";

let sessionId: string | undefined;

try {
  for await (const message of query({
    prompt: "Find and fix bugs in auth module",
    options: {
      allowedTools: ["Read", "Edit", "Bash", "Glob", "Grep"],
      settingSources: ["project"],
      maxTurns: 30,
      effort: "high"
    }
  })) {
    if (message.type === "system" && message.subtype === "init") {
      sessionId = message.session_id;
    }
    if (message.type === "result") {
      if (message.subtype === "success") {
        console.log(message.result);
      } else if (message.subtype === "error_max_turns") {
        console.log(`Hit turn limit. Resume session ${sessionId}`);
      }
      console.log(`Cost: $${message.total_cost_usd.toFixed(4)}`);
    }
  }
} catch (error) {
  console.log(`Session ended: ${error}`);
}
```
[Fuente: How the agent loop works — https://code.claude.com/docs/en/agent-sdk/agent-loop]

**Message type checking (Python):**
```python
from claude_agent_sdk import AssistantMessage, ResultMessage, ToolUseBlock

# Check message types
if isinstance(message, AssistantMessage):
    for block in message.content:
        if isinstance(block, ToolUseBlock):
            print(f"Tool called: {block.name}")
if isinstance(message, ResultMessage):
    print(f"Finished: {message.subtype}")
```
[Fuente: How the agent loop works — https://code.claude.com/docs/en/agent-sdk/agent-loop]

**Message type checking (TypeScript):**
```typescript
if (message.type === "assistant") {
  for (const block of message.message.content) {
    if (block.type === "tool_use") {
      console.log(`Tool called: ${block.name}`);
    }
  }
}
if (message.type === "result") {
  console.log(`Finished: ${message.subtype}`);
}
```
[Fuente: How the agent loop works — https://code.claude.com/docs/en/agent-sdk/agent-loop]

### Patrones

- **Model-driven decision-making:** Claude razones sobre qué tool llamar a continuación basándose en el contexto de la conversación. Esto es diferente de pre-configured decision trees o tool sequences.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 134]

- **Loop control basado en respuesta:** El SDK inspecciona automáticamente la respuesta de Claude (si contiene tool calls → continúa; si es solo texto → para). No se requiere parsing manual de natural language.
  [Fuente: How the agent loop works — https://code.claude.com/docs/en/agent-sdk/agent-loop]

- **Turn-by-turn context accumulation:** Tool results se añaden automáticamente a conversation history después de cada turn, permitiendo que Claude razones sobre nuevos hechos.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 138-139]

### Anti-patrones (y por qué fallan)

- **Parsing natural language signals para terminar:** Buscar frases como "I'm done" en la respuesta de Claude. Falla porque los agentes no siempre producen estas señales; mejor: confiar en stop_reason.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 140-142]

- **Arbitrary iteration caps como mecanismo principal:** Limitar simplemente a N iteraciones sin considerar si el task está completo. Falla porque arbitrariamente limita tareas legítimas que necesitan más pasos.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 140-142]

- **Checking for assistant text content:** Asumir que si hay texto en la respuesta, el task acabó. Falla porque Claude puede devolver tanto texto COMO tool calls en el mismo turn.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 140-142]

---

## TS 1.2 — Orchestrate multi-agent systems with coordinator-subagent patterns

### Hechos y comportamiento

- **Hub-and-spoke architecture:** Un coordinator agent maneja toda inter-subagent communication, error handling, e information routing. Los subagents no se comunican entre sí directamente; todo fluye a través del coordinator.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 146-147]

- **Subagent context isolation:** Los subagents operan con contexto aislado; no heredan automáticamente la conversation history del coordinator. Solo reciben lo que se pasa explícitamente en el prompt del Agent tool call.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 148-149]

- **Coordinator responsibilities:**
  1. Task decomposition: analizar query requirements
  2. Dynamic subagent selection: decidir cuáles subagents invocar basándose en complejidad de la query
  3. Result aggregation: recolectar outputs de subagents
  4. Iterative refinement: evaluar síntesis output para gaps, re-delegar con targeted queries, re-invocar synthesis hasta cobertura suficiente
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 150-164]

- **Anti-patrón: overly narrow task decomposition.** Si el coordinator descompone tareas demasiado estrechamente, puede resultar en incomplete coverage de broad research topics. Mejor: especificar research goals amplios y dejar que subagents decidan cómo investigar dentro de esos límites.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 155-156]

- **Parallel execution:** En la arquitectura de Anthropic's multi-agent research system, el lead agent spawna 3–5 subagents concurrentemente en lugar de secuencialmente. Además, cada subagent ejecuta 3+ tools en paralelo. Esto redujo research time hasta 90% para queries complejas.
  [Fuente: How we built our multi-agent research system — https://www.anthropic.com/engineering/built-multi-agent-research-system]

- **Delegation strategy:** El lead agent descompone tasks en subtasks con especificaciones explícitas: objetivos, formatos de output, tool guidance, y límites claros. Instrucciones vagas causaban duplicación; los agentes necesitan detailed task descriptions para dividir labor efectivamente.
  [Fuente: How we built our multi-agent research system — https://www.anthropic.com/engineering/built-multi-agent-research-system]

- **Iterative refinement loops:** El coordinator evalúa synthesis output para gaps, re-delega a search y analysis subagents con targeted queries, y re-invoca synthesis hasta que coverage es suficiente.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 162-164]

- **Routing all communication through coordinator:** Esto mantiene observability, consistent error handling, y controlled information flow. Todos los subagent calls deben fluir a través del coordinator.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 165-166]

### Sintaxis y configuración

```python
# Python: Definir y invocar subagents vía coordinator
from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition

async def main():
    async for message in query(
        prompt="Research AI safety and prepare a comprehensive report",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Grep", "Glob", "Agent"],  # Agent para subagent invocation
            agents={
                "search-agent": AgentDefinition(
                    description="Web search specialist for finding authoritative sources",
                    prompt="You are a research specialist. Find and catalog credible sources...",
                    tools=["WebSearch", "WebFetch"],
                ),
                "analysis-agent": AgentDefinition(
                    description="Document analysis specialist",
                    prompt="You analyze documents and extract key findings...",
                    tools=["Read", "Grep", "Glob"],
                ),
                "synthesis-agent": AgentDefinition(
                    description="Synthesis specialist that combines findings",
                    prompt="You synthesize findings from multiple sources...",
                    tools=["Read", "Write"],
                ),
            },
        ),
    ):
        if hasattr(message, "result"):
            print(message.result)
```
[Fuente: Subagents in the SDK — https://code.claude.com/docs/en/agent-sdk/subagents]

```typescript
// TypeScript: Estructura de agents dictionary
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Research AI safety and prepare comprehensive report",
  options: {
    allowedTools: ["Read", "Grep", "Glob", "Agent"],
    agents: {
      "search-agent": {
        description: "Web search specialist for finding authoritative sources",
        prompt: "You are a research specialist. Find and catalog credible sources...",
        tools: ["WebSearch", "WebFetch"],
      },
      "analysis-agent": {
        description: "Document analysis specialist",
        prompt: "You analyze documents and extract key findings...",
        tools: ["Read", "Grep", "Glob"],
      },
      "synthesis-agent": {
        description: "Synthesis specialist that combines findings",
        prompt: "You synthesize findings from multiple sources...",
        tools: ["Read", "Write"],
      },
    }
  }
})) {
  if ("result" in message) console.log(message.result);
}
```
[Fuente: Subagents in the SDK — https://code.claude.com/docs/en/agent-sdk/subagents]

### Patrones

- **Dynamic subagent selection:** El coordinator NO siempre rutea a través del pipeline completo. En lugar de eso, analiza requirements y selecciona dinámicamente cuáles subagents invocar.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 158-159]

- **Scope partitioning:** Asignar distinct subtopics o source types a cada subagent para minimizar duplicación.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 160-161]

- **Explicit task specification:** Proporcionar research goals y quality criteria en lugar de step-by-step procedural instructions, permitiendo adaptability del subagent.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 184-185]

### Anti-patrones (y por qué fallan)

- **Always routing through full pipeline:** Invocar todos los subagents incluso cuando la query es simple. Falla porque incurre costo innecesario y latencia.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 158-159]

- **Vague delegation instructions:** Diciendo "research AI safety" sin especificar objectives, output format, o tool guidance. Falla porque subagents no saben cómo dividir labor, resultando en duplicación.
  [Fuente: How we built our multi-agent research system — https://www.anthropic.com/engineering/built-multi-agent-research-system]

---

## TS 1.3 — Configure subagent invocation, context passing, and spawning

### Hechos y comportamiento

- **Agent tool:** El mecanismo para spawning subagents es el **Agent tool** (renamed from "Task" en SDK v2.1.63). Invocar subagents requiere que `allowedTools` incluya `"Agent"`.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 169-170]
  [Fuente: Subagents in the SDK — https://code.claude.com/docs/en/agent-sdk/subagents]

- **Context must be explicit:** Los subagents no heredan automáticamente parent context ni memory entre invocaciones. Todo context debe ser explícitamente proporcionado en el prompt del Agent tool call.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 171-172]

- **What subagents inherit:**
  - Su propio system prompt (`AgentDefinition.prompt`)
  - El prompt del Agent tool call
  - Project CLAUDE.md (si `settingSources` lo incluye)
  - Tool definitions (subset en `tools` field)
  [Fuente: Subagents in the SDK — https://code.claude.com/docs/en/agent-sdk/subagents]

- **What subagents DON'T inherit:**
  - Parent conversation history
  - Parent tool results
  - Parent system prompt
  - Preloaded skill content (a menos que listed en `AgentDefinition.skills`)
  [Fuente: Subagents in the SDK — https://code.claude.com/docs/en/agent-sdk/subagents]

- **Parallel spawning:** Para ejecutar múltiples subagents en paralelo, el coordinator emite múltiples Agent tool calls en una single response (single turn), no a través de turnos separados.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 182-183]

- **AgentDefinition configuration:** Definir subagents requires:
  - `description` (string, required): Natural language description de cuándo usar este agent
  - `prompt` (string, required): System prompt del agent defining role y behavior
  - `tools` (string[], optional): Array de allowed tool names; omitir = hereda todos los available tools
  - `disallowedTools` (string[], optional): Tools a remover
  - `model` (string, optional): Model override ('fable', 'opus', 'sonnet', 'haiku', 'inherit', o full model ID)
  - `skills` (string[], optional): Skill names a preload
  - `memory` ('user' | 'project' | 'local', optional): Memory source
  - `mcpServers` (array, optional): MCP servers available
  - `maxTurns` (number, optional): Max agentic turns
  - `background` (boolean, optional): Run as background task
  - `effort` ('low' | 'medium' | 'high' | 'xhigh' | 'max', optional): Reasoning effort
  [Fuente: Subagents in the SDK — https://code.claude.com/docs/en/agent-sdk/subagents]

- **Fork-based session management:** Para explorar divergent approaches desde un shared analysis baseline, usar `fork_session=true` (Python) / `forkSession: true` (TypeScript).
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 176-177]

- **Structured data formats para context passing:** Separar content from metadata (source URLs, document names, page numbers) cuando passing context entre agents para preservar attribution.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 180-181]

### Sintaxis y configuración

```python
# Python: AgentDefinition con full configuración
from claude_agent_sdk import AgentDefinition

code_reviewer = AgentDefinition(
    description="Expert code review specialist. Use for quality, security reviews.",
    prompt="""You are a code review specialist with expertise in security and performance.
When reviewing code:
- Identify security vulnerabilities
- Check for performance issues
- Verify adherence to coding standards

Be thorough but concise.""",
    tools=["Read", "Grep", "Glob"],  # Read-only tools
    model="sonnet",
    maxTurns=20,
    effort="high",
)

# Passing complete findings en agent prompt
web_search_results = "URL1: ..., URL2: ..., ..."
synthesis_prompt = f"""Synthesize these findings from search and analysis:

Search results:
{web_search_results}

Document analysis:
...

Create comprehensive report with proper attribution."""
```
[Fuente: Subagents in the SDK — https://code.claude.com/docs/en/agent-sdk/subagents]

```typescript
// TypeScript: Programmatic subagent definition
const codeReviewer: AgentDefinition = {
  description: "Expert code review specialist. Use for quality, security reviews.",
  prompt: `You are a code review specialist with expertise in security and performance.
When reviewing code:
- Identify security vulnerabilities
- Check for performance issues
- Verify adherence to coding standards

Be thorough but concise.`,
  tools: ["Read", "Grep", "Glob"],
  model: "sonnet",
  maxTurns: 20,
  effort: "high",
};

// Passing complete findings in agent prompt
const webSearchResults = "URL1: ..., URL2: ...";
const synthesisPrompt = `Synthesize these findings from search and analysis:

Search results:
${webSearchResults}

Document analysis:
...

Create comprehensive report with proper attribution.`;
```
[Fuente: Subagents in the SDK — https://code.claude.com/docs/en/agent-sdk/subagents]

**Detectar subagent invocation (Python):**
```python
from claude_agent_sdk import ToolUseBlock

for block in message.content:
    if isinstance(block, ToolUseBlock) and block.name in ("Task", "Agent"):
        subagent_type = block.input.get("subagent_type")
        print(f"Subagent invoked: {subagent_type}")
```
[Fuente: Subagents in the SDK — https://code.claude.com/docs/en/agent-sdk/subagents]

**Detectar subagent invocation (TypeScript):**
```typescript
for (const block of msg.message?.content ?? []) {
  if (block.type === "tool_use" && (block.name === "Task" || block.name === "Agent")) {
    console.log(`Subagent invoked: ${block.input.subagent_type}`);
  }
}
```
[Fuente: Subagents in the SDK — https://code.claude.com/docs/en/agent-sdk/subagents]

### Patrones

- **Explicit context injection:** Incluir complete findings (web search results, document analysis outputs) directamente en el subagent prompt en lugar de depender de automatic context inheritance.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 178-179]

- **Structured output formats:** Usar JSON o structured text para separar claims from evidence excerpts, source URLs, document names, page numbers. Esto preserva attribution cuando la synthesis agent combina findings.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 180-181]

- **Multiple Agent tool calls en single turn:** El coordinator emite múltiples Agent tool calls en una single response para parallelization.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 182-183]

- **Task specification over procedural instructions:** Especificar research goals y quality criteria en lugar de step-by-step instrucciones, permitiendo subagent adaptability.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 184-185]

### Anti-patrones (y por qué fallan)

- **Assuming automatic context inheritance:** Esperar que un subagent tenga access a prior conversation history del coordinator. Falla: subagents tienen isolated context; todo debe pasarse explícitamente.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 171-172]

- **Vague task descriptions en Agent tool calls:** Diciendo "research this" sin especificar objectives, expected format, o scope. Falla: el subagent no sabe qué investigar concretamente.
  [Fuente: How we built our multi-agent research system — https://www.anthropic.com/engineering/built-multi-agent-research-system]

---

## TS 1.4 — Implement multi-step workflows with enforcement and handoff patterns

### Hechos y comportamiento

- **Programmatic enforcement vs. prompt-based guidance:** Hay una distinción crítica. Programmatic enforcement (hooks, prerequisite gates) proporciona deterministic compliance; prompt-based guidance sola tiene non-zero failure rate.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 192-195]

- **When deterministic compliance is required:** Para critical business logic donde errors tienen consecuencias financieras o de seguridad (p. ej., customer verification antes de refunds), prompt instructions alone no son suficientes.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 194-195]

- **Structured handoff protocols:** Para mid-process escalation, incluir customer details, root cause analysis, recommended actions. Esto da al human agent contexto sin requerir acceso al conversation transcript.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 196-197]

- **Multi-concern decomposition:** Descomponer customer requests multi-concern en distinct items, luego investigar cada uno en paralelo using shared context antes de synthesizing unified resolution.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 202-203]

### Sintaxis y configuración

**Programmatic prerequisite enforcement con PreToolUse hook:**
```python
from claude_agent_sdk import query, ClaudeAgentOptions, PreToolUseHook

def prerequisite_gate_hook(hook_input) -> dict | None:
    """Block process_refund until get_customer has been called"""
    if hook_input.tool_name == "process_refund":
        # Check if get_customer was called earlier in conversation
        if not check_prior_tool_executed("get_customer"):
            return {
                "allowed": False,
                "error": "Customer verification required. Call get_customer first."
            }
    return {"allowed": True}

async def main():
    async for message in query(
        prompt="Help customer with their refund request",
        options=ClaudeAgentOptions(
            allowed_tools=["get_customer", "lookup_order", "process_refund"],
            hooks={
                "PreToolUse": [
                    {
                        "handler": prerequisite_gate_hook,
                    }
                ]
            },
        ),
    ):
        pass
```
[Basado en: Exam Guide Oficial y Agent SDK hooks documentation]

**Structured handoff summary (Python):**
```python
handoff_summary = {
    "customer_id": "CUST-12345",
    "root_cause": "Damaged package on arrival - photo evidence provided",
    "refund_amount": "$85.00",
    "recommended_action": "Process full refund + send replacement",
    "additional_context": "Customer has been with us 5 years, high lifetime value"
}

# Include en escalation message
escalation_prompt = f"""Escalating to human agent:
{json.dumps(handoff_summary, indent=2)}

Customer message: "Please help, my package arrived broken."
"""
```
[Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 204-205]

### Patrones

- **Prerequisite gates:** Implementar programmatic prerequisites que bloquean downstream tool calls hasta que prerequisite steps hayan completado (e.g., blocking process_refund hasta que get_customer haya returnado verified customer ID).
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 199-201]

- **Parallel investigation:** Descomponer multi-concern requests en distinct items, investigar cada uno en paralelo usando shared context, luego synthesizar unified resolution.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 202-203]

- **Structured escalation:** Compilar structured handoff summaries incluyendo customer ID, root cause, refund amount, recommended action.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 204-205]

### Anti-patrones (y por qué fallan)

- **Relying on prompt instructions for compliance:** Diciendo "always verify customer before processing refund" sin enforcement programmatic. Falla porque LLMs ocasionalmente saltan pasos (data muestra 12% de casos donde get_customer se salta).
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 194]

---

## TS 1.5 — Apply Agent SDK hooks for tool call interception and data normalization

### Hechos y comportamiento

- **Hook patterns:** Los hooks son callbacks que se ejecutan en respuesta a agent events. Algunos hooks comúnmente usados:
  - `PreToolUse`: Antes de que una tool se ejecute; casos: validate inputs, block dangerous commands
  - `PostToolUse`: Después de que una tool retorna; casos: audit outputs, normalize data
  - `UserPromptSubmit`: Cuando un prompt se envía; casos: inject additional context
  - `Stop`: Cuando el agent termina; casos: validate result, save session state
  [Fuente: How the agent loop works — https://code.claude.com/docs/en/agent-sdk/agent-loop]

- **PostToolUse para data normalization:** Interceptar tool results para transformación antes de que el modelo los procese. Ejemplo: normalizar timestamps heterogéneos (Unix, ISO 8601, numeric status codes) de diferentes MCP tools a un formato consistente.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 216-217]

- **Tool call interception para compliance:** Implementar hooks que bloqueen policy-violating actions (p. ej., refunds > $500) y redirijan a alternative workflows (p. ej., human escalation).
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 218-219]

- **Hooks vs. prompt-based enforcement:** Usar hooks para business rules que requieren guaranteed compliance; usar prompt instructions para guidance probabilistic.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 220-221]

- **Hooks run outside context window:** Los hooks se ejecutan en el application process, no dentro del agent's context window, así que no consumen context. También pueden short-circuit el loop: un PreToolUse hook que rechaza un tool call previene su ejecución, y Claude recibe rejection message en lugar.
  [Fuente: How the agent loop works — https://code.claude.com/docs/en/agent-sdk/agent-loop]

### Sintaxis y configuración

```python
# Python: PostToolUse hook para data normalization
from claude_agent_sdk import query, ClaudeAgentOptions, PostToolUseHook
from datetime import datetime
import json

def normalize_timestamps_hook(hook_input) -> dict:
    """Normalize heterogeneous timestamp formats"""
    if hook_input.tool_name == "lookup_order":
        # Parse output y normalize timestamps
        result = hook_input.result
        if isinstance(result, str):
            try:
                data = json.loads(result)
                # Convert various formats to ISO 8601
                if "order_date" in data:
                    data["order_date"] = convert_to_iso8601(data["order_date"])
                if "ship_date" in data:
                    data["ship_date"] = convert_to_iso8601(data["ship_date"])
                hook_input.result = json.dumps(data)
            except:
                pass
    return {"result": hook_input.result}

async def main():
    async for message in query(
        prompt="Look up order 12345",
        options=ClaudeAgentOptions(
            allowed_tools=["lookup_order"],
            hooks={
                "PostToolUse": [
                    {
                        "handler": normalize_timestamps_hook,
                    }
                ]
            },
        ),
    ):
        pass
```
[Basado en: Exam Guide Oficial y How the agent loop works]

```python
# Python: PreToolUse hook para policy enforcement (refund threshold)
def refund_threshold_hook(hook_input) -> dict | None:
    """Block refunds exceeding $500 and escalate to human"""
    if hook_input.tool_name == "process_refund":
        refund_amount = hook_input.tool_input.get("amount")
        if refund_amount and float(refund_amount) > 500:
            return {
                "allowed": False,
                "error": f"Refund amount ${refund_amount} exceeds policy limit of $500. Escalating to human agent."
            }
    return {"allowed": True}

# Register en options.hooks
```
[Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 218-219]

```typescript
// TypeScript: Hook structure
interface Hook {
  handler: (input: HookInput) => Promise<HookResult> | HookResult;
  matcher?: HookMatcher;  // Filter which tool calls trigger this hook
}

interface HookMatcher {
  toolNames?: string[];     // Only match specific tools
  toolNamePatterns?: string[];  // Regex patterns
}

// Example: PostToolUse hook
const hooks = {
  "PostToolUse": [
    {
      matcher: { toolNames: ["lookup_order"] },
      handler: async (hookInput) => {
        // Normalize timestamps
        const result = JSON.parse(hookInput.result);
        result.order_date = convertToISO8601(result.order_date);
        return { result: JSON.stringify(result) };
      }
    }
  ]
};
```
[Fuente: Hooks del Agent SDK — https://code.claude.com/docs/en/agent-sdk/hooks]

### Patrones

- **PostToolUse para transformación:** Normalizar heterogeneous data formats (Unix timestamps, ISO 8601, numeric status codes) de diferentes sources antes de que el agent procese.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 216-217]

- **PreToolUse para policy enforcement:** Bloquear tool calls que violen business rules (p. ej., refunds > threshold) y redireccionar a escalation workflows.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 218-219]

- **HookMatcher para selective application:** Usar matcher patterns para aplicar hooks solo a specific tools, reduciendo overhead.
  [Fuente: Hooks del Agent SDK — https://code.claude.com/docs/en/agent-sdk/hooks]

### Anti-patrones (y por qué fallan)

- **Relying on prompts alone para compliance:** Diciendo "never approve refunds > $500" sin hook enforcement. Falla porque el LLM ocasionalmente no sigue; mejor: interceptar con hook pre-execution.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 220-221]

---

## TS 1.6 — Design task decomposition strategies for complex workflows

### Hechos y comportamiento

- **Fixed sequential pipelines vs. dynamic decomposition:** Usar fixed sequential pipelines (prompt chaining) para workflows predictables; usar dynamic adaptive decomposition basado en intermediate findings para open-ended investigation.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 227-232]

- **Prompt chaining patterns:** Break reviews en sequential steps (p. ej., analyze each file individually, luego run cross-file integration pass) para evitar attention dilution.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 236-237]

- **Adaptive investigation plans:** Para tasks open-ended (p. ej., "add comprehensive tests to legacy codebase"), generar subtasks basados en discovered findings en cada step, creando prioritized plan que adapta conforme dependencies se descubren.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 238-240]

- **Task selection criteria:** 
  - **Prompt chaining:** Predictable multi-aspect reviews (p. ej., code review con análisis per-file + integration pass)
  - **Dynamic decomposition:** Open-ended investigation, multi-step problem-solving
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 234-235]

### Sintaxis y configuración

**Prompt chaining para multi-pass code review:**
```python
# Step 1: Per-file local analysis
local_analysis_prompt = """Analyze each file for bugs, security issues:
File: auth.py
...
File: config.py
...
"""

# Step 2: Cross-file integration pass
integration_prompt = f"""
Given these local findings:
{local_analysis_results}

Now analyze:
- Data flow across files
- Shared state dependencies
- Integration points
"""
```
[Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 236-237]

**Dynamic decomposition pattern:**
```python
# First: map codebase structure
mapping_prompt = "Map the structure of this codebase. List all test files and untested modules."

# Based on mapping, adaptively generate subtasks
# Example output: "High-impact untested modules: auth.py (30% coverage), db.py (20% coverage)"
# Next step: Generate tests for auth.py first (higher impact)

adaptive_subtasks = [
    {"module": "auth.py", "priority": "high", "target_coverage": "80%"},
    {"module": "db.py", "priority": "medium", "target_coverage": "75%"},
]
```
[Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 238-240]

### Patrones

- **Multi-pass architecture:** Split large code reviews en per-file local analysis passes + separate cross-file integration passes para evitar attention dilution.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 236-237]

- **Adaptive planning:** Para open-ended tasks, generar plan inicialmente, luego adaptar basándose en discovered dependencies y findings.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 238-240]

- **Explicit scope definition:** Especificar research goals y quality criteria para subagents en lugar de step-by-step procedural instructions.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 184-185]

### Anti-patrones (y por qué fallan)

- **Monolithic analysis pass:** Analizar todo el codebase en un único pass. Falla porque attention dilution causa inconsistent findings y missed issues.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 236-237]

- **Fixed decomposition para open-ended tasks:** Predecir exactamente qué investigar en una tarea open-ended sin adaptive refinement. Falla porque discovered findings pueden revelar necesidades investigativas no anticipadas.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 238-240]

---

## TS 1.7 — Manage session state, resumption, and forking

### Hechos y comportamiento

- **Named session resumption:** Usar `--resume <session-name>` (CLI) / `resume: sessionId` (SDK) para continuar una specific prior conversation.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 243-244]
  [Fuente: Work with sessions — https://code.claude.com/docs/en/agent-sdk/sessions]

- **fork_session:** Crear independent branches desde un shared analysis baseline para explorar divergent approaches sin perder el original. `fork_session=True` (Python) / `forkSession: true` (TypeScript).
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 245-246]
  [Fuente: Work with sessions — https://code.claude.com/docs/en/agent-sdk/sessions]

- **Session persistence:** Sessions persisten en disk automáticamente. El SDK escribe a `~/.claude/projects/<encoded-cwd>/*.jsonl` o `$CLAUDE_CONFIG_DIR/projects/<encoded-cwd>/*.jsonl`.
  [Fuente: Work with sessions — https://code.claude.com/docs/en/agent-sdk/sessions]

- **Continue vs. Resume vs. Fork:**
  - **Continue:** Encuentra the most recent session en current directory; no ID tracking requerido (TypeScript: `continue: true`; Python: `continue_conversation=True`)
  - **Resume:** Toma specific session ID; requerido cuando se tienen múltiples sessions o quieren volver a una que no es la más reciente
  - **Fork:** Crea new session con copy de original's history; original stays unchanged
  [Fuente: Work with sessions — https://code.claude.com/docs/en/agent-sdk/sessions]

- **Important caveat sobre resumption:** Informar al agent sobre changes a previously analyzed files cuando resuming sessions después de code modifications. No asumir que prior tool results siguen siendo válidos.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 247-248]

- **Starting fresh vs. resuming:** Starting a new session con structured summary es más reliable que resuming con stale tool results. Si archivos han sido modificados o tiempo ha pasado, el estado anterior puede ser inválido.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 249-250]

- **Capturando session ID:** Disponible en `ResultMessage.session_id` (ambos SDKs). En TypeScript también disponible directamente como field en init `SystemMessage`; en Python está nested en `SystemMessage.data`.
  [Fuente: Work with sessions — https://code.claude.com/docs/en/agent-sdk/sessions]

- **Forking branches conversation history, not filesystem:** Si un forked agent edita files, esos cambios son reales y visibles a any session trabajando en el mismo directory. Para branching file changes, usar file checkpointing.
  [Fuente: Work with sessions — https://code.claude.com/docs/en/agent-sdk/sessions]

### Sintaxis y configuración

```python
# Python: Resume session by ID
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

session_id = "5b3f2c1a-8d4e-4f6b-9a7c-2e1d0f9b8a6c"  # Captured earlier

async for message in query(
    prompt="Now implement the refactoring you suggested",
    options=ClaudeAgentOptions(
        resume=session_id,
        allowed_tools=["Read", "Edit", "Write", "Glob", "Grep"],
    ),
):
    if isinstance(message, ResultMessage) and message.subtype == "success":
        print(message.result)
```
[Fuente: Work with sessions — https://code.claude.com/docs/en/agent-sdk/sessions]

```typescript
// TypeScript: Resume session by ID
import { query } from "@anthropic-ai/claude-agent-sdk";

const sessionId = "5b3f2c1a-8d4e-4f6b-9a7c-2e1d0f9b8a6c";

for await (const message of query({
  prompt: "Now implement the refactoring you suggested",
  options: {
    resume: sessionId,
    allowedTools: ["Read", "Edit", "Write", "Glob", "Grep"]
  }
})) {
  if (message.type === "result" && message.subtype === "success") {
    console.log(message.result);
  }
}
```
[Fuente: Work with sessions — https://code.claude.com/docs/en/agent-sdk/sessions]

```python
# Python: Fork session para explorar alternativa
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

session_id = "..."  # Original session ID

forked_id = None
try:
    async for message in query(
        prompt="Instead of JWT, outline OAuth2 approach for auth module",
        options=ClaudeAgentOptions(
            resume=session_id,
            fork_session=True,  # Create fork instead of modifying original
            max_turns=5,
        ),
    ):
        if isinstance(message, ResultMessage):
            forked_id = message.session_id  # New session ID for fork
            if message.subtype == "success":
                print(message.result)
except Exception as error:
    print(f"Session ended: {error}")

# Ahora se tienen dos session IDs independientes
print(f"Original: {session_id}, Fork: {forked_id}")
```
[Fuente: Work with sessions — https://code.claude.com/docs/en/agent-sdk/sessions]

```typescript
// TypeScript: Continue (auto-resume most recent)
for await (const message of query({
  prompt: "Analyze the auth module",
  options: { allowedTools: ["Read", "Glob", "Grep"] }
})) {
  if (message.type === "result" && message.subtype === "success") {
    console.log(message.result);
  }
}

// Second call: continue: true resumes most recent session automatically
for await (const message of query({
  prompt: "Now refactor it to use JWT",
  options: {
    continue: true,  // Auto-find most recent session
    allowedTools: ["Read", "Edit", "Write", "Glob", "Grep"]
  }
})) {
  if (message.type === "result" && message.subtype === "success") {
    console.log(message.result);
  }
}
```
[Fuente: Work with sessions — https://code.claude.com/docs/en/agent-sdk/sessions]

```python
# Python: Capturar session ID para resumption
session_id = None

try:
    async for message in query(
        prompt="Analyze the auth module and suggest improvements",
        options=ClaudeAgentOptions(allowed_tools=["Read", "Glob", "Grep"]),
    ):
        if isinstance(message, ResultMessage):
            session_id = message.session_id
            if message.subtype == "success":
                print(message.result)
except Exception as error:
    print(f"Session ended: {error}")

print(f"Session ID: {session_id}")  # Use para resumption later
```
[Fuente: Work with sessions — https://code.claude.com/docs/en/agent-sdk/sessions]

**Informing agent about file changes on resume:**
```python
# If files have been modified since last session, tell the agent
modified_files_summary = """
Files modified since last session:
- auth.py: Added JWT token validation logic
- config.py: Updated database connection pool size
"""

resume_prompt = f"""Resume previous analysis of the auth module.

Note: The following files have been changed since the last session:
{modified_files_summary}

Please re-analyze for impacts of these changes."""

async for message in query(
    prompt=resume_prompt,
    options=ClaudeAgentOptions(resume=session_id),
):
    pass
```
[Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 247-248, 260-261]

### Patrones

- **Explicit session ID tracking:** Para multi-user apps o cuando necesitas multiple simultaneous sessions, capturar y pasar session IDs explícitamente.
  [Fuente: Work with sessions — https://code.claude.com/docs/en/agent-sdk/sessions]

- **Named session management:** Para long-running or inter-session workflows, usar named sessions para readability.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 243-244]

- **Fork para divergent exploration:** Cuando quieren explorar dos approaches (p. ej., JWT vs. OAuth2) desde un shared analysis baseline.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 245-246]

- **Informing on file changes:** Cuando resuming después de code modifications, notify el agent explícitamente sobre qué files cambiaron para targeted re-analysis.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 247-248, 260-261]

### Anti-patrones (y por qué fallan)

- **Resuming con stale context without informing:** Resumir una sesión old sin notificar al agent que los files han cambiado. Falla porque el agent usa old tool results que ya no son válidos.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 247-250]

- **Starting fresh cuando resume sería suficiente:** Si la prior context es mostly valid, resuming es más efficient que starting fresh con injected summaries.
  [Fuente: Exam Guide Oficial — exam-guide-oficial-v1.0.txt, línea 249-250]

---

## HUECOS

- **Detalle de HookMatcher syntax y matching patterns:** La documentación en hooks proporciona estructura high-level pero podrían necesitarse más ejemplos concretos de regex patterns y filtering logic. Se intentó extraer de https://code.claude.com/docs/en/agent-sdk/hooks pero la salida fue truncada.

- **Ejemplos detallados de error propagation en multi-agent systems:** El TS 1.5 (escalation/error propagation) está principalmente en Domain 5, no en Domain 1, pero hay overlap. Se cubrió parcialmente desde multi-agent research architecture.

- **Video content from YouTube workshops:** Los dos videos (Claude Agent SDK Full Workshop, Prompting for Agents) no fueron accesibles via WebFetch (contenido dinámico de YouTube). Solo se pudo extraer de transcripts indirectos en blogs.

## CONTRADICCIONES

- **Tool naming para subagent spawning:** La documentación indica que el tool se llamaba "Task" en versiones anteriores del SDK (pre v2.1.63) y ahora se llama "Agent" en versiones recientes. Las notas anotan ambas variantes. No es una contradicción funcional, solo versioning.

## FUENTES NO ACCESIBLES

- **Introduction to Subagents — https://anthropic.skilljar.com/introduction-to-subagents — Skilljar course (login requerido).** Se accedió parcialmente pero con contenido conceptual limitado, no código/sintaxis específica. Se extrajo lo disponible.

- **Claude Agent SDK Full Workshop — https://www.youtube.com/watch?v=TqC1qOfiVcQ — YouTube video (contenido dinámico).** WebFetch devolvió solo pie de página y navegación; contenido técnico no está disponible via text fetch. Para replicar: ver video manualmente.

- **Prompting for Agents — https://www.youtube.com/watch?v=XSZP9GhhuAc — YouTube video.** Mismo limitation que el anterior.

→ **Acción de revisión manual pendiente:** Los dos videos de YouTube podrían ser examinados directamente si acceso a video es viabilidad del proceso de certificación. Skilljar requeriría credenciales del usuario.

## FUENTES ADICIONALES INCORPORADAS

- **None.** Todas las fuentes principales son oficiales (code.claude.com, anthropic.com, exam-guide-oficial).

---

## RESUMEN DE COBERTURA POR TASK STATEMENT

| TS | Tema | Cobertura | Fuentes Principales |
|:---|:---|:---|:---|
| 1.1 | Agentic loops | ✓ Completa | agent-loop, exam-guide |
| 1.2 | Multi-agent coordination | ✓ Completa | subagents, multi-agent-research, exam-guide |
| 1.3 | Subagent config & context | ✓ Completa | subagents, exam-guide, skilljar (partial) |
| 1.4 | Workflows & enforcement | ✓ Buena | exam-guide, agent-loop (hooks) |
| 1.5 | Hooks & interception | ✓ Buena | hooks, agent-loop, exam-guide |
| 1.6 | Task decomposition | ✓ Buena | exam-guide, building-effective-agents |
| 1.7 | Sessions & resumption | ✓ Completa | sessions, exam-guide |

---

**Nota de trazabilidad:** Cada hecho lleva su cita exacta (URL o línea del documento oficial). Las fuentes de no-oficiales estarían marcadas `[NO OFICIAL]` pero aquí todos son oficiales o del exam guide.
