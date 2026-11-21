# The report file

The judgement of a full audit is written as one JSON file, then rendered by `scripts/render.py` into a page the user reads in two minutes. The page has no room for commentary: every field has a maximum length, and the script refuses the file and says which field to shorten. Write facts, drop adjectives.

`code` between backticks is rendered as code. Write everything in the language of the request, axis names included (in French: conception, détection, application).

## Fields

| Field | Required | Content | Limit |
|---|---|---|---|
| `lang` | yes | two-letter code of the language of the request (`fr`, `en`, `de`…). Fixed labels exist in `en` and `fr`; any other code gets English labels | |
| `title` | no | replaces the default title | 90 |
| `summary` | yes | the verdict: what holds, what does not, the first thing to connect | 280 characters |
| `repos[]` | yes, 1 to 6 | one entry per repository | |
| `repos[].name` | yes | repository name | |
| `repos[].regime` | yes | `production`, `v1` or `experiment` | |
| `repos[].design` · `detection` · `enforcement` | yes | whole number, 0 to 3 | |
| `repos[].next` | yes | what is missing to gain one level, on the weakest axis | 170 |
| `repos[].unsure` | no | `{"detection": "reason"}`: an axis scored on a partial view (triggers in an outside automation, a CI file read by hand); shown as "to confirm" under the meter | 110 per reason |
| `plus[]` | 0 to 5 | what holds: `text`, and `evidence` (scan line, `file:line`, PR number, date) | 170 · 130 |
| `minus[]` | 0 to 5 | what does not hold, same shape; empty when the setup is good | 170 · 130 |
| `actions[]` | 0 to 6, cheapest first | `title`, `cost`, `target`, `stops`, optional `how` | 90 · 170 · 900 |
| `actions[].cost` | yes | `free`, `minutes`, `hours` or `paid` | |
| `actions[].target` | yes | `branch`, `production`, `spend`, `secrets`, `cleanup` or `other` | |
| `actions[].how` | no | the few lines to paste (a YAML fragment, a rule, a command); shown folded | 900 |
| `criteria[]` | yes, C1 to C12 | `id`, `held_by`, `note`. One line per criterion; when repositories differ on one, repeat it with a `repo` field for each (72 lines at most) | note 120 |
| `criteria[].held_by` | yes | `nothing`, `sentence`, `script`, `hook`, `ci_reports`, `blocks` or `na` (not measured) | |
| `debt[]` | only for v1 and experiment repositories | `gap`, `repay_when` | 120 each |
| `limits[]` | 0 to 8 | what was not measured, what was assumed | 170 each |

The table of tested commands is not in this file: the renderer takes it from the scan's JSON (`--scan`).

## Example

```json
{
  "lang": "en",
  "summary": "Tests run on every pull request, so problems are seen. Nothing stops them: production deploys on any push to `main` and the push guard reads only the start of the command.",
  "repos": [
    {"name": "shop-api", "regime": "production", "design": 2, "detection": 2, "enforcement": 1,
     "next": "Enforcement 2: make `deploy-prod` wait for the test job."}
  ],
  "plus": [
    {"text": "Tests run on every pull request.", "evidence": "ci.yml, trigger pull_request"},
    {"text": "A written definition of done: `./check.sh` prints GATE: PASS.", "evidence": "AGENTS.md:14"}
  ],
  "minus": [
    {"text": "Production deploys on any push to `main` with no test job upstream.", "evidence": "deploy.yml, deploy-prod needs: build"},
    {"text": "The push guard is bypassed by `git -C <dir> push --force`.", "evidence": "tested by the scan probe"}
  ],
  "actions": [
    {"title": "Make the deploy wait for the tests", "cost": "free", "target": "production",
     "stops": "A red build reaching customers.", "how": "deploy-prod:\n  needs: [test, build]"},
    {"title": "Replace the guard with one that reads the whole command", "cost": "minutes", "target": "branch",
     "stops": "Force pushes through `git -C`, a `+refspec` or a chained command."}
  ],
  "criteria": [
    {"id": "C1", "held_by": "sentence", "note": "Done is defined once in AGENTS.md, not per task."},
    {"id": "C2", "held_by": "sentence", "note": "Map of 15 lines; it names Jest, the project uses vitest."},
    {"id": "C3", "held_by": "na", "note": "Not measured."},
    {"id": "C4", "held_by": "sentence", "note": "State file 13 commits behind."},
    {"id": "C5", "held_by": "ci_reports", "note": "CI on every pull request; no Stop hook."},
    {"id": "C6", "held_by": "nothing", "note": "No reviewer other than the author."},
    {"id": "C7", "held_by": "hook", "note": "10 of 13 risky commands get through."},
    {"id": "C8", "held_by": "nothing", "note": "2 unattended calls with no cap."},
    {"id": "C9", "held_by": "nothing", "note": "No remote: commits exist on one machine."},
    {"id": "C10", "held_by": "nothing", "note": "No lessons file, no structural lint."},
    {"id": "C11", "held_by": "na", "note": "3 agents, 2 skills; usage unknown."},
    {"id": "C12", "held_by": "nothing", "note": "No eval, no hook test."}
  ],
  "limits": ["No GitHub remote: branch protection and run history not measured."]
}
```

## Rendering

```bash
python3 "<skill base directory>/scripts/render.py" <folder>/audit.json --scan <folder>/scan.json --open
```

The page is written next to the report as `audit.html`. When the script lists problems, fix those fields and run it again: nothing is written until the file is clean.
