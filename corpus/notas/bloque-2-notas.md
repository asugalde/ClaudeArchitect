# Notas de extracción — Bloque 2: Claude Code: configuración y flujos
Fecha: 2026-08-05 · Fuentes procesadas: 11/13

## TS 3.1 — Configure CLAUDE.md files with appropriate hierarchy, scoping, and modular organization

### Hechos y comportamiento
- CLAUDE.md es un archivo markdown que proporciona instrucciones persistentes que Claude Code lee al inicio de cada sesión. [Fuente: Memory (CLAUDE.md) — https://code.claude.com/docs/en/memory]
- La jerarquía de CLAUDE.md sigue este orden de carga (de más general a más específico): managed policy (organización) → user-level (`~/.claude/CLAUDE.md`) → project-level (`./CLAUDE.md` o `./.claude/CLAUDE.md`) → local (`./.claude.local.md`) → subdirectories (on-demand). [Fuente: Memory — https://code.claude.com/docs/en/memory]
- User-level settings en `~/.claude/CLAUDE.md` aplican solo a ese usuario y no se comparten vía control de versiones. Instrucciones en este nivel no alcanzan al equipo. [Fuente: Memory — https://code.claude.com/docs/en/memory]
- Project-level CLAUDE.md se comparte con el equipo mediante version control. Usar para estándares de arquitectura, convenciones de código y workflows comunes. [Fuente: Memory — https://code.claude.com/docs/en/memory]
- Subdirectory CLAUDE.md files cargan on-demand cuando Claude lee archivos en esos directorios, no al inicio de la sesión. Útil en monorepos. [Fuente: Memory — https://code.claude.com/docs/en/memory]
- Local instructions (`.claude.local.md`) son personales y project-specific. Se agregan a `.gitignore` para no compartirse. [Fuente: Memory — https://code.claude.com/docs/en/memory]
- Archivos superiores en el árbol de directorios se cargan en contexto ANTES que los inferiores. Para `foo/bar/`, se carga `foo/CLAUDE.md` antes que `foo/bar/CLAUDE.md`, por lo que instrucciones más cercanas al directorio de trabajo se leen últimas. [Fuente: Memory — https://code.claude.com/docs/en/memory]
- Multiple CLAUDE.md files se concatenan en contexto en lugar de sobrescribirse mutuamente. [Fuente: Memory — https://code.claude.com/docs/en/memory]
- Managed CLAUDE.md (nivel organizacional) no puede ser excluido por configuración individual. Aplica a todas las sesiones en la máquina. [Fuente: Memory — https://code.claude.com/docs/en/memory]
- Target: CLAUDE.md files deben ser < 200 líneas. Archivos más largos consumen más contexto y reducen adherencia. Si se acerca a 200 líneas, dividir en `.claude/rules/`. [Fuente: Memory — https://code.claude.com/docs/en/memory]
- Comando `/memory` lista ubicaciones de CLAUDE.md, CLAUDE.local.md y otros archivos de memoria (user y project scope). Permite abrir y editar archivos. [Fuente: Memory — https://code.claude.com/docs/en/memory]
- Comando `/context` verifica qué archivos de memoria realmente cargaron en la sesión actual (bajo **Memory files**). [Fuente: Memory — https://code.claude.com/docs/en/memory]
- Auto memory: Claude escribe notas automáticamente basadas en correcciones y preferencias. Reside en `~/.claude/projects/<project>/memory/`. Se carga al inicio (primeras 200 líneas o 25KB de `MEMORY.md`). [Fuente: Memory — https://code.claude.com/docs/en/memory]
- Auto memory activo por defecto. Desactivar con `/memory` toggle o `autoMemoryEnabled: false` en settings. [Fuente: Memory — https://code.claude.com/docs/en/memory]

### Sintaxis y configuración
- ```
  # Archivo project-level: ./CLAUDE.md o ./.claude/CLAUDE.md
  # Ubicación alternativa para project instructions
  ```
- ```markdown
  # user-level (~/.claude/CLAUDE.md)
  ## Preferences
  - Use prettier for formatting
  - Prefer TypeScript over JavaScript
  ```
- ```json
  // .claude/settings.json para organizacional (managed CLAUDE.md)
  {
    "claudeMd": "Always run `make lint` before committing.\nNever push directly to main."
  }
  ```

### Patrones
- Usar CLAUDE.md cuando: Claude comete el mismo error dos veces, una code review atrapa algo que Claude debería saber, repites la misma corrección sesión tras sesión, o un nuevo teammate necesitaría ese contexto. [Fuente: Memory — https://code.claude.com/docs/en/memory]
- Mantener en CLAUDE.md: build commands, testing conventions, code style rules que difieren de defaults, naming conventions, architectural decisions específicos del proyecto, quirks del ambiente de desarrollo, gotchas no-obvios. [Fuente: Memory — https://code.claude.com/docs/en/memory]
- Excluir de CLAUDE.md: cosas que Claude puede inferir leyendo código, convenciones de lenguaje estándar, documentación API detallada (linkear en su lugar), información que cambia frecuentemente. [Fuente: Memory — https://code.claude.com/docs/en/memory]
- `/init` command analiza el codebase y genera un starter CLAUDE.md con build commands, test instructions y project conventions descubiertos. Si CLAUDE.md existe, sugiere mejoras en lugar de sobrescribir. [Fuente: Best practices — https://code.claude.com/docs/en/best-practices]
- Con `CLAUDE_CODE_NEW_INIT=1` habilitar flujo multi-fase interactivo que pregunta qué artefactos configurar (CLAUDE.md, skills, hooks). [Fuente: Memory — https://code.claude.com/docs/en/memory]

### Anti-patrones (y por qué fallan)
- CLAUDE.md > 200 líneas: reduce adherencia porque instrucciones importantes se pierden en el ruido. Solución: usar `@import` para importar archivos modulares o `.claude/rules/` con scoping por paths. [Fuente: Memory — https://code.claude.com/docs/en/memory]
- Instrucciones conflictivas entre CLAUDE.md files: Claude elige una arbitrariamente. Revisión periódica necesaria para eliminar contradicciones. [Fuente: Memory — https://code.claude.com/docs/en/memory]
- Trusts only `@import` syntax: sin backticks, Claude importa literalmente. Con backticks (`` `@path` ``), se trata como texto literal. [Fuente: Memory — https://code.claude.com/docs/en/memory]
- Instrucciones vagas (ej. "format code nicely") vs concretas (ej. "use 2-space indentation"): las concretas se siguen más consistentemente. [Fuente: Memory — https://code.claude.com/docs/en/memory]

---

## TS 3.2 — Create and configure custom slash commands and skills

### Hechos y comportamiento
- Skills y custom commands son ahora el mismo mecanismo. Un archivo en `.claude/commands/deploy.md` y una skill en `.claude/skills/deploy/SKILL.md` crean `/deploy` e funcionan idénticamente. [Fuente: Extend Claude with skills — https://code.claude.com/docs/en/skills]
- Project-scoped commands (`.claude/commands/` o `.claude/skills/`) se comparten vía version control con el equipo. [Fuente: Explore the .claude directory — https://code.claude.com/docs/en/claude-directory; Task Statement 3.2]
- User-scoped commands (`~/.claude/commands/` o `~/.claude/skills/`) son personales y no se comparten. [Fuente: Task Statement 3.2 knowledge]
- Skills cargan on-demand cuando se invocan o cuando Claude determina que son relevantes. A diferencia de CLAUDE.md, el cuerpo de una skill solo carga cuando se usa, por lo que referencias largo son gratuitas hasta necesitarse. [Fuente: Extend Claude with skills — https://code.claude.com/docs/en/skills]
- SKILL.md es el archivo de entrada requerido en cada directorio de skill. Contiene YAML frontmatter + markdown content. Archivos adicionales (templates, ejemplos, scripts) son opcionales. [Fuente: Extend Claude with skills — https://code.claude.com/docs/en/skills]
- Frontmatter field `context: fork` aísla la skill en un subagente context separado, evitando que outputs verbose contaminen la sesión principal. [Fuente: Extend Claude with skills — https://code.claude.com/docs/en/skills]
- Frontmatter field `allowed-tools` (space/comma-separated string o YAML list) preaprueba herramientas que Claude puede usar sin permiso durante el turno de invocación. El grant limpia cuando envías el siguiente mensaje. [Fuente: Extend Claude with skills — https://code.claude.com/docs/en/skills]
- Frontmatter field `argument-hint` proporciona un hint mostrado en autocomplete indicando argumentos esperados (ej. `[issue-number]` o `[filename] [format]`). [Fuente: Extend Claude with skills — https://code.claude.com/docs/en/skills]
- Frontmatter field `disable-model-invocation: true` previene que Claude cargue automáticamente la skill. Usar para workflows manual-trigger (ej. `/deploy`). También previene que la skill se precargue en subagentes. [Fuente: Extend Claude with skills — https://code.claude.com/docs/en/skills]
- Frontmatter field `description` (recomendado) define cuándo Claude debe invocar la skill. Es lo que Claude lee para decidir auto-invocar. [Fuente: Extend Claude with skills — https://code.claude.com/docs/en/skills]
- Whoami: skills y CLAUDE.md son complementarios. CLAUDE.md = always-loaded universal standards. Skills = on-demand task-specific workflows. [Fuente: Task Statement 3.2 knowledge]
- Directorio `.claude/skills/` soporta symlinks a directorios en otro lado del disco. Útil para mantener un set compartido de rules. [Fuente: Extend Claude with skills — https://code.claude.com/docs/en/skills]
- Personal skill customization: crear variantes personales en `~/.claude/skills/` con nombres diferentes para no afectar teammates. [Fuente: Task Statement 3.2 knowledge]

### Sintaxis y configuración
- ```markdown
  # .claude/skills/summarize-changes/SKILL.md
  ---
  description: Summarizes uncommitted changes and flags risky patterns. Use when asking about changes.
  ---
  
  ## Current changes
  !`git diff HEAD`
  
  Summarize above in 2-3 bullets. List risks: missing error handling, hardcoded values, untested changes.
  ```
- ```yaml
  ---
  name: my-skill
  description: What this skill does
  disable-model-invocation: true
  allowed-tools: "Read,Grep"
  argument-hint: "[issue-number]"
  context: fork
  ---
  Your skill instructions here...
  ```
- ```markdown
  # .claude/commands/fix-issue.md (single-file command alternative)
  Fix the GitHub issue: $ARGUMENTS
  1. Use `gh issue view` to get details
  2. Search codebase for relevant files
  3. Implement necessary changes
  4. Write and run tests
  5. Create commit and push
  ```
- Frontmatter boolean fields aceptan `yes`, `no`, `on`, `off`, `1`, `0` (case-insensitive) además de `true` y `false`. [Fuente: Extend Claude with skills — https://code.claude.com/docs/en/skills]

### Patrones
- Create skill cuando repites pasting las mismas instrucciones, checklist o multi-step procedure, o cuando una sección de CLAUDE.md creció en procedimiento en lugar de fact. [Fuente: Extend Claude with skills — https://code.claude.com/docs/en/skills]
- Reference content skills: agregan conocimiento que Claude aplica al trabajo actual (convenciones, patrones, style guides). Corre inline para Claude pueda usarlo con contexto. [Fuente: Extend Claude with skills — https://code.claude.com/docs/en/skills]
- Task content skills: step-by-step instrucciones para acciones específicas (deployments, commits, code generation). Often marked `disable-model-invocation: true` para manual-trigger. [Fuente: Extend Claude with skills — https://code.claude.com/docs/en/skills]
- Use `context: fork` para skills que producen output verbose (análisis de codebase) o exploratorio (brainstorming alternativas), aislándolas de la sesión principal. [Fuente: Task Statement 3.2 knowledge]
- Usar `allowed-tools` para restringir acceso durante skill execution. Ej. solo permitir Read/Grep para skills de análisis read-only, no Write/Bash. [Fuente: Task Statement 3.2 knowledge]

### Anti-patrones (y por qué fallan)
- Frontmatter `name` en personal skill solo cambia la label display, no el comando. El comando sigue viniendo del directory o file name. Para cambiar el comando debes renombrar la carpeta/archivo. [Fuente: Extend Claude with skills — https://code.claude.com/docs/en/skills]
- Skills y commands con igual nombre: si existe ambos, skill takes precedence. [Fuente: Extend Claude with skills — https://code.claude.com/docs/en/skills]
- Skills sin `description` no son auto-invoked. Claude no sabe cuándo usarlas. [Fuente: Extend Claude with skills — https://code.claude.com/docs/en/skills]

---

## TS 3.3 — Apply path-specific rules for conditional convention loading

### Hechos y comportamiento
- `.claude/rules/` directorio organiza instrucciones en archivos topic-specific markdown, cada uno cubriendo un tema. Descubrimiento recursivo: rules en subdirectorios (ej. `.claude/rules/frontend/react.md`) se encuentran automáticamente. [Fuente: Memory — https://code.claude.com/docs/en/memory]
- Rules sin frontmatter `paths:` cargan al startup igual que `.claude/CLAUDE.md`. Rules con `paths:` cargan on-demand cuando Claude lee archivos matching. [Fuente: Memory — https://code.claude.com/docs/en/memory]
- Path-scoped rules usan YAML frontmatter con campo `paths:` conteniendo glob patterns. Las rules cargan solo cuando editando matching files, reduciendo contexto irrelevante y uso de tokens. [Fuente: Task Statement 3.3 knowledge; Memory]
- Glob pattern `**/*.ts` matchea todos los archivos TypeScript en cualquier directorio. `src/**/*` matchea todos en `src/`. `*.md` matchea solo root. `src/components/*.tsx` es específico. [Fuente: Memory — https://code.claude.com/docs/en/memory]
- Multiple patterns en un solo rule: soportado con brace expansion (ej. `src/**/*.{ts,tsx}`). [Fuente: Memory — https://code.claude.com/docs/en/memory]
- Brace expansion tiene límites: budget compartido de 1,000 patrones expandidos y 4 MiB por rule. Patterns sin braces no cuentan. [Fuente: Memory — https://code.claude.com/docs/en/memory]
- Glob syntax trata `[` como bracket expression (ej. `[abc]`). Para literal `[`, escape como `\[`. Pattern como `photos [2024/**` sin bracket válido es inválido y matches nothing. [Fuente: Memory — https://code.claude.com/docs/en/memory]
- User-level rules en `~/.claude/rules/` aplican a todos los proyectos en la máquina. User-level rules cargan antes que project rules, dando project rules mayor precedencia. [Fuente: Memory — https://code.claude.com/docs/en/memory]
- Ventaja de glob-pattern rules sobre subdirectory CLAUDE.md files: puedo aplicar una convención a archivos spread across codebase sin crear CLAUDE.md en cada directorio. [Fuente: Task Statement 3.3 knowledge]
- Symlinks en `.claude/rules/` soportados. Resolver y cargar normally. Symlinks circulares detectados y handled gracefully. [Fuente: Memory — https://code.claude.com/docs/en/memory]

### Sintaxis y configuración
- ```markdown
  ---
  paths:
    - "**/*.test.ts"
    - "**/*.test.tsx"
  ---
  
  # Testing Rules
  - Use descriptive test names: "should [expected] when [condition]"
  - Mock external dependencies, not internal modules
  - Clean up side effects in afterEach
  ```
- ```markdown
  ---
  paths:
    - "src/api/**/*.ts"
  ---
  
  # API Design Rules
  - Validate input with Zod schemas
  - Return shape: { data: T } | { error: string }
  - Rate limit all public endpoints
  ```
- Multiple pattern con brace expansion:
  ```yaml
  ---
  paths:
    - "src/**/*.{ts,tsx}"
    - "lib/**/*.ts"
    - "tests/**/*.test.ts"
  ---
  ```

### Patrones
- Usar `.claude/rules/` cuando CLAUDE.md approaches 200 líneas: split en focused topic-specific files. [Fuente: Memory — https://code.claude.com/docs/en/memory]
- Path-scoped rules ideal para convenciones aplicables a archivos by type regardless of directory location. Ej. `**/*.test.tsx` para todos los test files. [Fuente: Task Statement 3.3 knowledge]
- Share rules across projects con symlinks: `ln -s ~/shared-claude-rules .claude/rules/shared` o `ln -s ~/company-standards/security.md .claude/rules/security.md`. [Fuente: Memory — https://code.claude.com/docs/en/memory]
- Live change detection: cambios en `.claude/rules/` se pican dentro sesión actual sin restart si el directory existía cuando la sesión comenzó. [Fuente: Memory — https://code.claude.com/docs/en/memory]

### Anti-patrones (y por qué fallan)
- Patterns con muchos brace groups: expandir a > 1,000 patrones o > 4 MiB hace que rg use pattern unexpanded (matches nada). Keep brace groups bounded. [Fuente: Memory — https://code.claude.com/docs/en/memory]
- Invalid bracket expression (ej. `[` sin closing o valid group) en pattern: pattern matches nothing pero el resto del rule sigue valiendo. Fix: escape literal `[` como `\[`. [Fuente: Memory — https://code.claude.com/docs/en/memory]

---

## TS 3.4 — Determine when to use plan mode vs direct execution

### Hechos y comportamiento
- Plan mode designado para complex tasks involucrando large-scale changes, múltiples enfoques válidos, architectural decisions, multi-file modifications. [Fuente: Task Statement 3.4 knowledge; Permission modes — https://code.claude.com/docs/en/permission-modes]
- Direct execution apropiado para simple, well-scoped changes (ej. agregar single validation check a una función). [Fuente: Task Statement 3.4 knowledge]
- Plan mode activado: presionar `Shift+Tab` hasta status bar muestre `⏸ plan mode on`, o startup con `claude --permission-mode plan`. [Fuente: Best practices — https://code.claude.com/docs/en/best-practices]
- En plan mode, Claude lee files y responde preguntas sin hacer cambios. Edits stay blocked hasta apruebas el plan. [Fuente: Permission modes — https://code.claude.com/docs/en/permission-modes]
- Plan mode enable safe codebase exploration y design antes de comprometerse a cambios, previniendo costly rework. [Fuente: Task Statement 3.4 knowledge]
- Cuando auto mode está disponible y `useAutoModeDuringPlan` está on (default), el clasificador revisa shell commands durante planning instead of prompting. [Fuente: Permission modes — https://code.claude.com/docs/en/permission-modes]
- Si auto mode no disponible durante plan, comandos outside built-in read-only set promptean para approval. [Fuente: Permission modes — https://code.claude.com/docs/en/permission-modes]
- Review plan: cuando listo, Claude presenta plan y pregunta cómo proceder. Opciones: Yes and use auto mode, Yes manually approve edits, No keep planning. [Fuente: Permission modes — https://code.claude.com/docs/en/permission-modes]
- `Ctrl+G` abre proposed plan en editor default para editar directamente antes de Claude procede. [Fuente: Permission modes — https://code.claude.com/docs/en/permission-modes]
- Explore subagent: para aislando verbose discovery output y returning summaries, preservando main conversation context. [Fuente: Task Statement 3.4 knowledge]
- Combinación: plan mode para investigation + direct execution para implementation (ej. plan library migration, then execute approach). [Fuente: Task Statement 3.4 knowledge]

### Sintaxis y configuración
- ```bash
  # Start en plan mode
  claude --permission-mode plan
  ```
- ```bash
  # Prefix un prompt con /plan en sesión normal para entrar plan mode
  /plan
  ```
- ```bash
  # Switchear dentro sesión: Shift+Tab cycles default → acceptEdits → plan
  Shift+Tab
  ```

### Patrones
- Use plan mode para tasks con architectural implications (microservice restructuring, library migrations affecting 45+ files, choosing between integration approaches con infraestructura requirements diferentes). [Fuente: Task Statement 3.4 knowledge]
- Use direct execution para well-understood changes con clear scope (single-file bug fix with clear stack trace, adding date validation conditional). [Fuente: Task Statement 3.4 knowledge]
- Workflow recommended: Explore → Plan → Implement → Commit. Fase Explore en plan mode. Aprove plan. Switch a default/acceptEdits/auto mode para implementation. [Fuente: Best practices — https://code.claude.com/docs/en/best-practices]
- Short tasks pueden skip plan: "If you could describe the diff in one sentence, skip the plan". Planning overhead no siempre vale. [Fuente: Best practices — https://code.claude.com/docs/en/best-practices]
- Delegate research con subagents: "use subagents to investigate X". Exploran en context separado, reportan summaries, keeping main conversation clean. [Fuente: Best practices — https://code.claude.com/docs/en/best-practices]

### Anti-patrones (y por qué fallan)
- Jumping straight to coding sin exploración/planning: puede producir código que soluciona wrong problem. [Fuente: Best practices — https://code.claude.com/docs/en/best-practices]
- Planificar todo: overhead para small, clear tasks. Workflow becomes slow si always doing plan mode even para single-file edits. [Fuente: Best practices — https://code.claude.com/docs/en/best-practices]

---

## TS 3.5 — Apply iterative refinement techniques for progressive improvement

### Hechos y comportamiento
- Concrete input/output examples son la way más efectiva para communicate expected transformations cuando prose descriptions se interpretan inconsistentemente. [Fuente: Task Statement 3.5 knowledge]
- Test-driven iteration: escribir test suites primero, then iterate compartiendo test failures para guiar progressive improvement. [Fuente: Task Statement 3.5 knowledge]
- Interview pattern: tener Claude ask questions para surface considerations el developer may not have anticipated antes de implementing. [Fuente: Task Statement 3.5 knowledge]
- When to provide all issues en single message vs sequential: interacting problems → single message. Independent problems → sequential fixing. [Fuente: Task Statement 3.5 knowledge]
- Verification check (tests, build, linter, screenshot, diff script): da a Claude way to verify work. Difference entre session Claude watches vs unattended. [Fuente: Best practices — https://code.claude.com/docs/en/best-practices]
- Give Claude evidence, no assertions: test output, command run + result, screenshot. Reviewing evidence es faster que re-running verification yourself. [Fuente: Best practices — https://code.claude.com/docs/en/best-practices]
- Context window llena rápido. Si Claude corriges más de dos veces sobre mismo issue en una sesión, context cluttered con failed approaches. [Fuente: Best practices — https://code.claude.com/docs/en/best-practices]
- After two failed corrections: `/clear` y write better initial prompt incorporating lo que leíste. Long session con accumulated corrections usually underperforms vs clean session con better prompt. [Fuente: Best practices — https://code.claude.com/docs/en/best-practices]
- Provide rich content: reference files con `@`, paste images, dar URLs, pipe data. Let Claude fetch lo que needs via Bash/MCP/Read. [Fuente: Best practices — https://code.claude.com/docs/en/best-practices]
- Point to sources para codebase questions: "look through ExecutionFactory's git history" instead of vague "why is this API weird?". [Fuente: Best practices — https://code.claude.com/docs/en/best-practices]
- Reference existing patterns: point Claude a implementations en codebase para understand patterns. "Follow pattern used en existing widgets, HotDogWidget.php es good example". [Fuente: Best practices — https://code.claude.com/docs/en/best-practices]
- /goal condition: set check como goal. Separate evaluator re-checks after every turn. Claude keeps working until hold. [Fuente: Best practices — https://code.claude.com/docs/en/best-practices]

### Sintaxis y configuración
- ```text
  Concrete input/output example pattern:
  
  "write a validateEmail function.
  example test cases:
  - user@example.com → true
  - invalid@.com → false
  - user@test.co.uk → true
  
  run tests after implementing"
  ```
- ```text
  Interview pattern prompt:
  
  "I want to build [feature]. Interview me in detail using AskUserQuestion.
  
  Ask about technical implementation, UI/UX, edge cases, concerns, tradeoffs.
  
  Keep interviewing until we've covered everything, then write spec to SPEC.md"
  ```
- ```bash
  # Esc: stop Claude mid-action
  Esc
  
  # Esc + Esc o /rewind: open rewind menu
  Esc + Esc
  /rewind
  ```

### Patrones
- Provide 2-3 concrete input/output examples para clarify transformation requirements cuando natural language descriptions produce inconsistent results. [Fuente: Task Statement 3.5 knowledge]
- Write test suites first covering expected behavior, edge cases, performance requirements. Then iterate sharing test failures para guide progressive improvement. [Fuente: Task Statement 3.5 knowledge]
- Use interview pattern para surface design considerations (cache invalidation, failure modes) antes de implementing en unfamiliar domains. [Fuente: Task Statement 3.5 knowledge]
- Provide specific test cases con example input + expected output para fix edge case handling (ej. null values en migration scripts). [Fuente: Task Statement 3.5 knowledge]
- Address interacting issues en single detailed message. Sequential iteration para independent issues. [Fuente: Task Statement 3.5 knowledge]
- Verification strategies: provide tests, build, linter, script diff output vs fixture, browser screenshot comparison. [Fuente: Best practices — https://code.claude.com/docs/en/best-practices]
- Course-correct early: correct Claude as soon as notice off-track. Tight feedback loops produce better solutions faster. [Fuente: Best practices — https://code.claude.com/docs/en/best-practices]
- Split specification writing from implementation: separate session para spec eliminates biased context. [Fuente: Best practices — https://code.claude.com/docs/en/best-practices]

### Anti-patrones (y por qué fallan)
- Vague prompts: "add tests for foo.py" vs specific "write test para foo.py covering edge case cuando user logged out. avoid mocks". Specific prompts produce better results con fewer corrections. [Fuente: Best practices — https://code.claude.com/docs/en/best-practices]
- Bloated CLAUDE.md: si Claude no sigue instrucciones a pesar de tenerla written, archivo probably too long y rule getting lost. Prune ruthlessly. [Fuente: Best practices — https://code.claude.com/docs/en/best-practices]
- Over-specification: spec so detailed deja zero room interpret puede under-engineer. Less detailed specs require más refinement loops. [Fuente: Best practices — https://code.claude.com/docs/en/best-practices]

---

## TS 3.6 — Integrate Claude Code into CI/CD pipelines

### Hechos y comportamiento
- Flag `-p` (o `--print`): ejecuta Claude Code en non-interactive mode en automated pipelines. Previene interactive input hangs. [Fuente: Headless — https://code.claude.com/docs/en/headless; Task Statement 3.6 knowledge]
- Flag `--output-format json`: returns structured JSON con result, session ID, metadata. Response includes `total_cost_usd` y per-model cost breakdown para track spend. [Fuente: Headless — https://code.claude.com/docs/en/headless]
- Flag `--json-schema`: enforces structured output conforming a JSON Schema. Response includes metadata + schema-conformant output en `structured_output` field. [Fuente: Headless — https://code.claude.com/docs/en/headless]
- CLAUDE.md mecanismo para providing project context (testing standards, fixture conventions, review criteria) a CI-invoked Claude Code. [Fuente: Task Statement 3.6 knowledge]
- Session context isolation: same Claude session que generó code es less effective at reviewing own changes comparado independent review instance. [Fuente: Task Statement 3.6 knowledge]
- Include prior review findings en context when re-running reviews after new commits. Instruct Claude report only new o still-unaddressed issues para avoid duplicate comments. [Fuente: Task Statement 3.6 knowledge]
- Provide existing test files en context so test generation avoids suggesting duplicate scenarios already covered. [Fuente: Task Statement 3.6 knowledge]
- Document testing standards, valuable test criteria, available fixtures en CLAUDE.md para improve test generation quality y reduce low-value test output. [Fuente: Task Statement 3.6 knowledge]
- `/install-github-app` command en Claude Code terminal instala interactively GitHub integration. Walks through GitHub App install, API key secret, workflow selection. [Fuente: GitHub Actions — https://code.claude.com/docs/en/github-actions]
- Claude Code GitHub Actions responde a `@claude` mentions en PR/issue comments. Triggers con actions on PR opened/synchronized, issue opened/assigned. [Fuente: GitHub Actions — https://code.claude.com/docs/en/github-actions]
- Workflow can invoke skills: `/skill-name` en prompt. Para skills en project `.claude/skills/`, correr `actions/checkout` before action step. [Fuente: GitHub Actions — https://code.claude.com/docs/en/github-actions]
- GitHub Actions accepts `claude_args` parameter para CLI arguments (ej. `--max-turns 5`, `--model claude-sonnet-5`). [Fuente: GitHub Actions — https://code.claude.com/docs/en/github-actions]
- `--bare` mode: reduce startup time skipping auto-discovery de hooks, skills, plugins, MCP servers, auto memory, CLAUDE.md. Useful para CI where consistent results matter. [Fuente: Headless — https://code.claude.com/docs/en/headless]
- Bare mode no read OAuth credentials o system keychain. Para Anthropic API set `ANTHROPIC_API_KEY` en environment. [Fuente: Headless — https://code.claude.com/docs/en/headless]
- Exit codes: Claude Code exits 0 on success, non-zero on failure. Scripts can branch on exit status. [Fuente: Headless — https://code.claude.com/docs/en/headless]
- Piped stdin capped at 10MB. Si exceed, Claude exits con error y non-zero status. Para larger inputs, write content a file y reference en prompt. [Fuente: Headless — https://code.claude.com/docs/en/headless]

### Sintaxis y configuración
- ```bash
  # Non-interactive mode básico
  claude -p "Find and fix the bug in auth.py"
  ```
- ```bash
  # Con pre-approved tools
  claude -p "Run the test suite and fix any failures" \
    --allowedTools "Bash,Read,Edit"
  ```
- ```bash
  # Structured JSON output
  claude -p "Summarize this project" --output-format json
  ```
- ```bash
  # JSON Schema for structured output
  claude -p "Extract the main function names from auth.py" \
    --output-format json \
    --json-schema '{"type":"object","properties":{"functions":{"type":"array","items":{"type":"string"}}},"required":["functions"]}'
  ```
- ```bash
  # Bare mode
  claude --bare -p "Summarize README.md" --allowedTools "Read"
  ```
- ```bash
  # Pipe data
  cat build-error.txt | claude -p 'concisely explain the root cause' > output.txt
  ```
- ```json
  // GitHub Actions workflow v1.0 (GA)
  - uses: anthropics/claude-code-action@v1
    with:
      anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
      prompt: "Review this PR for security issues"
      claude_args: |
        --append-system-prompt "Follow our coding standards"
        --max-turns 10
        --model claude-sonnet-5
  ```
- ```bash
  # Continue conversations
  session_id=$(claude -p "Start a review" --output-format json | jq -r '.session_id')
  claude -p "Continue that review" --resume "$session_id"
  ```

### Patrones
- Run Claude in CI with `-p` flag para prevent interactive input hangs. [Fuente: Task Statement 3.6 knowledge]
- Use `--output-format json` + `--json-schema` para produce machine-parseable structured findings para automated posting inline PR comments. [Fuente: Task Statement 3.6 knowledge]
- Include prior review findings cuando re-running reviews after new commits. Instruct Claude report only new o still-unaddressed para avoid duplicates. [Fuente: Task Statement 3.6 knowledge]
- Provide existing test files en context so test generation avoids duplicate scenarios. [Fuente: Task Statement 3.6 knowledge]
- Document testing standards, valuable criteria, available fixtures en CLAUDE.md para improve test generation quality. [Fuente: Task Statement 3.6 knowledge]
- Script pattern: wrap non-interactive call en script para use Claude as project-specific linter/reviewer. [Fuente: Headless — https://code.claude.com/docs/en/headless]
- ```json
  // package.json script example
  "lint:claude": "git diff main | claude -p \"you are typo linter. report filename:line and issue.\""
  ```
- Security review workflow: pipe diff to Claude, request audit para injection, auth, hardcoded secrets. [Fuente: Headless — https://code.claude.com/docs/en/headless]
- GitHub Actions: `/install-github-app` command walks through setup. Or manual: install app, add API key secret, copy workflow from examples/claude.yml. [Fuente: GitHub Actions — https://code.claude.com/docs/en/github-actions]

### Anti-patrones (y por qué fallan)
- Running same Claude session para code generation + review: contexto biased hacia own implementation. Use independent review instance para better results. [Fuente: Task Statement 3.6 knowledge]
- Forgetting test context: Claude generates duplicate test scenarios already covered, wasting tokens. Provide existing tests en context. [Fuente: Task Statement 3.6 knowledge]
- Under-documenting standards en CLAUDE.md: test generation quality suffers. Insufficient context para fixtures/criteria. [Fuente: Task Statement 3.6 knowledge]
- No exit code handling en scripts: scripts don't branch on failure. Always capture `$?` after non-interactive calls. [Fuente: Headless — https://code.claude.com/docs/en/headless]

---

## HUECOS
- **TS 3.1 (@import imports desde .claude/rules/)**: no hay evidencia literalmente que @import también funcione en .claude/rules/ files. Documentación lo menciona solo en contexto CLAUDE.md. Considerar buscar en docs adicionales.
- **TS 3.2 (disallowed-tools field)**: documentación menciona este field pero limitadamente. Integración con denied tools podría ser más precisa.
- **TS 3.4 (Explore subagent específico)**: documentación mentions "Explore subagent para isolating verbose output" pero escasamente detalles implementación. Task Statement no clarity cuánto es built-in vs custom.
- **TS 3.6 (GitHub Code Review automático sin trigger)**: GitHub Actions soporta automatic reviews on every PR, pero fuente accessed no especifica cómo diferente de `@claude` trigger.

## CONTRADICCIONES
- None detected. Todas las fuentes alineadas en comportamiento, configuración, y patrones de Claude Code.

## FUENTES NO ACCESIBLES
- "Claude Code 101" (Skilljar) — https://anthropic.skilljar.com/claude-code-101 — login requerido. Contenido básico extraído via resumen de página.
- "Claude Code in Action" (Skilljar) — https://anthropic.skilljar.com/claude-code-in-action — login requerido. No acceso directo.
- "Introduction to Agent Skills" (Skilljar) — https://anthropic.skilljar.com/introduction-to-agent-skills — login requerido. No acceso directo.
- "Claude Code: A Highly Agentic Coding Assistant" (DeepLearning.AI) — https://www.deeplearning.ai/courses/claude-code-a-highly-agentic-coding-assistant — contenido extraído via resumen de página.
- "Mastering Claude Code in 30 Minutes" (YouTube) — https://www.youtube.com/watch?v=AOfogJZ70OQ — video requiere ejecución JavaScript. No transcripción accesible via WebFetch.

## FUENTES ADICIONALES INCORPORADAS
- Ninguna. Todas las fuentes listadas fueron accesibles o parcialmente accesibles. No se requirieron búsquedas de terceros.
