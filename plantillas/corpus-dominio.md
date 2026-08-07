# Plantilla — Fichero de corpus por bloque/dominio

Esqueleto obligatorio de cada `corpus/bloque-N-<slug>.md`. Sustituir `{{...}}` y repetir el bloque de task statement tantas veces como toque. Mantener los anchors estables entre versiones MINOR: los recursos generados (`refSeccion` de quizzes y flashcards) apuntan a ellos.

---

```yaml
---
bloque: {{N}}
nombre: "{{NOMBRE_BLOQUE}}"
dominio_oficial: "{{D1..D5 | null si transversal}}"
peso_examen: {{PORCENTAJE | null}}
version: "{{X.Y}}"
fecha: "{{FECHA_ISO}}"
guia_oficial_examen: "{{VERSION_GUIA_OFICIAL}}"
task_statements: ["{{N.1}}", "{{N.2}}", "..."]
fuentes:
  - {titulo: "{{...}}", url: "{{...}}", origen: "{{anthropic|mcp|partner|comunidad}}", tipo: "{{doc|curso|blog|repo}}"}
estado: borrador   # borrador | verificado | aprobado (lo actualizan las skills)
---
```

# Bloque {{N}} — {{NOMBRE_BLOQUE}} {#bloque-{{N}}}

{{PARRAFO_APERTURA: qué cubre el bloque, cómo encaja con los demás y qué juicio evalúa el examen aquí — 3-5 frases.}}

## Mapa del bloque

{{TABLA: task statement → sección → conceptos clave (una fila por TS).}}

---

## {{N}}.{{i}} — {{TITULO_TASK_STATEMENT}} {#ts-{{N}}-{{i}}}

> *Task statement oficial:* «{{ENUNCIADO_LITERAL_EN_INGLES}}»

**Concepto.** {{Qué es y por qué existe; el problema que resuelve. Prosa desarrollada, 2-5 frases.}}

**Cómo funciona.** {{Mecánica exacta con sintaxis/configuración literal en fences con lenguaje. Incluir valores por defecto, límites y comportamientos concretos.}}

```{{lang}}
{{EJEMPLO_MINIMO_COMPLETO}}
```

**Patrón correcto.** {{El enfoque que el examen premia y cuándo aplicarlo.}}

**Anti-patrones.** {{Cada anti-patrón documentado: qué es, POR QUÉ falla, y cómo aparece como distractor. Uno por párrafo o lista desarrollada.}}

**Trampas de examen.** {{Confusiones típicas entre opciones parecidas, palabras señal del enunciado ("first step", "most effective", "deterministic"), features inexistentes usadas como distractor.}}

**Fuentes.** {{Lista de citas de esta sección: título — URL. Marcar [NO OFICIAL] si aplica.}}

---

(… repetir por task statement …)

## Tabla de decisión del dominio {#ts-{{N}}-decision}

{{TABLA consolidada X vs Y del bloque: situación → elección correcta → por qué. P. ej.: plan mode vs directo, batch vs sync, hook vs prompt, Grep vs Glob vs Edit.}}

## Diagramas

{{Al menos uno si el dominio tiene flujo/arquitectura (mermaid). Con lectura guiada debajo.}}

## Deuda conocida

{{Lista de <!-- HUECO --> pendientes o "Ninguna".}}
