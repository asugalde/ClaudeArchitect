---
name: adquirir-guia-oficial
description: Etapa 1 del pipeline CCAR-F - descarga la guía oficial del examen desde su URL S3, extrae el texto, determina su versión y genera el diff frente a la versión anterior en fuentes/. Relanzable; nunca sobrescribe versiones anteriores.
---

# /adquirir-guia-oficial

Adquiere (o refresca) la fuente de verdad absoluta del proyecto: la guía oficial del examen CCAR-F.

**URL canónica** (si el usuario no da otra):
`https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2F6nizmqk8tpzpfjvt6qmmav7rh%2Fpublic%2F1783542750%2FClaude+Certified+Architect+%E2%80%93+Foundations+Exam+Guide.pdf`

## Proceso

1. **Descarga** el PDF a un fichero temporal del scratchpad con `curl.exe -L -o` (o `Invoke-WebRequest`). Verifica que es un PDF válido (cabecera `%PDF`) y de tamaño plausible (>100 KB).
2. **Compara por hash** (SHA-256) con el PDF más reciente ya existente en `fuentes/exam-guide-oficial-v*.pdf`:
   - **Idéntico** → no hay guía nueva. Registra la fecha de comprobación en `versiones.json → guia_oficial_examen.fecha_descarga`, informa al usuario y termina (no dupliques ficheros).
   - **Distinto o no existe previo** → continúa.
3. **Extrae el texto** completo del PDF (Read por páginas, o `pdftotext`/python si están disponibles) y **determina la versión** declarada en el propio documento (portada/pie). Si el documento no declara versión, propona la siguiente MINOR y confírmala con el usuario.
4. **Guarda** como `fuentes/exam-guide-oficial-vX.Y.pdf` y `fuentes/exam-guide-oficial-vX.Y.txt`. NUNCA sobrescribas los de versiones anteriores.
5. **Diff**: lanza un subagente (`model: haiku`) que compare el txt nuevo con el txt de la versión anterior y escriba `fuentes/diff-exam-guide_vX.Y.md` centrado en lo que afecta al material: dominios y pesos, task statements (añadidos/retirados/reformulados), lista Out-of-Scope, escenarios, políticas del examen. Si no hay versión anterior, el diff es "primera adquisición".
6. **Registra**: `versiones.json → guia_oficial_examen` (`version`, `fecha_descarga`, `diff_vs_anterior`) y una línea en el Historial de `ESTADO.md`.

## Reglas
- El PDF oficial y su txt viven SOLO en `fuentes/`; jamás se copian al distribuible.
- Si la descarga falla (URL caducada), informa al usuario y pídele la URL nueva; no busques mirrors no oficiales.
- Si la versión cambia respecto a la usada por el corpus vigente, avisa: los bloques del corpus quedan marcados como desactualizados hasta reconsolidarse.
