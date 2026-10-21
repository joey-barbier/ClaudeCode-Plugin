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
  "cost": "unknown",
  "previous_experiment": {"tried": "personas before researchers", "kept": true, "why": "10 duplicates fewer"}
}
```

`cost` stays `"unknown"` unless the harness reported it. Never estimate it.

## Lessons file template (step C)

```markdown
# Research-plan lessons · rewritten 2026-10-21 · 3 runs

## Next experiment (ONE change for the next run)
Brief researchers with the personas' verdicts attached. Measure: duplicates after dedup (was 10).

## Rules that held (keep)
- Readers (personas, demand probe) before researchers: 10 fewer duplicates (run 2 vs run 1).
- Validators open every URL: 9 corrections on run 2, 0 on run 3's second wave.

## Rules that changed
- "One brief per angle" → "one brief per action type" (run 2: same action returned four times).

## Mistakes to watch
- A capability assumed in the plan did not exist in code (run 2, webhook). Phase 0 now verifies every assumed capability.
- A 49-minute wave with no reading in between (run 1). Max 15 minutes per wave.

## Scorecards (one line per run, newest first, last 10)
- 2026-10-21 · 18 agents · 2 waves · 44→10 actions · 329 figures, 0 false · cost unknown · experiment kept
- 2026-10-20 · ...
```

Rules for the file:

- **One experiment at a time.** The next run changes one thing and measures it; two changes at once cannot be attributed.
- A lesson is `situation → what we did → what to do next time`, general enough to apply to another project, specific enough to be testable.
- A lesson that was not confirmed by a second run stays under "Mistakes to watch", not under "Rules that held".
- The scorecard list keeps the last 10 lines; older ones are dropped, the file is not an archive.
- Everything in the file is also readable by the user: write it as you would say it to them.

## Phase 0 of the next run

1. Read the lessons file if it exists. Apply "Rules that held" to the common brief and run the "Next experiment".
2. In the scorecard of that run, fill `previous_experiment` with what happened: kept or dropped, and why.

If the file does not exist, this is run 1: write it at the end anyway.
