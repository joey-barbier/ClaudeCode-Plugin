---
name: horka-harness-audit
description: Audit how someone develops with AI agents (rules, hooks, permissions, CI, branch protection, review, spend caps) and say what actually holds each rule - a sentence, a script, a hook, CI or the platform. Asks 2-3 questions, runs a scan that edits nothing (about 30 seconds, no agents), then opens one HTML page read in two minutes, with a level from 0 to 3 on three axes (design, detection, enforcement), what holds and what does not, and the actions to take, cheapest first. Use when the user says "audit my harness", "rate my AI workflow", "judge how I work with agents", "what level am I", "do my guardrails hold", "is my never-push rule really enforced", "bilan de ma façon de dev avec l'IA", "audite mon harness", "mes garde-fous tiennent ?", "quel est mon niveau", or shares an article on harness engineering or agent best practices and wants to be compared with it. Do NOT use to review a code diff (code-review), to score one skill (horka-skill-evaluate) or to write a CLAUDE.md (horka-setup).
---

# Harness Audit

An agent is a model plus a harness: what the model sees, which tools it can touch, what it remembers, what counts as done, what it may not do, what happens when something breaks. This skill judges the harness with one question asked of every rule and every check:

**What holds it?** nothing → a sentence (CLAUDE.md, a skill, a brief) → a script someone must remember to run → a hook that runs by itself → CI that reports → CI or a platform rule that blocks.

A sentence holds as long as the model remembers it. Most setups are well designed and weakly enforced, and their owner cannot see the gap because every rule is written down somewhere.

## Scope

Reads the Claude Code config, the repositories, their CI files and, through `gh`, the GitHub settings and history. Edits nothing in them: no setting changed, no hook installed, no push, no fetch. The only files it writes are its own, in a dated folder under `~/.claude/harness-audit/` (the scan, the report, the page). Fixes are proposed; the user decides. Needs `python3` and `git`; `gh` is optional (without it, platform facts are reported as not measured).

One thing does run: to test the guards, the scan runs the user's own PreToolUse hooks, once for each of 13 fabricated risky commands, from an empty temporary folder. The risky commands themselves are never run, but a hook that writes a log or sends a notification will do so 13 times. Hooks defined inside a scanned repository are listed and not run, because their command line comes from that repository, and the user's hooks are never run from inside a scanned repository either. The scan quotes hook scripts by name only, and passes the lines it quotes from the user's files through a best-effort mask for credential shapes: it knows shapes, not secrets, so do not paste scan output anywhere public.

It judges the harness, not the code or one skill. It works next to the skills that do the rest: a code review for a diff, a skill evaluator for one skill's quality, a settings skill to apply a rule or a hook once the user has chosen it.

## Step 1 - Ask, in one message

Two or three questions, never more, and skip any the request already answers.

1. **Which repositories?** Default: the current one plus the global config. In a workspace of several repositories, the two or three that matter most.
2. **What regime is each one in?** Production (real users or money) · v1 (speed first, debt accepted for now) · experiment. The same gap is an oversight in the first and a choice in the second. An audit that blames a choice is rejected, and rightly.
3. **Do agents run without you watching?** Night jobs, agents in CI, large parallel batches. This decides how much the caps (C8) weigh.

In the same message, one line of notice, not a question: the scan will run their own PreToolUse hooks on 13 fabricated commands (see Scope), and they can say "no hook probe" to skip it. A user whose hooks log or notify needs to know before, not after.

If nobody can answer (headless run), treat any repository with a deploy job as production and say that you assumed it.

**A narrow question gets a narrow answer.** "Is my no-push rule enforced?" needs the scan and the short format of step 5, not the twelve criteria.

## Step 2 - Scan

```bash
R=~/.claude/harness-audit/$(date +%Y-%m-%d-%H%M) && mkdir -p "$R"      # the report folder
python3 "<this skill's base directory>/scripts/scan.py" --json "$R/scan.json" --repo <path> [--repo <path> ...]
```

Options: `--home <dir>` when the Claude Code config is not in `~/.claude`, `--no-network` to skip GitHub, `--no-hook-probe` to run no hook at all, `--usage-days N`. `--probe-repo-hooks` also runs the hooks a scanned repository defines, and runs every hook from inside that repository: pass it only when the user says the repository is theirs or trusted, never for a repository they just cloned. For a narrow question, drop the folder and `--json`.

- Every output line reads `[criterion] fact (source)`.
- Tracked files are read at `origin/<default branch>`, not in the working tree: a stale checkout tells a false story. When the scan prints an old last fetch, ask the user to run `git fetch` and scan again; if nobody can answer, carry on and put the fetch date in the limits.
- A headless agent call "with no turn or budget flag and no `timeout` on the same line" may be capped by its caller: open the caller before writing that it has no cap.
- The probe passes 13 risky commands as text to the permission rules and as input to the PreToolUse hooks, and lists the ones nothing stops. The commands are never run; the hooks are. A probe line that says a hook was not run, gave no answer or has a filter the scan did not understand is not a "passes": open that hook before writing that nothing stops the command.
- Write "tested" for what the probe shows and "read in the code" for what you deduced: they are not the same strength of evidence.
- Work from this output. A fact that is not in it, or in a file you opened yourself, does not go in the report.

## Step 3 - Read what the scan cannot see

Ten minutes, not an investigation. Per repository:

- **The map** (CLAUDE.md, AGENTS.md): open it, pick two concrete claims (a path, a command) and check them against the code. Record each false one under C2: a map that lies is worse than none. No map: record "no map".
- **The gate** (`check.sh`, the test job): open it, list the commands it runs and count the test files they reach. Zero: record "the gate passes on nothing" under C5. In a v1 or an experiment, a missing gate is chosen debt, not a finding.
- **Two recent pull requests or task briefs**: note whether "done when" was written before the work (C1) and whether anything other than the author looked at the result (C6). No pull request to read: say so.
- **The hook that has holes**, when the probe found some: open it and note the line that explains the hole, so the fix can be named.
- **Each unattended agent call** the scan lists: note the tools it is allowed and whether it reads text written by strangers (issues, pull request comments). Wide tools plus untrusted input is an open door, cap or no cap: record it under C7.
- **The lessons file**, if there is one: count the rules that name a script or a hook, and the ones that are another sentence (C10).

No agents. More than three repositories, or a deeper dig, is a separate job to propose, not to start.

## Step 4 - Judge

Read `references/grid.md` now: twelve criteria, the good level for each according to the primary sources, which scan lines answer it, and the cheapest wall.

Give a level from 0 to 3 on **three separate axes**, per repository. One whole number per axis, no range: between two levels, take the lower and say what is missing for the next. The conditions below are tests to apply, so that two audits of the same setup give the same numbers.

| Level | Design: what exists on paper | Detection: what runs and sees problems | Enforcement: what can say no by itself |
|---|---|---|---|
| 0 | no map, no written rule | no check runs by itself | no rule, hook or job dependency stops anything |
| 1 | a map or written rules, and at most one design piece | checks exist but someone must launch them, or they run on nothing (zero tests), or they run by themselves on a few branches only (release branches), so most changes are not seen | partial stops only: a hook or rule the probe gets past, sentences for the rest; none of the three targets has a wall |
| 2 | two to four design pieces | test-like checks run by themselves on every pull request or on a schedule, and reach real tests | at least one of the three targets has a wall that holds |
| 3 | five or six design pieces | level 2 plus a second pair of eyes that exercises the real product (end-to-end run, browser QA, reviewer on pull requests), and reds that get fixed, not a red streak left for days | every target that applies has a wall the agent cannot talk its way past |

The six **design pieces**. Count each one that exists in writing, in the repository or in the global config that applies to it (design is what is on paper; whether it holds is the two other axes):

1. state kept outside the chat (a state or memory file, even stale);
2. a definition of done written before the work (specs, acceptance lines, a gate named as the definition);
3. a verifier role other than the author, and launched at least once in the usage window;
4. a lessons file or loop;
5. permissions sorted by how hard an action is to undo (ask or deny rules, a soft-deny list, a guard hook);
6. caps written down (turns, budget, attempts, batch size).

A map is the root file the agent reads first: CLAUDE.md, AGENTS.md, or an architecture or memory file a hook loads at session start. In doubt, a piece counts when the agent meets it without being told (the tool or a hook loads it, a job runs it) and does not count when someone has to point to it. A budget gate in CI is a written cap.

A guard that stops some command forms and lets others through is enforcement level 1, not 0: something does say no, it just does not hold.

The three targets of enforcement: the **default branch** (platform protection, or a guard the probe could not get past), **production** (the deploy waits for a test job or an approval; applies when a deploy job exists) and **spend** (every unattended call is capped; applies when agents run unattended).

Rules of judgement. Each one comes from an audit that got it wrong.

- **Keep the axes apart.** A nightly suite that goes red is detection working and enforcement missing. One merged score hides exactly what the user needs to see. For each test suite, say what it is connected to: a suite that runs on a schedule and that no merge or deploy waits for is detection only.
- **Judge each repository on its own.** Never average a guarded repository with a rushed one.
- **Quote triggers from the scan line.** "Runs only at night" was wrong once: the workflow also ran on pull requests touching its own folder.
- **Chosen debt is not a fault.** In a v1 or an experiment, list the gaps under "debt you chose", each with the event that should trigger repayment (first paying user, second developer, first unattended run). Three things are never debt, whatever the regime: an unguarded push to the default branch, secrets readable by a broad allow rule, and unattended agents with no cap. In those repositories the weakest point and the actions come from that list of three only. A gap the user chose (no CI, no tests, no gate, no review) appears once, in the debt section, never as the weakest point and never as an action for now.
- **Sort by how hard it is to undo, before recommending anything on permissions.** Commits, branches and edits on a working branch are reversible: they stay free, and a pre-approved commit is never a finding. Never recommend removing an allow rule that covers only reversible actions, and never "read-only git". The targets are what leaves the machine or cannot be undone: a push to the default branch, a merge, a force push, a hard reset. A pre-approved push on a working branch may be the user's choice: say what it allows, and ask.
- **Free walls before paid ones.** A `needs:` on the deploy job, a hook, an ask or deny rule cost nothing. Recommend a paid plan only after them, and only for what they cannot do.
- **Prune before adding.** If C11 shows unused agents, duplicate skills or rules nobody enforces, one action removes something, and no action adds a component where removing one would do. Never answer "too heavy" with five additions.
- **Order of the actions.** First what closes one of the three targets, cheapest first; then pruning; then the rest. Removing a broad allow rule closes a target and prunes at once: it comes first.
- **No figure from memory.** The "not measured" block of the scan goes into the limits section as it is.
- **An absence seen from a partial view is not an absence.** When the scan does not parse the CI, or triggers can be set outside the file you read, do not write "nothing does X" under `minus` and do not lower a level on it: score what you saw and flag the axis in `unsure` with the reason.
- **A reviewer asked for problems always finds some.** Five facts at most, three to six actions. If the setup is good, say so and stop.

## Step 5 - Report

**Narrow question** (see step 1): skip the levels and the template below. Answer in 30 lines at most: the answer in the first line (yes, no, partly), a small table of the command forms that are stopped and the ones that pass, the fix, what could not be measured. Add a fact from another criterion only when it changes the answer (a deploy that fires on that very push, for instance).

**Full audit**: one HTML page, opened at the end. The user reads it in two minutes: levels, what holds, what does not, what to do. No prose report in the thread.

1. Read `references/report-schema.md`, then write the judgement to `<report folder>/audit.json`, in the language of the request (a request in French gets a page in French; the fixed labels of the page exist in English and French, any other language gets English labels around your text). What goes in:
   - `summary`: the verdict in two sentences.
   - per repository: three whole numbers (never "0-1") and what is missing for the next level; `unsure` for an axis whose decisive facts were out of reach.
   - `plus`, then `minus`: five facts at most on each side, each with its evidence (scan line, `file:line`, PR number, date). The user built this setup: fill `plus` first, with what really holds.
   - `actions`: three to six, cheapest first, each with what it stops; none when the setup is good. Put the few lines to paste in `how`.
   - `criteria`: C1 to C12, one short note each.
   - `debt` for v1 and experiment repositories, `limits` for what was not measured or was assumed.
2. Render and open it:
   ```bash
   python3 "<this skill's base directory>/scripts/render.py" <report folder>/audit.json --scan <report folder>/scan.json --open
   ```
   The script refuses fields that are too long and names them: shorten those fields, keep the facts, run it again. The table of tested commands is taken from the scan, do not retype it.
3. In the thread, five lines at most: the three levels per repository, the first action, the full path of the page. Nothing the page already says.

The user does not know this skill's folders. Never send them to a bare `references/…` or `scripts/…`: paste the few lines that matter (in `how`), or give the full absolute path of the file on their machine. The skill ships no ready-made guard: when an action says "a guard that reads the whole command", put in `how` the command forms it has to stop (from `references/fixes.md`), not a file to copy.

When the user wants a fix applied, read `references/fixes.md` (snippets and the test cases a push guard has to pass), change one thing, then run the scan again to show the line that moved.

## Example

Request: "Do my guardrails hold? Repo ~/code/shop, it is in production."

Scan, abridged:
```
[C7] 5 rule lines written as sentences (never / always / must) in CLAUDE.md
[C7] probe · force push through git -C: `git -C /tmp/x push --force origin main` → rules: allow by Bash(git:*) · hooks: passes every hook
[C7] deploy job `deploy-prod` in deploy.yml · needs: build · NO test-like job upstream in this workflow
[C5] test-like jobs run on every pull request: ci.yml
```

Levels: design 2, detection 2, enforcement 1. The `summary` of the page: "Your tests run on every pull request, so problems are seen. Nothing stops them: production deploys on any push to main without waiting for a test job, and your push guard reads only the start of the command, so `git -C <dir> push --force` goes through. Two free connections: `needs: test` on `deploy-prod`, and a guard that reads the whole command."

## Error handling

- **`gh` absent or signed out**: the scan says so; report branch protection, merges on red and run history as not measured. Do not guess them from the workflow files.
- **Path is a workspace, not a repository**: the scan lists the repositories inside; ask which ones.
- **No repository given**: only the global config is scanned; say that CI and platform walls were not looked at.
- **CI that is not GitHub Actions** (Bitrise, GitLab, CircleCI, Jenkins…): the scan names the file and does not parse it. Read it by hand for the three things the scan would have said: which pipelines run tests and on which branches, whether the delivery waits for them, and whether agents are called in it with a cap. Say in the limits that it was read by hand.
- **Another agent tool (Cursor, Codex, Gemini CLI)**: the repository, CI and platform parts apply unchanged; the global part reads Claude Code files only, so judge rules and hooks by reading that tool's own config.
- **A hook gives no answer or errors under the probe**: the probe line says so ("no answer in 8 s", "error (exit 1, which does not block)"), and a hook that timed out once is not run again. The scan waits 8 seconds where Claude Code waits much longer, so "no answer" is not a verdict: name the hook and read it. An exit code other than 2 does not block in Claude Code either. A hook that looks for its script inside the project (through `$CLAUDE_PROJECT_DIR`) errors under the probe, because the probe runs from an empty folder: read that script instead.
- **The permission mode is not set** in the settings: the scan says so. The built-in default is not the same in every version, so do not write that an unmatched command gets a prompt; write that the mode decides and that it is not set.
- **The page cannot be opened** (no display, remote session): the script says so; give the full path of the page and the five-line summary.
- **The report folder cannot be written**: use a temporary folder and say where the page is.

## References

- `references/grid.md`: the twelve criteria. Read at step 4.
- `references/report-schema.md`: the fields of `audit.json`, their limits, an example. Read at step 5.
- `references/sources.md`: what the articles and primary sources say, verified figures with URL and date, where popular advice departs from its sources, a short reading list. Read when the user asks why, wants sources, or brings an article to be compared with.
- `references/fixes.md`: ready-to-adapt walls. Read when asked to fix something.
