# Informe de verificación — corpus/bloque-5-contexto-fiabilidad.md (2026-08-05)

Veredicto: **APTO CON CAMBIOS** — 1 crítico · 4 mejoras. Corregidos por el orquestador el 2026-08-05 (ver "Correcciones aplicadas").

Contenido técnico sólido, bien acotado a D5, sin material out-of-scope y sin las cifras no trazables que v1.2 arrastraba. El crítico es de integridad del proceso de fuentes, no de exactitud del texto escrito.

## CRÍTICO (bloquea el gate)

- [C1] Las notas declaraban "7/7 fuentes procesadas", pero 2 fuentes asignadas al bloque en `fuentes.yaml` no aparecían citadas ni usadas, pese a cargar correctamente y ser pertinentes (verificado con WebFetch):
  - "Effective harnesses for long-running agents": describe exactamente el skill oficial de TS 5.4 (structured agent state exports/manifests, crash recovery) con artefactos concretos (`claude-progress.txt`, `feature_list.json` pass/fail, commits git como puntos de recuperación, `init.sh`).
  - "Prompt engineering for long context": scratchpad de extracción de citas que mejora el recall en contextos largos (TS 5.1).
  **[CORREGIDO: contenido de ambas incorporado en §5.4 y §5.1 con sus citas; fuentes añadidas al frontmatter]**

## MEJORA (no bloquea)

- [M1] Dos fences sin lenguaje (§5.2 system prompt, §5.4 parámetros de compaction). **[APLICADA]**
- [M2] Cita de "multi-agent research system" en §5.3 desalineada con la prosa (los fallos en cascada estaban en §5.2 sin cita). **[APLICADA: cita realineada]**
- [M3] pass@k vs pass^k y calibración de jueces (§5.5) exceden el Knowledge/Skills literal de TS 5.5: se ancla con una frase el porqué de la ampliación (fuente oficial asignada al bloque). **[APLICADA]**
- [M4] Umbral "0.70" del ejemplo de enrutamiento sin marca de ilustrativo. **[APLICADA: marcado como ejemplo ilustrativo, no cifra oficial]**

## Deriva vs v1.2

- [A] Ausente: framing "attention budget" (5.1) → HUECO menor (queda en deuda).
- [A] Ausente: catálogo de errores HTTP y stop_reason (5.3) → **OBSOLETO PARA D5**: ese material pertenece a D1/D2 (corrección de scope creep de v1.2, no regresión; vive en los corpus 0 y 4).
- [A] Ausente: `ESCALATION_CRITERIA` extendida con cifras `[NO OFICIAL]` (5.2) → **OBSOLETO**: sustituido por HUECO explícito (mejora de rigor).
- [A] Ausente: artefactos de recuperación de estado (5.4) → HUECO A RELLENAR (ligado a C1). **[CERRADO]**
- [A] Ausente: SEM / IC 95% (5.5) → **OBSOLETO** (fuente no asignada al bloque).
- [A] Ausente: umbrales/cadencias `[NO OFICIAL]` de 5.5 → **OBSOLETO** (mejora de rigor).
- [B] Nuevo: cita literal de la Sample Question 3 (55% FCR vs 80%) → **OK** (verificada palabra por palabra).
- [B] Nuevo: mermaid de escalación → **OK**.
- [C] Contradicciones: **ninguna** (reorganizaciones y eliminación de contenido no oficial).

## Matriz de cobertura

| TS | Estado |
|---|---|
| 5.1 | Cubierto (+ scratchpad de citas, C1) |
| 5.2 | Cubierto, HUECO declarado correctamente |
| 5.3 | Cubierto, correctamente acotado a D5 |
| 5.4 | Cubierto (+ artefactos de harnesses, C1) |
| 5.5 | Cubierto (M3, M4 aplicadas) |
| 5.6 | Cubierto (CitationAgent y claim-source verificados) |

## Enlaces verificados
- OK: 5/5 previas + las 2 incorporadas · Rotos: ninguno · Redirigidos: ninguno.

## Correcciones aplicadas por el orquestador (2026-08-05)
C1 (contenido de las 2 fuentes incorporado con cita y verificación en vivo), M1–M4; nota de las notas de extracción corregida implícitamente por esta incorporación; frontmatter `estado: borrador → verificado`.
