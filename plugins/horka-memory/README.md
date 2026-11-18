# horka-memory

Project memory that lives in the repository, so a fresh clone is enough to know where the work stands: across sessions, and across people who take over each other's tasks.

## Two zones

```
.claude/memory/
  PROJECT_STATE.md  ARCHITECTURE.md  DECISIONS.md  NEXT_STEPS.md  COMMANDS.md   project: durable, changes on the base branch
  in-progress/<task-id>/TASK.md  (+ DECISIONS.md)                               task: lives on its branch, removed before the merge
```

No hook guesses which base a task branch comes from. A branch's own work is the commits that are on no base branch; for a branch that is not on the remote, the commits made since it was created on this machine are counted too, and the larger number is kept; a task file is behind by the branch's own commits since it was written. The first save writes the branch the task merges into in `TASK.md` (`<!-- task-base: main -->`); only the skills use it, to check that the branch is up to date before a close, and they ask when it is missing.

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

Freshness is measured in commits that changed something other than the memory itself, merge commits excluded, and stops counting at 1,000. A shallow clone cannot be measured and is reported as unknown. Each hook has a 10 second timeout.

## Settings

Set these in the `env` of your Claude Code settings so the hooks see them.

| Variable | Default | Meaning |
|---|---|---|
| `HORKA_MEMORY_BASE_BRANCHES` | `main master develop dev integration staging trunk` | Branches that are never a task. The remote's default branch and `release/*` are always bases. Add yours, e.g. `main production`. A branch with no base to compare with (single-branch clone, a project with one line of work) is reported as `unknown` and nothing is assumed about a task. |
| `HORKA_MEMORY_STALE_COMMITS` | `20` | Project memory is called stale from this many commits behind. |
| `HORKA_MEMORY_TASK_STALE_COMMITS` | `3` | Same for a task file. |
| `HORKA_MEMORY_REMIND_SECONDS` | `1800` | Delay before the stop check repeats the same finding. |

## Keeping task memory off the base branch

`scripts/check-in-progress.sh` fails when anything is left in `.claude/memory/in-progress/`. The CI step to add to a project is in `skills/horka-memory-close/references/ci-check.md`. Two tasks closed in parallel can conflict when both add a row to the decisions table; `.claude/memory/DECISIONS.md merge=union` in `.gitattributes` avoids it (not for the other files: a line corrected on one side would be kept twice).

## Tests

```bash
bash plugins/horka-memory/tests/run.sh
```

Throwaway repositories in a temp folder, no network. Needs git, and jq or python3.
