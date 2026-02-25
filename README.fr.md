# ClaudeCode-Plugin

**[EN](README.md)** | **[ES](README.es.md)** | **[DE](README.de.md)**

Des plugins prêts à l'emploi qui rendent Claude Code réellement utile dans les vrais projets. Mémoire, révision de code, flux de travail de développement, garde-fous de sécurité — construits à partir de mois d'utilisation quotidienne.

> En parallèle, pour suivre vos librairies externes, les CVEs et plus encore, découvrez [LibTracker](https://app.libtracker.io/).

![Demo](assets/demo.gif)

## Installer tous les plugins d'un coup

Parcourez et installez tout depuis Claude Code :

```bash
/plugin marketplace add joey-barbier/ClaudeCode-Plugin
```

Puis utilisez `/plugin` → onglet **Discover** pour parcourir et installer ce dont vous avez besoin.

Ou installez les plugins individuellement en suivant les étapes ci-dessous.

## Commencer

Suivez les étapes dans l'ordre. Chacune s'appuie sur la précédente.

### Étape 1 : Configurer Claude Code (première fois seulement)

Installez `cc-setup` et exécutez l'assistant de configuration.

```bash
claude plugin add joey-barbier/ClaudeCode-Plugin/plugins/cc-setup
```
Puis tapez `/cc-setup:setup` — il vous interroge sur votre workflow git, style de communication, préférences de sécurité et plugins installés, puis génère un `CLAUDE.md` personnalisé qui dit à Claude comment VOUS travaillez.

### Étape 2 : Donner une mémoire à Claude

Installez `cc-memory` afin que Claude se souvienne de votre projet entre les sessions. Fini d'expliquer où vous en étiez après une compression ou une nouvelle conversation.

```bash
claude plugin add joey-barbier/ClaudeCode-Plugin/plugins/cc-memory
```

**Ce qui se passe :** Quand vous ouvrez Claude, il détecte automatiquement les fichiers de votre projet et restaure le contexte complet — ce qui est fait, ce qui ne l'est pas, sur quoi travailler ensuite. Tapez `/cc-memory:memory` pour initialiser la mémoire sur un nouveau projet (il scanne votre codebase et crée les fichiers PROJECT_STATE, ARCHITECTURE, DECISIONS, NEXT_STEPS et COMMANDS) ou restaurer le contexte manuellement en début de session.

### Étape 3 : Ajouter les outils dont vous avez besoin

Choisissez ce qui correspond à votre flux de travail. Chaque plugin fonctionne indépendamment.

---

#### code-review — *Autonome*

**Votre responsable technique senior personnel.** S'active automatiquement quand vous dites "review PR" ou quand Claude détecte du code prêt à être poussé. Fait un premier passage complet (architecture, sécurité, qualité) pour que quand vous révisiez, vous vous concentriez sur ce qui compte — pas les fautes de frappe et les ifs mal placés.

```bash
claude plugin add joey-barbier/ClaudeCode-Plugin/plugins/code-review
```

> Hook inclus (se lance automatiquement, aucune commande requise) : Bloque le push vers main/master. Vous rappelle de réviser avant de pousser les branches de fonctionnalités.

---

#### qa-testing — *Mixte (autonome + commande)*

**Validation QA et génération de tests.** Deux composants — un autonome, un manuel.

```bash
claude plugin add joey-barbier/ClaudeCode-Plugin/plugins/qa-testing
```

| Composant | Comment cela fonctionne |
|---|---|
| Agent de validation QA | Autonome — s'active quand vous affirmez qu'une fonctionnalité est terminée, remet vos assertions en question et teste les cas limites |
| `/qa-testing:unit-test-expert` | Génère des tests unitaires orientés métier : permissions, limites, cohérence des données. Lit d'abord vos conventions de test existantes, puis écrit des tests qui correspondent à vos patterns. Supporte tout langage/framework |

---

#### dev-workflow — *Commandes + agent autonome*

**Méthodologie de développement structurée.** L'agent s'active pour les implémentations complexes. Les compétences sont des commandes que vous tapez quand vous en avez besoin.

```bash
claude plugin add joey-barbier/ClaudeCode-Plugin/plugins/dev-workflow
```

| Composant | Comment cela fonctionne |
|---|---|
| Agent de méthodologie de développement | Autonome — s'active pour les travaux complexes multicouches |
| `/dev-workflow:implement` | Lance une session de dev structurée : analyse votre architecture, vérifie la doc par rapport au code, puis implémente dans le bon ordre de dépendances avec validation à chaque étape |
| `/dev-workflow:new-feature` | Prépare git pour une nouvelle fonctionnalité : bascule sur main/develop, pull le dernier état, propose de supprimer les branches mergées, puis crée une branche `feature/` |
| `/dev-workflow:time-check` | Détecte quand vous tournez en rond : même erreur 3+ fois, sur-ingénierie, débats sans décision. Propose la solution la plus rapide avec un plan d'action concret |
| `/dev-workflow:init-docs` | Crée la documentation d'architecture (ARCHITECTURE.md, CONVENTIONS.md, etc.) depuis votre codebase, ou met à jour chirurgicalement la doc existante quand les patterns changent |

> Hook inclus (se lance automatiquement, aucune commande requise) : Bloque les commandes git dangereuses (force push, hard reset, checkout ., restore ., clean, branch -D).

---

#### analytics — *Autonome*

**Expert en analytique SaaS.** S'active quand vous travaillez sur le suivi, les entonnoirs ou la conversion. Conçoit quoi mesurer, comment le mettre en place et quels tableaux de bord construire.

```bash
claude plugin add joey-barbier/ClaudeCode-Plugin/plugins/analytics
```

---

#### openclaw — *Commandes*

**Gestion de session pour la passerelle OpenClaw.** Outils pour les sessions longues — compresser le contexte, extraire les apprentissages, maintenir les performances.

```bash
claude plugin add joey-barbier/ClaudeCode-Plugin/plugins/openclaw
```

| Composant | Comment cela fonctionne |
|---|---|
| `/openclaw:compact` | Compresse les grosses sessions IA : scanne les fichiers de plus de 20 Mo, extrait décisions/configs/apprentissages, archive l'original et réduit la session au minimum |
| `/openclaw:extract` | Extrait les apprentissages de la session en cours et les sauvegarde dans les fichiers mémoire — à utiliser avant de supprimer des sessions ou quand le contexte devient lourd |
| Scripts shell | `context-monitor.sh`, `context-guardian-daemon.sh`, `self-reboot.sh`, `clean-session-blobs.sh` |

> Hook inclus (se lance automatiquement, aucune commande requise) : Vous avertit de sauvegarder les apprentissages avant que les grandes sessions ne soient compactées.

## Comment fonctionnent les plugins

Trois types de composants, trois comportements :

| Type | Comportement | Exemple |
|---|---|---|
| **Agents** | Autonome — Claude les active quand c'est pertinent | L'agent de révision de code se déclenche sur "review PR" |
| **Compétences** | Commandes — vous les tapez quand vous en avez besoin | `/cc-memory:memory` pour restaurer le contexte |
| **Hooks** | Silencieux — s'exécutent en arrière-plan, vous protègent des erreurs | Bloque automatiquement `git push --force` |

## Questions ?

Je fais un direct sur Twitch en construisant avec Claude Code. Venez poser des questions, voir les plugins en action, ou en suggérer de nouveaux.

**[twitch.tv/horka_tv](https://twitch.tv/horka_tv)**

## Licence

MIT — libre d'utilisation, de modification et de partage.
