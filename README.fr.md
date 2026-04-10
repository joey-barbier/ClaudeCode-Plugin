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
| **[horka-setup](#horka-setup)** | `CLAUDE.md` personnalisé + docs d'architecture | 2 skills |
| **[horka-memory](#horka-memory)** | Mémoire projet persistante entre sessions | 1 skill |
| **[horka-review](#horka-review)** | Antagonist + Tech Lead code review | agent + 2 skills + hook |
| **[horka-qa-testing](#horka-qa-testing)** | Validation QA + tests unitaires métier | agent + skill |
| **[horka-dev-workflow](#horka-dev-workflow)** | Méthodologie dev + sécurité git | agent + 2 skills + hook |
| **[horka-analytics](#horka-analytics)** | Expert tracking / funnels SaaS | agent |
| **[horka-openclaw](#horka-openclaw)** | Gestion des longues sessions IA | 2 skills + hook |
| **[horka-skill-eval](#horka-skill-eval)** | Auditeur qualité de skills | skill |

---

## Commencer

### 1. Configurer Claude — `horka-setup`

```bash
claude plugin install horka-setup
```

- `/horka-setup:horka-claude-setup` — questionnaire interactif → `CLAUDE.md` personnalisé
- `/horka-setup:horka-init-docs` — génère les docs d'architecture depuis ton code (ARCHITECTURE, CONVENTIONS, WORKFLOW_PATTERNS...)

### 2. Donner une mémoire à Claude — `horka-memory`

```bash
claude plugin install horka-memory
```

Restaure automatiquement le contexte projet au début de session. `/horka-memory:horka-memory-restore` pour initialiser sur un nouveau projet — scanne ta codebase et crée les fichiers PROJECT_STATE, ARCHITECTURE, DECISIONS, NEXT_STEPS, COMMANDS.

### 3. Choisis les outils ci-dessous

Chaque plugin fonctionne indépendamment.

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
| Hook review guard | auto | Bloque push vers branche par defaut, impose l'ordre de review sur feature branches |

**Ordre de review :** Antagonist (trouver les failles) → Fix → Tech Lead (valider) → Push/PR

---

## horka-qa-testing

**Validation QA + génération de tests unitaires métier.**

```bash
claude plugin install horka-qa-testing
```

| Composant | Déclenchement | Rôle |
|---|---|---|
| Agent `qa-validate` | affirmation "feature terminée" | Remet en cause les assertions, teste les cas limites |
| `/horka-qa-testing:horka-unit-test-generate` | commande | Génère des tests alignés sur tes conventions (permissions, limites, cohérence des données) |

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

## horka-openclaw

**Gestion des longues sessions IA.**

```bash
claude plugin install horka-openclaw
```

| Composant | Déclenchement | Rôle |
|---|---|---|
| `/horka-openclaw:horka-openclaw-session-compact` | commande | Compresse les sessions >20 Mo, extrait décisions/configs, archive l'original |
| `/horka-openclaw:horka-openclaw-session-extract` | commande | Extrait les apprentissages vers les fichiers mémoire |
| Hook session | auto | Alerte avant compaction lourde |

Outils shell : `context-monitor.sh`, `context-guardian-daemon.sh`, `self-reboot.sh`, `clean-session-blobs.sh`.

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
