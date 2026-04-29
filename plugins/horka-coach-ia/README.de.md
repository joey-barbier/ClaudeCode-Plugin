**[EN](README.en.md)** | **[FR](README.md)** | **[ES](README.es.md)**

# Coach IA — Ohne den Hype

Ein Agent, der dir die Wahrheit sagt: brauchst du dafuer KI, oder nicht?

## Das Problem

Du hast KI entdeckt. Du hast ChatGPT, Copilot, Claude ausprobiert. Manchmal funktioniert's. Oft ist es generisch, daneben, oder du verlierst mehr Zeit mit Korrekturen als es selbst zu machen. Du weisst nicht, wo anfangen, du weisst nicht, welches Tool nehmen, und niemand sagt dir, wann KI nichts bringt.

## Was der Coach macht

Er diagnostiziert dein echtes Problem und gibt dir ein **klares Urteil**. Wenn du ohne Kontext ankommst, stellt er erstmal 2-3 Fragen — das Urteil kommt danach, nicht vorher.

| Urteil | Wann | Beispiel |
|--------|------|----------|
| **A — Keine KI noetig** | Ein Script oder ein Prozess reicht | "200 Dateien umbenennen? Das sind 3 Zeilen Bash." |
| **B — Ja, so geht's** | KI ist sinnvoll, hier ist die Anleitung | "Dein Problem ist das Briefing. Installier horka-setup." |
| **C — Schlechte Idee** | Die Idee haelt nicht, hier ist warum | "Ein Bot der fuer dich auf Slack antwortet? Nein. Darum." |

Er verkauft nichts. Er validiert nicht, um zu gefallen. Wenn deine Idee schlecht ist, sagt er's dir.

## Install

### Option 1 — Claude Code (Devs, Tech Leads)

```bash
claude plugin install coach-ia
```

Dann in jeder beliebigen Konversation:

```
> coach, j'ai besoin d'aide avec l'IA
```

### Option 2 — Claude Desktop (POs, Manager, Nicht-Techniker)

Wenn du kein Terminal benutzt, kannst du den Coach direkt in Claude Desktop verwenden:

1. **Oeffne Claude Desktop** (lade es unter [claude.ai/download](https://claude.ai/download) herunter, falls noch nicht geschehen)
2. **Erstelle ein neues Projekt**: klicke oben links auf deinen Namen → "Projects" → "Create Project"
3. **Nenne es** "Coach IA" (oder wie du willst)
4. **Fuege die Instruktionen ein**: gehe auf dieser GitHub-Seite in den Ordner `skills/horka-coach-ia/`, oeffne die Datei `SKILL.md`, kopiere den gesamten Inhalt nach dem zweiten `---`, und fuege ihn im Feld "Project instructions" ein
5. **Fertig.** Oeffne eine Konversation in diesem Projekt und stell deine Frage

Funktioniert genau gleich: du beschreibst dein Problem, der Coach diagnostiziert und gibt dir ein Urteil.

> **Tipp**: Pinne das Projekt an, um schnell darauf zugreifen zu koennen. Jede neue Konversation in diesem Projekt startet mit aktivem Coach.

## Konkrete Beispiele

### Ein Junior-Dev, der mit generischem Code kaempft

```
> Je suis dev React depuis 8 mois. ChatGPT me sort des composants
> generiques qui correspondent pas a notre style. Je perds du temps.

Coach:
  Diagnostic : le probleme c'est pas l'outil, c'est le briefing.
  L'IA c'est un collegue brillant, premier jour. Sans contexte
  sur ta stack et tes conventions, elle code en generique. Normal.

  VERDICT B — Oui. Voila comment.
  1. Donne le contexte (stack, conventions, un exemple de composant)
  2. Itere au lieu de jeter (3 passes, 10 min au lieu de 45)
  3. Capitalise (sauvegarde le prompt qui marche)

  → Installe horka-setup pour creer ton CLAUDE.md.
```

---

### Ein skeptischer Senior-Dev

```
> J'ai 12 ans de Go. On a 200+ microservices et quand on change
> un contrat d'API, on sait jamais quels services sont impactes.
> On passe des heures a chercher.

Coach:
  VERDICT B — Oui. Voila comment.
  Ton besoin c'est de l'analyse d'impact. Socle deterministe
  d'abord (graphe de deps, specs OpenAPI). IA ensuite pour
  scanner les consumers et identifier les champs impactes.
  Teste sur UN changement de contrat reel d'abord — 20 min,
  pas 3 semaines.
```

---

### Ein PO, der alles automatisieren will

```
> Je veux que l'IA fasse 80% de mon job : user stories, backlog,
> CR de reunion, release notes, retours utilisateurs...

Coach:
  Stop. 80% de ton job c'est pas de l'automatisation,
  c'est une liste de courses sans savoir ce que tu cuisines.

  VERDICT C — Mauvaise approche.
  Vouloir tout automatiser d'un coup, c'est comme ca qu'on
  perd du temps au lieu d'en gagner. La priorisation du
  backlog c'est TON job — si tu delegues ca, tu delegues
  ton role.

  Commence par UN seul cas : les CR de reunion. Le plus
  simple, le moins risque. Tu apprends a briefer l'IA
  avant de passer aux cas complexes.
```

---

### Ein nicht-technischer Manager

```
> Mon N+1 veut que j'integre l'IA dans l'equipe de 8 devs.
> J'y connais rien en code. Comment je fais ?

Coach:
  Ton job c'est pas de comprendre le code. Ton job c'est
  de CADRER L'USAGE. C'est du management, pas de la tech.

  VERDICT B — Plan en 3 temps :
  1. Ecouter (cartographie des irritants de l'equipe)
  2. Cadrer (3 regles : securite, perimetre, mesure)
  3. Piloter (1 cas d'usage, 2-3 devs, 2 semaines)

  → Un slide, pas un roman. C'est un plan de manager.
```

---

### Eine schlechte Idee

```
> Je veux un agent IA qui repond a ma place sur Slack
> quand je suis en meeting.

Coach:
  VERDICT C — Mauvaise idee.
  1. Tes collegues pensent parler a toi. L'IA dit une
     connerie = ta credibilite qui prend.
  2. Le contexte Slack (sarcasme, politique, urgences),
     l'IA ne le capte pas.
  3. Le vrai probleme c'est un SPOF humain, pas un
     probleme d'outil.

  Alternative : statut Slack + delegation claire + FAQ.
  30 secondes, zero risque.
```

## Warum ihn benutzen

**Du faengst gerade mit KI an?** Der Coach erspart dir 3 Wochen mit dem falschen Tool. Er sagt dir, wo anfangen und in welcher Reihenfolge.

**Du benutzt KI schon?** Der Coach fordert dich heraus. Brauchst du wirklich einen Agenten dafuer? Oder reicht ein Script? Er zwingt dich, die richtige Frage zu stellen, bevor du loslegst.

**Du leitest ein Team?** Der Coach gibt dir einen Rahmen. Kein technisches Tool — eine Methode, um KI ohne Chaos zu integrieren.

## Was er NICHT macht

- Er codet nicht fuer dich (frag dafuer Claude direkt)
- Er debuggt nicht deinen Code (das ist nicht seine Rolle)
- Er verkauft nichts (kein "das ist magisch", kein "Game Changer")
- Er validiert deine Ideen nicht aus Hoeflichkeit (wenn's schlecht ist, sagt er's)

## Das Oekosystem

Wenn der Coach ein konkretes Problem identifiziert, leitet er dich zum richtigen Tool weiter:

| Dein Problem | Das Tool | Was sich aendert |
|--------------|----------|-----------------|
| Claude versteht mein Projekt nicht | `horka-setup` | Personalisiertes CLAUDE.md = kein generischer Code mehr |
| Er vergisst alles zwischen Sessions | `horka-memory` | Kontext automatisch gespeichert und wiederhergestellt |
| Niemand reviewt meinen Code | `horka-review` | Doppeltes Review: Antagonist + Tech Lead |
| Meine Tests decken nicht genug ab | `horka-qa-testing` | Hinterfragt deine "ist fertig"-Aussagen |
| Multi-Layer-Features = Chaos | `horka-dev-workflow` | Koordiniert Aenderungen in der richtigen Reihenfolge |
| Meine Sessions sind zu lang | `horka-openclaw` | Komprimiert und extrahiert Entscheidungen |
| Ist mein Skill gut gebaut? | `horka-skill-eval` | Audit /100 gegen Best Practices |

Alle Plugins sind auf der Marketplace verfuegbar:
```bash
/plugin marketplace add joey-barbier/ClaudeCode-Plugin
```

Der Coach listet nie alles auf. Er leitet dich zu **einem einzigen Tool** weiter, dem, das **dein** Problem loest.

## Philosophie

> Vous etiez deja cuisiniers. L'IA, c'est les bons couteaux.
> Mais un bon couteau dans les mains de quelqu'un qui ne sait pas cuisiner,
> ca coupe juste plus vite — dans la mauvaise direction.

3 Reflexe:
1. **Das richtige Tool waehlen** — das am wenigsten maechtige, das reicht
2. **Iterieren** — das erste Ergebnis ist eine Basis, kein Endurteil
3. **Kapitalisieren** — was funktioniert → daraus ein Tool machen

---

Gebaut von [HORKA_TV](https://twitch.tv/horka_tv). Kostenlos. MIT.
