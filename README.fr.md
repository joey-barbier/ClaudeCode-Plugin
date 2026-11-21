# ClaudeCode-Plugin

**[EN](README.md)** | **[ES](README.es.md)** | **[DE](README.de.md)**

Plugins Claude Code prêts à l'emploi : mémoire, revue de code, workflow dev, garde-fous. Construits à partir de mois d'utilisation quotidienne.

> Tu suis tes librairies externes, CVEs et plus ? Découvre [LibTracker](https://app.libtracker.io/).

![Demo](assets/demo.gif)

## Installation

```bash
/plugin marketplace add joey-barbier/ClaudeCode-Plugin
```

Puis `/plugin` → onglet **Discover** pour parcourir, ou installe les plugins individuellement ci-dessous.

## Catalogue des plugins

| Plugin | Rôle | Composants |
|---|---|---|
| **[horka-mentor](#horka-mentor)** | IA pedagogique pour devs juniors : evalue, enseigne, code pas-a-pas, suit la progression | 2 skills |
| **[horka-setup](#horka-setup)** | `CLAUDE.md` personnalisé + docs d'architecture + extracteur design system | 3 skills |
| **[horka-memory](#horka-memory)** | Mémoire projet persistante entre sessions, avec passation par tâche entre développeurs | 3 skills + hooks |
| **[horka-review](#horka-review)** | Antagonist + Tech Lead code review | agent + 2 skills + hook |
| **[horka-dev-workflow](#horka-dev-workflow)** | Méthodologie dev + sécurité git | agent + 2 skills + hook |
| **[horka-analytics](#horka-analytics)** | Expert tracking / funnels SaaS | agent |
| **[horka-skill-eval](#horka-skill-eval)** | Auditeur qualité de skills | skill |
| **[horka-agent-forge](#horka-agent-forge)** | Usine à skills avec gates de qualité obligatoires | skill |
| **[horka-project-index](#horka-project-index)** | Index global des projets : résout les commandes génériques vers le bon projet/workspace | skill + script |
| **[horka-research-plan](#horka-research-plan)** | Le bon modèle et le bon effort pour chaque rôle d'agent → recherche multi-agents économe en tokens, qui aboutit à un plan d'actions sourcé (page doc-style) ; variante code pour une migration menée par de nombreux agents (testeurs à l'aveugle avant les implémenteurs, branche d'intégration verte sur une porte, fils de validation séparés) ; chaque run est un graphe de tâches sur une page de suivi vivante, avec le débrief des jetons par tâche et par modèle ; des vérifications solides : le produit lancé de bout en bout avant tout push, tests différentiels ancien/nouveau, verdicts liés à un commit | skill |
| **[horka-harness-audit](#horka-harness-audit)** | Par quoi tes règles sont-elles tenues ? Un scan qui ne modifie rien (règles, tes propres hooks lancés face à des commandes à risque jamais exécutées, CI, protection de branche), puis un niveau de 0 à 3 en conception, détection et application, sur une page HTML ouverte à la fin | skill + scripts |
| **[horka-played](#horka-played)** | `/played` comme dans WoW : ta conso de tokens Claude Code par jour, machine et modèle, avec carte à partager et PNG story | skill + scripts |

---

## Commencer

### 1. Configurer Claude — `horka-setup`

```bash
claude plugin install horka-setup
```

- `/horka-setup:horka-claude-setup` — questionnaire interactif → `CLAUDE.md` personnalisé
- `/horka-setup:horka-init-docs` — génère les docs d'architecture depuis ton code (ARCHITECTURE, CONVENTIONS, WORKFLOW_PATTERNS...)
- `/horka-setup:horka-ds-extractor` — extrait le design system d'un projet frontend en Markdown (tokens, composants, layout, guide de style)

### 2. Donner une mémoire à Claude — `horka-memory`

```bash
claude plugin install horka-memory
```

Au début de session, annonce la mémoire du projet et, sur une branche de base, de combien de commits elle est en retard sur le code. `/horka-memory:horka-memory-restore` initialise un nouveau projet — scanne ta codebase et crée les fichiers PROJECT_STATE, ARCHITECTURE, DECISIONS, NEXT_STEPS, COMMANDS. Sur une branche de tâche, `/horka-memory:horka-memory-save` tient une fiche de tâche (point d'arrêt, suite, comment vérifier) dans `.claude/memory/in-progress/`, pour qu'un autre développeur reprenne le travail à partir du dépôt seul. `/horka-memory:horka-memory-close` promeut ce qui doit durer et supprime la fiche avant la fusion.

### 3. Choisis les outils ci-dessous

Chaque plugin fonctionne indépendamment.

---

## horka-mentor

**IA pedagogique pour developpeurs juniors.** T'accompagne pendant que tu codes au lieu de coder a ta place. Necessite le serveur MCP [Context7](https://github.com/upstash/context7).

```bash
claude plugin install horka-mentor
```

| Composant | Declenchement | Role |
|---|---|---|
| `/horka-mentor:horka-mentor` | "mentor", "mentor learn", "mentor build" | Evalue ta comprehension, enseigne les concepts, code pas-a-pas. Deux modes : learn (Socratique complet) et build (code ensemble — defaut) |
| `/horka-mentor:horka-mentor-quiz` | "mentor quiz", "teste-moi", "revision" | Quiz a repetition espacee sur les sujets couverts (J+1, J+3, J+7, J+14, J+30) |
| Mode proactif | auto (si active) | Detecte les concepts fondamentaux inconnus dans tes demandes — max 2 par session, skippable |

**Points cles :** suivi par topic (unknown/learning/understood/confident), anti-gaming (questions ouvertes uniquement), mode directif pour les sujets securite, traduction cross-stack pour les devs qui apprennent un nouveau stack.

---

## horka-review

**Toolkit complet de code review.** Double passe : l'antagonist trouve les failles, puis le Tech Lead valide.

```bash
claude plugin install horka-review
```

| Composant | Déclenchement | Rôle |
|---|---|---|
| `/horka-review:antagonist-reviewer` | "roast", "critique", "find flaws" | Chasseur de failles impitoyable — zero compliment, output BLOCKED/WARNINGS/WASTE |
| `/horka-review:horka-review-changes` | "review changes", "code review" | Revue Tech Lead structuree dans un contexte isole |
| Agent `review-pr` | "review PR" / pre-push | Passe complete architecture + securite + qualite |
| Hook review guard | auto | Bloque push vers branche par defaut (sauf dépôts listés dans `~/.claude/allow-push-default-branch`), impose l'ordre de review sur feature branches |

**Ordre de review :** Antagonist (trouver les failles) → Fix → Tech Lead (valider) → Push/PR

---

## horka-dev-workflow

**Méthodologie dev structurée + sécurité git.**

```bash
claude plugin install horka-dev-workflow
```

| Composant | Déclenchement | Rôle |
|---|---|---|
| Agent `dev-methodology` | implémentations complexes | Coordonne les changements multicouches dans le bon ordre |
| `/horka-dev-workflow:horka-git-new-feature` | commande | Prépare git : main → pull → supprime mergées → nouvelle branche `feature/` |
| `/horka-dev-workflow:horka-mvp-time-guardian` | commande | Détecte les boucles, propose la solution la plus rapide |
| Hook sécurité git | auto | Bloque force push, hard reset, checkout ., clean, branch -D |

---

## horka-analytics

**Expert analytics SaaS.** S'active automatiquement sur les sujets tracking / funnels / conversion. Conçoit quoi mesurer, l'implémentation et les dashboards.

```bash
claude plugin install horka-analytics
```

---

## horka-skill-eval

**Auditeur qualité de skills** contre les best practices Anthropic.

```bash
claude plugin install horka-skill-eval
```

| Composant | Déclenchement | Rôle |
|---|---|---|
| `/horka-skill-eval:horka-skill-evaluate` | commande | Note 5 catégories sur 100, propose des corrections, ré-évalue avant/après |

---

## horka-research-plan

**Le bon modèle, le bon effort, au bon moment, à chaque niveau.** Chaque sous-tâche va au palier le moins cher qui suffit (le plus capable juge, l'expert cherche ou code, le généraliste valide et fusionne, le moins cher fait les recherches), et chaque agent transmet la règle à ses propres sous-agents. Deux modes : **recherche**, qui finit en plan d'actions sourcé (une page doc-style, chaque chiffre avec URL et date), et **code**, une migration ou réécriture menée par de nombreux agents (testeurs à l'aveugle avant les implémenteurs, branche d'intégration verte sur une porte, fils de validation séparés).

Chaque run est un **graphe de tâches sur une page de suivi vivante**, avec le débrief des jetons par tâche et par modèle. **[Voir l'exemple animé](https://raw.githack.com/joey-barbier/ClaudeCode-Plugin/main/plugins/horka-research-plan/examples/task-graph-demo.html)**. La vérification suit la pratique de l'équipe Claude Code : le produit est lancé de bout en bout avant tout push, les migrations sont comparées ancien contre nouveau, les verdicts sont liés à un commit, et après trois tours en échec l'utilisateur tranche.

```bash
claude plugin install horka-research-plan
```

| Composant | Déclencheur | Rôle |
|---|---|---|
| `/horka-research-plan:horka-research-plan` | « check complet et un plan », « plan sourcé », « migre X vers Y avec plein d'agents », « lance plein d'agents », « quel modèle pour quelle tâche » | Dimensionne le run (voie courte ou complète), écrit le graphe, lance selon le graphe avec le routage de modèle, fait valider par des tiers, livre la page ou la branche verte, puis une rétrospective réécrit un fichier de leçons relu au run suivant |

**Trois règles :** aucun chiffre ni comportement de mémoire · aucun agent ne note son propre travail · rien n'est créé ni planifié sans le go de l'utilisateur. Détails : [README du plugin](plugins/horka-research-plan/README.md).

---

## horka-played

**`/played` pour Claude Code, comme dans World of Warcraft** : combien de tokens tu as brûlés. Lit tes transcripts locaux (30 jours par défaut), fusionne tes autres machines et ouvre une page doc-style.

```bash
claude plugin install horka-played
```

| Composant | Déclencheur | Rôle |
|---|---|---|
| `/horka-played:played` | « /played », « combien de tokens j'ai consommé », « ma conso Claude Code » | Totaux, par jour / machine / modèle, part des sous-agents, jour record, choix de période (dernier jour, 7 jours, plage libre, −1/+1 jour), carte à partager et PNG story 1080×1920 |

Lecture seule, aucun chiffre estimé. Plusieurs machines : lance-le sur chacune et copie `~/.claude/played/<label>.json` sur la machine où tu ouvres la page. Les sessions cloud ne sont pas mesurables, et la page le dit.

---

## horka-harness-audit

**Par quoi tes règles sont-elles tenues ?** Un audit de ta façon de développer avec des agents IA : pour chaque règle et chaque contrôle, est-ce une phrase, un script, un hook, la CI ou la plateforme qui le tient.

```bash
claude plugin install horka-harness-audit
```

| Composant | Déclencheur | Rôle |
|---|---|---|
| `/horka-harness-audit:horka-harness-audit` | « audite mon harness », « mes garde-fous tiennent ? », « quel est mon niveau », « bilan de ma façon de dev avec l'IA » | Deux ou trois questions, un scan d'environ 30 secondes qui ne modifie rien, puis une page HTML ouverte à la fin : un niveau de 0 à 3 sur trois axes (conception, détection, application), ce qui tient, ce qui ne tient pas, et les actions à faire, de la moins chère à la plus chère |

Le scan teste tes règles de permission et lance tes propres hooks PreToolUse face à une série de commandes à risque (les commandes ne sont jamais exécutées, mais un hook qui journalise les journalisera ; les hooks définis par un dépôt audité ne sont pas lancés), lit les dépendances de la CI et, via `gh`, la protection de branche et les fusions sur rouge. Détails : [README du plugin](plugins/horka-harness-audit/README.md).

---

## Fonctionnement des plugins

| Type | Comportement | Exemple |
|---|---|---|
| **Agents** | Autonomes — Claude les active quand pertinent | `review-pr` sur "review PR" |
| **Skills** | Commandes que tu tapes | `/horka-memory:horka-memory-restore` |
| **Hooks** | Garde-fous silencieux en arrière-plan | Bloque `git push --force` |

## Questions ?

Je stream en direct sur Twitch pendant que je code avec Claude Code. Viens poser des questions, voir les plugins en action, ou en suggérer de nouveaux.

**[twitch.tv/horka_tv](https://twitch.tv/horka_tv)**

## Licence

MIT — libre d'utilisation, de modification et de partage.
