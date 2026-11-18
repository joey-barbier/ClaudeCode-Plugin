# Initialize the project memory

Only for a repository whose `.claude/memory/` lacks files (`memory: absent` or `partial`), and only from a base branch (`task_branch: no`, or `unknown` once the user has confirmed this branch is the project's main line): the five project files are shared, a task branch must not create them. Never in a workspace folder (several repositories, `kind: workspace`). Create the files without asking.

## Gather

1. **Name**: `package.json`, `Cargo.toml`, `pyproject.toml`, `Package.swift`, `*.xcodeproj`; fallback `basename "$(git rev-parse --show-toplevel)"`.
2. **Stack and layout**: config files found with Glob (`*.config.*`, `Makefile`, `Dockerfile`, `*.toml`), `ls` of the top level, the README, `CLAUDE.md`.
3. **State**: `git log --oneline -15`, `git branch -a --sort=-committerdate | head`, open pull requests if `gh` is available.
4. **Commands**: only those written in the README, `CLAUDE.md`, `package.json` scripts or a Makefile. Do not guess one.

## Write

| File | Content |
|---|---|
| `PROJECT_STATE.md` | Phase, what exists, what is in progress, known issues. Under 200 lines. |
| `ARCHITECTURE.md` | Stack, top-level structure, key components and how they talk. |
| `DECISIONS.md` | Conventions visible in the code or stated in docs, as `| Decision | Rationale | Date |` rows. |
| `NEXT_STEPS.md` | Immediate, Short term, Backlog, from the README, issues and recent commits. |
| `COMMANDS.md` | The commands gathered above, with what each one proves. |

Mark every unknown `TBD` rather than filling it. End `PROJECT_STATE.md` with:

```
<!-- memory-saved: <git rev-parse --short HEAD> <YYYY-MM-DD> -->
```

If some of the five files already exist, create only the missing ones and leave the others untouched.

## Confirm

```
Memory initialized at .claude/memory/
Created: [files]
Next: /horka-memory:horka-memory-save after significant work, /horka-memory:horka-memory-close before merging a task branch.
```

Commit the new files with the project's commit convention if `.claude/memory` is not git-ignored, no attribution trailer; never push without the user's go:

```bash
git add .claude/memory
git commit -m "add(memory) - project memory" -- .claude/memory
```
