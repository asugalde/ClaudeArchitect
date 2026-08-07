# Informe de verificación — corpus/bloque-2-claude-code.md (2026-08-05)

Veredicto: **APTO CON CAMBIOS** — 2 críticos · 9 mejoras/huecos. Críticos corregidos y huecos de prioridad alta/media aplicados por el orquestador el 2026-08-05 (ver "Correcciones aplicadas"); los menores quedan en deuda conocida.

## CRÍTICO (bloquea el gate)

- [C1] Numeración de encabezados: decían `## 2.1 —`…`## 2.6 —` cuando corresponden a los TS **3.1–3.6** (D3), rompiendo la convención de los demás corpus (número visible = task statement real) y colisionando con los TS 2.x reales de D2 (bloque 3). Los anchors `{#ts-2-*}` sí siguen el patrón del proyecto y se conservan. **[CORREGIDO: encabezados renombrados a 3.1–3.6]**
- [C2] §TS 3.2 — afirmación incorrecta: "una skill sin `description` no se auto-invoca". La doc oficial ("Extend Claude with skills") dice que si se omite, **se usa el primer párrafo del markdown como descripción**: la skill sigue siendo candidata a auto-invocación, con peor matching. Presentado como trampa de examen inducía a error. **[CORREGIDO: reescrito con el fallback real]**

## MEJORA / HUECOS

- [M1] §TS 3.6 — el trigger por defecto del workflow `@claude` es `issue_comment`/`pull_request_review_comment`; los triggers `pull_request: [opened, synchronize]` e `issues: [opened, assigned]` son de ejemplos específicos. **[APLICADA: distinción aclarada]**
- [M2] §TS 3.6 — la revisión automática sin mención `@claude` la cubre la página oficial **GitHub Code Review** (`code.claude.com/docs/en/code-review`). **[APLICADA: fuente añadida y hueco cerrado]**
- [A-alta] "CLAUDE.md se inyecta como mensaje de usuario tras el system prompt, sin garantía de cumplimiento estricto" (trampa clásica de TS 3.1, confirmada vigente). **[APLICADA]**
- [A-alta] "`.claude/rules/`/CLAUDE.md son guía no vinculante; para bloquear de verdad, hook `PreToolUse`" (confirmado vigente). **[APLICADA]**
- [A-media] Campos de frontmatter `disallowed-tools` y `user-invocable` como distractores frente a `allowed-tools`/`disable-model-invocation` (confirmados vigentes). **[APLICADA]**
- [A-media] Trampa `/compact` vs `/clear` (confirmada vigente en best-practices). **[APLICADA]**
- [A-menor] `claudeMdExcludes` en monorepos. **[APLICADA]**
- [A-menor] Profundidad máxima de 4 saltos en `@import` recursivo (hallazgo nuevo). **[APLICADA]**
- [A-deuda] Niveles enterprise de skills, precedencia enterprise>personal>project, skills anidadas (`apps/web:deploy`), `skillOverrides`, campos avanzados (`paths`, `model`, `effort`, `background`, `agent`, `shell`, `arguments`), `/goal` condition y Stop hook como verification gate → **quedan en Deuda conocida** (el blueprint de TS 3.2 no los exige).

## Deriva vs v1.2 (resumen)

- [B] Nuevo OK verificado: auto memory (200 líneas/25KB, toggle), booleanos de frontmatter case-insensitive.
- [B] Nuevo INCORRECTO: la afirmación de C2 (error de novo, no venía de v1.2). **[CORREGIDO]**
- [C] Contradicciones directas: **ninguna** (todas las divergencias eran omisiones).

## Matriz de cobertura

| Task statement | Estado |
|---|---|
| 3.1 | Completa (trampa system-prompt/user-message y claudeMdExcludes añadidas) |
| 3.2 | Completa (C2 corregido; distractores de frontmatter añadidos; enterprise en deuda) |
| 3.3 | Completa (guía no vinculante → PreToolUse añadida) |
| 3.4 | Completa y precisa |
| 3.5 | Completa (/compact vs /clear añadida) |
| 3.6 | Completa (M1, M2 aplicadas) |

## Enlaces verificados
- OK: 7/7 · Rotos: ninguno · Redirigidos: ninguno.

## Correcciones aplicadas por el orquestador (2026-08-05)
C1, C2, M1, M2 y los 6 huecos [A] de prioridad alta/media/menor listados arriba; deuda conocida ampliada con los ítems [A-deuda]; frontmatter `estado: borrador → verificado`.
