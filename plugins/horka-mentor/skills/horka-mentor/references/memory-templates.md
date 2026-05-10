# Memory Templates

All mentor memory is stored globally at `~/.claude/mentor/`.

## dev-profile.md

```markdown
# Dev Profile

## Identity
- **Name**: [ask on cold start]
- **Language**: [ask on cold start — fr/en/es/de/etc.]
- **Experience**: [months/years of coding]
- **Background**: [bootcamp / self-taught / CS degree / career changer]
- **Current stack**: [languages, frameworks, tools]
- **Prior stacks**: [if cross-stack, what they already know]
- **Learning preference**: [learn (full explanations) / build (explain as we go)]
- **Proactive mode**: enabled | disabled

## Domains
[Updated after each interaction — per-domain speed assessment]

### frontend
- speed: [fast / moderate / slow / not-assessed]
- evidence: "[concrete observation]"

### backend
- speed: [fast / moderate / slow / not-assessed]
- evidence: "[concrete observation]"

### devops
- speed: [fast / moderate / slow / not-assessed]
- evidence: "[concrete observation]"

### database
- speed: [fast / moderate / slow / not-assessed]
- evidence: "[concrete observation]"

## Notes
[Freeform observations — transferable skills, personality traits, blockers]
```

## topics/<concept-slug>.md

```markdown
# [Concept Name]

## Status
- **Level**: unknown | learning | understood | confident
- **First seen**: [YYYY-MM-DD]
- **Last assessed**: [YYYY-MM-DD]
- **Next review**: [YYYY-MM-DD — calculated from spaced repetition]
- **Interval step**: [1=J+1, 2=J+3, 3=J+7, 4=J+14, 5=J+30, 6=every 30d]
- **Assessment count**: [number]
- **Consecutive miss count**: [0 — reset on any non-missed result]

## Context
- **Discovered during**: [what task/feature triggered this topic]
- **Related concepts**: [prerequisites or connected topics]

## Teaching History
### [YYYY-MM-DD]
- Mode: learn | build
- Depth: inline | brief | full
- Method: [analogy used, example given, exercise proposed]
- Outcome: [understood / partially / needs-revisit]

## Assessment History
### [YYYY-MM-DD]
- Type: predict-output | spot-bug | explain | mcq | practical-implementation
- Question: [the actual question asked]
- Answer quality: solid | shaky | missed
- Notes: [what was misunderstood, if anything]
```

## quiz-log.md

```markdown
# Quiz Log

## Spaced Repetition Schedule
Topics are reviewed at increasing intervals after teaching:
- J+1 (next day)
- J+3
- J+7
- J+14
- J+30
- Then every 30 days

A "missed" answer resets the interval to J+1.
A "shaky" answer keeps the current interval (no advancement).
A "solid" answer advances to the next interval.

## Upcoming Reviews
[Auto-maintained list sorted by next_review date]
Source of truth = topic files. This table is a convenience index.

| Topic | Level | Last assessed | Next review | Interval | Step |
|-------|-------|--------------|-------------|----------|------|

Step = position in the ladder (1=J+1, 2=J+3, 3=J+7, 4=J+14, 5=J+30, 6=every 30d).
Missed resets step to 1. Solid advances step by 1. Shaky keeps current step.
After 3 consecutive missed: step stays at 2 (J+3), topic marked needs-reteach.

## History
### [YYYY-MM-DD]
- **Session type**: manual (/mentor-quiz) | pre-coding check | spaced repetition
- **Topics assessed**: [list]
- **Results**:
  - [topic]: solid | shaky | missed → level adjusted to [new level]
- **Follow-up**: [concepts to re-teach, exercises to propose]
```

## Directory Structure

```
~/.claude/mentor/
├── dev-profile.md
├── quiz-log.md
└── topics/
    ├── async-await.md
    ├── jwt-authentication.md
    ├── database-transactions.md
    ├── react-hooks-lifecycle.md
    └── ...
```
