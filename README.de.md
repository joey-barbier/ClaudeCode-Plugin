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
| **[horka-coach-ia](#horka-coach-ia)** | KI-Coach: diagnostiziert deinen Bedarf, gibt ein Urteil, leitet zum richtigen Plugin weiter | Skill |
| **[horka-mentor](#horka-mentor)** | Padagogische KI fur Junior-Devs: bewertet, lehrt, baut Schritt fur Schritt, verfolgt Fortschritt | 2 Skills |
| **[horka-setup](#horka-setup)** | Personalisierte `CLAUDE.md` + Architektur-Docs + Design System Extraktor | 3 Skills |
| **[horka-memory](#horka-memory)** | Persistente Projekt-Memory zwischen Sitzungen | 1 Skill |
| **[horka-review](#horka-review)** | Antagonist + Tech Lead Code Review | Agent + 2 Skills + Hook |
| **[horka-qa-testing](#horka-qa-testing)** | QA-Validierung + Business Unit Tests | Agent + Skill |
| **[horka-dev-workflow](#horka-dev-workflow)** | Dev-Methodik + Git-Sicherheit | Agent + 2 Skills + Hook |
| **[horka-analytics](#horka-analytics)** | SaaS Tracking / Funnel Experte | Agent |
| **[horka-openclaw](#horka-openclaw)** | Lange KI-Sitzungsverwaltung | 2 Skills + Hook |
| **[horka-skill-eval](#horka-skill-eval)** | Skill-Qualitätsprüfer | Skill |
| **[horka-agent-forge](#horka-agent-forge)** | Skill-Fabrik mit verpflichtenden Qualitätsgates | Skill |
| **[horka-project-index](#horka-project-index)** | Globaler Projektindex: löst generische Befehle zum richtigen Projekt/Workspace auf | Skill + Skript |

---

## Erste Schritte

### 0. Weisst nicht wo du anfangen sollst? — `horka-coach-ia`

```bash
claude plugin install horka-coach-ia
```

Pragmatischer KI-Coach, der dir die Wahrheit sagt: brauchst du KI dafur, oder nicht?

- Beschreib dein Problem → klares Urteil: **"keine KI notig"** / **"ja, so geht's"** / **"schlechte Idee, darum"**
- Hilft dir zwischen Agent vs Skill vs Skript vs nichts zu unterscheiden
- Leitet dich zum richtigen HORKA-Plugin basierend auf DEINEM Bedarf weiter
- Fur Devs, POs, Tech Leads und Manager
- Funktioniert auch in Claude Desktop — [Anleitung lesen](plugins/horka-coach-ia/README.md)

Ausloser: `coach`, `coach ia`, `aide-moi avec l'IA`, `par ou commencer`

### 1. Claude konfigurieren — `horka-setup`

```bash
claude plugin install horka-setup
```

- `/horka-setup:horka-claude-setup` — interaktiver Fragebogen → personalisierte `CLAUDE.md`
- `/horka-setup:horka-init-docs` — generiert Architektur-Docs aus deiner Codebase (ARCHITECTURE, CONVENTIONS, WORKFLOW_PATTERNS...)
- `/horka-setup:horka-ds-extractor` — extrahiert das Design System eines Frontend-Projekts in Markdown (Tokens, Komponenten, Layout, Style Guide)

### 2. Gib Claude ein Gedächtnis — `horka-memory`

```bash
claude plugin install horka-memory
```

Stellt automatisch den Projektkontext bei Sitzungsbeginn wieder her. `/horka-memory:horka-memory-restore` zur Initialisierung in einem neuen Projekt — scannt deine Codebase und erstellt PROJECT_STATE, ARCHITECTURE, DECISIONS, NEXT_STEPS, COMMANDS Dateien.

### 3. Wähle die Tools unten

Jedes Plugin funktioniert unabhängig.

---

## horka-mentor

**Padagogische KI fur Junior-Entwickler.** Begleitet dich beim Coden, statt fur dich zu coden. Erfordert den [Context7](https://github.com/upstash/context7) MCP-Server.

```bash
claude plugin install horka-mentor
```

| Komponente | Ausloser | Funktion |
|---|---|---|
| `/horka-mentor:horka-mentor` | "mentor", "mentor learn", "mentor build" | Bewertet dein Verstandnis, lehrt Konzepte, baut Schritt fur Schritt. Zwei Modi: learn (vollstandig Sokratisch) und build (zusammen coden — Standard) |
| `/horka-mentor:horka-mentor-quiz` | "mentor quiz", "teste-moi", "revision" | Quiz mit verteilter Wiederholung uber behandelte Themen (T+1, T+3, T+7, T+14, T+30) |
| Proaktiver Modus | auto (wenn aktiviert) | Erkennt unbekannte grundlegende Konzepte in deinen Anfragen — max 2 pro Sitzung, uberspringbar |

**Hauptmerkmale:** Verfolgung pro Thema (unknown/learning/understood/confident), Anti-Gaming (nur offene Fragen), direktiver Modus fur sicherheitskritische Themen, Cross-Stack-Ubersetzung fur Devs, die einen neuen Stack lernen.

---

## horka-review

**Komplettes Code-Review-Toolkit.** Zwei Durchgange: der Antagonist findet Fehler, dann validiert der Tech Lead.

```bash
claude plugin install horka-review
```

| Komponente | Ausloser | Funktion |
|---|---|---|
| `/horka-review:antagonist-reviewer` | "roast", "critique", "find flaws" | Gnadenloser Fehlerfinder — null Komplimente, Output BLOCKED/WARNINGS/WASTE |
| `/horka-review:horka-review-changes` | "review changes", "code review" | Strukturiertes Tech-Lead-Review in isoliertem Kontext |
| Agent `review-pr` | "review PR" / Pre-Push | Vollstandige Durchsicht: Architektur + Sicherheit + Qualitat |
| Review-Guard-Hook | auto | Blockiert Push zum Default-Branch, erzwingt Review-Reihenfolge auf Feature Branches |

**Review-Reihenfolge:** Antagonist (Fehler finden) → Fix → Tech Lead (validieren) → Push/PR

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
