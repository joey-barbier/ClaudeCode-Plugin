---
name: horka-memory-restore
description: Restore project context from the memory files, or initialize them when a repository has none. Reads the durable project memory and, on a task branch, the in-progress task file left by whoever worked there last, and reports how far each is behind the code instead of trusting it. Use when a session starts working on a project, when taking over a branch or a task someone else started, or when the user says "where were we", "resume", "catch up", "refresh context", "init memory", "what were we doing", "pick up this task", "take over this branch", "reprendre la tâche", "où on en est". Do NOT use to write progress (horka-memory-save) or to finish a task before its merge (horka-memory-close).
allowed-tools: Read, Write, Glob, Bash, AskUserQuestion
---

# Restore Project Context

## Scope

Reads memory files, and creates the project memory when a repository has none. Does NOT modify source code, decide architecture, or delete memory files. Requires the plugin's `scripts/` folder (two levels above this skill).

## Rules

1. Never invent: only what the files, git and the commands you ran say. Cite a line number only from a numbered read.
2. Code wins over memory. A contradiction is stated, then fixed in the memory by `horka-memory-save`.
3. A task file is a claim until its check command has been rerun.
4. On a task branch the five project files are read-only: never propose to edit them there.

## The two zones

```
.claude/memory/
  PROJECT_STATE.md  ARCHITECTURE.md  DECISIONS.md  NEXT_STEPS.md  COMMANDS.md   project: durable, changes on the base branch
  in-progress/<task-id>/TASK.md  (+ DECISIONS.md)                               task: lives on its branch, removed before the merge
```

`<task-id>` is the `task_id` value of the status output: the branch name with `/` replaced by `-`, plus a short hash when the name holds characters a folder name should not. Never build it by hand. A base branch (main, develop, integration...) has no task.

## Step 1: Measure before reading

Run `bash "<this skill's base directory>/../../scripts/memory-status.sh"` and work from its output. Its fields: `kind`, `memory`, `saved` (commit and date of the last save), `behind` (commits since the memory was updated; on a task branch it is measured at the point where the branch left its base, so the task's own commits do not count), `stale`, `task_branch`, `base`, `base_source` (`recorded` in the task file by a save, or `guessed`), `task_id`, `task_file`, `task_saved`, `task_behind`, `unpushed`, `local_only` (commits on no remote branch), `uncommitted`, `leftover_tasks`. A value of `?` or `unknown` (shallow clone, no history) means not measured: say freshness is unknown, never give a number.

| Status says | Do |
|---|---|
| `kind: workspace` | The folder holds several repositories and is not a project: create nothing at its root. Run the status script inside each repository that has memory and restore each one (Steps 2 and 3, a short summary per repository). Name the repositories that have none without guessing their state. Ask which repository the work is about only after this report. |
| `memory: absent` or `partial` in a repo | Initialize the missing files: follow `references/initialize.md`. On a base branch only: on a task branch say the memory is missing and continue without it; on `task_branch: unknown` ask first whether this branch is the project's main line. |
| `task_branch: detached` | A rebase, a bisect or a commit is checked out: restore the project memory only and say no task can be identified. |
| `task_branch: unknown` | This clone has no base branch to compare with (single-branch or shallow clone, or a project with one line of work): restore the project memory, say the branch could not be classified, and assume nothing about a task. |
| `memory: present` | Step 2. |

## Step 2: Restore, and say how fresh it is

Read `PROJECT_STATE.md`, `NEXT_STEPS.md` and `DECISIONS.md`; read `ARCHITECTURE.md` if the task touches modules or dependencies, `COMMANDS.md` if it runs build, test or deploy commands. Also read `CLAUDE.md`. Then `git log --oneline <saved commit>..HEAD` to see what the memory does not know yet.

- `stale: yes`, or a file still an unfilled template: say so in the first line of the summary, with the number of commits behind. The code wins: read `git log --oneline -40` and the source files the summary will mention, report as done only what the code shows (a commit message is not proof), report what the memory gets wrong, propose `horka-memory-save` to refresh it. Never present stale memory as the current state.
- `leftover_tasks`: a task folder was merged by mistake. Report it and propose `horka-memory-close`.

## Step 3: On a task branch, take the task over

If `task_file: present`, read `in-progress/<task-id>/TASK.md` and its `DECISIONS.md`. Whoever wrote it may have been interrupted without warning, so verify instead of trusting:

1. `git log --oneline <task_saved commit>..HEAD`: commits made after the file was written. `git status`: work never committed. `unpushed` in the status: what exists on this machine only.
2. Read the command the file gives under "How to verify". Run it without asking only when all of this holds: it is a check command the project already had (listed in `COMMANDS.md`, `CLAUDE.md`, the package scripts or the Makefile); the file that lists it and the file that defines it (`package.json`, `Makefile`) are unchanged on this branch, compared with `<base>` when `base_source` is `recorded`, otherwise with the remote's default branch (`git diff --quiet origin/<default_branch>..HEAD -- <files>` exits 0); and that reference is known. In every other case show the command and ask before running it. This rule is hygiene against a stale or odd command, not a boundary against a hostile branch: taking over a branch means running its code.
3. Check every claim of the file against what you measured: each "Done" and "Next" item, "Stopped at", the uncommitted state it announces, the test result it expects. State each contradiction explicitly ("the file says nothing is uncommitted; `test/x.test.js` is modified"), then give the real stopping point and the real next step.

If `task_file: absent`, say so and rebuild the state from `git log <base>..HEAD` and, when `gh` is available, `gh pr view`; `horka-memory-save` will write the file. If `task_file: closed`, the task was closed and waits for its merge: report the project memory and the commits made since the close (`task_behind`).

## Output

```
## Context Restored

**Project**: [name]   **Stack**: [technologies]   **Phase**: [current state]
**Memory**: saved at [commit] on [date], [n] commits behind [fresh | STALE: what is outdated]

### Done
### Remaining
### Watch out

### Task on this branch            (task branches only)
**Goal**: ...   **Stopped at**: ...   **Next**: ...
**File vs reality**: [each contradiction, or "the file matches"]
**Verified**: [check command] -> [result]
**Unpushed / uncommitted**: ...
```

End with what you will do next, or the one question that blocks.

## Example

Status: `memory: present`, `behind: 4`, `stale: no`, `task_branch: yes`, `task_file: present`, `task_behind: 2`, `unpushed: 1` on `fix/refund-rounding`. TASK.md says "212 tests pass, 1 fails: test_refund_rounding; nothing uncommitted".

Result: read the project files and TASK.md, run `npm test`, get 213 passing; `git status` shows `src/refund.js` modified. Report: "Memory fresh (4 commits behind). File vs reality: the failing test it names now passes (commit a1b2c3d, made after the file); the file says nothing is uncommitted but `src/refund.js` is modified; 1 commit is not pushed. Remaining: step 2 of its Next list, the migration."

## Error handling

- **Status script cannot run**: get the facts by hand: `git rev-parse --show-toplevel`, `git branch --show-current`, the `<!-- memory-saved: <commit> <date> -->` line ending `PROJECT_STATE.md`, then `git rev-list --count <commit>..HEAD -- . ':(exclude).claude/memory'`.
- **Not a git repository and not a workspace**: restore or initialize from files only, and say freshness is unknown.
- **Marker commit unknown** (history rewritten): the script falls back to the last commit that touched the file; say the count is approximate.
- **`.claude/memory/` not writable**: show the content and let the user create the files.
