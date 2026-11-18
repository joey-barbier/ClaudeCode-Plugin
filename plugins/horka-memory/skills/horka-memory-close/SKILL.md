---
name: horka-memory-close
description: Close a task's memory just before its branch is merged. Promotes what must last (decisions, architecture changes, proven commands, the new project state) from the in-progress task folder into the durable project memory, then deletes the task folder so the base branch never contains it; can also install the CI check that enforces this. Use when the user says "close the task", "ready to merge", "before merge", "wrap up this branch", "clôture la tâche", "on fusionne", when a branch has been approved for merge, or when a check reports task memory left in progress. Do NOT use to save progress mid-task (horka-memory-save) or to read context (horka-memory-restore).
allowed-tools: Read, Write, Edit, Bash, AskUserQuestion
---

# Close a Task Before Merge

## Scope

Moves lasting knowledge from `.claude/memory/in-progress/<task-id>/` into the five project files, deletes the task folder, commits. Does NOT merge, push, rebase, or modify source code. Requires the plugin's `scripts/` folder (two levels above this skill).

Why a separate step: during the task, saves stay inside the task folder so two branches never edit the same memory file. The project files are touched once per task, here, right before the merge.

## Rules

1. Never invent: promote only what the task files and git show. Before writing a claim about the code into the project memory, read the code it describes.
2. Never delete a task folder before its content has been read and sorted.
3. A task that fails its own check is not closed.
4. Never push, merge or rebase without the user's go.

## Step 1: Measure

Run `bash "<this skill's base directory>/../../scripts/memory-status.sh"`. Below, `<task-id>`, `<task_dir>` and `<base>` are its `task_id`, `task_dir` and `base` values: never build them by hand.

| Status says | Do |
|---|---|
| `task_branch: yes`, `task_file: present` | Step 2. |
| `task_branch: yes`, `task_file: absent` | No task file to promote from. Say so, do Step 2, then Step 3 from what git shows (`git log <base>..HEAD`) so the project state still records what the branch delivered; Step 4 has no folder to delete. |
| `task_file: closed` | Already closed. If commits were made since (`task_behind` above 0), check whether they change what was promoted and correct the project files; otherwise say there is nothing to do. |
| `task_branch: detached` | Stop: no branch is checked out. |
| `task_branch: no` with `leftover_tasks` | A task folder was merged by mistake. Tell the user which folders, and close each one they confirm, from this branch: skip Step 2 (there is no branch to compare), do Steps 3 to 5. |
| `task_branch: unknown` | No base branch in this clone to compare with: stop and ask the user; never treat a folder of `in-progress/` as a leftover here. |
| `task_branch: no`, nothing left over | Say there is no task to close and stop. |

## Step 2: Check the task is really ready

1. Read the command TASK.md gives under "How to verify" (no task file: the project's test command). Run it without asking only when it is a check command the project already had and the branch did not redefine: it is listed in `COMMANDS.md`, `CLAUDE.md`, the package scripts or the Makefile, and both that file and the file that defines the command (`package.json`, `Makefile`) are the same as on the base (`git diff --quiet <base>..HEAD -- <files>` exits 0). Otherwise, or when `base` is `unknown`, it is a shell command written by whoever pushed the branch: show it and ask before running it. If the check fails, stop: report the failure and do not close.
2. `git fetch`, then `git rev-list --count HEAD..<base>`. If the count is not 0, stop: tell the user the branch is behind and resume at Step 3 once they have brought the base in. Do not rebase or merge on your own. If `base` is `unknown` (this clone has no base branch), ask the user which branch it merges into and fetch it before counting.

## Step 3: Promote what lasts

Read `TASK.md` and the task's `DECISIONS.md`. For each item ask: will this still matter once the branch is gone?

| From the task | Goes to | When |
|---|---|---|
| A decision that constrains future work | `DECISIONS.md`, one row with rationale and date | Always |
| A pitfall someone else would hit again | `DECISIONS.md` or the known issues of `PROJECT_STATE.md` | If not specific to this task |
| New module, changed data flow, new dependency | `ARCHITECTURE.md` | If the structure changed |
| A command proven to work | `COMMANDS.md` | If not already there |
| What the task delivered | `PROJECT_STATE.md`, one or two lines under completed; lines the task made false ("not started") are corrected | Always |
| Follow-ups the task did not do | `NEXT_STEPS.md`; the item the task completed is removed from it | Always, or say there are none |
| Something tried and dropped (a dead end) | Nowhere: it stays in the branch history | Unless it sets a rule no existing decision states; then write the rule, not the story |

Not promoted either: stopping points and the step-by-step log. Before adding a row to `DECISIONS.md`, check that no existing row already says it.

Use Edit to add rows and lines; leave the rest of each file as it is (another branch may be closing too). The only deletions allowed: lines the task made false, and the oldest completed items of `PROJECT_STATE.md` when it exceeds 200 lines. Leave the `memory-saved` marker line of `PROJECT_STATE.md` exactly as it is: a close neither rewrites nor removes it (either would conflict with a save made on the base meanwhile, and freshness is read from the commit itself). Leave no placeholder behind (an emptied section says "Nothing planned", never an unchecked `- [ ] None`).

## Step 4: Delete the task folder and commit

Delete exactly the `<task_dir>` the status printed, a direct child of `.claude/memory/in-progress/`. If `task_id` is empty, `.` or `..`, stop and report it.

```bash
git rm -r -- <task_dir>
git add .claude/memory
git commit -m "update(memory) - close task <task-id>" -- .claude/memory   # use the project's commit convention when CLAUDE.md gives one
```

The pathspec keeps anything else the user staged out of this commit; no attribution trailer in the message. It should be the last commit of the branch before the merge; commits added later (review fixes) are fine, the hooks know the task is closed.

## Step 5: Report

```
## Task Closed

**Task**: <task-id>
**Verified**: [check command] -> [result]
**Promoted**: [file: what was added]
**Dropped**: [what stayed in the branch history only]
**Follow-ups**: [added to NEXT_STEPS, or none]
**Commit**: [hash], NOT pushed: the push and the merge are yours
```

## Example

Task `feature-export-csv`. TASK.md lists: exporter done, decision "stream rows instead of building the file in memory (orders can exceed 200k rows)", pitfall "Excel needs a BOM to read UTF-8", dead end "tried the csv-writer package, dropped: it adds a dependency", follow-up "export for invoices". The project already has the decision "no runtime dependency".

Result: `npm test` green; `DECISIONS.md` gains two rows (streaming, BOM); `PROJECT_STATE.md` gains "CSV export of orders" and loses "exports have not started"; `NEXT_STEPS.md` loses "CSV export of orders" and keeps "CSV export for invoices"; the csv-writer dead end is not promoted (the existing decision covers it); the folder is deleted; one commit `update(memory) - close task feature-export-csv`.

## The CI check

A task folder that reaches the base branch means this step was skipped. When the user asks for the guard, or the project has CI and no such check, follow `references/ci-check.md`: it fails a pull request that still contains a task folder. Write the workflow step only after the user agrees.

## Error handling

- **Status script cannot run**: `git branch --show-current` and `ls .claude/memory/in-progress/`; pick the folder that matches the branch name with `/` replaced by `-`, and ask if none matches exactly.
- **Task folder name does not match the branch** (branch renamed): list the folders, ask which one belongs to this branch, close that one.
- **The user reports a conflict in a memory file after merging**: keep both sides' rows. To avoid the next one in the decisions table, which only grows, you may propose the line `.claude/memory/DECISIONS.md merge=union` in `.gitattributes` and add it only if the user agrees. Not for `PROJECT_STATE.md` or `NEXT_STEPS.md`: a line corrected on one side would be kept twice.
- **Unsure whether an item lasts**: keep it as one short row in `DECISIONS.md` rather than lose it.
