# horka-research-plan

Multi-agent research that ends in a **sourced action plan**, delivered as one doc-style HTML page.

Built after a real run: 18 agents in two waves, 44 candidate actions, 329 figures opened at the source by validators (0 false, 9 corrections), 10 actions kept by an antagonist critic. The skill encodes what that run taught: readers (personas, real demand) *before* researchers, one brief per action type, validators separate from researchers, short waves with reading in between, and an orchestration scorecard so the next run starts smarter.

## What's included

| Component | Trigger | Role |
|-------|---------|------|
| `/horka-research-plan:horka-research-plan` | "full check and a plan", "how do we get discovered", "go-to-market", "sourced plan", "check complet et un plan", "plan sourcé" | Orchestrates the waves, writes the page, hands over product needs and tasks |
| `references/briefs.md` | — | Brief templates per role (persona, demand probe, researcher, validator, critic, feasibility, completeness) |
| `references/schemas.md` | — | JSON schemas to impose on every agent |
| `references/workflow-skeleton.md` | — | `Workflow` scripts per wave (falls back to the `Agent` tool) |
| `references/page-structure.md` | — | The doc-style page: look, tabs, build |

## The waves

```
0  Reality check in three states (prod / develop / open PRs) + dated point zero
1  Personas (buyer, impacted third party) + real-demand probe        ← before any research
2  Researchers, one brief per action type
3  Dedup in code
4  Validators (a different agent per researcher) open every URL
5  Antagonist critic: 8–12 actions, 90-day sequence, two decision gates
6  Feasibility of every assumed flow + completeness ("what is missing?")
→  One HTML page · nothing created or scheduled · scorecard saved to memory
```

## Three rules

1. No number from memory: URL opened, date, status chip (verified / partial / hypothesis / not found).
2. No agent grades its own work.
3. Nothing is created or scheduled: product needs and tasks go in a hand-over tab.

## Model and effort per role

| Role | Model | Effort |
|---|---|---|
| Orchestrator, critic, personas, synthesis | most capable (Fable) | high |
| Researchers | expert tier (Opus) | high |
| Validators, demand probe, counting | generalist tier (Sonnet) | medium |

## Requirements

- `WebFetch` / `WebSearch` for validators and researchers.
- `Workflow` tool optional (Agent tool fallback).
- Optional: `horka-review:antagonist-reviewer` for the critic's voice, a project `doc-style` skill for the page.

## Install

```bash
claude plugin install horka-research-plan
```
