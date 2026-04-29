**[EN](README.en.md)** | **[ES](README.es.md)** | **[DE](README.de.md)**

# Coach IA — Sans la hype

Un agent qui te dit la verite : est-ce que t'as besoin d'IA pour ca, ou pas ?

## Le probleme

Tu as decouvert l'IA. Tu as essaye ChatGPT, Copilot, Claude. Parfois ca marche. Souvent c'est generique, a cote, ou tu perds plus de temps a corriger qu'a faire toi-meme. Tu sais pas par ou commencer, tu sais pas quel outil utiliser, et personne te dit quand l'IA sert a rien.

## Ce que fait le Coach

Il diagnostique ton vrai besoin et te donne un **verdict tranche**. Si tu arrives sans contexte, il te pose 2-3 questions d'abord — le verdict vient apres, pas avant.

| Verdict | Quand | Exemple |
|---------|-------|---------|
| **A — Pas besoin d'IA** | Un script ou un process suffit | "Renommer 200 fichiers ? C'est 3 lignes de bash." |
| **B — Oui, voila comment** | L'IA est pertinente, voici la marche a suivre | "Ton probleme c'est le briefing. Installe horka-setup." |
| **C — Mauvaise idee** | L'idee ne tient pas, voici pourquoi | "Un bot qui repond a ta place sur Slack ? Non. Voila pourquoi." |

Il ne vend rien. Il ne valide pas pour faire plaisir. Si ton idee est mauvaise, il te le dit.

## Install

### Option 1 — Claude Code (devs, tech leads)

```bash
claude plugin install coach-ia
```

Puis dans n'importe quelle conversation :

```
> coach, j'ai besoin d'aide avec l'IA
```

### Option 2 — Claude Desktop (PO, managers, non-devs)

Si tu n'utilises pas le terminal, tu peux utiliser le coach directement dans Claude Desktop :

1. **Ouvre Claude Desktop** (telecharge sur [claude.ai/download](https://claude.ai/download) si c'est pas fait)
2. **Cree un nouveau Projet** : clique sur ton nom en haut a gauche → "Projects" → "Create Project"
3. **Nomme-le** "Coach IA" (ou ce que tu veux)
4. **Colle les instructions** : sur cette page GitHub, va dans le dossier `skills/horka-coach-ia/`, ouvre le fichier `SKILL.md`, copie tout le contenu apres le second `---`, et colle-le dans le champ "Project instructions"
5. **C'est pret.** Ouvre une conversation dans ce projet et pose ta question

Ca marche exactement pareil : tu decris ton probleme, le coach diagnostique et te donne un verdict.

> **Astuce** : Epingle le projet pour y acceder rapidement. Chaque nouvelle conversation dans ce projet demarre avec le coach actif.

## Exemples concrets

### Un dev junior qui galere avec le code generique

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

### Un dev senior sceptique

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

### Un PO qui veut tout automatiser

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

### Un manager non-technique

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

### Une mauvaise idee

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

## Pourquoi l'utiliser

**Tu debutes avec l'IA ?** Le coach t'evite de perdre 3 semaines sur le mauvais outil. Il te dit par ou commencer et dans quel ordre.

**Tu utilises deja l'IA ?** Le coach te challenge. T'as vraiment besoin d'un agent pour ca ? Ou un script suffit ? Il te force a poser la bonne question avant de foncer.

**Tu geres une equipe ?** Le coach te donne un cadre. Pas un outil technique — une methode pour integrer l'IA sans chaos.

## Ce qu'il ne fait PAS

- Il ne code pas a ta place (demande ca a Claude directement)
- Il ne debug pas ton code (c'est pas son role)
- Il ne vend rien (pas de "c'est magique", pas de "game changer")
- Il ne valide pas tes idees par politesse (si c'est mauvais, il le dit)

## L'ecosysteme

Quand le coach identifie un besoin concret, il te redirige vers le bon outil :

| Ton besoin | L'outil | Ce que ca change |
|------------|---------|-----------------|
| Claude comprend pas mon projet | `horka-setup` | CLAUDE.md personnalise = plus de code generique |
| Il oublie tout entre les sessions | `horka-memory` | Contexte sauvegarde et restaure automatiquement |
| Personne relit mon code | `horka-review` | Double review : antagoniste + tech lead |
| Mes tests couvrent pas assez | `horka-qa-testing` | Challenge tes claims "c'est fini" |
| Features multi-couches = bordel | `horka-dev-workflow` | Coordonne les changements dans l'ordre |
| Mes sessions sont trop longues | `horka-openclaw` | Compresse et extrait les decisions |
| Mon skill est-il bien fait ? | `horka-skill-eval` | Audit /100 contre les best practices |

Tous les plugins sont disponibles sur la marketplace :
```bash
/plugin marketplace add joey-barbier/ClaudeCode-Plugin
```

Le coach ne liste jamais tout. Il redirige vers **un seul outil**, celui qui repond a **ton** probleme.

## Philosophie

> Vous etiez deja cuisiniers. L'IA, c'est les bons couteaux.
> Mais un bon couteau dans les mains de quelqu'un qui ne sait pas cuisiner,
> ca coupe juste plus vite — dans la mauvaise direction.

3 reflexes :
1. **Choisir l'outil** — le moins puissant qui suffit
2. **Iterer** — le premier resultat est une base, pas un verdict
3. **Capitaliser** — un truc qui marche → en faire un outil

---

Construit par [HORKA_TV](https://twitch.tv/horka_tv). Gratuit. MIT.
