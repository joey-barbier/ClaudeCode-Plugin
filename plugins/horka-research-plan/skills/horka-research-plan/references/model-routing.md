# Model routing — for any task, at every level

This rule is not tied to research or migration. It applies to any work split across agents, and it is **recursive**: the orchestrator launches agents with it, every agent it launches applies it to its own sub-agents, and so on down. Nothing in the harness picks a model for a sub-agent: a sub-agent inherits its parent's model unless the launch says otherwise. So the rule travels in the brief, or it does not travel at all.

## The tiers

| Tier | Example (today) | Use for | Effort |
|---|---|---|---|
| Top | Fable 5.1 | Orchestration of the whole run, final judgement, synthesis, retrospective critic | high (medium for pure orchestration) |
| Expert | Opus 5.5 | Anything where a wrong detail costs a rerun: research with long tool sequences, writing or porting code, writing tests from a reference, architecture decisions, antagonist review, reconciliation of conflicting work | high |
| Generalist | Sonnet 5.5 | Mechanical work with a clear check: open and compare, count, merge a branch and rerun a gate, "is it green?", format a report, update a board, validate URLs | medium |
| Cheapest | Haiku 5.5 (the `Explore` agent type) | Lookups whose conclusion is all that matters: where is X used, inventory of a folder, which files mention Y, list the endpoints, first triage of a log | low |

Names change; the four tiers do not. Write the tier, not the model name, in briefs when you can.

## The decision, per sub-task

Ask three questions before launching an agent:

1. **Does a wrong answer cost a rerun or a wrong decision?** Yes → expert tier (or top for judgement). No → go down.
2. **Is there a mechanical check of the result** (a test run, a diff, a count, a URL that opens)? Yes → generalist tier.
3. **Is only the conclusion kept**, and the raw material would otherwise sit in an expensive context for the rest of the run? Yes → cheapest tier, as a sub-agent of whoever needs the answer.

A task that mixes the three is split: the expert agent does the judgement part itself and delegates the two others.

## How the model is actually set (Claude Code mechanics)

- The model of a sub-agent is fixed at launch, in this order: the `model` parameter passed to the `Agent` call; otherwise the `model` in the agent type's frontmatter; otherwise it **inherits its parent's model**. An expert agent that forgets `model` launches another expert: that is the main cost leak. Always pass `model` explicitly.
- A `fork` always inherits the parent's model and ignores `model`: it is not a way to route to a cheaper tier.
- A sub-agent can only delegate if it has the `Agent` tool and its brief says so. Check both before relying on nested delegation; if sub-agents cannot delegate, the orchestrator launches the cheap steps itself.
- Keep the depth at three levels at most (orchestrator → agent → sub-agent): deeper chains lose the question on the way back up.

## When a sub-agent cannot launch an agent (measured 16/11/2026)

In cloud sessions a `general-purpose` sub-agent had no `Agent` tool: the pass-down line did nothing, and every run stayed at depth 1 (379 agents, none launched by another, no cheapest-tier call). Two ways round it, both tested on the same lookup (count the Swift files of two folders, right answer 69 and 39):

| Way | How | Measured |
|---|---|---|
| Direct call | The agent runs `claude -p "<question and answer format>" --model <cheaper model id> --tools Read,Glob,Grep --permission-mode default --output-format json < /dev/null` (prompt right after `-p`, stdin closed; `--tools` restricts the call to read-only tools, no shell; the JSON gives `result` and `total_cost_usd`). Wrapper: `scripts/ask.sh`. | One test, cloud session, 16/11/2026: right answer in 16 s for 0.013 $ on the cheapest tier, no turn of the parent. Each call loads its own fixed context (about 160 k tokens of system prompt, tools and skills): batch questions rather than firing hundreds. |
| Relay through the parent | The agent sends one line `ASK PARENT: <tier> · <precise question> · <answer format>` to its parent and hands back; the parent launches the cheaper agent and resumes the first one with the answer | One test, same day: works. The agent cannot wait for the reply: one round trip of about a minute and one full re-read of the agent's context (60 k tokens in the test) per ask. The parent handles an ask as soon as it arrives. |

Prefer the direct call; keep the relay for agents without a shell. Run a 30-second dry run of whichever you rely on before the first wave.

**Threshold.** One turn of an expert agent costs the re-read of its whole context (about 0.06 $ at 150 k tokens of context on a 4 $/MTok input tier with cache reads at a tenth; twice that on the top tier). One complete call on the cheapest tier costs about a cent. The agent spends one turn to launch the call either way, so: a single command, it runs itself; a lookup whose conclusion is all it keeps, or a mechanical check, that would take it two turns or more, it delegates, and the material read stays out of its context. Exactness is never delegated without a check afterwards (table below).

## The recursion rule

- An agent may launch agents of **its own tier or cheaper**, never a more expensive one. If it needs more judgement than it has, it reports back to its parent with the question instead of escalating by itself.
- Every brief ends with the **pass-down line**: "You may launch sub-agents. Choose their tier with `references/model-routing.md` (path: `<absolute path of this file>`): judgement → your tier at most, mechanical with a check → generalist, lookup whose conclusion is all you keep → cheapest (`Explore`). Put this same line in every brief you write."
- The orchestrator records, per agent, the tier used and the tokens per model (from the transcripts, cache reads included). That is the only way to know whether the routing paid off.

## When delegating a lookup wins, and when it loses

| Situation | Delegate to the cheapest tier? | Why |
|---|---|---|
| Wide search where only the conclusion is kept | Yes | Done by the agent, everything read stays in its window and is re-sent on each of its 50 to 100 later turns (500 M of the 566 M tokens of the Guild run were cache reads). |
| Content the agent needs in full (a module to port line by line, a spec to make pass) | No | It will read it again anyway: double cost. |
| A small lookup (one `grep`, one `ls`) | No | A sub-agent costs a few thousand tokens and 30 s to 2 min, more than the lookup. |
| Anything that needs exactness (signatures, formats, numbers) | No, or verify afterwards | A sub-agent's summary can be wrong. |

On the Guild run the routing paid off on mechanics (19 Sonnet tasks, 1 redone on Opus; merges and gates at ~1 % of tokens) but not on the bill: 80 % of tokens were Opus contexts re-read; the cost lever is context length, not model tier.

## Examples

- Top (Fable) orchestrates a migration: launches expert (Opus) testers and implementers; each implementer launches cheapest (Haiku) `Explore` sub-agents for "where is this type used"; the orchestrator launches generalist (Sonnet) agents to merge branches and rerun the gate.
- Expert (Opus) writes a report over 40 pages of docs: launches cheapest sub-agents to extract one fact per page, keeps the writing.
- Generalist (Sonnet) validates 300 URLs: may launch cheapest sub-agents to open batches and return status lines, never an expert.
