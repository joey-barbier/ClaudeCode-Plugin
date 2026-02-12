# ClaudeCode-Plugin

**[EN](README.md)** | **[ES](README.es.md)** | **[DE](README.de.md)**

Des plugins prêts à l'emploi qui rendent Claude Code réellement utile dans les vrais projets. Mémoire, révision de code, flux de travail de développement, garde-fous de sécurité — construits à partir de mois d'utilisation quotidienne.

> En parallèle, pour suivre vos librairies externes, les CVEs et plus encore, découvrez [LibTracker](https://app.libtracker.io/).

![Demo](assets/demo.gif)

## Commencer

Suivez les étapes dans l'ordre. Chacune s'appuie sur la précédente.

### Étape 1 : Configurer Claude Code (première fois seulement)

Installez `cc-setup` et exécutez l'assistant de configuration. Il vous pose des questions sur votre flux de travail et génère un `CLAUDE.md` personnalisé — le fichier qui dit à Claude comment VOUS travaillez.

```bash
claude plugin add github:joey-barbier/ClaudeCode-Plugin/plugins/cc-setup
```
Puis tapez `/cc-setup:setup` et répondez aux questions.

### Étape 2 : Donner une mémoire à Claude

Installez `cc-memory` afin que Claude se souvienne de votre projet entre les sessions. Fini d'expliquer où vous en étiez après une compression ou une nouvelle conversation.

```bash
claude plugin add github:joey-barbier/ClaudeCode-Plugin/plugins/cc-memory
```

**Ce qui se passe :** Quand vous ouvrez Claude, il détecte automatiquement les fichiers de votre projet et restaure le contexte complet — ce qui est fait, ce qui ne l'est pas, sur quoi travailler ensuite. Tapez `/cc-memory:memory` pour initialiser la mémoire sur un nouveau projet ou la restaurer manuellement.

### Étape 3 : Ajouter les outils dont vous avez besoin

Choisissez ce qui correspond à votre flux de travail. Chaque plugin fonctionne indépendamment.

---

#### code-review — *Autonome*

**Votre responsable technique senior personnel.** S'active automatiquement quand vous dites "review PR" ou quand Claude détecte du code prêt à être poussé. Fait un premier passage complet (architecture, sécurité, qualité) pour que quand vous révisiez, vous vous concentriez sur ce qui compte — pas les fautes de frappe et les ifs mal placés.

```bash
claude plugin add github:joey-barbier/ClaudeCode-Plugin/plugins/code-review
```

> Hook inclus (se lance automatiquement, aucune commande requise) : Bloque le push vers main/master. Vous rappelle de réviser avant de pousser les branches de fonctionnalités.

---

#### qa-testing — *Mixte (autonome + commande)*

**Validation QA et génération de tests.** L'agent QA s'active automatiquement quand vous affirmez qu'une fonctionnalité est terminée — il remet vos assertions en question et teste les cas limites. Le générateur de tests est une commande manuelle.

```bash
claude plugin add github:joey-barbier/ClaudeCode-Plugin/plugins/qa-testing
```

| Composant | Comment cela fonctionne |
|---|---|
| Agent de validation QA | Autonome — s'active lors de la validation des fonctionnalités |
| Générateur de tests | Commande — tapez `/qa-testing:unit-test-expert` |

---

#### dev-workflow — *Commandes + agent autonome*

**Méthodologie de développement structurée.** L'agent s'active pour les implémentations complexes. Les compétences sont des commandes que vous tapez quand vous en avez besoin.

```bash
claude plugin add github:joey-barbier/ClaudeCode-Plugin/plugins/dev-workflow
```

| Composant | Comment cela fonctionne |
|---|---|
| Agent de méthodologie de développement | Autonome — s'active pour les travaux complexes multicouches |
| `/dev-workflow:implement` | Commande — lancer une session de développement structurée |
| `/dev-workflow:new-feature` | Commande — préparer git pour une nouvelle fonctionnalité |
| `/dev-workflow:time-check` | Commande — détecter la sur-ingénierie et les boucles |
| `/dev-workflow:init-docs` | Commande — initialiser la documentation du projet |

> Hook inclus (se lance automatiquement, aucune commande requise) : Bloque les commandes git dangereuses (force push, hard reset, checkout ., restore ., clean, branch -D).

---

#### analytics — *Autonome*

**Expert en analytique SaaS.** S'active quand vous travaillez sur le suivi, les entonnoirs ou la conversion. Conçoit quoi mesurer, comment le mettre en place et quels tableaux de bord construire.

```bash
claude plugin add github:joey-barbier/ClaudeCode-Plugin/plugins/analytics
```

---

#### openclaw — *Commandes*

**Gestion de session pour la passerelle OpenClaw.** Outils pour les sessions longues — compresser le contexte, extraire les apprentissages, maintenir les performances.

```bash
claude plugin add github:joey-barbier/ClaudeCode-Plugin/plugins/openclaw
```

| Composant | Comment cela fonctionne |
|---|---|
| `/openclaw:compact` | Commande — compresser une grande session |
| `/openclaw:extract` | Commande — sauvegarder les apprentissages avant le nettoyage |
| Scripts shell | `context-monitor.sh`, `context-guardian-daemon.sh`, `self-reboot.sh`, `clean-session-blobs.sh` |

> Hook inclus (se lance automatiquement, aucune commande requise) : Vous avertit de sauvegarder les apprentissages avant que les grandes sessions ne soient compactées.

## Comment fonctionnent les plugins

Trois types de composants, trois comportements :

| Type | Comportement | Exemple |
|---|---|---|
| **Agents** | Autonome — Claude les active quand c'est pertinent | L'agent de révision de code se déclenche sur "review PR" |
| **Compétences** | Commandes — vous les tapez quand vous en avez besoin | `/cc-memory:memory` pour restaurer le contexte |
| **Hooks** | Silencieux — s'exécutent en arrière-plan, vous protègent des erreurs | Bloque automatiquement `git push --force` |

## Installer la marketplace

Pour parcourir tous les plugins depuis Claude Code :

```bash
/plugin marketplace add github:joey-barbier/ClaudeCode-Plugin
```

Puis utilisez `/plugin` → onglet **Discover** pour parcourir et installer.

## Questions ?

Je fais un direct sur Twitch en construisant avec Claude Code. Venez poser des questions, voir les plugins en action, ou en suggérer de nouveaux.

**[twitch.tv/horka_tv](https://twitch.tv/horka_tv)**

## Licence

MIT — libre d'utilisation, de modification et de partage.
