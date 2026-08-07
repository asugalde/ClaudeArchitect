---
name: consolidar-corpus
description: Etapa 3 del pipeline CCAR-F - redacta el corpus por bloque desde las notas de extracción y lo verifica contra la guía oficial vigente y la doc oficial en vivo, con informe en corpus/contraste/. Termina SIEMPRE en el gate del usuario. Uso - /consolidar-corpus [0-5|todos].
---

# /consolidar-corpus [bloque|todos]

Convierte las notas de extracción en el corpus consolidado: **la fuente de verdad** de la que se generan todos los recursos.

**Prerequisito**: existen `corpus/notas/bloque-N-notas.md` de los bloques pedidos (si no, ejecutar antes `/investigar-fuentes`).

## Proceso (por bloque; los bloques pueden ir en paralelo)

1. **Lee** `ESTADO.md` y `versiones.json`. Determina la versión del corpus a generar (nueva MINOR si ya existe una; los ficheros anteriores no se tocan).
2. **Redacción**: despacha `redactor-didactico` (model: sonnet) en modo `corpus-dominio` con: bloque, task statements literales de la guía oficial vigente, entrada `corpus/notas/bloque-N-notas.md`, plantilla `plantillas/corpus-dominio.md`, salida `corpus/bloque-N-<slug>.md`, versión y fecha.
3. **Verificación**: despacha `verificador-contenido` (model: sonnet) sobre el corpus recién escrito, con salida `corpus/contraste/informe-contraste-bloque-N_vX.Y.md`. (El contraste de deriva vs v1.2 quedó RETIRADO el 2026-08-07: ese material fue eliminado; la verificación es contra la guía oficial vigente y la doc oficial en vivo.)
4. **Triaje de hallazgos**:
   - CRÍTICOS → corrígelos tú (orquestador) editando el corpus con la evidencia del informe, o re-despacha al redactor si son de fondo. Anota en el informe qué se corrigió.
   - MEJORAS y deriva tipo (a)/(b) → quedan en el informe para la decisión del usuario en el gate.
   - El campo `estado` del frontmatter pasa a `verificado` cuando no quedan CRÍTICOS abiertos.
5. **Manifest**: crea/actualiza `corpus/corpus.yaml` (por bloque: fichero, versión, estado, fecha, nº task statements cubiertos, huecos abiertos) y `versiones.json → corpus.bloques.N`. Línea en `ESTADO.md`.
6. **GATE (regla dura)**: presenta al usuario, por bloque: veredicto del verificador y huecos conocidos. **Espera su aprobación explícita; nunca se infiere ni se arrastra entre sesiones.** Solo cuando apruebe: `estado: aprobado` en el frontmatter y en `corpus.yaml`, y si TODOS los bloques del corpus están aprobados, `versiones.json → corpus.gate_general.estado = "aprobado"` con fecha. La generación de recursos (`/generar-recursos`) exige ese gate.

## Reglas
- Toda afirmación del corpus debe trazarse a las notas (y estas a sus fuentes). `<!-- HUECO -->` explícito antes que rellenar con conocimiento propio.
- (Retirado 2026-08-07) El contraste de deriva vs la referencia v1.2 ya no existe; sus informes históricos viven en `corpus/contraste/`.
- Anchors `{#ts-N-i}` estables entre versiones MINOR: los `refSeccion` de quizzes y flashcards dependen de ellos.
