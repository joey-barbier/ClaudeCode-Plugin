**[FR](README.md)** | **[ES](README.es.md)** | **[DE](README.de.md)**

# AI Coach — No Hype

An agent that tells you the truth: do you actually need AI for this, or not?

## The Problem

You discovered AI. You tried ChatGPT, Copilot, Claude. Sometimes it works. Often it's generic, off-target, or you spend more time fixing the output than doing it yourself. You don't know where to start, you don't know which tool to use, and nobody tells you when AI is pointless.

## What the Coach Does

It diagnoses your real need and gives you a **clear-cut verdict**. If you show up without context, it asks 2-3 questions first — the verdict comes after, not before.

| Verdict | When | Example |
|---------|------|---------|
| **A — No AI needed** | A script or a process is enough | "Renommer 200 fichiers ? C'est 3 lignes de bash." |
| **B — Yes, here's how** | AI is relevant, here's the plan | "Ton probleme c'est le briefing. Installe horka-setup." |
| **C — Bad idea** | The idea doesn't hold up, here's why | "Un bot qui repond a ta place sur Slack ? Non. Voila pourquoi." |

It doesn't sell anything. It doesn't validate just to be nice. If your idea is bad, it tells you.

## Install

### Option 1 — Claude Code (devs, tech leads)

```bash
claude plugin install coach-ia
```

Then in any conversation:

```
> coach, j'ai besoin d'aide avec l'IA
```

### Option 2 — Claude Desktop (POs, managers, non-devs)

If you don't use the terminal, you can use the coach directly in Claude Desktop:

1. **Open Claude Desktop** (download from [claude.ai/download](https://claude.ai/download) if you haven't)
2. **Create a new Project**: click your name top-left → "Projects" → "Create Project"
3. **Name it** "Coach IA" (or whatever you want)
4. **Paste the instructions**: on this GitHub page, go to the `skills/horka-coach-ia/` folder, open the `SKILL.md` file, copy everything after the second `---`, and paste it into the "Project instructions" field
5. **Done.** Open a conversation in this project and ask your question

Works exactly the same: you describe your problem, the coach diagnoses and gives you a verdict.

> **Tip**: Pin the project for quick access. Every new conversation in this project starts with the coach active.

## Real Examples

### A junior dev struggling with generic code

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

### A skeptical senior dev

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

### A PO who wants to automate everything

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

### A non-technical manager

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

### A bad idea

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

## Why Use It

**New to AI?** The coach saves you from wasting 3 weeks on the wrong tool. It tells you where to start and in what order.

**Already using AI?** The coach challenges you. Do you really need an agent for that? Or would a script do? It forces you to ask the right question before diving in.

**Managing a team?** The coach gives you a framework. Not a technical tool — a method to integrate AI without chaos.

## What It Does NOT Do

- It doesn't code for you (ask Claude directly for that)
- It doesn't debug your code (not its job)
- It doesn't sell anything (no "it's magic", no "game changer")
- It doesn't validate your ideas out of politeness (if it's bad, it says so)

## The Ecosystem

When the coach identifies a concrete need, it points you to the right tool:

| Your need | The tool | What it changes |
|-----------|----------|-----------------|
| Claude doesn't get my project | `horka-setup` | Custom CLAUDE.md = no more generic code |
| It forgets everything between sessions | `horka-memory` | Context saved and restored automatically |
| Nobody reviews my code | `horka-review` | Double review: antagonist + tech lead |
| My tests don't cover enough | `horka-qa-testing` | Challenges your "it's done" claims |
| Multi-layer features = mess | `horka-dev-workflow` | Coordinates changes in the right order |
| My sessions are too long | `horka-openclaw` | Compresses and extracts decisions |
| Is my skill well-built? | `horka-skill-eval` | Audit /100 against best practices |

All plugins are available on the marketplace:
```bash
/plugin marketplace add joey-barbier/ClaudeCode-Plugin
```

The coach never lists everything. It points you to **one tool** — the one that solves **your** problem.

## Philosophy

> Vous etiez deja cuisiniers. L'IA, c'est les bons couteaux.
> Mais un bon couteau dans les mains de quelqu'un qui ne sait pas cuisiner,
> ca coupe juste plus vite — dans la mauvaise direction.

3 reflexes:
1. **Pick the tool** — the least powerful one that's enough
2. **Iterate** — the first result is a starting point, not a verdict
3. **Capitalize** — something works → turn it into a tool

---

Built by [HORKA_TV](https://twitch.tv/horka_tv). Free. MIT.
