# ClaudeCode-Plugin

**[EN](README.md)** | **[FR](README.fr.md)** | **[DE](README.de.md)**

Una colección de plugins listos para usar para [Claude Code](https://docs.anthropic.com/en/docs/claude-code) que mejoran tu asistente de IA con buenas prácticas, medidas de seguridad y herramientas de productividad.

> Creado por el equipo detrás de [LibTracker](https://app.libtracker.io/) — flujos de trabajo probados en batalla, forjados construyendo un producto SaaS real con Claude Code.

## ¿Qué son los Plugins?

Los plugins de Claude Code amplían lo que Claude puede hacer en tu terminal. Añaden:

- **Skills** — Comandos que tecleas (como `/memory` o `/setup`) para activar flujos de trabajo específicos
- **Agents** — Personas de IA especializadas que se activan automáticamente cuando es relevante (como un revisor de código)
- **Hooks** — Verificaciones de seguridad automáticas que se ejecutan en segundo plano (como bloquear pérdida accidental de datos)

Solo instalas lo que necesitas. Cada plugin funciona de manera independiente.

## Plugins Disponibles

### code-review

**Tu Tech Lead Senior personal.**
Revisa tus cambios de código antes de que se publiquen, detectando errores, problemas de seguridad y fallos de calidad.

| Qué obtienes | Cómo usarlo |
|---|---|
| Agente de revisión de PR | Di "review PR" o se activa automáticamente |

> Hook: Te recuerda revisar el código antes de enviar cambios en ramas de características.

---

### qa-testing

**Aseguramiento de calidad y pruebas.**
Valida tu trabajo como lo haría un Product Owner, y genera pruebas para tu código en cualquier lenguaje.

| Qué obtienes | Cómo usarlo |
|---|---|
| Agente de validación QA | Se activa al validar características |
| Generador de pruebas | Escribe `/qa-testing:unit-test-expert` |

---

### dev-workflow

**Metodología de desarrollo estructurada.**
Te mantiene organizado, previene pérdidas de tiempo y protege contra pérdida accidental de datos.

| Qué obtienes | Cómo usarlo |
|---|---|
| Agente de metodología de desarrollo | Se activa para implementaciones complejas |
| Iniciar implementación | Escribe `/dev-workflow:implement` |
| Detector de pérdida de tiempo | Escribe `/dev-workflow:time-check` |
| Configuración de documentación | Escribe `/dev-workflow:init-docs` |
| Preparación de nueva característica | Escribe `/dev-workflow:new-feature` |

> Hook: Bloquea comandos git peligrosos (force push, hard reset, clean) para prevenir pérdida de datos.

---

### cc-memory

**Memoria de sesión y contexto.**
Recuerda tu proyecto entre sesiones para que Claude nunca pierda la pista de dónde lo dejaste.

| Qué obtienes | Cómo usarlo |
|---|---|
| Restaurar / iniciar contexto | Escribe `/cc-memory:memory` |

> Hook: Detecta automáticamente archivos de memoria del proyecto cuando inicia una sesión y restaura el contexto.

---

### cc-setup

**Asistente de configuración interactivo.**
Genera un archivo de configuración personalizado (CLAUDE.md) a través de un cuestionario simple. Funciona para desarrolladores, gestores de proyectos, escritores — cualquiera que use Claude Code.

| Qué obtienes | Cómo usarlo |
|---|---|
| Generador de CLAUDE.md | Escribe `/cc-setup:setup` |

---

### analytics

**Experto en analítica SaaS.**
Diseña estrategias de seguimiento para aplicaciones web — qué medir, cómo configurarlo y qué paneles construir.

| Qué obtienes | Cómo usarlo |
|---|---|
| Agente arquitecto de analítica | Se activa para tareas relacionadas con analítica |

---

### openclaw

**Gestión de sesiones para gateway OpenClaw.**
Herramientas para gestionar sesiones de IA de larga duración — comprimir contexto, extraer aprendizajes y mantener el rendimiento.

| Qué obtienes | Cómo usarlo |
|---|---|
| Compresor de sesión | Escribe `/openclaw:compact` |
| Extractor de aprendizajes | Escribe `/openclaw:extract` |
| Monitor de contexto | Ejecuta `context-monitor.sh` |
| Guardián de contexto | Ejecuta `context-guardian-daemon.sh` |
| Reinicio de gateway | Ejecuta `self-reboot.sh` |
| Limpiador de blobs | Ejecuta `clean-session-blobs.sh` |

> Hook: Te recuerda guardar aprendizajes antes de que las sesiones grandes sean comprimidas.

## Instalación

### Instalar un solo plugin

Elige solo lo que necesitas:

```bash
claude plugin add github:joey-barbier/ClaudeCode-Plugin/plugins/code-review
```

### Probar antes de instalar

Prueba un plugin temporalmente:

```bash
claude --plugin-dir ./plugins/dev-workflow
```

### Instalar desde una copia local

```bash
git clone https://github.com/joey-barbier/ClaudeCode-Plugin.git
claude plugin add ./ClaudeCode-Plugin/plugins/cc-memory
```

## Inicio Rápido

1. **Instala los plugins que quieras** (ver arriba)
2. **Los agentes funcionan automáticamente** — se activan cuando Claude detecta una situación relevante
3. **Los skills son comandos** — escríbelos cuando los necesites:
   ```
   /cc-setup:setup              # Configura tus preferencias de Claude Code
   /cc-memory:memory            # Restaura el contexto del proyecto
   /dev-workflow:new-feature    # Prepara una nueva característica
   /dev-workflow:implement      # Comienza a construir
   /dev-workflow:time-check     # Verifica si estás sobre-ingeniando
   /dev-workflow:init-docs      # Configura la documentación del proyecto
   /qa-testing:unit-test-expert # Genera pruebas
   /openclaw:compact            # Comprime una sesión grande
   /openclaw:extract            # Guarda aprendizajes de una sesión
   ```
4. **Los hooks se ejecutan silenciosamente** — protegiéndote de errores en segundo plano

## Configuraciones Recomendadas

| Perfil | Plugins recomendados |
|---|---|
| **Empezando con Claude Code** | `cc-setup` → ejecuta `/cc-setup:setup` |
| **Desarrollador individual** | `cc-memory` + `dev-workflow` + `code-review` |
| **Equipo con revisiones de código** | `code-review` + `qa-testing` + `dev-workflow` |
| **Gestor de proyecto o escritor** | `cc-setup` + `cc-memory` |
| **Operador de gateway OpenClaw** | `openclaw` + `cc-memory` |

## Estructura

```
plugins/
├── code-review/     # Agente de revisión de PR + hook de protección de push
├── qa-testing/      # Validación QA + generación de pruebas
├── dev-workflow/    # Metodología de desarrollo + hook de seguridad git
├── cc-memory/       # Restauración de contexto + hook de detección automática
├── cc-setup/        # Generador interactivo de CLAUDE.md
├── analytics/       # Seguimiento de analítica SaaS
└── openclaw/        # Gestión de sesiones + hook pre-compactación
```

## Licencia

MIT — libre para usar, modificar y compartir.
