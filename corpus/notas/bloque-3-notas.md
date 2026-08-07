# Notas de extracción — Bloque 3: Diseño de tools y MCP
Fecha: 2026-08-05 · Fuentes procesadas: 10/10

## TS 2.1 — Design effective tool interfaces with clear descriptions and boundaries

### Hechos y comportamiento
- Tool descriptions are the **primary mechanism LLMs use for tool selection**; minimal descriptions lead to unreliable selection among similar tools. [Fuente: Define tools — https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools]
- When descriptions are minimal (e.g., "Retrieves customer information" / "Retrieves order details"), models lack context to differentiate between similar tools, causing misrouting. [Fuente: Define tools — https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools]
- Ambiguous or overlapping tool descriptions cause misrouting; renaming tools and updating descriptions to eliminate functional overlap is effective (e.g., renaming `analyze_content` to `extract_web_results` with web-specific description). [Fuente: Exam Guide (TS 2.1) — líneas 270-278]
- System prompt wording impacts tool selection; keyword-sensitive instructions can create unintended tool associations and override well-written tool descriptions. [Fuente: Exam Guide (TS 2.1) — línea 282]
- Tool descriptions should explicitly state: **what the tool does**, **when to use it vs alternatives**, **expected inputs and outputs**, **boundary conditions and limitations**, and **example queries or use cases**. Aim for 3–4 sentences minimum, more for complex tools. [Fuente: Define tools — https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools]
- Consolidation principle: avoid implementing every API endpoint as a separate tool. Group related operations into single tools with action parameters (e.g., `schedule_event` instead of separate `list_users`, `list_events`, `create_event`). Fewer, more capable tools reduce selection ambiguity. [Fuente: Writing effective tools for agents — https://www.anthropic.com/engineering/writing-tools-for-agents]
- Splitting generic tools into purpose-specific tools: decompose broad tools into distinct functions with defined input/output contracts (e.g., split `analyze_document` into `extract_data_points`, `summarize_content`, `verify_claim_against_source`). [Fuente: Exam Guide (TS 2.1) — líneas 279-281]
- Namespacing with prefixes/suffixes helps agents select appropriate tools (e.g., `asana_search`, `asana_projects_search`). This delineation prevents misrouting between overlapping tools. [Fuente: Writing effective tools for agents — https://www.anthropic.com/engineering/writing-tools-for-agents]

### Sintaxis y configuración
- Tool definition JSON structure (minimum required fields):
```json
{
  "name": "tool_name",                    // Must match regex ^[a-zA-Z0-9_-]{1,64}$
  "description": "Detailed description...", // Explain what, when to use, boundaries, caveats
  "input_schema": {
    "type": "object",
    "properties": { /* parameter definitions */ },
    "required": ["param1"]
  }
}
```
[Fuente: Define tools — https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools]

- Tool descriptions best practice example:
```
Good: "Retrieves the current stock price for a given ticker symbol. The ticker symbol must be a valid symbol for a publicly traded company on a major US stock exchange like NYSE or NASDAQ. The tool will return the latest trade price in USD. It should be used when the user asks about the current or most recent price of a specific stock. It will not provide any other information about the stock or company."

Poor: "Gets the stock price for a ticker."
```
[Fuente: Define tools — https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools]

- Optional `input_examples` field provides concrete sample inputs (array of valid objects per schema) to clarify ambiguous usage patterns, especially for nested objects or format-sensitive parameters. Token cost: ~20–50 tokens for simple examples, ~100–200 for complex nested objects. [Fuente: Define tools — https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools]

### Patrones
- **Hierarchical tool descriptions**: Start with one-line purpose, then expand with expected inputs, example queries, boundary conditions, and what the tool does NOT do. This layering clarifies selection decisions. [Fuente: Writing effective tools for agents — https://www.anthropic.com/engineering/writing-tools-for-agents]
- **Semantic naming over opaque identifiers**: Return meaningful field names (`name`, `image_url`) instead of technical identifiers (`uuid`, `256px_image_url`). This reduces token consumption and improves model reasoning. [Fuente: Writing effective tools for agents — https://www.anthropic.com/engineering/writing-tools-for-agents]
- **Pagination and filtering with sensible defaults**: Implement tools to return only high-signal information, using pagination and truncation to prevent context bloat. [Fuente: Writing effective tools for agents — https://www.anthropic.com/engineering/writing-tools-for-agents]
- **Few-shot examples for ambiguous scenarios**: When descriptions alone are insufficient, include 2–4 concrete examples showing tool selection reasoning for ambiguous requests and output formatting expectations. [Fuente: Exam Guide (Domain 4, TS 4.2) — referenced in tool design context]

### Anti-patrones (y por qué fallan)
- **Minimal descriptions** ("Gets the stock price" or "Retrieves customer information") lead to unreliable tool selection because models lack context to differentiate similar tools. This results in incorrect tool routing and failures. [Fuente: Define tools — https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools]
- **Creating separate tools for every API endpoint** (e.g., `list_users`, `list_events`, `create_event`) causes decision complexity and misrouting. Consolidation into action-parameterized tools is preferred. [Fuente: Writing effective tools for agents — https://www.anthropic.com/engineering/writing-tools-for-agents]
- **Overlapping tool purposes without clear boundaries** (e.g., `analyze_content` vs `analyze_document` with nearly identical descriptions) prevent models from selecting the correct tool. Renaming with purpose-specific descriptions fixes this. [Fuente: Exam Guide (TS 2.1) — líneas 270-278]
- **Bloated response payloads** with every field returned force models to parse irrelevant data and waste context. Returning only high-signal fields is essential. [Fuente: Writing effective tools for agents — https://www.anthropic.com/engineering/writing-tools-for-agents]
- **Keyword-sensitive system prompts** that create unintended tool associations can override well-designed descriptions. System prompt wording must not prioritize tools based on isolated keywords. [Fuente: Exam Guide (TS 2.1) — línea 282]

## TS 2.2 — Implement structured error responses for MCP tools

### Hechos y comportamiento
- MCP tools communicate failures to agents via the **`isError` flag pattern** in tool results; this is the standard mechanism for indicating errors in MCP. [Fuente: Build an MCP server — https://modelcontextprotocol.io/docs/develop/build-server]
- Error responses must distinguish between **transient errors** (timeouts, service unavailability—retryable), **validation errors** (invalid input—not retryable), **business errors** (policy violations—not retryable), and **permission errors** (access denied—not retryable). [Fuente: Exam Guide (TS 2.2) — líneas 287–288]
- Uniform generic error responses ("Operation failed") prevent agents from making appropriate recovery decisions. Structured metadata enables agents to determine whether to retry, escalate, or abandon a task. [Fuente: Exam Guide (TS 2.2) — líneas 293–295]
- Retryable vs non-retryable errors must be explicitly signaled; returning `isRetryable: false` with customer-friendly explanations enables agents to communicate appropriately instead of wasting retry attempts. [Fuente: Exam Guide (TS 2.2) — líneas 298–300]
- **Local error recovery within subagents**: subagents should implement recovery for transient failures and propagate to the coordinator only errors they cannot resolve, along with partial results and what was attempted. [Fuente: Exam Guide (TS 2.2) — líneas 301–303]
- **Access failures vs valid empty results must be distinguished**: a successful query returning no matches is different from a timeout or permission denied. Returning empty results as failure (with isError: true) prevents correct interpretation. [Fuente: Exam Guide (TS 2.2) — líneas 304–305]

### Sintaxis y configuración
- Structured error response format (MCP pattern):
```json
{
  "isError": true,
  "content": [
    {
      "type": "text",
      "text": "Human-readable error description"
    }
  ],
  "_metadata": {
    "errorCategory": "transient|validation|permission|business",
    "isRetryable": true,
    "originalQuery": "what was attempted",
    "partialResults": [ /* partial data if available */ ]
  }
}
```
[Fuente: Build an MCP server — https://modelcontextprotocol.io/docs/develop/build-server; synthesized from MCP spec patterns]

- Successful (non-error) response structure:
```json
{
  "isError": false,
  "content": [
    {
      "type": "text",
      "text": "Response content"
    }
  ]
}
```
[Fuente: Build an MCP server — https://modelcontextprotocol.io/docs/develop/build-server]

- Customer-friendly error message with business rule violation example:
```
"isRetryable": false,
"text": "Refund amount $750 exceeds the maximum single-transaction limit of $500. 
         Please contact the customer support team for policy exceptions."
```
[Fuente: Exam Guide (TS 2.2) — línea 299]

### Patrones
- **Categorized error metadata**: Always include `errorCategory` (transient/validation/permission/business) so downstream agents can apply appropriate recovery logic without parsing natural language error text. [Fuente: Exam Guide (TS 2.2) — línea 298]
- **Partial results with context**: When an operation partially succeeds, return both partial results and metadata about what was attempted, enabling coordinators to continue with partial data or decide to escalate. [Fuente: Exam Guide (TS 2.2) — líneas 301–303]
- **Subagent local recovery pattern**: Subagents implement retry logic for transient failures (with exponential backoff) and only propagate errors they cannot resolve to the coordinator, reducing coordinator-level noise. [Fuente: Exam Guide (TS 2.2) — líneas 301–303]
- **Empty results as valid success**: A query that returns zero matches is `isError: false` with empty content, distinct from a timeout (which is transient and retryable). [Fuente: Exam Guide (TS 2.2) — líneas 304–305]

### Anti-patrones (y por qué fallan)
- **Generic error responses** ("Operation failed", "Error occurred") without category or retry hints force agents to retry indiscriminately or escalate prematurely, wasting time and user patience. [Fuente: Exam Guide (TS 2.2) — línea 293]
- **Treating all errors as retryable** (or all as non-retryable) prevents intelligent recovery; validation errors and permission errors must not be retried, only transient errors should be. [Fuente: Exam Guide (TS 2.2) — líneas 294–300]
- **Silently suppressing errors** (returning empty results as success for a failed query) prevents coordinators from knowing whether a task succeeded or failed, breaking error propagation. [Fuente: Exam Guide (TS 5.3) — línea 688]
- **Missing partial results in error context** when an operation is partially successful makes it impossible for coordinators to continue with available data. [Fuente: Exam Guide (TS 2.2) — líneas 301–303]

## TS 2.3 — Distribute tools appropriately across agents and configure tool choice

### Hechos y comportamiento
- Giving an agent access to too many tools (e.g., 18 instead of 4–5) **degrades tool selection reliability** by increasing decision complexity; agents become confused about which tool to use. [Fuente: Exam Guide (TS 2.3) — líneas 309–310]
- **Agents with tools outside their specialization tend to misuse them**; a synthesis agent should not have access to web search tools if its role is to aggregate findings, or it will attempt searches instead of relying on provided data. [Fuente: Exam Guide (TS 2.3) — líneas 311–312]
- **Scoped tool access principle**: give each agent only the tools needed for its role, with limited cross-role tools for specific high-frequency needs (e.g., a verify_fact tool for synthesis agents). [Fuente: Exam Guide (TS 2.3) — líneas 313–314]
- **`tool_choice: "auto"`** allows Claude to decide whether to call any provided tools or not. This is the default when `tools` are provided. [Fuente: Define tools — https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools]
- **`tool_choice: "any"`** tells Claude it must use one of the provided tools but doesn't force a particular tool. This guarantees a tool will be called. [Fuente: Define tools — https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools]
- **Forced tool selection** (`tool_choice: {"type": "tool", "name": "..."}`) ensures a specific tool is called first; useful for enforcing sequencing (e.g., force `extract_metadata` before enrichment tools). [Fuente: Exam Guide (TS 2.3) — línea 327; Define tools]
- **`tool_choice: "any"` guarantees tool calls** without letting the model return conversational text alone; when combined with strict tool use, it guarantees both tool execution and schema compliance. [Fuente: Exam Guide (TS 2.3) — línea 330]
- Fewer tools reduce token overhead per session because every connected server's tools load into context at session start; removing unused servers frees space. [Fuente: MCP quickstart — https://code.claude.com/docs/en/mcp-quickstart]

### Sintaxis y configuración
- Tool choice configuration in API request:
```json
{
  "model": "claude-opus-5",
  "tools": [/* tool definitions */],
  "tool_choice": "auto"  // or "any" or {"type": "tool", "name": "extract_metadata"}
}
```
[Fuente: Define tools — https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools]

- Forced specific tool selection:
```json
"tool_choice": {"type": "tool", "name": "get_weather"}
```
[Fuente: Define tools — https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools]

- Agent SDK subagent tool restriction in YAML frontmatter:
```yaml
---
name: "synthesis-agent"
tools: ["verify_fact", "read_documents"]
disallowedTools: ["web_search"]
---
```
[Fuente: Exam Guide (TS 2.3) — línea 319 context]

### Patrones
- **Role-based tool scoping**: web search agent has `[search_web, fetch_url]`; analysis agent has `[extract_data, analyze_text]`; synthesis agent has `[verify_fact, summarize]`. Cross-specialization tools (like `verify_fact`) are explicitly listed only where needed. [Fuente: Exam Guide (TS 2.3) — líneas 318–323]
- **Constrained tool alternatives**: replace generic `fetch_url` with `load_document` that validates document URLs, reducing footgun risk. [Fuente: Exam Guide (TS 2.3) — línea 320]
- **Forced sequencing with tool_choice**: use `{"type": "tool", "name": "extract_metadata"}` to ensure prerequisite data collection before downstream enrichment, then handle follow-up steps in subsequent turns. [Fuente: Exam Guide (TS 2.3) — línea 327]
- **Guaranteeing tool invocation**: combine `tool_choice: "any"` with `strict: true` on tool definitions to guarantee both that a tool will be called and that inputs strictly conform to the schema. [Fuente: Define tools — https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools]

### Anti-patrones (y por qué fallan)
- **Giving all tools to all agents** increases context size per session and causes misuse (synthesis agents attempting searches, etc.). Scoping prevents confusion. [Fuente: Exam Guide (TS 2.3) — líneas 309–312]
- **Over-relying on `tool_choice: "auto"`** when sequencing is critical (e.g., authentication before refund processing) results in agents skipping prerequisites. Forced selection is needed for deterministic ordering. [Fuente: Exam Guide (TS 2.3) — línea 327]
- **Not using `tool_choice: "any"`** when output must be structured data instead of conversational text; the model will return text commentary instead of calling tools. [Fuente: Exam Guide (TS 2.3) — línea 330]

## TS 2.4 — Integrate MCP servers into Claude Code and agent workflows

### Hechos y comportamiento
- **MCP server scoping**: project-level (`.mcp.json`) for shared team tooling—checked into version control and available to all teammates; user-level (`~/.claude.json`) for personal/experimental servers—private to one user. [Fuente: Exam Guide (TS 2.4) — líneas 334–335; MCP quickstart — https://code.claude.com/docs/en/mcp-quickstart]
- **Environment variable expansion in `.mcp.json`** (e.g., `${GITHUB_TOKEN}`) allows credential management without committing secrets; variables are resolved at connection time. [Fuente: Exam Guide (TS 2.4) — línea 336; Connect Claude Code to tools via MCP — https://code.claude.com/docs/en/mcp]
- **Tools from all configured MCP servers are discovered at connection time** and available simultaneously to the agent; there is no explicit selection step—agents choose among all available tools. [Fuente: Exam Guide (TS 2.4) — línea 338]
- **MCP resources as content catalogs**: expose issue summaries, documentation hierarchies, database schemas as resources to reduce exploratory tool calls; agents see available data without requiring tool-based discovery. [Fuente: Exam Guide (TS 2.4) — líneas 340–341]
- **Project-scoped `.mcp.json`**: shared via version control; first-time access prompts user for approval before connecting (security measure). Once approved, available across all sessions in that project. [Fuente: Connect Claude Code to tools via MCP — https://code.claude.com/docs/en/mcp]
- **User-scoped `~/.claude.json`**: registered once for all projects; registered servers activate automatically in every project without per-project approval. [Fuente: Connect Claude Code to tools via MCP — https://code.claude.com/docs/en/mcp]
- **MCP tool descriptions must be enhanced** with explicit capability explanations and output details; under-described MCP tools cause agents to prefer built-in tools (like Grep) over more capable MCP alternatives. [Fuente: Exam Guide (TS 2.4) — línea 346]
- **Community MCP servers should be preferred** over custom implementations for standard integrations (Jira, Slack, GitHub); custom servers should be reserved for team-specific workflows. [Fuente: Exam Guide (TS 2.4) — línea 348]

### Sintaxis y configuração
- Project-scoped `.mcp.json` (HTTP server):
```json
{
  "mcpServers": {
    "claude-code-docs": {
      "type": "http",
      "url": "https://code.claude.com/docs/mcp"
    }
  }
}
```
[Fuente: Connect Claude Code to tools via MCP — https://code.claude.com/docs/en/mcp]

- Project-scoped `.mcp.json` (local stdio server):
```json
{
  "mcpServers": {
    "playwright": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"]
    }
  }
}
```
[Fuente: MCP quickstart — https://code.claude.com/docs/en/mcp-quickstart]

- Environment variable expansion:
```json
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://github.com/mcp",
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```
[Fuente: Connect Claude Code to tools via MCP — https://code.claude.com/docs/en/mcp]

- User-scoped `~/.claude.json` structure (at `mcpServers` top-level key):
```json
{
  "mcpServers": {
    "personal-server": {
      "type": "http",
      "url": "https://my-service.local/mcp"
    }
  }
}
```
[Fuente: Connect Claude Code to tools via MCP — https://code.claude.com/docs/en/mcp]

- CLI command to add server:
```bash
claude mcp add --transport http server-name https://example.com/mcp
```
[Fuente: MCP quickstart — https://code.claude.com/docs/en/mcp-quickstart]

- MCP resource URI reference in prompts (@ mention):
```
@mcp-server:resource-path
```
[Fuente: Connect Claude Code to tools via MCP — https://code.claude.com/docs/en/mcp]

### Patrones
- **Layered server configuration**: project-scoped servers (`.mcp.json`) for team standards (GitHub, Jira); user-scoped servers (`~/.claude.json`) for personal utilities and experimental integrations. [Fuente: Exam Guide (TS 2.4) — líneas 334–345]
- **Enhancing MCP tool descriptions**: override default descriptions in agents to clarify capabilities (e.g., for search tools, explicitly state "Returns full-text search results with relevance ranking and snippet context"). [Fuente: Exam Guide (TS 2.4) — línea 346]
- **Resource-first design**: when designing MCP servers, expose data as resources (read-only) rather than tools (executable) where possible, reducing the need for exploratory tool calls. [Fuente: Exam Guide (TS 2.4) — líneas 340–341]
- **Community server integration prioritization**: evaluate community servers (Anthropic Directory) before implementing custom servers for standard integrations; custom servers for domain-specific workflows. [Fuente: Exam Guide (TS 2.4) — línea 348]

### Anti-patrones (y por qué fallan)
- **Committing secrets to `.mcp.json`** breaks security; always use environment variable expansion (`${VAR}` syntax) for credentials. [Fuente: Exam Guide (TS 2.4) — línea 336; Connect Claude Code to tools via MCP]
- **Defining too many servers per project** increases context overhead and token consumption per session; remove unused servers. [Fuente: Connect Claude Code to tools via MCP — https://code.claude.com/docs/en/mcp]
- **Poor MCP tool descriptions** cause agents to ignore capable MCP tools and prefer built-in alternatives; descriptions must be explicit and capability-focused. [Fuente: Exam Guide (TS 2.4) — línea 346]
- **Building custom servers for standard integrations** (Jira, Slack) wastes effort when community servers already exist; reserve custom development for team-specific workflows. [Fuente: Exam Guide (TS 2.4) — línea 348]

## TS 2.5 — Select and apply built-in tools (Read, Write, Edit, Bash, Grep, Glob) effectively

### Hechos y comportamiento

#### Read tool
- **Read** loads the full contents of files with line numbers; returns up to token limit. For files exceeding token limit, returns first page with `PARTIAL view` notice and supports `offset`/`limit` parameters. [Fuente: Tools reference — https://code.claude.com/docs/en/tools-reference; Read tool behavior]
- **Read handles special file types**: PNG/JPG images as visual content (auto-downscaled for large files); PDFs in full for short documents, by page ranges (pages: "1-5") for PDFs longer than 10 pages, up to 20 pages per call; Jupyter notebooks (.ipynb) with all cells and outputs. [Fuente: Tools reference — https://code.claude.com/docs/en/tools-reference; Read tool behavior]
- Read is **read-only**, no permission required by default for paths inside working directory (marked "Permission required: No"). [Fuente: Tools reference — https://code.claude.com/docs/en/tools-reference]

#### Write tool
- **Write** creates a new file or overwrites an existing one with full content (no append/merge). Requires that Claude has previously read the target file in the current conversation if the file already exists. Write to unread existing files fails with error. [Fuente: Tools reference — https://code.claude.com/docs/en/tools-reference; Write tool behavior]
- New files don't require prior read; overwriting existing files does. [Fuente: Tools reference — https://code.claude.com/docs/en/tools-reference; Write tool behavior]
- Write tool is permission-protected ("Permission required: Yes"). [Fuente: Tools reference — https://code.claude.com/docs/en/tools-reference]

#### Edit tool
- **Edit** performs exact string replacement: takes `old_string` and `new_string` and replaces the first exact match. No regex or fuzzy matching. [Fuente: Tools reference — https://code.claude.com/docs/en/tools-reference; Edit tool behavior]
- Three checks must pass for Edit to apply: **(1) Read-before-edit** (Claude must have read the file in current conversation before editing, though newer models may edit unread files when read wouldn't require permission), **(2) Match** (old_string must appear exactly), **(3) Uniqueness** (old_string must appear exactly once, or use `replace_all: true`). [Fuente: Tools reference — https://code.claude.com/docs/en/tools-reference; Edit tool behavior]
- **When Edit fails due to non-unique text matches**, use Read + Write as fallback for reliable file modifications. [Fuente: Exam Guide (TS 2.5) — líneas 361–362]
- **Edit can reread changed files**: if a file changed on disk after last read and `old_string` matches current content exactly and unambiguously, Edit can proceed (Claude Code v2.1.208+). [Fuente: Tools reference — https://code.claude.com/docs/en/tools-reference; Edit tool behavior]
- Edit tool is permission-protected ("Permission required: Yes"). An Edit allow rule also grants read access to the same path. [Fuente: Tools reference — https://code.claude.com/docs/en/tools-reference; Edit tool behavior]

#### Bash tool
- **Bash** executes shell commands. A built-in set of read-only commands (ls, cat, echo, pwd, head, tail, grep, find, wc, which, diff, stat, du, cd, git) run without permission prompts. [Fuente: Tools reference — https://code.claude.com/docs/en/tools-reference; Bash tool behavior]
- Environment variables don't persist between commands unless set with `CLAUDE_ENV_FILE`. Bash runs each command in separate process. [Fuente: Tools reference — https://code.claude.com/docs/en/tools-reference; Bash tool behavior]
- Each command has a timeout (default 2 minutes; max 10 minutes; configurable with `BASH_DEFAULT_TIMEOUT_MS` and `BASH_MAX_TIMEOUT_MS`). Commands running past timeout are auto-backgrounded. [Fuente: Tools reference — https://code.claude.com/docs/en/tools-reference; Bash tool behavior]
- Bash tool is permission-protected ("Permission required: Yes"). [Fuente: Tools reference — https://code.claude.com/docs/en/tools-reference]

#### Grep tool
- **Grep** searches file contents for patterns; finds lines, not files. Built on ripgrep (not POSIX grep); uses ripgrep regex syntax requiring escape sequences (e.g., `interface\{\}` to find `interface{}` in Go). [Fuente: Exam Guide (TS 2.5) — líneas 354–355; Tools reference]
- Three output modes: `files_with_matches` (file paths only, default), `content` (matching lines with file/line numbers), `count` (match count per file plus total). [Fuente: Tools reference — https://code.claude.com/docs/en/tools-reference; Grep tool behavior]
- Grep respects `.gitignore` by default; to search gitignored files, pass the file path directly. Supports `glob` parameter (e.g., `**/*.tsx`) and `type` parameter (e.g., `py`, `rust`). Default is single-line matching; set `multiline: true` for cross-line patterns. [Fuente: Tools reference — https://code.claude.com/docs/en/tools-reference; Grep tool behavior]
- Grep is read-only ("Permission required: No"). [Fuente: Tools reference — https://code.claude.com/docs/en/tools-reference]

#### Glob tool
- **Glob** finds files by name pattern matching. Supports `**` for recursive directory matching (e.g., `**/*.js` matches `.js` at any depth; `src/**/*.ts` matches `.ts` under `src/`); brace expansion (e.g., `*.{json,yaml}`). [Fuente: Exam Guide (TS 2.5) — línea 366; Tools reference]
- Results sorted by modification time, capped at 100 files; truncation flag tells Claude to narrow pattern if cap is hit. [Fuente: Tools reference — https://code.claude.com/docs/en/tools-reference; Glob tool behavior]
- Glob doesn't respect `.gitignore` by default (set `CLAUDE_CODE_GLOB_NO_IGNORE=false` to enable gitignore respect). [Fuente: Tools reference — https://code.claude.com/docs/en/tools-reference; Glob tool behavior]
- Glob is read-only ("Permission required: No"). [Fuente: Tools reference — https://code.claude.com/docs/en/tools-reference]

### Patrones
- **Grep for content search**: use Grep when searching code content across a codebase (finding function callers, locating error messages, searching for import statements). [Fuente: Exam Guide (TS 2.5) — línea 364]
- **Glob for file discovery**: use Glob to find files matching naming patterns (e.g., `**/*.test.tsx` for all test files, `src/**/*.ts` for TypeScript files under src). [Fuente: Exam Guide (TS 2.5) — línea 366]
- **Read + Write as Edit fallback**: when Edit fails due to non-unique text, read the file contents, make changes, write it back. This ensures reliable modifications when Edit cannot pin down a unique anchor. [Fuente: Exam Guide (TS 2.5) — línea 367]
- **Incremental codebase understanding**: start with Grep to find entry points, then Read to follow imports and trace flows, rather than reading all files upfront. This preserves context and focuses exploration. [Fuente: Exam Guide (TS 2.5) — línea 368]
- **Tracing function usage**: identify all exported names first, then Grep for each name across the codebase to trace usage across wrapper modules. [Fuente: Exam Guide (TS 2.5) — línea 371]
- **Combining Bash commands with Read/Grep**: use Bash (cat, head, tail, grep on a single file) to satisfy read-before-edit requirement, then Edit becomes eligible if unique match found. [Fuente: Tools reference — https://code.claude.com/docs/en/tools-reference; Edit tool behavior]

### Anti-patrones (y por qué fallan)
- **Reading entire large codebases upfront** exhausts context and prevents incremental exploration. Start with Grep for targeted searches. [Fuente: Exam Guide (TS 2.5) — línea 368]
- **Using Edit without reading the file first** fails the read-before-edit check (except in newer models with reduced permission checks). Always read or view file before editing. [Fuente: Tools reference — https://code.claude.com/docs/en/tools-reference; Edit tool behavior]
- **Editing with non-unique `old_string`** fails when the text appears multiple times. Use Read + Write instead when Edit cannot disambiguate. [Fuente: Exam Guide (TS 2.5) — línea 361]
- **Using Edit instead of Write for new files** is inefficient; Write is the correct tool for file creation. [Fuente: Tools reference — https://code.claude.com/docs/en/tools-reference]
- **Over-relying on Bash for large file reads** instead of using Read; Bash tools like cat, head, tail may truncate or lose context. Use Read for complete file contents. [Fuente: Tools reference — https://code.claude.com/docs/en/tools-reference]
- **Not using Glob for file discovery**: manual directory listing with Bash ls/find is slower than Glob's pattern matching. [Fuente: Exam Guide (TS 2.5) — línea 366]

## HUECOS
- Ninguno detectado. Los task statements 2.1–2.5 están cubiertos completamente por las fuentes oficiales (platform.claude.com, code.claude.com, modelcontextprotocol.io, anthropic.skilljar.com, deeplearning.ai).

## CONTRADICCIONES
- Ninguna detectada entre fuentes oficiales.

## FUENTES NO ACCESIBLES
- Ninguna. Todas las 10 fuentes del bloque fueron accesibles (incluyendo skilljar y deeplearning.ai).

## FUENTES ADICIONALES INCORPORADAS
- Ninguna fuente adicional de terceros fue necesaria; todos los task statements quedaron cubiertos por las fuentes oficiales listadas.
