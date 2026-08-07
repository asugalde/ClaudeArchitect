# Informe de verificación — corpus/bloque-0-fundamentos.md (2026-08-05)

Veredicto: APTO CON CAMBIOS → **críticos corregidos por el orquestador el 2026-08-05** (ver "Correcciones aplicadas" al final). Mejoras y deriva pendientes de la decisión del usuario en el gate.

## CRÍTICO (bloquea el gate)

- [C1] bloque-0-fundamentos.md §0.1 — La sección afirmaba que el `content` de la respuesta del asistente es un "array de blocks: `text`, `tool_use`, `tool_result`, `image`, `document`". Incorrecto: los bloques `tool_result` (y las imágenes/documentos que puede contener) pertenecen a los mensajes `role: "user"` que el CLIENTE envía a Claude, no a la respuesta del asistente. Confirmado en "Handle tool calls" (platform.claude.com): *"user messages include client content and tool_result, while assistant messages contain AI-generated content and tool_use."* Riesgo real de examen: confunde qué bloques puede emitir el modelo vs qué bloques construye el cliente (distinción que TS 1.1 examina).

- [C2] bloque-0-fundamentos.md §0.2 y §0.5 — El corpus afirmaba que `strict: true` "requiere que `tool_choice` sea `any` o tool forzado", y lo repetía como "trampa de examen" con la respuesta incorrecta presentada como correcta. **Falso**: según la página oficial "Strict tool use", strict funciona por *grammar-constrained sampling* sobre el `input` **independientemente del valor de `tool_choice`** — garantiza que, siempre que Claude llame a esa tool (con `auto`, `any` o forzada), el input cumple el schema. El tip de "Define tools" ("Combine `tool_choice: any` with strict tool use to guarantee BOTH that a tool will be called AND that inputs follow the schema") describe una garantía *compuesta* (llamada + conformidad), no una dependencia de strict respecto a tool_choice.

## MEJORA (no bloquea) — TODAS APLICADAS el 2026-08-05

- [M1] §0.6 — La cifra "~10-12% documentado" no coincidía con la fuente: el exam guide (Sample Question 1, pág. 27) dice literalmente "in **12%** of cases". **[APLICADA: 12% en las dos apariciones]**
- [M2] §0.2 — Faltaba la restricción oficial "`input_examples` no soportado en server-side tools" (confirmada en "Define tools"). **[APLICADA]**
- [M3] §0.3 — No se nombraban los tools Anthropic-schema client-executed (`memory`, `bash`, `text_editor`, `computer`). **[APLICADA]**
- [M4] §0.3 — El contenido de `tool_result` omitía el tipo `search_result`. **[APLICADA]**
- [M5] Frontmatter — Añadir la fuente "Strict tool use". **[APLICADA junto con la corrección de C2]**
- [M6] §0.1 — Faltaba el patrón de mensajes `assistant` sintéticos (few-shot, contexto preconfigurado), confirmado en "Using the Messages API". **[APLICADA]**

## Deriva vs v1.2

- [A] Ausente: mensajes `assistant` sintéticos como patrón válido (v1.2 §0.1) → **HUECO A RELLENAR** — vigente en la doc oficial actual (ver M6).
- [A] Ausente: "`input_examples` no soportado en server tools" (v1.2 §0.2) → **HUECO A RELLENAR** — vigente (ver M2).
- [A] Ausente: enumeración de tools Anthropic-schema (`bash`, `text_editor`, `memory`) como ejemplos de client tools (v1.2 §0.3) → **HUECO A RELLENAR** (menor) — vigente (ver M3).
- [A] Ausente: patrones de workflow "routing" y "parallelization" (v1.2 §0.6, del post "Building Effective Agents") → **OBSOLETO/FUERA DE FOCO** — TS 1.1/1.6 solo exigen distinguir "model-driven decision-making" de "pre-configured decision trees" y "fixed sequential pipelines" vs "dynamic adaptive decomposition"; omisión defendible.
- [A] Ausente: matiz "stateless del servidor ≠ sin memoria de la aplicación" (v1.2 §0.1, trampas) → **HUECO A RELLENAR** (menor, prioridad baja).
- [B] Nuevo: token cost de `input_examples` (20-50 / 100-200 tokens) → **OK** — verbatim en "Define tools".
- [B] Nuevo: incompatibilidad de `tool_choice: any`/forzada con extended thinking manual (solo adaptive) → **OK** — verbatim en "Define tools".
- [B] Nuevo: framing "4-5 tools con `action` vs 20 hiperespecíficas" → **OK** — coherente con el ejemplo "18 instead of 4-5" de TS 2.3.
- [B] Nuevo: dependencia de `strict` respecto a `tool_choice` → **INCORRECTO**, ver [C2] (error de novo, no venía de v1.2). **[CORREGIDO]**
- [B] Nuevo: tipos de content block de la respuesta incluyendo `tool_result`/`image`/`document` → **INCORRECTO**, ver [C1] (error de novo). **[CORREGIDO]**
- [C] Contradicciones directas v1.2 vs corpus: **ninguna detectada.**

## Matriz de cobertura

| Eje | TS oficial sustentado | Estado |
|---|---|---|
| 0.1 Anatomía Messages API | 1.1 | Completa; C1 corregido |
| 0.2 Definición de tools / JSON Schema | 2.1, 4.3 | Completa; C2 corregido; hueco M2 |
| 0.3 Ciclo tool_use/tool_result | 1.1 | Completa; huecos menores M3, M4 |
| 0.4 stop_reason | 1.1 | Completa y precisa (7 valores verificados verbatim) |
| 0.5 tool_choice | 2.3, 4.3 | Completa; C2 corregido |
| 0.6 Modelo vs workflow determinista | 1.1 | Completa; mejora M1 (cifra 12%) |

## Enlaces verificados

- OK: 6 de 6 (todas las URLs del frontmatter original) · Rotos: ninguno · Redirigidos: ninguno.
- Verificada además `strict-tool-use` (fuente que resuelve C2), añadida al frontmatter tras la corrección.

## Correcciones aplicadas por el orquestador (2026-08-05)

1. **C1**: §0.1 reescrito — la respuesta del asistente contiene solo blocks `text` y `tool_use`; `tool_result`/`image`/`document` pertenecen a mensajes `role: "user"` del cliente.
2. **C2**: §0.2 "Cómo funciona" reescrito (strict = grammar-constrained sampling, independiente de `tool_choice`; con `"any"` se logra la garantía compuesta) y la "trampa de examen" de §0.2 invertida para enseñar la respuesta correcta. Los pasajes de §0.5 y la tabla de decisión ya describían correctamente la garantía compuesta y no se tocaron.
3. **M5**: fuente "Strict tool use" añadida al frontmatter y a las fuentes de §0.2 (evidencia de la corrección C2).
4. Frontmatter: `estado: borrador → verificado` (sin críticos abiertos). M1–M4 y M6 quedan pendientes del gate.
