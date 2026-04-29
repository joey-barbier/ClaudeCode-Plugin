**[EN](README.en.md)** | **[FR](README.md)** | **[DE](README.de.md)**

# Coach IA — Sin el hype

Un agente que te dice la verdad: necesitas IA para esto, o no?

## El problema

Descubriste la IA. Probaste ChatGPT, Copilot, Claude. A veces funciona. Muchas veces es generico, fuera de foco, o perdes mas tiempo corrigiendo que haciendolo vos mismo. No sabes por donde empezar, no sabes que herramienta usar, y nadie te dice cuando la IA no sirve para nada.

## Lo que hace el Coach

Diagnostica tu necesidad real y te da un **veredicto tajante**. Si llegas sin contexto, te hace 2-3 preguntas primero — el veredicto viene despues, no antes.

| Veredicto | Cuando | Ejemplo |
|-----------|--------|---------|
| **A — No necesitas IA** | Un script o un proceso alcanza | "Renommer 200 fichiers ? C'est 3 lignes de bash." |
| **B — Si, asi se hace** | La IA es pertinente, aca esta el paso a paso | "Ton probleme c'est le briefing. Installe horka-setup." |
| **C — Mala idea** | La idea no se sostiene, aca esta por que | "Un bot qui repond a ta place sur Slack ? Non. Voila pourquoi." |

No vende nada. No valida por cortesia. Si tu idea es mala, te lo dice.

## Install

### Opcion 1 — Claude Code (devs, tech leads)

```bash
claude plugin install coach-ia
```

Despues, en cualquier conversacion:

```
> coach, j'ai besoin d'aide avec l'IA
```

### Opcion 2 — Claude Desktop (PO, managers, no-devs)

Si no usas la terminal, podes usar el coach directamente en Claude Desktop:

1. **Abri Claude Desktop** (descargalo de [claude.ai/download](https://claude.ai/download) si todavia no lo hiciste)
2. **Crea un nuevo Proyecto**: click en tu nombre arriba a la izquierda → "Projects" → "Create Project"
3. **Ponele nombre** "Coach IA" (o lo que quieras)
4. **Pega las instrucciones**: en esta pagina de GitHub, ve a la carpeta `skills/horka-coach-ia/`, abri el archivo `SKILL.md`, copia todo el contenido despues del segundo `---`, y pegalo en el campo "Project instructions"
5. **Listo.** Abri una conversacion en ese proyecto y hace tu pregunta

Funciona exactamente igual: describis tu problema, el coach diagnostica y te da un veredicto.

> **Tip**: Fija el proyecto para acceder rapido. Cada nueva conversacion en ese proyecto arranca con el coach activo.

## Ejemplos concretos

### Un dev junior que no le sale el codigo generico

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

### Un dev senior esceptico

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

### Un PO que quiere automatizar todo

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

### Un manager no tecnico

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

### Una mala idea

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

## Por que usarlo

**Recien empezas con la IA?** El coach te evita perder 3 semanas con la herramienta equivocada. Te dice por donde arrancar y en que orden.

**Ya usas IA?** El coach te desafia. De verdad necesitas un agente para eso? O alcanza con un script? Te obliga a hacerte la pregunta correcta antes de salir corriendo.

**Manejas un equipo?** El coach te da un marco. No una herramienta tecnica — un metodo para integrar la IA sin caos.

## Lo que NO hace

- No codea por vos (pedile eso a Claude directamente)
- No debuggea tu codigo (no es su rol)
- No vende nada (nada de "es magico", nada de "game changer")
- No valida tus ideas por cortesia (si es malo, te lo dice)

## El ecosistema

Cuando el coach identifica una necesidad concreta, te redirige a la herramienta correcta:

| Tu necesidad | La herramienta | Lo que cambia |
|--------------|----------------|---------------|
| Claude no entiende mi proyecto | `horka-setup` | CLAUDE.md personalizado = no mas codigo generico |
| Se olvida todo entre sesiones | `horka-memory` | Contexto guardado y restaurado automaticamente |
| Nadie revisa mi codigo | `horka-review` | Doble review: antagonista + tech lead |
| Mis tests no cubren suficiente | `horka-qa-testing` | Desafia tus claims de "esta listo" |
| Features multi-capa = quilombo | `horka-dev-workflow` | Coordina los cambios en orden |
| Mis sesiones son demasiado largas | `horka-openclaw` | Comprime y extrae las decisiones |
| Mi skill esta bien hecho? | `horka-skill-eval` | Auditoria /100 contra las best practices |

Todos los plugins estan disponibles en la marketplace:
```bash
/plugin marketplace add joey-barbier/ClaudeCode-Plugin
```

El coach nunca lista todo. Te redirige a **una sola herramienta**, la que responde a **tu** problema.

## Filosofia

> Ustedes ya eran cocineros. La IA son los buenos cuchillos.
> Pero un buen cuchillo en manos de alguien que no sabe cocinar,
> simplemente corta mas rapido — en la direccion equivocada.

3 reflejos:
1. **Elegir la herramienta** — la menos potente que alcance
2. **Iterar** — el primer resultado es una base, no un veredicto
3. **Capitalizar** — algo que funciona → convertirlo en herramienta

---

Construido por [HORKA_TV](https://twitch.tv/horka_tv). Gratis. MIT.
