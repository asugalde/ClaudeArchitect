---
name: iterar-formato-recurso
description: Etapa 4b del pipeline CCAR-F (modo pruebas) - genera UN tipo de recurso (flashcards|guia|quiz|pdf-resumen) para un bloque piloto y lo itera con el usuario, gateado paso a paso, hasta que el formato quede validado en versiones.json → formato_validado. Uso - /iterar-formato-recurso <tipo> <bloque>.
---

# /iterar-formato-recurso <tipo> <bloque>

Modo pruebas de formato: se usa mientras `versiones.json → formato_validado.<tipo>` sea `false`. Cuando los 4 tipos estén en `true`, la generación pasa a `/generar-recursos` (sin gates de formato).

**Prerequisito**: el corpus del bloque piloto está `aprobado` (gate de `/consolidar-corpus`).

## Proceso

1. **Lee** `ESTADO.md`, `versiones.json` y el corpus del bloque (`corpus/bloque-N-*.md`).
2. **Genera el recurso** según el tipo:
   - **flashcards**: despacha `generador-flashcards` (model: haiku) → `recursos/flashcards/mazos/mazo-bloque-N_vX.Y.json`; valida contra `plantillas/esquema-flashcard.schema.json` (script o validación manual exhaustiva); inyecta el JSON en `plantillas/flashcards.template.html` → `recursos/flashcards/html/flashcards-bloque-N_vX.Y.html`.
   - **guia**: despacha `redactor-didactico` (model: sonnet, modo `leccion-bloque`) → `recursos/guias/bloque-N/guia_vX.Y.md`; genera el HTML con `plantillas/guia-interactiva.template.html` → `guia_vX.Y.html`.
   - **quiz**: despacha `generador-quiz` (model: sonnet) → `recursos/quiz/bloque-N/preguntas_vX.Y.json`; valida contra `plantillas/esquema-pregunta.schema.json`; inyecta en `plantillas/quiz.template.html` → `quiz_vX.Y.html`.
   - **pdf-resumen**: despacha `generador-resumen-pdf` (model: sonnet) → HTML compacto desde `plantillas/resumen-pdf.template.html` → PDF con `herramientas/html-a-pdf.ps1`.
3. **Verificación técnica automática** antes de enseñar nada: abre el HTML en Edge headless (o revisa estáticamente) — sin errores JS, JSON inyectado parsea, tema claro/oscuro, sin desbordes obvios; los JSON pasan su schema; el PDF se genera sin errores de mermaid.
4. **GATE de formato (regla dura)**: presenta el recurso al usuario y espera su feedback. Itera (contenido, plantilla, schema) hasta que **valide explícitamente el formato**. Cada iteración se pliega sobre la misma versión durante las pruebas.
5. **Al validar**: `versiones.json → formato_validado.<tipo> = true`, registra el recurso en `versiones.json → recursos.bloques.N.<tipo>` (con `generado_desde_corpus`), línea en `ESTADO.md`. La plantilla y el schema del tipo quedan CONGELADOS (cambios posteriores = decisión explícita del usuario).

## Reglas
- Contenido de tarjetas/preguntas en **inglés**; UI en español.
- El JSON es la fuente única del recurso; el HTML se regenera desde él, nunca se edita a mano.
- HTML autocontenido (JS vanilla; solo mermaid CDN si aplica). Identidad visual consistente con el curso (variables CSS de las plantillas existentes).
- Todo ítem generado lleva `refSeccion` que debe existir como anchor en el corpus del bloque.
