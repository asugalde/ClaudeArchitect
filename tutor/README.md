# Tutor de estudio CCAR-F — montaje en un Proyecto de Claude

Convierte el material del curso en un tutor interactivo al que preguntar dudas, pedir quiz oral y repasar errores.

## Pasos

1. En claude.ai → **Projects → Create project** (p. ej. "Tutor CCAR-F").
2. En **Instructions** del proyecto, pega el contenido íntegro de `instrucciones-tutor.md`.
3. En **Files**, sube el material (desde tu copia local del repositorio):
   - **Imprescindible**: los 6 corpus — `corpus/bloque-0-*.md` … `corpus/bloque-5-*.md` (fuente de verdad del material) — y `fuentes/exam-guide-oficial-v1.0.txt` (la guía oficial del examen: autoridad máxima; solo existe en tu copia local, no en el sitio publicado).
   - Recomendado: las 6 guías — `recursos/guias/bloque-N/guia_v1.0.md`.
   - Opcional: los bancos de preguntas — `recursos/quiz/bloque-N/preguntas_v1.0.json` (permiten la "sesión de errores" con las preguntas exactas y que el tutor calibre el estilo de las suyas).
4. Abre un chat del proyecto y prueba: `pregúntame sobre el bloque 3` o `explícame stop_reason`.

## Notas

- Los `.md` del corpus son la referencia que el tutor debe citar (bloque + task statement); si el corpus sube de versión, resube los ficheros cambiados.
- La guía oficial (`.txt` o PDF) es para tu proyecto **personal**: si contiene la guía, no compartas el proyecto con terceros (la regla del curso es no redistribuirla). Las instrucciones incluyen además la URL canónica para que el tutor pueda avisarte si Anthropic publica una versión nueva.
- El tutor complementa —no sustituye— los quizzes y el simulacro del curso: la nota escalada solo la dan estos.
