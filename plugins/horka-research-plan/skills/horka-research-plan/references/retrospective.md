# Retrospective and lessons file

The skill ends with a step back. Its product is one file, the **lessons file**, that the next run reads in Phase 0 before anything else. This is the whole continuous-improvement loop: one run writes, the next one reads and tries one change, the one after measures whether it helped.

## Where the lessons file lives

Pick the first that applies, and say which one you used in the delivery summary:

1. A project memory folder exists (claude.ai project thread, or a `.claude/memory/` directory at the repo root): `research-plan-lessons.md` in that folder.
2. Otherwise, inside the repository: `.claude/memory/research-plan-lessons.md` (create the directory; it is the convention Horka's repos already use for `DECISIONS.md`).
3. No repository: `~/.claude/research-plan-lessons.md`.

One file for the skill, **rewritten as a whole** on every run, never appended to. Under 4 KB. No secret, no credential, no personal data, no figure that is not already on the delivered page.

## Who writes what (rule 2 still holds: no agent grades its own work)

| Step | Who | Input | Output |
|---|---|---|---|
| A · Facts | the orchestrator (you) | your own log of the run | the **scorecard** below: counts, timings, models, what failed, what you changed mid-run. Facts only, no judgement. |
| B · Judgement | one fresh agent (critic voice, most capable model, high effort), who did **not** write the page | the brief, the scorecard, the delivered page, the previous lessons file | ≤ 5 lessons, one next experiment, verdict on the previous experiment |
| C · Merge | the orchestrator | A + B | the lessons file, rewritten in full; 3 lines "what I learned" in the delivery summary |

Step B is the step people skip. Do not skip it: an orchestrator reviewing its own run keeps the same blind spots.

## Scorecard (step A)

```json
{
  "run": "2026-10-21",
  "question": "one sentence",
  "waves": [
    {"name": "readers", "agents": 3, "models": {"persona": "fable/high", "probe": "sonnet/medium"},
     "minutes": 12, "failed": 0, "corrections_to_brief": "added the maintainer persona"}
  ],
  "actions": {"candidates": 44, "after_dedup": 34, "kept": 10},
  "figures": {"opened": 329, "verified": 290, "partial": 30, "false": 0, "not_found": 9},
  "late_discoveries": ["the webhook assumed by action 5 does not exist in code"],
  "reviewers": [{"who": "security thread", "found": 6, "missed": 1, "missed_found_by": "user, in prod",
                 "flagged_wrongly": 2, "rounds": 3}],
  "verification": {"verify_run": "pasted", "differential": {"inputs": 412, "diffs": 3, "approved": 3},
                   "new_gates_in_observe": ["spec-diff script"]},
  "tokens": {"by_model": {"opus": {"all_in": 502363204, "output": 3280662, "turns": 2065},
                          "fable": {"all_in": 62608453, "output": 209208, "turns": 137}},
             "source": "transcripts (session + subagents), cache reads included"},
  "time": {"elapsed_minutes": 85, "cumulated_agent_minutes": 1008, "parallelism": 11.7},
  "code_variant": {"tests_green_on_gate": 1391, "blocking_found": {"antagonist": 18, "validation_threads": 4},
                   "agents_relaunched": [{"agent": "guard implementer", "why": "L0 API changed after its spec"}]},
  "cost": "unknown",
  "previous_experiment": {"tried": "personas before researchers", "kept": true, "why": "10 duplicates fewer"}
}
```

`cost` stays `"unknown"` unless the harness reported it. Never estimate it. `tokens` is read from the transcripts (`message.usage` of every assistant turn, deduplicated by message id), never from the harness's per-agent count, which ignores cache reads and was 5.9 M where the transcripts said 404 M on the Guild run. Record cache reads per agent: it is the figure the delegation rule (Phase 2) is meant to lower.

## Lessons file template (step C)

```markdown
# Research-plan lessons · rewritten 2026-10-21 · 3 runs

## Next experiment (ONE change for the next run)
Brief researchers with the personas' verdicts attached. Measure: duplicates after dedup (was 10).

## Rules (trigger · check · origin; last fired)
- The plan relies on a capability (webhook, endpoint, limit) · verify it in code in Phase 0 · run 2, webhook missing · run 3.
- Research question with an audience · personas and demand probe before researchers · run 2: 10 fewer duplicates · run 3.

## Rules removed or changed (one line each, last 3 runs)
- "One brief per angle" → "one brief per action type" (run 2: same action returned four times).

## Candidates (seen once; a second occurrence promotes them)
- Trigger: a wave planned over 15 min · Check: split it · Origin: run 1, 49-min wave, no reading in between.

## Scorecards (one line per run, newest first, last 10)
- 2026-10-21 · 18 agents · 2 waves · 44→10 actions · 329 figures, 0 false · cost unknown · experiment kept
- 2026-10-20 · ...
```

Rules for the file:

- **One experiment at a time.** The next run changes one thing and measures it; two changes at once cannot be attributed.
- A lesson is `situation → what we did → what to do next time`, general enough to apply to another project, specific enough to be testable.
- A rule has a **trigger** readable from the question or the diff ("the change touches session storage"), a **check**, and its **origin** (the run or incident). Phase 0 applies only the rules whose trigger matches, not the whole file.
- A lesson seen once stays a candidate; a second occurrence promotes it to a rule. A rule that has not fired in the last 5 runs is removed: the file is pruned, not grown.
- Reviewer misses become rules: a point a reviewer missed and someone found later (the user, prod, a later pass) gets a rule with the trigger that would have caught it.
- The scorecard list keeps the last 10 lines; older ones are dropped, the file is not an archive.
- Everything in the file is also readable by the user: write it as you would say it to them.

## Phase 0 of the next run

1. Read the lessons file from the base branch or memory folder (never from a branch under review). Apply the rules whose trigger matches this run, and run the "Next experiment".
2. In the scorecard of that run, fill `previous_experiment` with what happened: kept or dropped, and why.

If the file does not exist, this is run 1: write it at the end anyway.

**Next experiment for code mode (from the Guild run):** cap every agent's context (~150k). Past it the agent writes a hand-over report and a fresh agent continues; the orchestrator is relieved each wave with a state file. Measure: Opus cache-read/output ratio (174 on the Guild run) and orchestrator share of tokens (16 %).
