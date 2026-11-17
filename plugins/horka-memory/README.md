# horka-memory

Project memory that lives in the repository, so a fresh clone is enough to know where the work stands: across sessions, and across people who take over each other's tasks.

## Two zones

```
.claude/memory/
  PROJECT_STATE.md  ARCHITECTURE.md  DECISIONS.md  NEXT_STEPS.md  COMMANDS.md   project: durable, changes on the base branch
  in-progress/<task-id>/TASK.md  (+ DECISIONS.md)                               task: lives on its branch, removed before the merge
```

The task id is the branch name with `/` replaced by `-` (a short hash is added when the name holds characters a folder name should not; `feature/login` and `feature-login` share one id).

## Skills

| Skill | When | What it does |
|---|---|---|
| `/horka-memory:horka-memory-restore` | Start of a session, taking over a branch | Reads both zones, says how many commits each is behind the code, checks a task file against git and its own check command before trusting it. Initializes the project memory in a repository that has none (never in a folder of several repositories). |
| `/horka-memory:horka-memory-save` | After a milestone, before stopping | On a base branch updates the project files. On a task branch writes only the task file: goal, exact stopping point, next steps, how to verify. Commits the memory paths only, says what is not pushed. |
| `/horka-memory:horka-memory-close` | The branch is approved for merge | Reruns the task's check, promotes what must last into the project files, deletes the task folder, commits. |

## Hooks

| Event | What it says |
|---|---|
| SessionStart | Which memory exists and how far behind the code it is; the task file of the current branch; a folder of several repositories is not a project. |
| Stop | One line to the user when work would be lost if nobody came back: task file behind, commits not pushed, branch not on the remote, uncommitted files. At most once per kind of finding every 30 minutes per session. |
| PreCompact | Which memory file is behind before the conversation is summarized. |

Freshness is measured in commits that changed something other than the memory itself, merge commits excluded. A shallow clone cannot be measured and is reported as unknown.

## Settings

Set these in the `env` of your Claude Code settings so the hooks see them.

| Variable | Default | Meaning |
|---|---|---|
| `HORKA_MEMORY_BASE_BRANCHES` | `main master develop dev integration staging trunk` | Branches that are never a task. The remote's default branch, `release/*` and a repository's only branch are always bases. Add yours, e.g. `main production`. |
| `HORKA_MEMORY_STALE_COMMITS` | `20` | Project memory is called stale from this many commits behind. |
| `HORKA_MEMORY_TASK_STALE_COMMITS` | `3` | Same for a task file. |
| `HORKA_MEMORY_REMIND_SECONDS` | `1800` | Delay before the stop check repeats the same finding. |

## Keeping task memory off the base branch

`scripts/check-in-progress.sh` fails when anything is left in `.claude/memory/in-progress/`. The CI step to add to a project is in `skills/horka-memory-close/references/ci-check.md`. To let two branches add lines to the same memory file without a merge conflict, add `.claude/memory/*.md merge=union` to `.gitattributes`.

## Tests

```bash
bash plugins/horka-memory/tests/run.sh
```

Throwaway repositories in a temp folder, no network. Needs git, and jq or python3.
