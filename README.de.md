# ClaudeCode-Plugin

**[EN](README.md)** | **[FR](README.fr.md)** | **[ES](README.es.md)**

Einsatzbereite Plugins, die Claude Code in echten Projekten tatsächlich nützlich machen. Memory, Code-Review, Entwicklungs-Workflow, Sicherheitsvorkehrungen — gebaut aus Monaten täglicher Nutzung.

> Nebenbei, um deine externen Bibliotheken, CVEs und mehr zu verfolgen, entdecke [LibTracker](https://app.libtracker.io/).

![Demo](assets/demo.gif)

## Erste Schritte

Folge den Schritten der Reihe nach. Jeder baut auf dem vorherigen auf.

### Schritt 1: Claude Code konfigurieren (nur beim ersten Mal)

Installiere `cc-setup` und führe den Setup-Assistenten aus. Er fragt nach deinem Workflow und generiert eine personalisierte `CLAUDE.md` — die Datei, die Claude sagt, wie DU arbeitest.

```bash
claude plugin add github:joey-barbier/ClaudeCode-Plugin/plugins/cc-setup
```
Dann gebe `/cc-setup:setup` ein und beantworte die Fragen.

### Schritt 2: Gib Claude ein Gedächtnis

Installiere `cc-memory`, damit Claude dein Projekt zwischen Sitzungen im Gedächtnis behält. Nicht mehr erklären müssen, wo du aufgehört hast, nach einem Komprimieren oder einem neuen Gespräch.

```bash
claude plugin add github:joey-barbier/ClaudeCode-Plugin/plugins/cc-memory
```

**Was passiert:** Wenn du Claude öffnest, erkennt es automatisch deine Projektdateien und stellt den vollständigen Kontext wieder her — was erledigt ist, was nicht, worauf du dich als nächstes konzentrieren solltest. Gebe `/cc-memory:memory` ein, um Memory in einem neuen Projekt zu initialisieren oder es manuell wiederherzustellen.

### Schritt 3: Füge die Tools hinzu, die du brauchst

Wähle, was zu deinem Workflow passt. Jedes Plugin funktioniert unabhängig.

---

#### code-review — *Autonom*

**Dein persönlicher Senior Tech Lead.** Aktiviert sich automatisch, wenn du "review PR" sagst oder wenn Claude erkennt, dass Code bereit zum Push ist. Führt einen vollständigen ersten Durchgang durch (Architektur, Sicherheit, Qualität), damit du dich beim Review auf das Wesentliche konzentrieren kannst — nicht auf Tippfehler und fehlplatzierte Ifs.

```bash
claude plugin add github:joey-barbier/ClaudeCode-Plugin/plugins/code-review
```

> Hook enthalten (läuft automatisch, kein Befehl nötig): Blockiert Push zu main/master. Erinnert dich daran, vor dem Push von Feature Branches zu überprüfen.

---

#### qa-testing — *Gemischt (autonom + Befehl)*

**QA-Validierung und Test-Generierung.** Der QA-Agent aktiviert sich automatisch, wenn du behauptest, dass eine Funktion erledigt ist — er hinterfragt deine Aussagen und testet Grenzfälle. Der Test-Generator ist ein manueller Befehl.

```bash
claude plugin add github:joey-barbier/ClaudeCode-Plugin/plugins/qa-testing
```

| Komponente | Funktionsweise |
|---|---|
| QA-Validierungs-Agent | Autonom — aktiviert sich bei der Validierung von Funktionen |
| Test-Generator | Befehl — gebe `/qa-testing:unit-test-expert` ein |

---

#### dev-workflow — *Befehle + autonomer Agent*

**Strukturierte Entwicklungsmethodik.** Der Agent aktiviert sich bei komplexen Implementierungen. Die Skills sind Befehle, die du eingibst, wenn nötig.

```bash
claude plugin add github:joey-barbier/ClaudeCode-Plugin/plugins/dev-workflow
```

| Komponente | Funktionsweise |
|---|---|
| Dev-Methodik-Agent | Autonom — aktiviert sich bei komplexen mehrschichtigen Arbeiten |
| `/dev-workflow:implement` | Befehl — starte eine strukturierte Dev-Sitzung |
| `/dev-workflow:new-feature` | Befehl — bereite Git für eine neue Funktion vor |
| `/dev-workflow:time-check` | Befehl — erkenne Over-Engineering und Schleifen |
| `/dev-workflow:init-docs` | Befehl — initialisiere Projektdokumentation |

> Hook enthalten (läuft automatisch, kein Befehl nötig): Blockiert gefährliche Git-Befehle (Force Push, Hard Reset, Checkout ., Restore ., Clean, Branch -D).

---

#### analytics — *Autonom*

**SaaS-Analytics-Experte.** Aktiviert sich, wenn du an Tracking, Funnels oder Konvertierung arbeitest. Entwirft, was gemessen werden soll, wie es eingerichtet wird und welche Dashboards zu erstellen sind.

```bash
claude plugin add github:joey-barbier/ClaudeCode-Plugin/plugins/analytics
```

---

#### openclaw — *Befehle*

**Sitzungsverwaltung für OpenClaw Gateway.** Tools für lange laufende KI-Sitzungen — komprimiere Kontext, extrahiere Erkenntnisse, erhalte Leistung.

```bash
claude plugin add github:joey-barbier/ClaudeCode-Plugin/plugins/openclaw
```

| Komponente | Funktionsweise |
|---|---|
| `/openclaw:compact` | Befehl — komprimiere eine große Sitzung |
| `/openclaw:extract` | Befehl — speichere Erkenntnisse vor Cleanup |
| Shell-Skripte | `context-monitor.sh`, `context-guardian-daemon.sh`, `self-reboot.sh`, `clean-session-blobs.sh` |

> Hook enthalten (läuft automatisch, kein Befehl nötig): Erinnert dich daran, Erkenntnisse zu speichern, bevor große Sitzungen komprimiert werden.

## Wie Plugins funktionieren

Drei Arten von Komponenten, drei Verhaltensweisen:

| Typ | Verhalten | Beispiel |
|---|---|---|
| **Agents** | Autonom — Claude aktiviert sie, wenn relevant | Code-Review-Agent wird bei "review PR" ausgelöst |
| **Skills** | Befehle — du gibst sie ein, wenn nötig | `/cc-memory:memory` zum Wiederherstellen des Kontexts |
| **Hooks** | Stumm — laufen im Hintergrund, schützen dich vor Fehlern | Blockiert `git push --force` automatisch |

## Installiere den Marketplace

Um alle Plugins aus Claude Code zu durchsuchen:

```bash
/plugin marketplace add github:joey-barbier/ClaudeCode-Plugin
```

Verwende dann `/plugin` → **Discover** Tab zum Durchsuchen und Installieren.

## Fragen?

Ich streame live auf Twitch, während ich mit Claude Code baue. Komme Fragen stellen, sehe die Plugins in Aktion oder schlage neue vor.

**[twitch.tv/horka_tv](https://twitch.tv/horka_tv)**

## Lizenz

MIT — kostenlos zu verwenden, zu modifizieren und zu teilen.
