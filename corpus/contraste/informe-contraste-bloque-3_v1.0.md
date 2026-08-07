# Informe de verificación — corpus/bloque-3-tools-mcp.md (2026-08-05)

Veredicto: **APTO CON CAMBIOS** — 2 críticos · 5 mejoras. Críticos corregidos y mejoras aplicadas por el orquestador el 2026-08-05 (ver "Correcciones aplicadas").

Cobertura de los 5 task statements (2.1–2.5) completa y con muy buena exactitud técnica (contrastada contra la guía oficial y las páginas fuente en vivo). Nada fuera de alcance, ningún enlace roto.

## CRÍTICO (bloquea el gate)

- [C1] §2.2 (`{#ts-3-2}`) — Los campos `_metadata.originalQuery`/`partialResults` del ejemplo de error se presentaban como parte del esquema base de cualquier respuesta `isError`. La guía oficial solo especifica `errorCategory` (transient/validation/permission; "business" aparte), `isRetryable` y descripción legible; esos campos corresponden al skill de propagación subagente→coordinador, no a todo error MCP. v1.2 resolvió el mismo riesgo con `suggestedAction` marcándolo ilustrativo. **[CORREGIDO: separado/marcado como caso de propagación]**
- [C2] §2.4 (`{#ts-3-4}`) — Sintaxis de referencia a MCP resources incorrecta: `@mcp-server:resource-path` en lugar del formato real `@server:protocol://resource/path` (ejemplos oficiales: `@github:issue://123`, `@docs:file://api/authentication`). Verificado en vivo en la doc "Connect Claude Code to tools via MCP". **[CORREGIDO]**

## MEJORA (no bloquea)

- [M1] Tres fences sin identificador de lenguaje. **[APLICADA]**
- [M2] §2.3 — Faltaba el matiz de "prefill" al forzar `tool_choice` (`any`/forzada impide texto previo; para contexto natural + llamada garantizada, `auto` + instrucción explícita). Confirmado vigente en "Define tools". **[APLICADA]**
- [M3] §2.4 — Faltaba el distractor de `.mcp.json` con `url` sin `"type"` (se lee como stdio y falla). Confirmado vigente. **[APLICADA]**
- [M4] §2.4 — Faltaban los nombres de servidor reservados (`workspace`, `claude-in-chrome`, `computer-use`, `Claude Preview`, `Claude Browser`). Confirmado vigente. **[APLICADA]**
- [M5] §2.1 — Faltaba el ciclo de iteración de diseño de tools (prototipar → evaluar → iterar sobre transcripciones → validar), respaldado por "Writing effective tools for agents". **[APLICADA]**

## Deriva vs v1.2

- [A] Ausente: ejemplo Python FastMCP (descripción autogenerada) → HUECO menor, no imprescindible (queda como deuda).
- [A] Ausente: ciclo de iteración de diseño de tools → HUECO (ver M5). **[CERRADO]**
- [A] Ausente: matiz "prefill" al forzar `tool_choice` → HUECO A RELLENAR (ver M2). **[CERRADO]**
- [A] Ausente: distractor `.mcp.json` sin `type` → HUECO A RELLENAR (ver M3). **[CERRADO]**
- [A] Ausente: nombres de servidor reservados → HUECO (ver M4). **[CERRADO]**
- [A] Ausente: `tool_choice: "none"` → **OBSOLETO/FUERA DE BLUEPRINT** (el blueprint de TS 2.3 solo lista auto/any/forzada; omisión correcta).
- [A] Ausente: scope *local* de `~/.claude.json` → **OBSOLETO/FUERA DE BLUEPRINT** (el blueprint solo distingue project vs user).
- [B] Nuevo: `input_examples` con coste en tokens → **OK** (verificado).
- [B] Nuevo: mecánica detallada de las built-in tools (offset/limit, PDF, timeouts, modos de Grep, cap de Glob) → **OK** (verificado contra "Tools reference"; mejora sustancial vs v1.2).
- [B] Nuevo: `_metadata` en el ejemplo base → INCORRECTO, ver C1. **[CORREGIDO]**
- [B] Nuevo: sintaxis de resources → INCORRECTO, ver C2. **[CORREGIDO]**
- [B] Nuevo: `tools`/`disallowedTools` en frontmatter de subagente → **OK** (confirmado en "Tools reference").
- [C] Contradicciones: **ninguna detectada**.

## Matriz de cobertura

| Task statement | Anchor | Estado |
|---|---|---|
| 2.1 Tool interfaces | {#ts-3-1} | Cubierto (M5 aplicada) |
| 2.2 Structured errors | {#ts-3-2} | Cubierto (C1 corregido) |
| 2.3 Distribute tools / tool_choice | {#ts-3-3} | Cubierto (M2 aplicada) |
| 2.4 Integrate MCP servers | {#ts-3-4} | Cubierto (C2 corregido; M3, M4 aplicadas) |
| 2.5 Built-in tools | {#ts-3-5} | Cubierto, muy sólido |

## Enlaces verificados
- OK: 6/6 · Rotos: ninguno · Redirigidos: ninguno.

## Correcciones aplicadas por el orquestador (2026-08-05)
C1, C2, M1–M5 según se indica arriba; frontmatter `estado: borrador → verificado`. Deuda restante: ejemplo FastMCP (menor).
