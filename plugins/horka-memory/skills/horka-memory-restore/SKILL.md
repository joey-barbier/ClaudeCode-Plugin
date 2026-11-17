---
name: horka-memory-restore
description: Restore project context from the memory files, or initialize them when a repository has none. Reads the durable project memory and, on a task branch, the in-progress task file left by whoever worked there last, and reports how far each is behind the code instead of trusting it. Use when a session starts working on a project, when taking over a branch or a task someone else started, or when the user says "where were we", "resume", "catch up", "refresh context", "init memory", "what were we doing", "pick up this task", "take over this branch", "reprendre la tâche", "où on en est". Do NOT use to write progress (horka-memory-save) or to finish a task before its merge (horka-memory-close).
allowed-tools: Read, Write, Glob, Bash, AskUserQuestion
---

# Restore Project Context

## Scope

Reads memory files, and creates the project memory when a repository has none. Does NOT modify source code, decide architecture, or delete memory files.

## The two zones

```
.claude/memory/
  PROJECT_STATE.md  ARCHITECTURE.md  DECISIONS.md  NEXT_STEPS.md  COMMANDS.md   project: durable, changes on the base branch
  in-progress/<task-id>/TASK.md  (+ DECISIONS.md)                               task: lives on its branch, removed before the merge
```

`<task-id>` is the branch name with `/` replaced by `-`. A base branch (main, develop, integration...) has no task.

## Step 1: Measure before reading

Run `bash "<this skill's base directory>/../../scripts/memory-status.sh"` and work from its output.

| Status says | Do |
|---|---|
| `kind: workspace` | Stop: this folder holds several repositories and is not a project. Create nothing here. Name the repositories that have memory and ask the user which one the work is about. |
| `memory: absent` in a repo | Initialize: follow `references/initialize.md`. |
| `memory: present` | Step 2. |

## Step 2: Restore, and say how fresh it is

Read `PROJECT_STATE.md`, `NEXT_STEPS.md`, `DECISIONS.md`, then `ARCHITECTURE.md` and `COMMANDS.md` when the task needs them. Also read `CLAUDE.md`.

- `stale: yes`, or a file still an unfilled template: say so in the first line of the summary, with the number of commits behind. The code wins: read `git log --oneline -30` and the files the task touches, report what the memory gets wrong, propose `horka-memory-save` to refresh it. Never present stale memory as the current state.
- `leftover_tasks`: a task folder was merged by mistake. Report it and propose `horka-memory-close`.

## Step 3: On a task branch, take the task over

If `task_file: present`, read `in-progress/<task-id>/TASK.md` and its `DECISIONS.md`. Whoever wrote it may have been interrupted without warning, so verify instead of trusting:

1. `git log --oneline <task_saved commit>..HEAD` shows what happened after the file was written; `git status` shows work never committed.
2. Run the command the file gives under "How to verify" and compare with the result it announces.
3. State any gap between the file and what you measured, then continue from the real stopping point.

If `task_file: absent`, say so and rebuild the state from `git log <default_branch>..HEAD` and the pull request (`gh pr view`); `horka-memory-save` will write the file.

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
**Verified**: [check command] -> [result, and whether it matches the file]
**Unpushed / uncommitted**: ...
```

End with what you will do next, or the one question that blocks.

## Example

Status: `memory: present`, `behind: 4`, `stale: no`, `task_branch: yes`, `task_file: present`, `task_behind: 2`, `unpushed: 0` on `fix/refund-rounding`. TASK.md says "212 tests pass, 1 fails: test_refund_rounding".

Result: read the five files and TASK.md, run `npm test`, get 213 passing. Report: "Memory fresh (4 commits behind). Task file is 2 commits behind: the failing test it names now passes (commit a1b2c3d fixed it). Remaining from its Next list: step 2, the migration."

## Error handling

- **Status script cannot run**: get the facts by hand: `git rev-parse --show-toplevel`, `git branch --show-current`, the `<!-- memory-saved: <commit> <date> -->` line ending `PROJECT_STATE.md`, then `git rev-list --count <commit>..HEAD -- . ':(exclude).claude/memory'`.
- **Not a git repository and not a workspace**: restore or initialize from files only, and say freshness is unknown.
- **Marker commit unknown** (history rewritten): the script falls back to the last commit that touched the file; say the count is approximate.
- **`.claude/memory/` not writable**: show the content and let the user create the files.

## Rules

1. Never invent: only what the files, git and the commands you ran say.
2. Code wins over memory; a contradiction is reported, then fixed in the memory by `horka-memory-save`.
3. A task file is a claim until its check command has been rerun.
