---
name: generar-recursos
description: Etapa 4 del pipeline CCAR-F (régimen estable) - genera los 4 recursos de estudio de uno o varios bloques desde el corpus aprobado, sin gates de formato. Exige corpus con gate aprobado y formato_validado=true para cada tipo. '/generar-recursos simulacro' compone el simulacro desde los bancos existentes. Uso - /generar-recursos [0-5|todos|simulacro].
---

# /generar-recursos [bloque|todos|simulacro]

Generación en régimen estable: corre entera sin gates intermedios. Los dos candados previos son duros:

1. `versiones.json → corpus.gate_general.estado == "aprobado"` (o, para un bloque suelto, su `corpus.bloques.N.corpus.estado == "aprobado"`).
2. `versiones.json → formato_validado.<tipo> == true` para CADA tipo a generar. Si alguno está en `false`, ese tipo se genera solo vía `/iterar-formato-recurso` (modo pruebas); avisa y sáltalo.

## Proceso por bloque (bloques en paralelo; dentro del bloque, los 4 tipos en paralelo)

1. **Lee** `ESTADO.md`, `versiones.json`, `corpus/corpus.yaml` y determina versión de los recursos (nueva MINOR si ya existen; nunca sobrescribir).
2. **Despacha los generadores** (mismos contratos que en `/iterar-formato-recurso`):
   - `generador-flashcards` (haiku) → mazo JSON → `generar-flashcards-html.py` → HTML.
   - `redactor-didactico` (sonnet, `leccion-bloque`) → guía md → conversión a HTML con `plantillas/guia-interactiva.template.html` (agente sonnet de conversión con el contrato de markup de la plantilla).
   - `generador-quiz` (sonnet) → banco JSON → `generar-quiz-html.py` → HTML.
   - `generador-resumen-pdf` (sonnet) → HTML compacto → `herramientas/html-a-pdf.ps1` → PDF.
3. **Verificación técnica automática**: schemas y anchors (los .py ya fallan en explícito), render en Edge headless (JS ejecuta, sin placeholders, sin datos demo), páginas del PDF (1-3).
4. **Verificación de contenido**: al cierre del lote, `verificador-contenido` (sonnet) sobre los bancos/mazos nuevos (tipo JSON) por muestreo.
5. **Registra** cada recurso en `versiones.json → recursos.bloques.N.<tipo>` con `generado_desde_corpus`, y una línea en `ESTADO.md`. Si el corpus del bloque sube de versión después, estos recursos quedan desactualizados hasta regenerarse.

## `/generar-recursos simulacro`

Compone `recursos/simulacro/preguntas_vX.Y.json` tomando preguntas VERBATIM de los bancos vigentes de los 6 bloques, proporcional a los pesos del blueprint (D1 27% / D3 20% / D4 20% / D2 18% / D5 15%; el bloque 0 aporta pocas, es transversal), 60 preguntas, barajado determinista, cobertura de todos los task statements posibles y mezcla de dificultad. Config del banco: `solo_examen: true`, `duracion_examen_min: 120`. Después `generar-quiz-html.py` → `recursos/simulacro/simulacro_vX.Y.html`. Requiere los 6 bancos generados.

## Reglas
- Contenido de quiz/flashcards en inglés; guías y resumen en español.
- El JSON es la fuente única de quiz y flashcards; el HTML se regenera, nunca se edita.
- Nada que no esté en el corpus del bloque. Deuda conocida fuera.
