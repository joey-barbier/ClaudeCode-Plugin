# ClaudeCode-Plugin

**[EN](README.md)** | **[ES](README.es.md)** | **[DE](README.de.md)**

Une collection de plugins prêts à l'emploi pour [Claude Code](https://docs.anthropic.com/en/docs/claude-code) qui enrichissent votre assistant IA avec des bonnes pratiques, des garde-fous de sécurité et des outils de productivité.

> Construit par l'équipe derrière [LibTracker](https://app.libtracker.io/) — des workflows éprouvés, forgés en construisant un vrai produit SaaS avec Claude Code.

## Qu'est-ce qu'un plugin ?

Les plugins Claude Code étendent les capacités de Claude dans votre terminal. Ils ajoutent :

- **Skills** — Des commandes que vous tapez (comme `/memory` ou `/setup`) pour déclencher des flux de travail spécifiques
- **Agents** — Des personas IA spécialisées qui s'activent automatiquement quand c'est pertinent (comme un réviseur de code)
- **Hooks** — Des vérifications de sécurité automatiques qui s'exécutent en arrière-plan (comme le blocage de pertes de données accidentelles)

Vous installez uniquement ce dont vous avez besoin. Chaque plugin fonctionne de manière indépendante.

## Plugins disponibles

### code-review

**Votre Tech Lead senior personnel.**
Révise vos modifications de code avant leur mise en ligne, détectant les bugs, les problèmes de sécurité et les défauts de qualité.

| Ce que vous obtenez | Comment l'utiliser |
|---|---|
| Agent de révision de PR | Dites "review PR" ou s'active automatiquement |

> Hook : Vous rappelle de réviser le code avant de pousser des modifications sur les branches de fonctionnalité.

---

### qa-testing

**Assurance qualité et tests.**
Valide votre travail comme le ferait un Product Owner, et génère des tests pour votre code dans n'importe quel langage.

| Ce que vous obtenez | Comment l'utiliser |
|---|---|
| Agent de validation QA | S'active lors de la validation de fonctionnalités |
| Générateur de tests | Tapez `/qa-testing:unit-test-expert` |

---

### dev-workflow

**Méthodologie de développement structurée.**
Vous garde organisé, prévient les pertes de temps et protège contre les pertes accidentelles de données.

| Ce que vous obtenez | Comment l'utiliser |
|---|---|
| Agent de méthodologie de développement | S'active pour les implémentations complexes |
| Démarrer l'implémentation | Tapez `/dev-workflow:implement` |
| Détecteur de perte de temps | Tapez `/dev-workflow:time-check` |
| Configuration de la documentation | Tapez `/dev-workflow:init-docs` |
| Préparation nouvelle fonctionnalité | Tapez `/dev-workflow:new-feature` |

> Hook : Bloque les commandes git dangereuses (force push, hard reset, clean) pour prévenir la perte de données.

---

### cc-memory

**Mémoire de session et contexte.**
Mémorise votre projet entre les sessions afin que Claude ne perde jamais le fil de là où vous en étiez.

| Ce que vous obtenez | Comment l'utiliser |
|---|---|
| Restauration / initialisation du contexte | Tapez `/cc-memory:memory` |

> Hook : Détecte automatiquement les fichiers de mémoire du projet au démarrage d'une session et restaure le contexte.

---

### cc-setup

**Assistant de configuration interactif.**
Génère un fichier de configuration personnalisé (CLAUDE.md) via un questionnaire simple. Fonctionne pour les développeurs, chefs de projet, rédacteurs — toute personne utilisant Claude Code.

| Ce que vous obtenez | Comment l'utiliser |
|---|---|
| Générateur CLAUDE.md | Tapez `/cc-setup:setup` |

---

### analytics

**Expert en analytics SaaS.**
Conçoit des stratégies de suivi pour les applications web — quoi mesurer, comment le configurer et quels tableaux de bord construire.

| Ce que vous obtenez | Comment l'utiliser |
|---|---|
| Agent architecte analytics | S'active pour les tâches liées aux analytics |

---

### openclaw

**Gestion de session pour la passerelle OpenClaw.**
Outils pour gérer les sessions IA de longue durée — compresser le contexte, extraire les apprentissages et maintenir les performances.

| Ce que vous obtenez | Comment l'utiliser |
|---|---|
| Compresseur de session | Tapez `/openclaw:compact` |
| Extracteur d'apprentissage | Tapez `/openclaw:extract` |
| Moniteur de contexte | Exécutez `context-monitor.sh` |
| Gardien de contexte | Exécutez `context-guardian-daemon.sh` |
| Redémarrage de la passerelle | Exécutez `self-reboot.sh` |
| Nettoyeur de blobs | Exécutez `clean-session-blobs.sh` |

> Hook : Vous rappelle de sauvegarder les apprentissages avant que les grandes sessions ne soient compressées.

## Installation

### Installer un seul plugin

Choisissez uniquement ce dont vous avez besoin :

```bash
claude plugin add github:joey-barbier/ClaudeCode-Plugin/plugins/code-review
```

### Essayer avant d'installer

Testez un plugin temporairement :

```bash
claude --plugin-dir ./plugins/dev-workflow
```

### Installer depuis une copie locale

```bash
git clone https://github.com/joey-barbier/ClaudeCode-Plugin.git
claude plugin add ./ClaudeCode-Plugin/plugins/cc-memory
```

## Démarrage rapide

1. **Installez les plugins dont vous avez besoin** (voir ci-dessus)
2. **Les agents fonctionnent automatiquement** — ils s'activent quand Claude détecte une situation pertinente
3. **Les skills sont des commandes** — tapez-les quand nécessaire :
   ```
   /cc-setup:setup              # Configurer vos préférences Claude Code
   /cc-memory:memory            # Restaurer le contexte du projet
   /dev-workflow:new-feature    # Préparer une nouvelle fonctionnalité
   /dev-workflow:implement      # Démarrer la construction
   /dev-workflow:time-check     # Vérifier si vous sur-ingénieurez
   /dev-workflow:init-docs      # Configurer la documentation du projet
   /qa-testing:unit-test-expert # Générer des tests
   /openclaw:compact            # Compresser une grande session
   /openclaw:extract            # Sauvegarder les apprentissages d'une session
   ```
4. **Les hooks s'exécutent silencieusement** — vous protégeant des erreurs en arrière-plan

## Configurations recommandées

| Profil | Plugins recommandés |
|---|---|
| **Débute avec Claude Code** | `cc-setup` → exécutez `/cc-setup:setup` |
| **Développeur solo** | `cc-memory` + `dev-workflow` + `code-review` |
| **Équipe avec revues de code** | `code-review` + `qa-testing` + `dev-workflow` |
| **Chef de projet ou rédacteur** | `cc-setup` + `cc-memory` |
| **Opérateur de passerelle OpenClaw** | `openclaw` + `cc-memory` |

## Structure

```
plugins/
├── code-review/     # Agent de révision de PR + hook de garde de push
├── qa-testing/      # Validation QA + génération de tests
├── dev-workflow/    # Méthodologie de dev + hook de sécurité git
├── cc-memory/       # Restauration de contexte + hook de détection auto
├── cc-setup/        # Générateur interactif CLAUDE.md
├── analytics/       # Suivi analytics SaaS
└── openclaw/        # Gestion de session + hook pré-compaction
```

## Licence

MIT — libre d'utilisation, de modification et de partage.
