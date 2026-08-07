---
name: investigar-fuentes
description: Etapa 2 del pipeline CCAR-F - verifica y amplía el catálogo fuentes/fuentes.yaml y produce las notas de extracción por bloque (corpus/notas/) despachando investigador-fuentes (haiku) en paralelo. Uso - /investigar-fuentes [0-5|todos].
---

# /investigar-fuentes [bloque|todos]

Produce la materia prima del corpus: notas de extracción trazables por bloque.

**Prerequisito**: existe un `fuentes/exam-guide-oficial-vX.Y.txt` vigente (si no, ejecutar antes `/adquirir-guia-oficial`).

## Proceso

1. **Lee** `ESTADO.md`, `versiones.json` y `fuentes/fuentes.yaml`. Determina los bloques a procesar según el argumento.
2. **Extrae de la guía oficial** los task statements literales (en inglés) de cada bloque a procesar y la lista Out-of-Scope.
3. **Revisa el catálogo** de fuentes del bloque en `fuentes.yaml`: si hay indicios de URLs desactualizadas (dominio docs.anthropic.com, rutas antiguas), anótalo en el prompt del investigador para que use y registre las URL finales. Añade al catálogo las fuentes nuevas que el usuario haya indicado.
4. **Despacha `investigador-fuentes` (model: haiku), UNO POR BLOQUE, EN PARALELO** (un solo mensaje con múltiples Task). Cada despacho recibe: bloque y nombre, task statements literales, lista de fuentes del bloque, y ruta de salida `corpus/notas/bloque-N-notas.md`.
5. **Al volver los agentes**: revisa cada notas por encima (estructura del contrato, secciones HUECOS/CONTRADICCIONES/FUENTES NO ACCESIBLES presentes). Actualiza `fuentes/fuentes.yaml` con URLs corregidas y fuentes añadidas `[NO OFICIAL]` que reportaron los agentes.
6. **Registra** en `versiones.json → corpus.bloques.N` (`notas: {fecha, fuentes_procesadas, huecos}`) y una línea en `ESTADO.md`.
7. **Informe al usuario**: por bloque, fuentes procesadas/fallidas, huecos detectados y fuentes que requieren revisión manual (login). NO continúes a `/consolidar-corpus` por tu cuenta.

## Reglas
- Las notas son material de trabajo: se sobrescriben en cada ejecución (no se versionan como artefacto).
- Fuentes que exigen login (skilljar) → "revisión manual pendiente", nunca bloquean el bloque.
- Nada de contenido Out-of-Scope en las notas aunque las fuentes lo cubran.
