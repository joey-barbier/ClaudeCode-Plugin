---
name: horka-memory-save
description: Save the session's progress to the project memory so anyone can continue from the repository alone. On a base branch it updates PROJECT_STATE, DECISIONS, NEXT_STEPS, ARCHITECTURE, COMMANDS; on a task branch it writes the in-progress task file (goal, exact stopping point, next steps, how to verify) and leaves the project files alone. Use when the user says "save progress", "update memory", "save state", "checkpoint", "handoff", "hand this over", "passation", "je m'arrête là", before ending a session, before a context compaction, and proactively after a milestone (once per completed step, decision taken or bug fixed). Do NOT use to read context (horka-memory-restore) or to finish a task before its merge (horka-memory-close).
allowed-tools: Read, Write, Edit, Bash
---

# Save Session Progress

## Scope

Writes memory files and commits them. Does NOT modify source code, push, or create the project memory from nothing (`horka-memory-restore` does that). Requires the plugin's `scripts/` folder (two levels above this skill).

The test of a good save: a clone of the repository, with nothing else, is enough for someone who never saw this session to know where the work stands and what to do next. People stop without warning, so save at each milestone, not at the end of the day.

## Rules

1. Never invent: only what the session, git and the commands you ran show. An unknown is written as unknown; an intention nobody stated is not written as fact.
2. On a task branch, never edit the five project files.
3. Deduplicate before adding; date every decision.
4. Never push without the user's go.

## Step 1: Measure

Run `bash "<this skill's base directory>/../../scripts/memory-status.sh"`. Below, `<head>` and `<today>` are its `head` and `today` values, `<task-id>` its `task_id` (never built by hand) and `<task_dir>` its `task_dir`.

| Status says | Do |
|---|---|
| `kind: workspace` | Stop: this folder is not a project. Save from the repository the work was done in. |
| `memory: absent` | Say "No memory files found. Run `/horka-memory:horka-memory-restore` first to initialize." and stop. |
| `task_branch: no` | Step 2 (project memory). |
| `task_branch: yes` | Step 3 (task file). |
| `task_file: closed` | The task was closed and waits for its merge. Review fixes need no task file: if they change what was promoted, correct the project files directly (they are this branch's until the merge) and say so. If the task is reopened, create `TASK.md` again (Step 3). |
| `task_branch: detached` | Stop: no branch is checked out. Ask the user to return to their branch. |
| `task_branch: unknown` | No base branch in this clone to compare with. Ask the user whether this branch is a task (Step 3) or the project's main line (Step 2); do not guess. |

What happened since the last save: `git log --oneline <saved commit>..HEAD`, `git status`, `git diff --stat <saved commit>..HEAD` (no marker: the last 20 commits). Run the project's check command (tests) so the state you write is measured. Add, from the conversation: decisions with their reason, approaches tried and dropped, items waiting on a person.

## Step 2: Base branch, project memory

Use Edit for precise changes; do not rewrite whole files.

- **PROJECT_STATE.md**: current phase, what was completed, known issues, blockers. Keep it under 200 lines: past that, drop the oldest completed items (git history keeps them).
- **DECISIONS.md**: one row per new decision, `| Decision | Rationale | YYYY-MM-DD |`.
- **NEXT_STEPS.md**: reorder by current priority (Immediate, Short term, Backlog).
- **ARCHITECTURE.md**: only if modules, data flow or dependencies changed.
- **COMMANDS.md**: only commands proven to work in this session.

Replace the marker ending `PROJECT_STATE.md` with `<!-- memory-saved: <head> <today> -->`.

## Step 3: Task branch, task file only

Everything goes in `<task_dir>` (`.claude/memory/in-progress/<task-id>/`); two people saving on two branches must never edit the same file.

- **TASK.md**: create it from `references/task-template.md`, or update it. Every section must be true now. "Stopped at" names the exact point: file and function being edited, the failing test, the command that errors and its message.
- **The base**: `TASK.md` must hold the line `<!-- task-base: <branch> -->` on a line of its own, where `<branch>` is the branch this task will be merged into, without `origin/`. Nothing guesses it: when the status says `base: unknown`, write the remote's default branch (`default_branch`) if the session gave no sign of another target, and say in the report which branch you wrote so the user can correct it; if `default_branch` is `unknown` or another target was mentioned, ask. Never change a recorded base unless the user says the target changed. The skills use it to check that the branch is up to date and whether a check command may run unasked; the hooks do not depend on it.
- **DECISIONS.md** (same folder), only when there is a decision to record: decisions taken for this task, with rationale and date. `horka-memory-close` promotes the lasting ones. No empty placeholder file.
- Do not write the push state into the file (it is wrong after the next commit); it goes in the report.

Replace the marker ending `TASK.md` with `<!-- memory-saved: <head> <today> -->`.

## Step 4: Commit, and say what is not pushed

If `git check-ignore -q .claude/memory` exits non-zero (the memory is not ignored), commit the memory paths only, whatever else is staged:

```bash
git add .claude/memory
git commit -m "update(memory) - <what the save records>" -- .claude/memory   # use the project's commit convention when CLAUDE.md gives one
```

No attribution trailer in the message. Then run the status script again. If `unpushed` is not `0` (a count, or `not-on-remote`), list every local-only commit by hash and subject (`git log --oneline origin/<branch>..HEAD` when the branch is on the remote, `git log --oneline HEAD --not --remotes` when it is not): the memory commit and each work commit. If `uncommitted` is not `0`, name the files. Say it plainly: work that is not on the remote cannot be taken over by anyone else.

## Step 5: Report

```
## Memory Saved

**Where**: [project memory | task <task-id> on <branch>]
**Files**: [file: what changed]
**Commit**: [hash], [pushed | NOT pushed: each local-only commit, hash and subject]
**Stopped at**: [one line]
**Next**: [the first thing the next person does]
```

## Example

Branch `feature/export-csv`, status `task_file: present`, `task_behind: 3`. Since the marker: two commits adding the exporter, one failing test.

Result: TASK.md "Done" gains "CSV exporter for orders (a1b2c3d, d4e5f6a)", "Stopped at" becomes "`test_export_escapes_quotes` fails: quotes inside a field are not doubled, in `exporter.ts` `escapeField`", "How to verify" keeps `npm test -- export` with "expected now: 41 pass, 1 fails". Marker updated, one commit `update(memory) - export task: exporter done, quote escaping open`, report says "NOT pushed: 4 commits local only".

## Error handling

- **Status script cannot run**: `git branch --show-current`, `git rev-parse --short HEAD`, and the marker line of the file you are about to update.
- **Git not available**: save from the conversation only, write the date without a commit in the marker's place, and note "git unavailable" in the report.
- **Memory is git-ignored**: write the files, skip the commit, and say they stay on this machine only.
- **Write permission denied**: show the proposed content and let the user apply it.
- **Nothing changed since the marker and nothing new in the conversation**: say "Nothing to save" and write nothing.
