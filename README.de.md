# ClaudeCode-Plugin

**[EN](README.md)** | **[FR](README.fr.md)** | **[ES](README.es.md)**

Einsatzbereite Plugins, die Claude Code in echten Projekten tatsächlich nützlich machen. Memory, Code-Review, Entwicklungs-Workflow, Sicherheitsvorkehrungen — gebaut aus Monaten täglicher Nutzung.

> Nebenbei, um deine externen Bibliotheken, CVEs und mehr zu verfolgen, entdecke [LibTracker](https://app.libtracker.io/).

![Demo](assets/demo.gif)

## Alle Plugins auf einmal installieren

Durchsuche und installiere alles direkt aus Claude Code:

```bash
/plugin marketplace add joey-barbier/ClaudeCode-Plugin
```

Verwende dann `/plugin` → **Discover** Tab, um zu durchsuchen und zu installieren, was du brauchst.

Oder installiere Plugins einzeln, indem du die folgenden Schritte befolgst.

## Erste Schritte

Folge den Schritten der Reihe nach. Jeder baut auf dem vorherigen auf.

### Schritt 1: Claude Code konfigurieren (nur beim ersten Mal)

Installiere `cc-setup` und führe den Setup-Assistenten aus.

```bash
claude plugin add joey-barbier/ClaudeCode-Plugin/plugins/cc-setup
```
Dann gebe `/cc-setup:setup` ein — fragt nach deinem Git-Workflow, Kommunikationsstil, Sicherheitspräferenzen und installierten Plugins, dann generiert eine personalisierte `CLAUDE.md`, die Claude sagt wie DU arbeitest.

### Schritt 2: Gib Claude ein Gedächtnis

Installiere `cc-memory`, damit Claude dein Projekt zwischen Sitzungen im Gedächtnis behält. Nicht mehr erklären müssen, wo du aufgehört hast, nach einem Komprimieren oder einem neuen Gespräch.

```bash
claude plugin add joey-barbier/ClaudeCode-Plugin/plugins/cc-memory
```

**Was passiert:** Wenn du Claude öffnest, erkennt es automatisch deine Projektdateien und stellt den vollständigen Kontext wieder her — was erledigt ist, was nicht, worauf du dich als nächstes konzentrieren solltest. Gebe `/cc-memory:memory` ein, um Memory in einem neuen Projekt zu initialisieren (scannt deine Codebase und erstellt PROJECT_STATE, ARCHITECTURE, DECISIONS, NEXT_STEPS und COMMANDS Dateien) oder den Kontext manuell zu Sitzungsbeginn wiederherzustellen.

### Schritt 3: Füge die Tools hinzu, die du brauchst

Wähle, was zu deinem Workflow passt. Jedes Plugin funktioniert unabhängig.

---

#### code-review — *Autonom*

**Dein persönlicher Senior Tech Lead.** Aktiviert sich automatisch, wenn du "review PR" sagst oder wenn Claude erkennt, dass Code bereit zum Push ist. Führt einen vollständigen ersten Durchgang durch (Architektur, Sicherheit, Qualität), damit du dich beim Review auf das Wesentliche konzentrieren kannst — nicht auf Tippfehler und fehlplatzierte Ifs.

```bash
claude plugin add joey-barbier/ClaudeCode-Plugin/plugins/code-review
```

> Hook enthalten (läuft automatisch, kein Befehl nötig): Blockiert Push zu main/master. Erinnert dich daran, vor dem Push von Feature Branches zu überprüfen.

---

#### qa-testing — *Gemischt (autonom + Befehl)*

**QA-Validierung und Test-Generierung.** Zwei Komponenten — eine autonom, eine manuell.

```bash
claude plugin add joey-barbier/ClaudeCode-Plugin/plugins/qa-testing
```

| Komponente | Funktionsweise |
|---|---|
| QA-Validierungs-Agent | Autonom — aktiviert sich wenn du behauptest eine Funktion sei fertig, hinterfragt deine Aussagen und testet Grenzfälle |
| `/qa-testing:unit-test-expert` | Generiert geschäftsorientierte Unit-Tests: Berechtigungen, Limits, Datenkonsistenz. Liest zuerst deine bestehenden Test-Konventionen, schreibt dann Tests die zu deinen Patterns passen. Unterstützt jede Sprache/Framework |

---

#### dev-workflow — *Befehle + autonomer Agent*

**Strukturierte Entwicklungsmethodik.** Der Agent aktiviert sich bei komplexen Implementierungen. Die Skills sind Befehle, die du eingibst, wenn nötig.

```bash
claude plugin add joey-barbier/ClaudeCode-Plugin/plugins/dev-workflow
```

| Komponente | Funktionsweise |
|---|---|
| Dev-Methodik-Agent | Autonom — aktiviert sich bei komplexen mehrschichtigen Arbeiten |
| `/dev-workflow:implement` | Startet eine strukturierte Dev-Sitzung: analysiert deine Architektur, prüft Doku gegen Code, implementiert dann in der richtigen Abhängigkeitsreihenfolge mit Validierung bei jedem Schritt |
| `/dev-workflow:new-feature` | Bereitet Git für eine neue Funktion vor: wechselt zu main/develop, zieht den neuesten Stand, bietet an gemergte Branches zu löschen, erstellt dann einen `feature/`-Branch |
| `/dev-workflow:time-check` | Erkennt wenn du dich im Kreis drehst: gleicher Fehler 3+ mal, Over-Engineering, Debatten ohne Entscheidung. Schlägt die schnellste funktionierende Lösung mit konkretem Aktionsplan vor |
| `/dev-workflow:init-docs` | Erstellt Architektur-Doku (ARCHITECTURE.md, CONVENTIONS.md, etc.) aus deiner Codebase, oder aktualisiert bestehende Doku chirurgisch wenn sich Patterns ändern |

> Hook enthalten (läuft automatisch, kein Befehl nötig): Blockiert gefährliche Git-Befehle (Force Push, Hard Reset, Checkout ., Restore ., Clean, Branch -D).

---

#### analytics — *Autonom*

**SaaS-Analytics-Experte.** Aktiviert sich, wenn du an Tracking, Funnels oder Konvertierung arbeitest. Entwirft, was gemessen werden soll, wie es eingerichtet wird und welche Dashboards zu erstellen sind.

```bash
claude plugin add joey-barbier/ClaudeCode-Plugin/plugins/analytics
```

---

#### openclaw — *Befehle*

**Sitzungsverwaltung für OpenClaw Gateway.** Tools für lange laufende KI-Sitzungen — komprimiere Kontext, extrahiere Erkenntnisse, erhalte Leistung.

```bash
claude plugin add joey-barbier/ClaudeCode-Plugin/plugins/openclaw
```

| Komponente | Funktionsweise |
|---|---|
| `/openclaw:compact` | Komprimiert große KI-Sitzungen: scannt Dateien über 20 MB, extrahiert Entscheidungen/Configs/Erkenntnisse, archiviert das Original und reduziert die Sitzung auf ein Minimum |
| `/openclaw:extract` | Extrahiert Erkenntnisse aus der aktuellen Sitzung und speichert sie in Memory-Dateien — vor dem Löschen von Sitzungen oder wenn der Kontext schwer wird verwenden |
| Shell-Skripte | `context-monitor.sh`, `context-guardian-daemon.sh`, `self-reboot.sh`, `clean-session-blobs.sh` |

> Hook enthalten (läuft automatisch, kein Befehl nötig): Erinnert dich daran, Erkenntnisse zu speichern, bevor große Sitzungen komprimiert werden.

## Wie Plugins funktionieren

Drei Arten von Komponenten, drei Verhaltensweisen:

| Typ | Verhalten | Beispiel |
|---|---|---|
| **Agents** | Autonom — Claude aktiviert sie, wenn relevant | Code-Review-Agent wird bei "review PR" ausgelöst |
| **Skills** | Befehle — du gibst sie ein, wenn nötig | `/cc-memory:memory` zum Wiederherstellen des Kontexts |
| **Hooks** | Stumm — laufen im Hintergrund, schützen dich vor Fehlern | Blockiert `git push --force` automatisch |

## Fragen?

Ich streame live auf Twitch, während ich mit Claude Code baue. Komme Fragen stellen, sehe die Plugins in Aktion oder schlage neue vor.

**[twitch.tv/horka_tv](https://twitch.tv/horka_tv)**

## Lizenz

MIT — kostenlos zu verwenden, zu modifizieren und zu teilen.
