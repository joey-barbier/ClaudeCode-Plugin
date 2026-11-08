# Code mode — migration, rewrite, new foundation run by many agents

Read this when the request is "migrate X to Y with many agents", "rewrite the engine in parallel", a new foundation with strict layers. Same orchestrator and waves as research mode; what changes is below.

## The three rules, adapted

| Research mode | Code mode |
|---|---|
| No number from memory | **No behaviour from memory.** The reference is the existing code on the remote `main` (fresh clone, read-only), never a local copy that may be behind. The old test branches and fix branches are the specification of record. Every test cites `file:line` or the base section it comes from. |
| No agent grades its own work | Unchanged, and extended: testers never see implementation code, implementers never change a spec assertion, validation is done by separate threads. |
| Nothing is created or scheduled | **Branches, yes.** One worktree and branch per agent. A push only on the user's explicit go in the thread; never a PR, a merge or a schedule without it. Secrets are never read. Commits carry no attribution trailer when the user's rules say so. |

## Waves (replace research waves 1 to 6)

5 to 8 agents per wave; read every report between waves; one worktree per agent; file ownership declared in every brief (two agents never write the same file; a type an agent needs but does not own is declared locally and marked `// TEMP: reconcile at merge`).

| Wave | Agents | Purpose |
|---|---|---|
| S · Spike and decisions | 1 agent per proof (the build compiles on the reference platform, the walls hold, the risky mechanism works) + 1 author per architecture decision record | Prove before writing. A decision record is reviewed by an antagonist who did not write it, twice: the second pass states, per blocking point, "lifted / partially / not lifted" with the line that proves it. |
| T · Blind testers | 1 per target, **before** any implementer | Write `Tests/<Target>/Spec/API.md` (the contract they assume) then the tests, from the reference and the base only. They never open `Sources/`, anywhere. A throwaway stub package outside the repo checks that the tests compile. |
| I · Implementers | 1 per target, own worktree and branch | Make `Spec/` pass without changing an assertion. Only mechanical API renames, each listed in the report. A test they believe wrong stays red and is explained with `file:line`. Proof pasted (full test run, reference gate green). |
| R · Reconciliation | 1 agent after each wave I | Blind specs drift on shared names. The lowest layer's `API.md` is the authority; provisional `TEMP` types are removed; branches are merged into `integration`; the gate runs again. |
| V · Validation threads | separate threads: code, AI behaviour, security | Receive only the branch, the base and the validation type, never the orchestrator's context. Expect BLOCKED first; fix on a `fix/` branch; ask for a second pass. |
| M · Mechanical steps | generalist-tier agents | Merge a fix branch, rerun the gate, update the board. No decision. |

Briefs for each role: `references/briefs.md`, section "Code variant".

## Delegating lookups: when it wins, when it loses

The model is chosen by whoever launches an agent; nothing picks it automatically, and a sub-agent inherits its parent's model unless told otherwise. Put this rule in every brief:

> For any wide search, or a read of several files of which you keep only a conclusion, launch an `Explore` sub-agent on the cheapest tier and keep only its answer. Read in full only what you modify or port line by line.

| Situation | Delegate? | Why |
|---|---|---|
| Wide search where only the conclusion is kept ("where is X used", inventory of a folder) | Yes | Done by the agent, everything read stays in its window and is re-sent on each of its 50 to 100 later turns. |
| Content the agent needs in full (a module to port line by line, a spec to make pass) | No | It will read it again anyway: double cost. |
| A small lookup (one `grep`, one `ls`) | No | A sub-agent costs a few thousand tokens and 30 s to 2 min, more than the lookup. |
| Anything that needs exactness (signatures, formats, numbers) | No, or verify afterwards | A sub-agent's summary can be wrong. |

Measure it: the scorecard records cache-read tokens per agent, read from the transcripts (the harness count ignores cache reads). If the rule works, that figure drops on the agents that apply it.

## The deliverable

- The `integration` branch, green on the reference gate (for example `docker run … swift:6.2-noble swift test`), pushed only on the user's go.
- The `Spec/` folders, one per target, each test citing its source.
- A local progress board (doc-style HTML regenerated from the worktrees and the transcripts): tokens per model all-in and output, wall time vs cumulated agent time, parallelism factor, tests green, verdicts of the validation threads. It replaces progress messages in the thread; the thread summary stays under 80 words.
- The lessons file (Phase 5), with the scorecard fields of `references/retrospective.md`.

## What the Guild run showed (07/11/2026)

32 agents, ×11.7 parallelism (1 h 25 elapsed for 16 h 48 of agent time), 566 M tokens of which 500 M cache reads, 1 391 green tests on the gate. The antagonist reviews found 11 + 7 blocking points in two decision records; the blind testers found cases no implementer had coded (key order of a journal line, a refusal never recorded, a delay measured on the first entry instead of the last); the code thread found two secret-masking holes; the security thread bypassed the grep-based layer walls with 13 of 18 attack variants. None of it would have surfaced from the authors.
