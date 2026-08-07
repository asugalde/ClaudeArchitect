# Informe de verificación — corpus/bloque-1-prompt-engineering.md (2026-08-05)

Veredicto: **APTO CON CAMBIOS** — 0 críticos · 5 mejoras. Las mejoras M1–M4 se aplicaron el 2026-08-05 (ver "Correcciones aplicadas" al final); la M5 se descartó por estar fuera del blueprint (justificación en el propio hallazgo).

No se han encontrado errores técnicos, contradicciones con la guía oficial ni contenido fuera de alcance. Las citas de líneas a `exam-guide-oficial-v1.0.txt` son exactas para los 6 task statements. Se verificaron 7 URLs (100%): todas resuelven y su contenido respalda las afirmaciones del corpus, incluida la lista de parámetros no soportados en batch, confirmada literalmente contra la doc viva de Anthropic.

## CRÍTICO (bloquea el gate)
Ninguno.

## MEJORA (no bloquea)
- [M1] §4.6 — la guía oficial enumera tres *skills* distintos: (1) instancia independiente, (2) split local/integration, (3) *"running verification passes"* con confidence self-report. El corpus fusionaba (3) dentro de (2), sin representar una pasada de verificación independiente como sí hacía v1.2 (Pass 3, instancia D). **[APLICADA]**
- [M2] §4.5 — faltaba el formato exacto de `custom_id` (1-64 caracteres, `^[a-zA-Z0-9_-]{1,64}$`), documentado en la fuente citada y potencial distractor de examen. **[APLICADA]**
- [M3] §4.3 — la lista de soportado/no-soportado en JSON Schema strict era un subconjunto presentado con aire de exhaustividad. **[APLICADA: matizada como lista no exhaustiva con puntero a la doc]**
- [M4] "Mapa del bloque" sin enlaces a los anchors `{#ts-1-N}` (v1.2 sí enlazaba). **[APLICADA]**
- [M5] §4.1 — v1.2 incluía estructura de prompt recomendada (context→task→examples→format→constraints) y role-prompting; no exigida por los knowledge/skills oficiales de TS 4.1. **[DESCARTADA: fuera de blueprint]**

## Deriva vs v1.2

- [A] Ausente: estructura de prompt "context→task→examples→format→constraints" + role-prompting (v1.2 §1.1) → **OBSOLETO/FUERA DE BLUEPRINT** para TS 4.1.
- [A] Ausente: tags `<thinking>` embebidos en few-shot (v1.2 §1.2) → **OBSOLETO** (la guía solo exige "show reasoning", no una etiqueta concreta).
- [A] Ausente: límite numérico "2-3 reintentos máximo" (v1.2 §1.4) → **OBSOLETO** (sin fuente oficial; correctamente omitido).
- [A] Ausente: pasada de verificación explícita como tercera instancia (v1.2 §1.6, Pass 3) → **HUECO A RELLENAR** (ver M1). **[CERRADO]**
- [A] Ausente: formato de `custom_id` → **HUECO A RELLENAR** menor (ver M2). **[CERRADO]**
- [B] Nuevo: lista de tipos soportados/no soportados en strict mode → **DUDOSO** (correcta pero incompleta — ver M3). **[MATIZADA]**
- [B] Nuevo: parámetros no soportados en batch → **OK** (verificado literal contra doc viva).
- [B] Nuevo: límites de batch (100k/256MB, <1h típico/24h máx., resultados 29 días) → **OK** (verificado).
- [C] Contradicciones: **ninguna detectada** (coinciden: 50% descuento y 24h de batch, semántica de strict, tool_choice, rangos few-shot, límites de self-review).

## Matriz de cobertura

| Task statement | Sección | Estado |
|---|---|---|
| 4.1 | Criterios explícitos y falsos positivos | Cubierto |
| 4.2 | Few-shot prompting | Cubierto |
| 4.3 | Tool use y JSON schemas | Cubierto (M3 aplicada) |
| 4.4 | Validación, retry y feedback loops | Cubierto |
| 4.5 | Batch processing | Cubierto (M2 aplicada) |
| 4.6 | Multi-instancia y multi-pass review | Cubierto (M1 aplicada) |

## Enlaces verificados
- OK: 7/7 · Rotos: [] · Redirigidos: [] (best-practices, structured-outputs, strict-tool-use, batch-processing, develop-tests, prompt-eng-interactive-tutorial, claude-cookbooks).

## Correcciones aplicadas por el orquestador (2026-08-05)
- M1: añadida la pasada de verificación independiente como tercera variante arquitectónica de §4.6 (trazada al skill oficial "running verification passes" de TS 4.6).
- M2: añadido el formato de `custom_id` (1-64 caracteres, `^[a-zA-Z0-9_-]{1,64}$`) en §4.5.
- M3: la lista de strict mode queda marcada como no exhaustiva, con puntero a la página oficial structured-outputs.
- M4: el mapa del bloque enlaza ahora a los anchors de cada sección.
- Frontmatter: `estado: borrador → verificado`.
