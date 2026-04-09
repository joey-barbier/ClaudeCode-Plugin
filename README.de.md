# ClaudeCode-Plugin

**[EN](README.md)** | **[FR](README.fr.md)** | **[ES](README.es.md)**

Einsatzbereite Claude Code Plugins: Memory, Code-Review, Dev-Workflow, Sicherheitsvorkehrungen. Gebaut aus Monaten täglicher Nutzung.

> Du verfolgst externe Bibliotheken, CVEs und mehr? Entdecke [LibTracker](https://app.libtracker.io/).

![Demo](assets/demo.gif)

## Installation

```bash
/plugin marketplace add joey-barbier/ClaudeCode-Plugin
```

Dann `/plugin` → **Discover** Tab zum Durchsuchen, oder installiere Plugins einzeln unten.

## Plugin-Katalog

| Plugin | Funktion | Komponenten |
|---|---|---|
| **[horka-setup](#horka-setup)** | Personalisierte `CLAUDE.md` + Architektur-Docs | 2 Skills |
| **[horka-memory](#horka-memory)** | Persistente Projekt-Memory zwischen Sitzungen | 1 Skill |
| **[horka-code-review](#horka-code-review)** | PR-Review von einem Senior Tech Lead | Agent + Skill + Hook |
| **[horka-qa-testing](#horka-qa-testing)** | QA-Validierung + Business Unit Tests | Agent + Skill |
| **[horka-dev-workflow](#horka-dev-workflow)** | Dev-Methodik + Git-Sicherheit | Agent + 2 Skills + Hook |
| **[horka-analytics](#horka-analytics)** | SaaS Tracking / Funnel Experte | Agent |
| **[horka-openclaw](#horka-openclaw)** | Lange KI-Sitzungsverwaltung | 2 Skills + Hook |
| **[horka-skill-eval](#horka-skill-eval)** | Skill-Qualitätsprüfer | Skill |

---

## Erste Schritte

### 1. Claude konfigurieren — `horka-setup`

```bash
claude plugin install horka-setup
```

- `/horka-setup:horka-claude-setup` — interaktiver Fragebogen → personalisierte `CLAUDE.md`
- `/horka-setup:horka-init-docs` — generiert Architektur-Docs aus deiner Codebase (ARCHITECTURE, CONVENTIONS, WORKFLOW_PATTERNS...)

### 2. Gib Claude ein Gedächtnis — `horka-memory`

```bash
claude plugin install horka-memory
```

Stellt automatisch den Projektkontext bei Sitzungsbeginn wieder her. `/horka-memory:horka-memory-restore` zur Initialisierung in einem neuen Projekt — scannt deine Codebase und erstellt PROJECT_STATE, ARCHITECTURE, DECISIONS, NEXT_STEPS, COMMANDS Dateien.

### 3. Wähle die Tools unten

Jedes Plugin funktioniert unabhängig.

---

## horka-code-review

**PR-Review von einem Senior Tech Lead.** Aktiviert sich automatisch bei "review PR" oder vor dem Push.

```bash
claude plugin install horka-code-review
```

| Komponente | Auslöser | Funktion |
|---|---|---|
| Agent `review-pr` | "review PR" / Pre-Push | Vollständige Durchsicht: Architektur + Sicherheit + Qualität |
| `/horka-code-review:horka-review-changes` | Befehl | On-Demand-Review aktueller Änderungen in isoliertem Kontext |
| Push-Hook | auto | Blockiert Push zu main/master, warnt bei Feature Branches |

---

## horka-qa-testing

**QA-Validierung + Generierung von Business Unit Tests.**

```bash
claude plugin install horka-qa-testing
```

| Komponente | Auslöser | Funktion |
|---|---|---|
| Agent `qa-validate` | "Feature fertig"-Behauptungen | Hinterfragt Aussagen, testet Grenzfälle |
| `/horka-qa-testing:horka-unit-test-generate` | Befehl | Generiert Tests passend zu deinen Konventionen (Berechtigungen, Limits, Konsistenz) |

---

## horka-dev-workflow

**Strukturierte Dev-Methodik + Git-Sicherheit.**

```bash
claude plugin install horka-dev-workflow
```

| Komponente | Auslöser | Funktion |
|---|---|---|
| Agent `dev-methodology` | komplexe Implementierungen | Koordiniert mehrschichtige Änderungen in richtiger Reihenfolge |
| `/horka-dev-workflow:horka-git-new-feature` | Befehl | Bereitet Git vor: main → pull → gemergte löschen → neuer `feature/` Branch |
| `/horka-dev-workflow:horka-mvp-time-guardian` | Befehl | Erkennt Schleifen, schlägt schnellste Lösung vor |
| Git-Sicherheits-Hook | auto | Blockiert Force Push, Hard Reset, Checkout ., Clean, Branch -D |

---

## horka-analytics

**SaaS-Analytics-Experte.** Aktiviert sich automatisch bei Tracking / Funnel / Konvertierungs-Themen. Entwirft was zu messen ist, Implementierung und Dashboards.

```bash
claude plugin install horka-analytics
```

---

## horka-openclaw

**Verwaltung langer KI-Sitzungen.**

```bash
claude plugin install horka-openclaw
```

| Komponente | Auslöser | Funktion |
|---|---|---|
| `/horka-openclaw:horka-openclaw-session-compact` | Befehl | Komprimiert Sitzungen >20 MB, extrahiert Entscheidungen/Configs, archiviert Original |
| `/horka-openclaw:horka-openclaw-session-extract` | Befehl | Extrahiert Erkenntnisse in Memory-Dateien |
| Session-Hook | auto | Warnt vor schwerer Kompaktierung |

Shell-Tools: `context-monitor.sh`, `context-guardian-daemon.sh`, `self-reboot.sh`, `clean-session-blobs.sh`.

---

## horka-skill-eval

**Skill-Qualitätsprüfer** gegen Anthropics offizielle Best Practices.

```bash
claude plugin install horka-skill-eval
```

| Komponente | Auslöser | Funktion |
|---|---|---|
| `/horka-skill-eval:horka-skill-evaluate` | Befehl | Bewertet 5 Kategorien auf 100, schlägt Korrekturen vor, bewertet vor/nach |

---

## Wie Plugins funktionieren

| Typ | Verhalten | Beispiel |
|---|---|---|
| **Agents** | Autonom — Claude aktiviert sie bei Relevanz | `review-pr` bei "review PR" |
| **Skills** | Befehle, die du eingibst | `/horka-memory:horka-memory-restore` |
| **Hooks** | Stille Wächter im Hintergrund | Blockiert `git push --force` |

## Fragen?

Ich streame live auf Twitch während ich mit Claude Code baue. Komm Fragen stellen, Plugins in Aktion sehen oder neue vorschlagen.

**[twitch.tv/horka_tv](https://twitch.tv/horka_tv)**

## Lizenz

MIT — kostenlos zu verwenden, zu modifizieren und zu teilen.
