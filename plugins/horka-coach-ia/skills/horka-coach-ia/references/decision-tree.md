# Arbre de decision : quoi utiliser ?

## Logique de decision

```
Le besoin est-il recurrent ?
|-- NON → Complexe ?
|   |-- NON → Fais-le a la main. Pas besoin d'outiller.
|   +-- OUI → Un prompt bien construit suffit.
|
+-- OUI → La logique est deterministe (regles fixes, pas de jugement) ?
    |-- OUI → Script ou automatisation. Pas d'IA.
    |
    +-- NON → Ca demande du jugement, de l'adaptation ?
        |-- C'est une PROCEDURE (etapes connues, resultat previsible)
        |   +-- SKILL
        |
        +-- C'est un ROLE (personnalite, perimetre, decisions autonomes)
            +-- AGENT
```

## Exemples concrets

| Besoin | Verdict | Pourquoi |
|--------|---------|----------|
| CR de reunion depuis notes | Skill | Procedure : input → format → output |
| Reviewer les PR comme un tech lead | Agent | Role : personnalite + jugement |
| Renommer 200 fichiers | Script | Deterministe, zero jugement |
| Choisir entre deux archis | Prompt | Ponctuel + complexe |
| Diagnostiquer un bug cache | Skill | Procedure reproductible |
| Assistant qui connait tout le projet | Agent | Role persistant + contexte |
| Mail de relance chaque lundi | Automatisation | Regle fixe, zero jugement |
| Parser un CSV et generer un rapport | Script | Deterministe, format fixe |
| Onboarder un nouveau dev sur le projet | Agent | Role + contexte accumule |
| Generer des tests unitaires | Skill | Procedure : input code → output tests |

## Cas special : le prompt recurrent

L'arbre ci-dessus a un cas intermediaire : un besoin recurrent, qui demande du jugement, mais dont le scope est petit (un seul prompt bien construit suffit). Exemple : "chaque semaine je reformule un mail delicat".

→ **Prompt sauvegarde**. Pas un skill, pas un agent. Juste un prompt que tu gardes et que tu reutilises. Si le prompt grossit et se structure en etapes → il devient un skill.

## Questions rapides pour trancher

Si tu hesites, pose-toi ces 4 questions dans l'ordre :

1. **Est-ce que ca revient ?** NON → prompt ou main. OUI → continue.
2. **Est-ce que c'est toujours pareil ?** OUI → script. NON → continue.
3. **Est-ce que c'est un seul prompt bien construit ?** OUI → prompt sauvegarde. NON → continue.
4. **Est-ce que ca demande un ROLE ou une PROCEDURE ?** Role → agent. Procedure → skill.
