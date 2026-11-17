---
name: horka-memory-close
description: Close a task's memory just before its branch is merged. Promotes what must last (decisions, architecture changes, proven commands, the new project state) from the in-progress task folder into the durable project memory, then deletes the task folder so the base branch never contains it; can also install the CI check that enforces this. Use when the user says "close the task", "ready to merge", "before merge", "wrap up this branch", "clôture la tâche", "on fusionne", when a pull request leaves draft, or when a check reports task memory left in progress. Do NOT use to save progress mid-task (horka-memory-save) or to read context (horka-memory-restore).
allowed-tools: Read, Write, Edit, Bash, AskUserQuestion
---

# Close a Task Before Merge

## Scope

Moves lasting knowledge from `.claude/memory/in-progress/<task-id>/` into the five project files, deletes the task folder, commits. Does NOT merge, push, rebase, or modify source code.

Why a separate step: during the task, saves stay inside the task folder so two branches never edit the same memory file. The project files are touched once per task, here, right before the merge.

## Step 1: Measure

Run `bash "<this skill's base directory>/../../scripts/memory-status.sh"`.

| Status says | Do |
|---|---|
| `task_branch: yes`, `task_file: present` | Step 2. |
| `task_branch: yes`, `task_file: absent` | No task file to promote from. Say so, then do Step 3 from what git shows (`git log <default_branch>..HEAD`) so the project state still records what the branch delivered; Step 4 has no folder to delete. |
| `task_branch: no` with `leftover_tasks` | A task folder was merged by mistake. Close each one listed, from this branch, with Steps 3 to 5. |
| `task_branch: no`, nothing left over | Say there is no task to close and stop. |

## Step 2: Check the branch is up to date

Closing edits shared files, so do it on top of the current base to keep the conflict window short: `git fetch`, then `git rev-list --count HEAD..origin/<default_branch>`. If the count is not 0, tell the user and let them bring the base in first. Do not rebase on your own.

## Step 3: Promote what lasts

Read `TASK.md` and the task's `DECISIONS.md`. For each item ask: will this still matter once the branch is gone?

| From the task | Goes to | When |
|---|---|---|
| A decision that constrains future work | `DECISIONS.md`, one row with rationale and date | Always |
| A pitfall someone else would hit again | `DECISIONS.md` or the known issues of `PROJECT_STATE.md` | If not specific to this task |
| New module, changed data flow, new dependency | `ARCHITECTURE.md` | If the structure changed |
| A command proven to work | `COMMANDS.md` | If not already there |
| What the task delivered | `PROJECT_STATE.md`, one or two lines under completed | Always |
| Follow-ups the task did not do | `NEXT_STEPS.md` | Always, or say there are none |

Leave behind the stopping points, the step-by-step log and the dead ends that only explain this branch: the branch history and the pull request keep them.

Use Edit to add rows and lines; do not reorder or rewrite existing content (another branch may be closing too). Keep `PROJECT_STATE.md` under 200 lines by dropping its oldest completed items. Set its marker to `<!-- memory-saved: <head> <today> -->`.

## Step 4: Delete the task folder and commit

```bash
git rm -r .claude/memory/in-progress/<task_id>
git add .claude/memory
git commit -m "update(memory) - close task <task_id>"   # use the project's commit convention when CLAUDE.md gives one
```

This must be the last commit of the branch before the merge. Never push without the user's go.

## Step 5: Report

```
## Task Closed

**Task**: <task_id>
**Promoted**: [file: what was added]
**Dropped**: [what stayed in the branch history only]
**Follow-ups**: [added to NEXT_STEPS, or none]
**Commit**: [hash], [pushed | not pushed]
```

## Example

Task `feature-export-csv`. TASK.md lists: exporter done, decision "stream rows instead of building the file in memory (orders can exceed 200k rows)", pitfall "Excel needs a BOM to read UTF-8", dead end "tried the csv-writer package, dropped", follow-up "export for invoices".

Result: `DECISIONS.md` gains two rows (streaming, BOM); `PROJECT_STATE.md` gains "CSV export of orders"; `NEXT_STEPS.md` gains "CSV export for invoices"; the dead end is dropped; the folder is deleted; one commit `update(memory) - close task feature-export-csv`.

## The CI check

A task folder that reaches the base branch means this step was skipped. When the user asks for the guard, or the project has CI and no such check, follow `references/ci-check.md`: it fails a pull request that still contains a task folder. Write the workflow step only after the user agrees.

## Error handling

- **Status script cannot run**: `git branch --show-current` and `ls .claude/memory/in-progress/`; the task id is the branch name with `/` replaced by `-`.
- **Task folder name does not match the branch** (branch renamed): list the folders, ask which one belongs to this branch, close that one.
- **Conflict in a memory file at merge time**: keep both sides' rows, then fix the marker.
- **Unsure whether an item lasts**: keep it as one short row in `DECISIONS.md` rather than lose it.

## Rules

1. Never invent: promote only what the task files and git show.
2. Never delete a task folder before its content has been read and sorted.
