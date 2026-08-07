# Informe de verificación — corpus/bloque-4-agent-sdk.md (2026-08-05)

Veredicto: **NO APTO** — 3 críticos · 6 mejoras. Correcciones aplicadas por el orquestador el 2026-08-05 con re-verificación contra la doc oficial en vivo (ver "Correcciones aplicadas"); tras ellas el bloque queda `verificado`.

## CRÍTICO (bloquea el gate)

- [C1] §1.4/§1.5 — **Sintaxis de hooks inventada** presentada como real: `HookMatcher{toolNames, toolNamePatterns}`, `handler`, salidas `{allowed, error}`/`{result}` y acceso por atributo. La API real (verificada en vivo en code.claude.com/docs/en/agent-sdk/hooks): registro `{ matcher?: string, hooks: HookCallback[], timeout? }` con `matcher` **string** (lista `|`/`,` o regex; `mcp__server__.*` para MCP); salida vía `hookSpecificOutput` (`permissionDecision: "allow"|"deny"|"ask"|"defer"` + `permissionDecisionReason`, `updatedInput` en PreToolUse; `updatedToolOutput`, `additionalContext` en PostToolUse); callback de 3 argumentos con acceso por diccionario en Python. Agravante doble: v1.2 ya tenía la sintaxis correcta (regresión) y la propia deuda conocida del corpus admitía no haber confirmado la sintaxis, pero se publicó código concreto igualmente. **[CORREGIDO]**
- [C2] §1.1 — Ausencia total de `stop_reason` (`"tool_use"` vs `"end_turn"`), vocabulario **literal** del blueprint (TS 1.1: "control flow that continues when stop_reason is 'tool_use' and terminates when stop_reason is 'end_turn'"). **[CORREGIDO: párrafo que conecta la abstracción del SDK con el stop_reason subyacente y los valores de ResultMessage]**
- [C3] §1.3 — Faltaban los patrones `mcp__server` / `mcp__server__*` / `mcp__*` en `disallowedTools` (confirmados en la tabla de AgentDefinition de la doc de subagents; ya cerrado en v1.2 — regresión). **[CORREGIDO, incluida la mención de `mcpServers` con tipo `(string | object)[]`]**

## MEJORA (no bloquea)

- [M1] `AgentDefinition` omitía `background`, `permissionMode`, `initialPrompt` (las notas ya capturaban `background`). **[APLICADA]**
- [M2] §1.1 no explicaba `maxBudgetUsd`/`max_budget_usd` pese a cubrir `error_max_budget_usd`. **[APLICADA]**
- [M3] §1.2/1.3 — matiz: el coordinator puede resumir el mensaje final del subagente; para preservarlo textual hay que pedirlo en el prompt. **[APLICADA]**
- [M4] §1.5 — bloqueo en base al resultado en PostToolUse (v1.2 lo marca como distractor peligroso: `permissionDecision` no tiene efecto en PostToolUse). El verificador no pudo confirmar al 100% el mecanismo alternativo en la doc viva. **[APLAZADA: queda en deuda conocida con nota de verificación pendiente — no se publica contenido no confirmado]**
- [M5] §1.7 — mención de `ClaudeSDKClient` (Python) como gestión automática de sesión. **[APLICADA, breve]**
- [M6] Proceso: un `<!-- HUECO -->` reconocido derivó en código publicado como hecho. **[Lección incorporada: el corrector re-verifica la sintaxis en vivo antes de escribir; considerar regla explícita en el agent redactor-didactico]**

## Deriva vs v1.2 (resumen)

- [A] HUECOS A RELLENAR confirmados: stop_reason/tool_use/end_turn (C2), max_budget_usd (M2), patrones mcp__ (C3), PostToolUse post-hoc (M4, aplazado), resumen del mensaje del subagente (M3). Menores en deuda: routing vía description (no exigido por TS 1.6), ClaudeSDKClient (M5, aplicado breve).
- [B] Nuevo OK verificado: tipos de mensaje completos (SystemMessage con subtypes compact_boundary/informational/worker_shutting_down, StreamEvent) y subtypes de ResultMessage.
- [C] **Contradicción directa** v1.2 vs corpus en la sintaxis de hooks → resuelta a favor de v1.2 + doc oficial en vivo (ver C1).

## Matriz de cobertura

| TS | Estado tras correcciones |
|---|---|
| 1.1 | Completo (C2, M2 aplicados) |
| 1.2 | Bueno (cifras 3-5 subagentes y 90% verificadas; M3 aplicada) |
| 1.3 | Completo (C3, M1 aplicados) |
| 1.4 | Corregido (sintaxis real de hooks) |
| 1.5 | Corregido (sintaxis); M4 en deuda con verificación pendiente |
| 1.6 | Bueno |
| 1.7 | Bueno (continue/resume/fork verificados; M5 añadida) |

## Enlaces verificados
- OK: 5/6 en vivo (agent-loop, subagents, hooks, sessions, built-multi-agent-research-system) · skilljar requiere login (sin cambios) · Rotos: ninguno.

## Correcciones aplicadas por el orquestador (2026-08-05)
C1–C3 y M1–M3/M5 según arriba, con la sintaxis re-verificada en vivo por el agente corrector antes de escribir; M4 documentada como deuda; frontmatter `estado: borrador → verificado`.
