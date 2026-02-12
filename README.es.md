# ClaudeCode-Plugin

**[EN](README.md)** | **[FR](README.fr.md)** | **[DE](README.de.md)**

Plugins listos para usar que hacen Claude Code realmente útil en proyectos reales. Memoria, revisión de código, flujo de desarrollo, guardias de seguridad — construidos a partir de meses de uso diario.

> Además, para seguir tus librerías externas, los CVEs y más, descubre [LibTracker](https://app.libtracker.io/).

![Demo](assets/demo.gif)

## Primeros pasos

Sigue los pasos en orden. Cada uno se basa en el anterior.

### Paso 1: Configura Claude Code (solo la primera vez)

Instala `cc-setup` y ejecuta el asistente de configuración. Pregunta sobre tu flujo de trabajo y genera un `CLAUDE.md` personalizado — el archivo que le dice a Claude cómo TRABAJAS.

```bash
claude plugin add github:joey-barbier/ClaudeCode-Plugin/plugins/cc-setup
```
Luego escribe `/cc-setup:setup` y responde las preguntas.

### Paso 2: Dale a Claude una memoria

Instala `cc-memory` para que Claude recuerde tu proyecto entre sesiones. No más re-explicar dónde te quedaste después de una compactación o una nueva conversación.

```bash
claude plugin add github:joey-barbier/ClaudeCode-Plugin/plugins/cc-memory
```

**Qué sucede:** Cuando abres Claude, detecta automáticamente los archivos de tu proyecto y restaura el contexto completo — qué está hecho, qué no, en qué trabajar a continuación. Escribe `/cc-memory:memory` para inicializar la memoria en un nuevo proyecto o restaurarla manualmente.

### Paso 3: Añade las herramientas que necesitas

Elige lo que se ajuste a tu flujo de trabajo. Cada plugin funciona de forma independiente.

---

#### code-review — *Autónomo*

**Tu Líder Técnico Sénior personal.** Se activa automáticamente cuando dices "review PR" o cuando Claude detecta código listo para enviar. Realiza un primer pase completo (arquitectura, seguridad, calidad) para que cuando revises, te concentres en lo que importa — no en errores tipográficos e ifs mal colocados.

```bash
claude plugin add github:joey-barbier/ClaudeCode-Plugin/plugins/code-review
```

> Hook incluido (se ejecuta automáticamente, sin necesidad de comando): Bloquea el envío a main/master. Te recuerda que revises antes de enviar ramas de características.

---

#### qa-testing — *Mixto (autónomo + comando)*

**Validación de QA y generación de pruebas.** El agente de QA se activa automáticamente cuando afirmas que una característica está completa — cuestiona tus afirmaciones y prueba casos extremos. El generador de pruebas es un comando manual.

```bash
claude plugin add github:joey-barbier/ClaudeCode-Plugin/plugins/qa-testing
```

| Componente | Cómo funciona |
|---|---|
| Agente de validación de QA | Autónomo — se activa cuando se validan características |
| Generador de pruebas | Comando — escribe `/qa-testing:unit-test-expert` |

---

#### dev-workflow — *Comandos + agente autónomo*

**Metodología de desarrollo estructurada.** El agente se activa para implementaciones complejas. Las habilidades son comandos que escribes cuando sea necesario.

```bash
claude plugin add github:joey-barbier/ClaudeCode-Plugin/plugins/dev-workflow
```

| Componente | Cómo funciona |
|---|---|
| Agente de metodología de desarrollo | Autónomo — se activa para trabajo complejo multicapa |
| `/dev-workflow:implement` | Comando — lanza una sesión de desarrollo estructurada |
| `/dev-workflow:new-feature` | Comando — prepara git para una nueva característica |
| `/dev-workflow:time-check` | Comando — detecta exceso de ingeniería y bucles |
| `/dev-workflow:init-docs` | Comando — inicializa la documentación del proyecto |

> Hook incluido (se ejecuta automáticamente, sin necesidad de comando): Bloquea comandos de git peligrosos (force push, hard reset, checkout ., restore ., clean, branch -D).

---

#### analytics — *Autónomo*

**Experto en análisis de SaaS.** Se activa cuando trabajas en seguimiento, embudos o conversión. Diseña qué medir, cómo configurarlo y qué paneles construir.

```bash
claude plugin add github:joey-barbier/ClaudeCode-Plugin/plugins/analytics
```

---

#### openclaw — *Comandos*

**Gestión de sesiones para la puerta de enlace OpenClaw.** Herramientas para sesiones de larga duración — comprimir contexto, extraer aprendizajes, mantener el rendimiento.

```bash
claude plugin add github:joey-barbier/ClaudeCode-Plugin/plugins/openclaw
```

| Componente | Cómo funciona |
|---|---|
| `/openclaw:compact` | Comando — comprime una sesión grande |
| `/openclaw:extract` | Comando — guarda los aprendizajes antes de la limpieza |
| Scripts de shell | `context-monitor.sh`, `context-guardian-daemon.sh`, `self-reboot.sh`, `clean-session-blobs.sh` |

> Hook incluido (se ejecuta automáticamente, sin necesidad de comando): Te advierte que guardes los aprendizajes antes de que se compacten sesiones grandes.

## Cómo funcionan los plugins

Tres tipos de componentes, tres comportamientos:

| Tipo | Comportamiento | Ejemplo |
|---|---|---|
| **Agentes** | Autónomos — Claude los activa cuando son relevantes | El agente de revisión de código se activa en "review PR" |
| **Habilidades** | Comandos — los escribes cuando sea necesario | `/cc-memory:memory` para restaurar el contexto |
| **Hooks** | Silenciosos — se ejecutan en segundo plano, te protegen de errores | Bloquea `git push --force` automáticamente |

## Instala el marketplace

Para explorar todos los plugins desde Claude Code:

```bash
/plugin marketplace add github:joey-barbier/ClaudeCode-Plugin
```

Luego usa `/plugin` → pestaña **Discover** para explorar e instalar.

## ¿Preguntas?

Transmito en vivo en Twitch mientras construyo con Claude Code. Ven a hacer preguntas, ver los plugins en acción, o sugerir nuevos.

**[twitch.tv/horka_tv](https://twitch.tv/horka_tv)**

## Licencia

MIT — libre de usar, modificar y compartir.
