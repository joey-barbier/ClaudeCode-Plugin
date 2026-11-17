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
| S · Spike and decisions | 1 agent per proof (the build compiles on the reference platform, the walls hold, the risky mechanism works) + 1 author per architecture decision record | Prove before writing. A decision record is reviewed by an antagonist who did not write it (twice in the full lane only: the second pass reads the corrections and states, per blocking point, "lifted / partially / not lifted" with the line that proves it). **Probe before spec:** one real probe per external dependency (API, CI runner, hosting platform, tool): run the real thing once with a disposable instance and record what it actually sends or requires; the blind spec of that piece starts from the record, never from the decision record alone. **Gate = CI from wave 1:** the gate runs with the CI's user (non root), core count and runner from wave 1; green means N consecutive passes (root hid a permission bug, 4 cores starved the cooperative pool, `Foundation.Process` crashed 4 runs out of 13). |
| T · Blind testers | 1 per target, **before** any implementer | Write `Tests/<Target>/Spec/API.md` (the contract they assume) then the tests, from the reference and the base only. They never open `Sources/`, anywhere. A throwaway stub package outside the repo checks that the tests compile. |
| I · Implementers | 1 per target, own worktree and branch | Make `Spec/` pass without changing an assertion. Only mechanical API renames, each listed in the report. A test they believe wrong stays red and is explained with `file:line`. Proof pasted (full test run, reference gate green). |
| R · Reconciliation | 1 agent after each wave I | Blind specs drift on shared names. The lowest layer's `API.md` is the authority; provisional `TEMP` types are removed; branches are merged into `integration`; the gate runs again. |
| V · Validation threads | separate threads: code, AI behaviour, security | Receive only the branch, the base and the validation type, never the orchestrator's context. Expect BLOCKED first; fix on a `fix/` branch; ask for a second pass on the fixes only. |
| M · Mechanical steps | generalist-tier agents | Merge a fix branch, rerun the gate, update the board. No decision. |

Briefs for each role: `references/briefs.md`, section "Code variant".

## Gates: four by default, in parallel, never "just to see"

What a mid-size run showed (one craft and one connector, 16/11/2026): the real probe and the first antagonist review found what mattered (an API with no history, a forged-message hole across two agents, a state marked before the work was done); the second full review found two small points in ten minutes; a reference gate rerun locally and a 280-line decision record for three deliveries bought nothing; the base branch was red before the run started and nobody had looked.

- **Default gates:** real probe; one antagonist review of the decision record; blind tests for pure engines and security boundaries; a third party validates before the push. The second review pass, blind tests for every target and the three validation threads are for migrations and rewrites.
- **Phase 0:** read the CI status of the base branch (do not rerun the gate) and check the gate can run where you are (container runtime, outbound proxy and its CA, architecture). A red base goes to the user at once.
- **While agents work:** filtered tests of their own target only. No full gate per agent.
- **One full gate,** once, after reconciliation, where the user said long runs go. The validations start at the same time.
- **Decision record:** only what ships in this delivery; later deliveries get three lines each.
- **Reports:** one verdict line, then one line per point (`file:line` · problem · fix), 15 lines at most.

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
- The run board of `references/task-graph.md` (task graph, tokens per task and per model, wall time vs cumulated agent time, parallelism factor), with tests green and the verdicts of the validation threads in its essentials. It replaces progress messages in the thread; the thread summary stays under 80 words.
- The lessons file (Phase 5), with the scorecard fields of `references/retrospective.md`.

## What the Guild run showed (07/11/2026)

32 agents, ×11.7 parallelism (1 h 25 elapsed for 16 h 48 of agent time), 566 M tokens of which 500 M cache reads, 1 391 green tests on the gate. The antagonist reviews found 11 + 7 blocking points in two decision records; the blind testers found cases no implementer had coded (key order of a journal line, a refusal never recorded, a delay measured on the first entry instead of the last); the code thread found two secret-masking holes; the security thread bypassed the grep-based layer walls with 13 of 18 attack variants. None of it would have surfaced from the authors.

Probe before spec: a relay specified from the decision record alone refused all 6 requests of the real Claude Code (7 unknown betas, 2 unknown fields, `max_tokens` 128 000). Blacksmith only supports GitHub organisations, found after the CI was written. A 10-minute probe would have saved two agents.
