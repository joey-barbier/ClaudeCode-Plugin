# Level-Up Rules

## Progression Table

| From | To | Condition |
|------|-----|-----------|
| unknown | learning | Concept taught, dev showed partial understanding |
| unknown | understood | DIRECTIVE only: post-teaching quiz answered solid |
| learning | understood | Dev answered correctly on assessment (predict/spot/explain/practical) |
| understood | confident | Solid on spaced quiz OR correct practical implementation in code |
| confident | understood | Spaced quiz missed — regression detected |
| understood | learning | Two consecutive spaced quizzes shaky |

## Special Cases

### Inline Teaching (no formal assessment)
A concept taught inline during a build (no formal question) can move `unknown → learning` if the dev showed partial understanding in conversation (e.g., correct response to an inline check like "tu vois pourquoi ?"). No formal assessment required for `unknown → learning`.

### Skip
A skipped concept stays at its current level (usually `unknown`). Create the topic file with `level: unknown`, `last_assessed: never`, `next_review: J+1`. Code is delivered with WHY comments inline but no pedagogical pauses. Mark the concept `needs-revisit` in notes.

### Consecutive Misses
After 3 consecutive "missed" on the same topic in quiz, stop retesting at J+1. Instead:
- Mark the topic `needs-reteach` in notes
- Schedule a dedicated /mentor session
- Set quiz interval to J+3 to avoid fatigue
- Track `consecutive_miss_count` in the topic file Status section. Reset to 0 on any non-missed result.

### needs-reteach Flow
When the dev invokes `/mentor` on a topic marked `needs-reteach`:
1. Use full depth (not brief) even if the topic was at `learning`
2. Use a different approach than previous (consult Teaching History to avoid repeating)
3. After successful teaching (partial or full understanding), remove the `needs-reteach` tag
4. Quiz resumes normally after the re-teach session

In proactive mode, a `needs-reteach` topic triggers an intervention even if not directly involved in the request, IF the concept is a direct prerequisite or dependent in the dependency map of pedagogy.md.

### Bridge Concepts
A bridge (1-sentence context given for a depth-3 prerequisite) creates a topic file at `unknown` with note `bridge-given`. A bridge is NOT teaching — it does not qualify for `unknown → learning`.
