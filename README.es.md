# ClaudeCode-Plugin

**[EN](README.md)** | **[FR](README.fr.md)** | **[DE](README.de.md)**

Plugins listos para usar de Claude Code: memoria, revisión de código, flujo dev, guardias de seguridad. Construidos a partir de meses de uso diario.

> ¿Sigues tus librerías externas, CVEs y más? Descubre [LibTracker](https://app.libtracker.io/).

![Demo](assets/demo.gif)

## Instalación

```bash
/plugin marketplace add joey-barbier/ClaudeCode-Plugin
```

Luego `/plugin` → pestaña **Discover** para explorar, o instala plugins individualmente abajo.

## Catálogo de plugins

| Plugin | Función | Componentes |
|---|---|---|
| **[horka-setup](#horka-setup)** | `CLAUDE.md` personalizado + docs de arquitectura | 2 skills |
| **[horka-memory](#horka-memory)** | Memoria de proyecto persistente entre sesiones | 1 skill |
| **[horka-review](#horka-review)** | Antagonist + Tech Lead code review | agent + 2 skills + hook |
| **[horka-qa-testing](#horka-qa-testing)** | Validación QA + tests unitarios de negocio | agent + skill |
| **[horka-dev-workflow](#horka-dev-workflow)** | Metodología dev + seguridad git | agent + 2 skills + hook |
| **[horka-analytics](#horka-analytics)** | Experto en tracking / funnels SaaS | agent |
| **[horka-openclaw](#horka-openclaw)** | Gestión de sesiones largas de IA | 2 skills + hook |
| **[horka-skill-eval](#horka-skill-eval)** | Auditor de calidad de skills | skill |

---

## Primeros pasos

### 1. Configurar Claude — `horka-setup`

```bash
claude plugin install horka-setup
```

- `/horka-setup:horka-claude-setup` — cuestionario interactivo → `CLAUDE.md` personalizado
- `/horka-setup:horka-init-docs` — genera docs de arquitectura desde tu código (ARCHITECTURE, CONVENTIONS, WORKFLOW_PATTERNS...)

### 2. Dale memoria a Claude — `horka-memory`

```bash
claude plugin install horka-memory
```

Restaura automáticamente el contexto del proyecto al iniciar sesión. `/horka-memory:horka-memory-restore` para inicializar en un nuevo proyecto — escanea tu codebase y crea los archivos PROJECT_STATE, ARCHITECTURE, DECISIONS, NEXT_STEPS, COMMANDS.

### 3. Elige las herramientas abajo

Cada plugin funciona de forma independiente.

---

## horka-review

**Toolkit completo de code review.** Doble pasada: el antagonist encuentra fallos, luego el Tech Lead valida.

```bash
claude plugin install horka-review
```

| Componente | Activacion | Funcion |
|---|---|---|
| `/horka-review:antagonist-reviewer` | "roast", "critique", "find flaws" | Cazador de fallos implacable — cero cumplidos, output BLOCKED/WARNINGS/WASTE |
| `/horka-review:horka-review-changes` | "review changes", "code review" | Revision Tech Lead estructurada en contexto aislado |
| Agente `review-pr` | "review PR" / pre-push | Pasada completa: arquitectura + seguridad + calidad |
| Hook review guard | auto | Bloquea push a rama por defecto, impone orden de review en feature branches |

**Orden de review:** Antagonist (encontrar fallos) → Fix → Tech Lead (validar) → Push/PR

---

## horka-qa-testing

**Validación QA + generación de tests unitarios de negocio.**

```bash
claude plugin install horka-qa-testing
```

| Componente | Activación | Función |
|---|---|---|
| Agente `qa-validate` | afirmación "feature terminada" | Cuestiona afirmaciones, prueba casos límite |
| `/horka-qa-testing:horka-unit-test-generate` | comando | Genera tests alineados con tus convenciones (permisos, límites, consistencia) |

---

## horka-dev-workflow

**Metodología dev estructurada + seguridad git.**

```bash
claude plugin install horka-dev-workflow
```

| Componente | Activación | Función |
|---|---|---|
| Agente `dev-methodology` | implementaciones complejas | Coordina cambios multicapa en el orden correcto |
| `/horka-dev-workflow:horka-git-new-feature` | comando | Prepara git: main → pull → elimina mergeadas → nueva rama `feature/` |
| `/horka-dev-workflow:horka-mvp-time-guardian` | comando | Detecta bucles, propone la solución más rápida |
| Hook seguridad git | auto | Bloquea force push, hard reset, checkout ., clean, branch -D |

---

## horka-analytics

**Experto en analytics SaaS.** Se activa automáticamente en temas de tracking / funnels / conversión. Diseña qué medir, implementación y dashboards.

```bash
claude plugin install horka-analytics
```

---

## horka-openclaw

**Gestión de sesiones largas de IA.**

```bash
claude plugin install horka-openclaw
```

| Componente | Activación | Función |
|---|---|---|
| `/horka-openclaw:horka-openclaw-session-compact` | comando | Comprime sesiones >20 MB, extrae decisiones/configs, archiva el original |
| `/horka-openclaw:horka-openclaw-session-extract` | comando | Extrae aprendizajes a archivos de memoria |
| Hook sesión | auto | Avisa antes de compactación pesada |

Herramientas shell: `context-monitor.sh`, `context-guardian-daemon.sh`, `self-reboot.sh`, `clean-session-blobs.sh`.

---

## horka-skill-eval

**Auditor de calidad de skills** contra las best practices oficiales de Anthropic.

```bash
claude plugin install horka-skill-eval
```

| Componente | Activación | Función |
|---|---|---|
| `/horka-skill-eval:horka-skill-evaluate` | comando | Puntúa 5 categorías sobre 100, propone correcciones, re-evalúa antes/después |

---

## Cómo funcionan los plugins

| Tipo | Comportamiento | Ejemplo |
|---|---|---|
| **Agents** | Autónomos — Claude los activa cuando es relevante | `review-pr` en "review PR" |
| **Skills** | Comandos que escribes | `/horka-memory:horka-memory-restore` |
| **Hooks** | Guardias silenciosos en segundo plano | Bloquea `git push --force` |

## ¿Preguntas?

Hago stream en vivo en Twitch mientras construyo con Claude Code. Ven a hacer preguntas, ver los plugins en acción o sugerir nuevos.

**[twitch.tv/horka_tv](https://twitch.tv/horka_tv)**

## Licencia

MIT — libre de usar, modificar y compartir.
