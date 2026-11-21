# horka-research-plan

**Right model, right effort, right moment, at every level.** By default every subagent inherits the session's model, so a ten-agent run on the top model pays top price for work that is mostly opening pages and counting. This skill routes each sub-task to the cheapest tier that can do it, and every agent passes the same rule to its own sub-agents:

| Tier | Does | Example |
|---|---|---|
| Top | Orchestrates and judges: critic, personas, synthesis | Fable / Opus, high effort |
| Expert | Researches, writes specs, tests and code | Opus, high |
| Generalist | Validates, merges, reruns a gate, counts | Sonnet, medium |
| Cheapest | Wide lookups whose conclusion is all you keep | Haiku (`Explore`), low |

An agent never launches a tier above its own. Delegation is a direct `claude -p` call (`scripts/ask.sh`) when the agent has a shell, or one `ASK PARENT` line otherwise.

**Two modes:**

- **Research**: multi-agent research that ends in a **sourced action plan**, one doc-style HTML page where every figure has a URL, a date and a status.
- **Code**: a migration or rewrite run by many agents. Blind testers write the specs before the implementers, each agent has its own worktree, the integration branch must be green on a gate, and separate threads validate it.

**Two lanes:** short (2 or 3 agents, one antagonist pass, the report in the thread) for a question about your own systems, full for market research or a multi-target migration.

## See it run

**[Example board, animated](https://raw.githack.com/joey-barbier/ClaudeCode-Plugin/main/plugins/horka-research-plan/examples/task-graph-demo.html)** (`examples/task-graph-demo.html`, open it locally if the link is blocked). A fictional project: 45 tasks, 5 agents at most, reviews that come back BLOCKED, a decision you click for the user, a machine cut, the debrief per model, and a comparison of one-by-one vs waves vs graph.

## What's included

| Component | Role |
|---|---|
| `/horka-research-plan:horka-research-plan` | Triggers on "full check and a plan", "plan sourcé", "migre X vers Y avec plein d'agents", "lance plein d'agents", "quel modèle pour quelle tâche". Orchestrates the run. |
| `references/model-routing.md` | The four tiers, the three questions that pick one, the pass-down line for every brief, when delegating loses |
| `references/task-graph.md` + `scripts/board/` | The task graph every run follows (`graph.json`, `set.py`) and the board (`build.py` → `board.html`) |
| `references/code-variant.md` | Code mode: waves S/T/I/R/V/M, gates, differential harness, deliverable |
| `references/briefs.md` | Brief templates per role, with the short report format |
| `references/schemas.md` · `workflow-skeleton.md` · `page-structure.md` | JSON schemas, `Workflow` scripts, the doc-style page |
| `references/retrospective.md` | Scorecard, lessons file, one experiment per run |
| `scripts/ask.sh` | Direct call to a cheaper model, read-only tools, logged on the board |
| `examples/task-graph-demo.html` | The animated example board above |

## The task graph and the board

Every run, short or full, is a task graph. A task starts as soon as what it reads is done. A blocked task blocks only its descendants. A decision waiting on the user is a node of its own. `scripts/board/set.py` updates a task, prints what can start now and rebuilds `board.html`: the graph coloured by status, then the consumption debrief read from the transcripts (tokens per task and per model, cache reads, direct calls, wall time vs cumulated agent time, parallelism factor). On the page, a click on a task opens its detail (note, agents, tokens, the whole chain of tasks that led to it with the direct ones marked, what depends on it and on demand its whole descent, each one a link) and fades the rest; the graph zooms, pans and goes full screen, and a sticky contents bar reaches every part, from what waits for the user to tokens per model. The board replaces progress messages and feeds the scorecard.

## Verification

Based on [how the Claude Code team verifies agent work](https://claude.dev/blog/how-the-claude-code-team-thinks-about-verification/):

- **Run the real thing.** Before any push, the product runs end to end (a real job, a browser, a simulator, an API harness) and the trace is pasted. Research mode's equivalent: a validator opens every URL.
- **Migrations compare old and new** on the same inputs; any difference is a bug unless it is on the approved-differences list the user signed. Pure engines get property tests.
- **Checks stay out of reach of the change.** Verdicts name the commit SHA, rules are read from the base branch, and a script checks that no spec assertion moved.
- **Three red rounds, then the user decides.** A flaky test is never retried to green.
- **One reviewer made better, not more reviewers stacked.** Every point has a severity: blocking, minor or pre-existing. A new gate starts in observe mode.

## Research waves

```
0  Lessons file · reality check in three states (prod / develop / open PRs) · dated point zero
1  Personas (buyer, impacted third party) + real-demand probe        ← before any research
2  Researchers, one brief per action type
3  Dedup in code
4  Validators (a different agent per researcher) open every URL
5  Antagonist critic: 8–12 actions, 90-day sequence, two decision gates
6  Feasibility of every assumed flow + completeness
7  Retrospective
```

Code mode replaces them with S (probes, decision records) → T (blind testers, differential harness) → I (implementers) → R (reconciliation) → V (validation threads) → M (mechanical steps).

## Three rules

1. No number (or behaviour) from memory: URL opened, date, status; in code, `file:line` of the reference.
2. No agent grades its own work.
3. Nothing is created or scheduled; in code, branches yes, a push only on the user's go.

## Self-improvement loop

The orchestrator writes the facts (scorecard from the board), a separate agent writes the judgement (at most five lessons, a verdict on the previous experiment, one experiment for the next run), and the orchestrator rewrites `research-plan-lessons.md`. Lessons are rules with a trigger, a check and an origin: a rule enters after two occurrences, applies only when its trigger matches, and is dropped when it stops firing. Reviewers are measured on what they found, missed and flagged wrongly.

## Requirements

- `Agent` tool (or `Workflow`), `WebFetch` / `WebSearch` for research mode.
- A shell with `claude` for direct delegation; otherwise the `ASK PARENT` relay.
- Optional: `horka-review:antagonist-reviewer` for the critic's voice, a project `doc-style` skill for the page.

## Install

```bash
claude plugin install horka-research-plan
```
