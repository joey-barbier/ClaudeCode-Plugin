---
name: horka-memory-restore
description: Restore project context from memory files, or initialize them if none exist. This skill MUST run at the very start of any new session before doing anything else. If no memory files exist, create them automatically from project analysis. Trigger on "where were we", "resume", "catch up", "refresh context", "init memory", "what were we doing", "reload context", or any first message in a new conversation. Also trigger proactively when .claude/memory/ does not exist in the current project.
allowed-tools: Read, Write, Glob, Bash
---

# Restore Project Context

## Scope

Reads and creates memory files only. Does NOT:
- Modify project source code
- Make architectural decisions
- Delete existing memory files (only adds/updates)

## Step 1: Find memory files

Use Glob to search these locations in priority order:

1. `.claude/memory/**/*.md`
2. `docs-architecture/**/*.md`
3. `CLAUDE.md`, `.claude/CLAUDE.md`
4. `documentations/**/*.md`, `docs/**/*.md`
5. `README.md`

If ANY files found -> Step 2.
If NOTHING found -> Step 3.

## Step 2: Restore and summarize

Read each file found. Priority order:

| File | Why it matters |
|------|---------------|
| `PROJECT_STATE.md` | Current phase, blockers, recent completions |
| `ARCHITECTURE.md` | Tech stack, structure, key flows |
| `DECISIONS.md` | Conventions and rationale behind them |
| `NEXT_STEPS.md` | What to work on next |
| `COMMANDS.md` | Dev commands to avoid re-discovery |
| `CLAUDE.md` | Project-level instructions |

Output this structure:

```
## Context Restored

**Project**: [name from files or directory]
**Stack**: [technologies identified]
**Phase**: [current state]

### Done
- [completed items]

### Remaining
- [priority tasks]

### Watch Out
- [known bugs, blockers, important decisions]

---
What do we work on next?
```

## Step 3: Initialize memory

When no memory files exist, create them automatically -- do NOT ask for permission, just analyze and create.

1. **Project name**: Use Glob for `package.json`, `Cargo.toml`, `setup.py`, `*.xcodeproj`. Fallback: run `basename $(pwd)` via Bash.
2. **Tech stack**: Use Glob for config files (`*.config.*`, `Makefile`, `Dockerfile`, `*.toml`). Read the ones found.
3. **Current state**: Run `git log --oneline -10` via Bash. Read `README.md` if it exists.
4. **Structure**: Run `ls -la` via Bash for top-level layout.

Create `.claude/memory/` with these files:

- `PROJECT_STATE.md` -- Current phase, done/remaining, known issues
- `ARCHITECTURE.md` -- Tech stack, structure, key components
- `DECISIONS.md` -- Conventions and key choices
- `NEXT_STEPS.md` -- Prioritized roadmap
- `COMMANDS.md` -- Useful dev commands

Fill each with real data from project analysis. Mark unknowns as "TBD".

Confirm:

```
Memory initialized at .claude/memory/

Created: PROJECT_STATE.md, ARCHITECTURE.md, DECISIONS.md, NEXT_STEPS.md, COMMANDS.md

Use /horka-memory:horka-memory-restore to reload context in future sessions.
Use /horka-memory:horka-memory-save to save progress after significant work.
```

## Error Handling

- **No files found anywhere**: Proceed directly to Step 3 (initialize). Do not ask for confirmation.
- **Git not available**: Skip git analysis in Step 3, use file system and README only.
- **`.claude/memory/` not writable**: Show generated content in output and let user create files manually.
- **Partial memory files exist**: Only create the missing ones, never overwrite existing files.

## Rules

1. Never invent information -- only use what's in actual files or project analysis
2. If some memory files already exist, only create the missing ones
3. Always end with "What do we work on next?" or equivalent
