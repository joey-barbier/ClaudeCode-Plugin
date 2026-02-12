# ClaudeCode-Plugin

**[EN](README.md)** | **[FR](README.fr.md)** | **[ES](README.es.md)**

Eine Sammlung einsatzbereiter Plugins für [Claude Code](https://docs.anthropic.com/en/docs/claude-code), die Ihren KI-Assistenten mit Best Practices, Sicherheitsvorkehrungen und Produktivitätswerkzeugen erweitern.

> Entwickelt vom Team hinter [LibTracker](https://app.libtracker.io/) — praxiserprobte Workflows aus dem Aufbau eines echten SaaS-Produkts mit Claude Code.

## Was sind Plugins?

Claude Code Plugins erweitern die Möglichkeiten von Claude in Ihrem Terminal. Sie fügen hinzu:

- **Skills** — Befehle, die Sie eingeben (wie `/memory` oder `/setup`), um bestimmte Abläufe auszulösen
- **Agents** — Spezialisierte KI-Personas, die sich automatisch aktivieren, wenn sie relevant sind (wie ein Code-Reviewer)
- **Hooks** — Automatische Sicherheitsprüfungen, die im Hintergrund laufen (wie das Blockieren versehentlicher Datenverluste)

Sie installieren nur das, was Sie benötigen. Jedes Plugin funktioniert unabhängig.

## Verfügbare Plugins

### code-review

**Ihr persönlicher Senior Tech Lead.**
Überprüft Ihre Code-Änderungen, bevor sie live gehen, und erkennt Fehler, Sicherheitsprobleme und Qualitätsmängel.

| Was Sie bekommen | Wie Sie es verwenden |
|---|---|
| PR review agent | Sagen Sie "review PR" oder aktiviert sich automatisch |

> Hook: Erinnert Sie daran, Code zu überprüfen, bevor Sie Änderungen auf Feature-Branches pushen.

---

### qa-testing

**Qualitätssicherung und Tests.**
Validiert Ihre Arbeit wie ein Product Owner und generiert Tests für Ihren Code in jeder Sprache.

| Was Sie bekommen | Wie Sie es verwenden |
|---|---|
| QA validation agent | Aktiviert sich bei der Validierung von Features |
| Test generator | Geben Sie `/qa-testing:unit-test-expert` ein |

---

### dev-workflow

**Strukturierte Entwicklungsmethodik.**
Hält Sie organisiert, verhindert Zeitverschwendung und schützt vor versehentlichem Datenverlust.

| Was Sie bekommen | Wie Sie es verwenden |
|---|---|
| Development methodology agent | Aktiviert sich bei komplexen Implementierungen |
| Start implementation | Geben Sie `/dev-workflow:implement` ein |
| Time waste detector | Geben Sie `/dev-workflow:time-check` ein |
| Documentation setup | Geben Sie `/dev-workflow:init-docs` ein |
| New feature prep | Geben Sie `/dev-workflow:new-feature` ein |

> Hook: Blockiert gefährliche git-Befehle (force push, hard reset, clean), um Datenverlust zu verhindern.

---

### cc-memory

**Sitzungsgedächtnis und Kontext.**
Merkt sich Ihr Projekt zwischen Sitzungen, damit Claude nie den Überblick darüber verliert, wo Sie aufgehört haben.

| Was Sie bekommen | Wie Sie es verwenden |
|---|---|
| Context restore / init | Geben Sie `/cc-memory:memory` ein |

> Hook: Erkennt automatisch Projekt-Gedächtnisdateien, wenn eine Sitzung startet, und stellt den Kontext wieder her.

---

### cc-setup

**Interaktiver Einrichtungsassistent.**
Generiert eine personalisierte Konfigurationsdatei (CLAUDE.md) durch einen einfachen Fragebogen. Funktioniert für Entwickler, Projektmanager, Autoren — jeden, der Claude Code verwendet.

| Was Sie bekommen | Wie Sie es verwenden |
|---|---|
| CLAUDE.md generator | Geben Sie `/cc-setup:setup` ein |

---

### analytics

**SaaS-Analytics-Experte.**
Entwirft Tracking-Strategien für Webanwendungen — was gemessen werden soll, wie es eingerichtet wird und welche Dashboards erstellt werden.

| Was Sie bekommen | Wie Sie es verwenden |
|---|---|
| Analytics architect agent | Aktiviert sich bei Analytics-bezogenen Aufgaben |

---

### openclaw

**Session-Management für OpenClaw-Gateway.**
Werkzeuge zur Verwaltung langlebiger KI-Sitzungen — Kontext komprimieren, Erkenntnisse extrahieren und Leistung aufrechterhalten.

| Was Sie bekommen | Wie Sie es verwenden |
|---|---|
| Session compressor | Geben Sie `/openclaw:compact` ein |
| Learning extractor | Geben Sie `/openclaw:extract` ein |
| Context monitor | Führen Sie `context-monitor.sh` aus |
| Context guardian | Führen Sie `context-guardian-daemon.sh` aus |
| Gateway restart | Führen Sie `self-reboot.sh` aus |
| Blob cleaner | Führen Sie `clean-session-blobs.sh` aus |

> Hook: Erinnert Sie daran, Erkenntnisse zu speichern, bevor große Sitzungen komprimiert werden.

## Installation

### Ein einzelnes Plugin installieren

Wählen Sie nur das aus, was Sie brauchen:

```bash
claude plugin add github:joey-barbier/ClaudeCode-Plugin/plugins/code-review
```

### Vor der Installation testen

Ein Plugin temporär testen:

```bash
claude --plugin-dir ./plugins/dev-workflow
```

### Von einer lokalen Kopie installieren

```bash
git clone https://github.com/joey-barbier/ClaudeCode-Plugin.git
claude plugin add ./ClaudeCode-Plugin/plugins/cc-memory
```

## Schnellstart

1. **Installieren Sie die gewünschten Plugins** (siehe oben)
2. **Agents arbeiten automatisch** — sie aktivieren sich, wenn Claude eine relevante Situation erkennt
3. **Skills sind Befehle** — geben Sie sie bei Bedarf ein:
   ```
   /cc-setup:setup              # Claude Code Einstellungen konfigurieren
   /cc-memory:memory            # Projektkontext wiederherstellen
   /dev-workflow:new-feature    # Vorbereitung für ein neues Feature
   /dev-workflow:implement      # Mit der Entwicklung beginnen
   /dev-workflow:time-check     # Prüfen, ob Sie zu komplex denken
   /dev-workflow:init-docs      # Projektdokumentation einrichten
   /qa-testing:unit-test-expert # Tests generieren
   /openclaw:compact            # Eine große Sitzung komprimieren
   /openclaw:extract            # Erkenntnisse aus einer Sitzung speichern
   ```
4. **Hooks laufen im Hintergrund** — schützen Sie vor Fehlern

## Empfohlene Setups

| Profil | Empfohlene Plugins |
|---|---|
| **Gerade erst mit Claude Code begonnen** | `cc-setup` → führen Sie `/cc-setup:setup` aus |
| **Solo-Entwickler** | `cc-memory` + `dev-workflow` + `code-review` |
| **Team mit Code-Reviews** | `code-review` + `qa-testing` + `dev-workflow` |
| **Projektmanager oder Autor** | `cc-setup` + `cc-memory` |
| **OpenClaw-Gateway-Operator** | `openclaw` + `cc-memory` |

## Struktur

```
plugins/
├── code-review/     # PR review agent + push guard hook
├── qa-testing/      # QA validation + test generation
├── dev-workflow/    # Dev methodology + git safety hook
├── cc-memory/       # Context restoration + auto-detect hook
├── cc-setup/        # Interactive CLAUDE.md generator
├── analytics/       # SaaS analytics tracking
└── openclaw/        # Session management + pre-compact hook
```

## Lizenz

MIT — frei zu verwenden, zu modifizieren und zu teilen.
