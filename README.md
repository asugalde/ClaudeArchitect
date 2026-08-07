# Material de estudio CCAR-F

Material de estudio **no oficial** para el examen **Claude Certified Architect – Foundations (CCAR-F)**, elaborado a partir de documentación pública de Anthropic (docs.claude.com, platform.claude.com, modelcontextprotocol.io) y de la guía oficial del examen. No reproduce preguntas del examen real.

## Contenido

- **Índice del curso** (`recursos/index_v1.0.html`): portada con introducción, blueprint de dominios y pesos, seguimiento de progreso (localStorage) y acceso a todos los recursos. **Empieza por aquí.**
- **Guías interactivas** (`recursos/guias/bloque-N/`): una por bloque (0–5), con lecciones, mini-checks autocorregibles, diagramas y referencias oficiales.
- **Quizzes** (`recursos/quiz/bloque-N/`): 18 preguntas por bloque en inglés (condiciones reales del examen), modos estudio y examen.
- **Simulacro** (`recursos/simulacro/`): examen completo de 60 preguntas, 120 minutos, composición por los pesos del blueprint y corte oficial 720/1000.
- **Flashcards** y **resumen imprimible** (`recursos/flashcards/`, `recursos/pdf/`): bloque 0 (piloto); el resto se generará al cerrar la validación de formato.

Todo es HTML autocontenido (JS vanilla; únicas dependencias externas: Google Fonts y mermaid vía CDN). El progreso se guarda en el navegador (localStorage): cambiar de dispositivo o navegador lo reinicia.

## Cómo estudiar

Abre `recursos/index_v1.0.html` en el navegador y navega desde ahí. El botón **Continuar** retoma donde lo dejaste; cada bloque se marca completado automáticamente al leer su guía entera y aprobar su quiz.

## Estructura del proyecto

```
├── ESTADO.md        # estado vivo del pipeline — leer al empezar cualquier sesión
├── fuentes/         # entradas: guía oficial del examen + catálogo de fuentes (NUNCA se distribuye)
├── corpus/          # fuente de verdad consolidada (un .md por bloque, verificado y aprobado)
├── recursos/        # salida: index, guías, quizzes, simulacro, flashcards, resúmenes
├── plantillas/      # plantillas HTML (sistema de diseño Volt) y schemas JSON
├── herramientas/    # generadores (los HTML de quiz/flashcards/index se regeneran desde su JSON/manifest)
└── versiones.json   # manifest de versiones, gates y trazabilidad
```

El pipeline de generación (adquisición de guía oficial → investigación de fuentes → consolidación de corpus → generación de recursos) está descrito en `CLAUDE.md` y su estado en `ESTADO.md`.

## Regenerar recursos

Requisitos: Python 3 y Microsoft Edge (para verificación headless y PDFs).

```bash
python herramientas/generar-quiz-html.py <preguntas.json> <salida.html>
python herramientas/generar-flashcards-html.py <mazo.json> <salida.html>
python herramientas/generar-index-html.py
python herramientas/componer-simulacro.py
```

Los JSON son la fuente única de quizzes y flashcards: el HTML se regenera siempre, nunca se edita a mano.

---

*Material de estudio personal, no afiliado a Anthropic. Los nombres de productos y la documentación citada pertenecen a sus propietarios.*
