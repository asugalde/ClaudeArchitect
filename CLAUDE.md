# Proyecto: Certificación Claude Certified Architect – Foundations (CCAR-F)

Sistema de generación de material de estudio para el examen CCAR-F.

> **NOTA TRANSICIONAL (2026-08-05, actualizada 2026-08-07):** el proyecto se replanteó desde cero. El material v1.2 anterior fue **eliminado definitivamente** (2026-08-07, decisión del usuario; el proyecto nuevo diverge totalmente del anterior — no referenciar su material ni su canal de publicación). Este fichero se reescribirá en versión definitiva al cerrar los gates de formato. Mientras tanto: **leer `ESTADO.md` al empezar cualquier sesión.**

## Pipeline nuevo (en construcción)

```
1. /adquirir-guia-oficial      → fuentes/exam-guide-oficial-vX.Y.{pdf,txt} + diff vs versión anterior
2. /investigar-fuentes [N|todos] → fuentes/fuentes.yaml actualizado + corpus/notas/bloque-N-notas.md
3. /consolidar-corpus [N|todos]  → corpus/bloque-N-*.md + corpus/corpus.yaml + corpus/contraste/informe-*.md
   ══ GATE ÚNICO: el usuario revisa el corpus y aprueba ══
4. /generar-recursos [N|todos]   → recursos/ (guías, quizzes, flashcards, PDFs de resumen, simulacro)
   4b. /iterar-formato-recurso <tipo> <bloque>  → modo pruebas gateado, hasta validar cada formato
5. /distribuir                   → dist/ (canal final por definir)
```

Contrato entre etapas: cada skill solo lee lo que escribió la anterior. El corpus (`corpus/*.md`) es **la fuente de verdad** del material generado. (El contraste contra la referencia v1.2 se ejecutó durante la consolidación — informes en `corpus/contraste/` —; el material v1.2 ya no existe, así que futuras re-verificaciones del corpus serán solo contra la guía oficial y la doc oficial en vivo.)

## Estructura

```
├── ESTADO.md                # estado vivo del pipeline — LEER AL EMPEZAR
├── fuentes/                 # entradas: guía oficial del examen + catálogo fuentes.yaml (NUNCA va a dist/)
├── corpus/                  # fuente de verdad consolidada (un .md por bloque + corpus.yaml + notas + contraste)
├── recursos/                # salida: guias/ quiz/ flashcards/ pdf/ simulacro/
├── plantillas/              # plantillas HTML/md y schemas (reutilizadas de v1.2 + nuevas)
├── herramientas/            # html-a-pdf.ps1 (Edge headless) + construir-dist.py (por reescribir)
├── versiones.json           # manifest de versiones, gates y trazabilidad del pipeline nuevo
└── .claude/                 # skills y agents del pipeline nuevo
```

## Reglas (se mantienen del proyecto anterior)

- **Jerarquía de fuentes**: guía oficial del examen > docs oficiales Anthropic (docs.claude.com / platform.claude.com) y modelcontextprotocol.io > terceros de calidad marcados `[NO OFICIAL]`. Si dos fuentes contradicen, gana la de mayor rango y se anota. Nada inventado: toda afirmación técnica trazable a una fuente.
- **Idioma**: prosa didáctica en español (términos técnicos en inglés en primera mención); preguntas de quiz, simulacro y flashcards en **inglés** (condiciones reales del examen; la UI puede estar en español); código, identificadores y configuración en inglés.
- **Versionado**: artefactos `<nombre>_vMAYOR.MINOR.<ext>`; las versiones antiguas no se borran ni sobrescriben. Todo recurso registra en `versiones.json` desde qué versión del corpus se generó (`generado_desde_corpus`).
- **Gates**: durante la fase de pruebas de formato, cada recurso se valida contigo paso a paso (`/iterar-formato-recurso`); en régimen estable solo existe el GATE único corpus→recursos. La aprobación es siempre explícita del usuario, nunca inferida.
- **HTML autocontenido**: JS vanilla, sin build; única dependencia externa permitida, mermaid vía CDN. PDF con `herramientas/html-a-pdf.ps1` (Edge headless, `?print=1` revela respuestas).
- **Quiz/flashcards**: el JSON es la fuente única (validar contra su schema en `plantillas/`); el HTML se regenera desde el JSON, nunca se edita a mano.
- **Subagentes**: siempre con `model` explícito — haiku para extracción/tareas mecánicas, sonnet para redacción/verificación.
- **Markdown**: editar solo con editores de texto plano (los WYSIWYG corrompen `**` en código inline).
- **Distribución**: `dist/` es el único distribuible; **nunca** incluye `fuentes/` ni el PDF oficial del examen. Canal de publicación por definir.
- **Git**: repo sin commits todavía; el primer commit y el modelo de ramas los decide el usuario. No commitear sin petición explícita.
