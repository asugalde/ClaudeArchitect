# Guía de estilo — material de estudio CCAR-F

Reglas obligatorias para toda prosa generada (referencia y guías de bloque). El objetivo: material que se entiende leyéndolo una vez, sin ser un esquema ni un volcado de documentación.

## Voz y estructura de cada lección

**Prohibido el "PowerPoint prose"**: fragmentos telegráficos, listas de sintagmas sin verbo, cadenas de flechas (`A → B → falla`). Las listas se reservan para enumeraciones reales (valores de un parámetro, pasos de un procedimiento).

Cada concepto de una **lección de bloque** se desarrolla con esta progresión (sin titularla explícitamente, debe fluir):
1. **Qué es y por qué existe** — el problema que resuelve, en 2–4 frases.
2. **Cómo funciona** — con el ejemplo desarrollado: código o configuración REAL comentada, no pseudocódigo.
3. **Caso de producción** — "en producción te encuentras con X…" anclado al estilo de los escenarios del examen (métricas, logs, síntomas concretos).
4. **Anti-patrón narrado** — qué haría alguien razonable pero equivocado, POR QUÉ falla, y qué distractor de examen genera.
5. **Regla mnemotécnica o tabla de decisión** cuando hay elección entre alternativas.

En un **capítulo de referencia** la progresión es la de su plantilla (denso, sin narrativa de producción extensa), pero se mantiene la regla de desarrollo: nada de bullets crípticos; cada afirmación con sujeto, verbo y consecuencia.

## Idioma

- Prosa en **español**. Preguntas de quiz en **inglés** (las genera otro agente; no mezclar).
- Término técnico en inglés en su primera aparición, con glosa: «el *system prompt* (instrucciones de sistema)». Después, úsalo en inglés sin glosa.
- SIEMPRE en inglés y en `inline code`: identificadores, campos JSON/YAML, flags CLI, rutas de configuración, valores de enum (`stop_reason`, `tool_choice: "any"`, `-p/--print`, `.mcp.json`, `context: fork`).
- No traducir nombres propios de features: plan mode, hooks, skills, Task tool, Message Batches API.

## Código, configuración y markdown

- Fences con lenguaje: ```json, ```python, ```yaml, ```bash, ```mermaid. Ejemplos ejecutables o copiables tal cual; comentarios del código en inglés.
- Patrones glob y cualquier texto con `**` van SIEMPRE dentro de backticks (`**/*.test.tsx`); nunca en prosa desnuda (los editores WYSIWYG los corrompen).
- Tablas solo para datos enumerables cortos; la explicación va en la prosa circundante, no en las celdas.
- Anchors estables: los títulos de sección de la referencia no se renombran entre MINORs (rompen los enlaces de las guías).

## Diagramas mermaid

- Úsalos cuando hay flujo, jerarquía o arquitectura; nunca como decoración. Máximo ~10 nodos por diagrama; etiquetas cortas; sin estilos custom (tema por defecto).
- Tipos preferidos: `flowchart TD/LR` (flujos y jerarquías), `sequenceDiagram` (bucle agéntico, handoffs).
- Todo diagrama lleva 1–2 frases de lectura guiada debajo ("El diagrama muestra que…").

## Mini-checks (guías de bloque)

Formato EXACTO en el markdown fuente (el generador de HTML lo convierte al componente interactivo):

```markdown
> **Mini-check N.** <pregunta en español, una sola frase>
> - [ ] A. <opción>
> - [x] B. <opción correcta>
> - [ ] C. <opción>
>
> _Respuesta: B — <justificación en 1–2 frases>._
```

Reglas: 3–6 por guía, colocados tras la lección que evalúan; una sola correcta (los multiple-response se dejan para el quiz); la justificación siempre presente.

## Rigor

- Nada inventado: si el material de entrada no lo respalda, se marca `<!-- HUECO: descripción -->` y se sigue.
- Cifras y límites, literales de la fuente (60 preguntas, 720/1000, 24 h del batch, 500 $ del hook…).
- Las citas de fuente van al final de cada sección (referencia) o en la lista final anotada (guías), no inline en cada frase.
- Longitudes orientativas: lección de bloque 400–900 palabras por task statement; sección de referencia 250–600. Si sobra, recorta relleno, no contenido técnico.
