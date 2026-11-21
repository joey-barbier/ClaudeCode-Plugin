# Fixes: walls to adapt, cheapest first

Change one thing at a time, then run the scan again and show the line that moved. Setting and flag names change between versions: open the tool's documentation page before writing them into someone's config (URLs in `sources.md`).

## 1. Production waits for tests (free, minutes)

The deploy job must not start unless a test job in the same run succeeded.

```yaml
jobs:
  test:
    uses: ./.github/workflows/test.yml   # that workflow needs `on: workflow_call`; or put the steps here
  build:
    runs-on: ubuntu-latest
    steps: [...]
  deploy-prod:
    needs: [test, build]                  # the wall
    environment: production
```

When the suite that matters runs in another workflow (a nightly end-to-end campaign against a staging site), nothing links it to the deploy. Add a first step to the deploy job that refuses when the last completed run is not green:

```yaml
      - name: Last end-to-end run must be green
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          c=$(gh run list --workflow e2e.yml --branch develop --status completed --limit 1 --json conclusion --jq '.[0].conclusion')
          [ "$c" = "success" ] || { echo "Last end-to-end run: ${c:-none}. Fix it or rerun it, then deploy again."; exit 1; }
```

The job needs `permissions: actions: read`. A suite that has been red for days will block every deploy: that is the point, and the reason to fix or quarantine a flaky test instead of ignoring the red.

## 2. A push guard that reads the whole command (free, minutes)

This skill does not ship a guard: reading shell commands reliably is a project of its own, and a guard that looks finished and is not is worse than none. What it gives is the specification below. A PreToolUse hook on Bash that deserves the name strips git's global options before looking for the subcommand, judges every chained part, resolves the current branch when the target is implicit, and asks when a push hides in a form it cannot parse (in doubt, ask).

Whatever guard the user writes or adopts, test it against these, which are the forms real agents produce:

| Command | Must be |
|---|---|
| `git push origin main` | stopped |
| `git push --force origin feature/x` and `-f` | stopped |
| `git push origin feature/x --force` (flag at the end) | stopped |
| `git push origin +feature/x` | stopped |
| `git -C /some/dir push --force origin main` | stopped |
| `echo ok && git push --force origin main` | stopped |
| `git -c user.name=a -C /some/dir push origin HEAD:main` | stopped |
| `git push`, `git push origin HEAD`, `cd <repo> && git push` while on the default branch | stopped (the guard has to resolve the current branch) |
| `bash -c 'git push origin main'`, `(git reset --hard HEAD~1)`, `/usr/bin/git reset --hard` | at least asked |
| `gh -R owner/repo pr merge 12`, `gh api -X PUT …/pulls/12/merge` | asked |
| `git log --grep push`, `echo 'git push later'` | untouched (a prompt on harmless text teaches the user to click yes) |
| `git push origin feature/x` | asked (or allowed, if the user wants that) |
| `git status`, `git log`, `grep -r push src/` | untouched |

A guard that matches only the start of the command passes the first two lines and none of the others. Briefs that tell agents to use `git -C <dir>` (common with worktrees) make the bypass the normal path.

Register it in `settings.json` (user level to cover every project):

```json
{"hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "/absolute/path/to/your-guard"}]}]}}
```

Keep the test cases next to the hook and run them when it changes: a blocking hook without tests fails silently in one of two directions.

A hook of this kind is a guard, not a sandbox: a command built at run time (a script file, an alias, a variable holding the subcommand) is out of its reach. Keep "ask" as its answer for ordinary pushes; where pushes are pre-approved, the wall for the default branch is branch protection on the platform (section 5).

Until such a guard exists, the walls that hold without one are the ask rules of section 3 (they miss `git -C <dir> push`, and catch the plain forms) and branch protection (section 5). Say so in the report instead of promising a hook.

## 3. Permission rules (free, minutes)

Rules complement the hook; they do not replace it, because a prefix rule on `git push` does not see `git -C <dir> push`.

```json
{"permissions": {
  "ask":  ["Bash(git push:*)", "Bash(gh pr merge:*)"],
  "deny": ["Read(./.env)", "Read(./.env.*)", "Read(./secrets/**)", "Bash(rm -rf:*)"]
}}
```

Do not take commits away. Committing on a working branch is local and reversible, and it is what lets an agent work in small steps: `git add`, `git commit`, `git switch`, `git stash` stay pre-approved, and a broad `Bash(git:*)` can stay too. Ask and deny rules are evaluated before allow rules (check it on the permissions page for the user's version), so the two `ask` lines above are enough to put a prompt on push and on merge without touching the rest.

What to look at is narrower: an explicit allow on `git push`, `git merge` or `gh pr merge` in a project's local settings. Ask whether it is deliberate. On a project where the user wants the agent to push its working branch by itself, keep it and put the wall where it matters: the default branch and production. In an automatic permission mode a "soft deny" entry is read by a classifier model: a useful filter, not a wall. The documentation also says that an action matching an allow rule is resolved before the classifier runs, so a push pre-approved by a Bash allow rule may never reach the soft-deny list, while deny and explicit ask rules are evaluated before the classifier. The two `ask` lines above are what puts a prompt on push in that mode too; confirm it with one push on a throwaway repository.

## 4. Caps (free, minutes)

- Headless calls (scripts, cron, CI): a turn cap and a budget cap on the command line of every call. The scan lists the calls that have neither.
- Sub-agents: a turn cap in the agent definition.
- CI jobs: `timeout-minutes` on every job.
- Parallel batches: the size (agents, review passes) is fixed before launch and refused beyond by the launching script, not by a sentence in the brief. If the account limit is shared with scheduled agents, keep batches out of their hours.
- A loop rule worth writing down: same failure twice with nothing changed means stop and report, not retry.

## 5. Branch protection and environment approval (free on public repositories, paid on private ones for some plans)

Protect the default branch with a required status check, and add a required reviewer on the production environment. The scan prints what the platform answered. When it answers that the plan does not offer protection, sections 1 and 2 are the walls; decide about the paid plan after they are in place, and check which plan opens which rule before paying.

## 6. Templates

Task contract, written before the work:

```
Goal:            one sentence
Constraints:     what must not change
Deliverable:     one reviewable pull request
Done when:       - the gate script passes (paste its output)
                 - <observable behaviour>
Needs approval:  anything visible outside this machine
If blocked:      stop, write what was tried in the state file, do not guess
```

Verifier brief, for an agent that did not write the change:

```
You did not write this change. Look for reasons to reject it.
Inputs: the contract, the diff, the output of the gate.
1. Each "done when" line: quote the evidence, or reject.
2. Anything touched outside the constraints?
3. Any test removed, skipped or weakened?
4. One input that could break it: try it.
Answer REJECT: <criterion and evidence> or ACCEPT: <one line of evidence per criterion>.
Judge against the contract and correctness only, not style.
```

State file, next to the work: current step · decisions and why · artefacts (branch, pull request) · open risks · next action.

## 7. Pruning (free)

- An agent or skill with no launch in the window: delete it, or move a project-specific one into its repository.
- A rule now enforced by a hook or a CI job: remove the sentence from the map.
- Worktrees whose branch is merged: remove them.
- A map file with a false claim: fix the claim first; a wrong instruction costs more than a missing one.
