# horka-harness-audit

**What actually holds your rules?** An audit of how you develop with AI agents: two or three questions, a scan of about 30 seconds that edits nothing, then one HTML page, opened at the end and read in two minutes: a level from 0 to 3 on three separate axes, what holds, what does not, and the actions to take, cheapest first.

```bash
claude plugin install horka-harness-audit
```

## Why

An agent is a model plus a harness: what it sees, what it can touch, what it remembers, what counts as done, what it may not do. Most setups are well designed and weakly enforced. "Never push to main" in a CLAUDE.md is a wish; a protected branch or a hook that reads the whole command is a wall. The owner rarely sees the gap, because every rule is written down somewhere.

The skill asks one question of every rule and every check: **what holds it?** Nothing, a sentence, a script someone must remember to run, a hook, CI that reports, or CI and platform rules that block.

## What you get

| | |
|---|---|
| Three levels, 0 to 3 | **Design** (what exists on paper), **detection** (what runs and sees problems), **enforcement** (what can say no by itself). Kept apart, because a nightly suite that goes red is detection working and enforcement missing. |
| One page, no prose | The audit is written as a small JSON file and rendered by `scripts/render.py` into a single self-contained HTML page. Every field has a maximum length: the script refuses a report that is too long to scan and names the field to shorten. The table of tested commands comes straight from the scan. |
| Twelve criteria | Definition of done, map, tools, state, evidence, separate verifier, permissions, caps, recovery, lessons turned into checks, harness size, measuring the harness. One line each, with the evidence. |
| Missing connections | Three to six, the free ones first: a `needs:` on the deploy job, a guard that reads the whole command, an ask or deny rule, a cap on headless calls. |
| Chosen debt | In a v1 or an experiment, gaps are listed as debt you chose, each with the event that should trigger repayment. Three things are never debt: an unguarded push to the default branch, readable secrets, uncapped unattended agents. |

## The scan

`scripts/scan.py` is plain Python (standard library only). It never pushes, fetches or edits a repository or a setting, and the skill writes only its own files, in a dated folder under `~/.claude/harness-audit/`.

What it does run, besides `git` and `gh` reads: **your own PreToolUse hooks**, once for each of 13 fabricated risky commands, from an empty temporary folder. That is how it tests your guards. The risky commands themselves are never run, but a hook that writes a log or sends a notification will do so 13 times; `--no-hook-probe` skips this. Hooks defined inside a scanned repository are listed and not run, because their command line comes from that repository, and your own hooks are never run from inside a scanned repository; `--probe-repo-hooks` lifts both, for a repository you trust.

The scan names hook scripts and never quotes their command line. The lines it does quote from your files (rules written as sentences, permission rules) go through a mask for credential shapes. That mask is best effort: it knows shapes, not secrets. Read the output before pasting it anywhere public.

For the global Claude Code config and each repository it reports:

- permission rules (allow, ask, deny), broad allow rules, hooks by event, rules written as sentences;
- a probe: a set of risky commands (push to the default branch, force push in several forms including `git -C <dir> push --force`, hard reset, PR merge, recursive delete, reading an env file) passed as text to the rules and as input to your PreToolUse hooks; it prints which ones nothing stops, and says so when a hook could not be judged (not run, no answer, filter not understood);
- CI: triggers of each workflow, whether tests run on every pull request, whether each deploy job waits for a test job, jobs without timeout;
- GitHub, through `gh` when available: branch protection, rulesets, environment rules, merged pull requests with a failing check, run history with red streaks;
- headless agent calls with no turn or budget cap, state files and how far behind they are, worktrees, agents and skills never launched in the last 30 days.

Tracked files are read at `origin/<default branch>`, not in the working tree: a stale checkout tells a false story.

```bash
python3 skills/horka-harness-audit/scripts/scan.py --repo ~/code/my-api --repo ~/code/my-front
```

## Also inside

- `references/sources.md`: a digest of the primary sources on harness engineering (OpenAI, LangChain, Anthropic engineering posts, Claude Code documentation), each figure with its URL, date and status, and the three places where popular advice departs from those sources.
- `references/fixes.md`: walls to adapt, cheapest first.
- `references/report-schema.md` and `assets/report.tpl.html`: the fields of the report and the page template.
- `evals/`: three test requests and a script that builds an offline fixture with planted facts.

## Limits

- The global part reads Claude Code files. For another agent tool, the repository, CI and platform parts apply unchanged.
- The rule matching in the probe is an approximation of the real matcher.
- The probe waits 8 seconds for a hook where Claude Code waits much longer: a slow hook is reported as "no answer", not as a pass.
- The fixed labels of the page exist in English and French; a report in another language gets English labels around its text.
- It informs, it does not install: version 1 ships no ready-made push guard. `references/fixes.md` lists the command forms a guard has to stop, so that you can test the one you write or adopt.
- CI parsing covers GitHub Actions; other CI systems are reported as present and not parsed.
- The scan shows that specs, reviews and lessons exist, not that they are good: the skill reads a sample by hand.
