---
name: memory
description: Restore project context from memory files, or initialize them if none exist. Use at session start, when losing track, or to bootstrap a new project's memory. Trigger on "context", "memory", "where were we", "resume", "catch up", "refresh context", "init memory".
allowed-tools: Read, Write, Glob, Grep, Bash
---

# Memory

Manage project memory files: restore context from existing files, or create them from scratch.

## Step 1: Find Memory Files

Use Glob to search in priority order:

1. `.claude/memory/**/*.md` - Dedicated memory folder
2. `docs-architecture/**/*.md` - Architecture documentation
3. `CLAUDE.md`, `.claude/CLAUDE.md` - Root config
4. `documentations/**/*.md`, `docs/**/*.md` - General docs
5. `README.md` - Fallback

**If files found** -> go to Step 2 (Restore)
**If no files found** -> go to Step 3 (Initialize)

## Step 2: Restore Context

Read each file found. Priority order:

| File | Content |
|------|---------|
| `PROJECT_STATE.md` | Current state, done/not done, bugs |
| `ARCHITECTURE.md` | Structure, flows, components |
| `DECISIONS.md` | Technical choices, conventions |
| `NEXT_STEPS.md` | Roadmap, next tasks |
| `COMMANDS.md` | Useful commands |
| `CLAUDE.md` | Project instructions |

Produce a structured summary:

```markdown
## Context Restored

**Project**: [Name deduced from files]
**Stack**: [Technologies identified]
**Phase**: [Current state]

### What's DONE
- [Feature 1]
- [Feature 2]

### What REMAINS
- [Priority 1]
- [Priority 2]

### Points of Attention
- [Known bugs, limitations, important decisions]

---
What do we work on next?
```

## Step 3: Initialize Memory

When no memory files exist, offer to create them:

```
No memory files found in this project.

Locations checked:
- .claude/memory/
- docs-architecture/
- CLAUDE.md
- documentations/

I can initialize memory files by analyzing the project. Proceed?
```

If the user agrees:

### 3a. Gather Project Information

Explore the project to determine:
1. **Project name**: from `package.json`, `Cargo.toml`, `setup.py`, `*.xcodeproj`, or directory name
2. **Tech stack**: from config files, dependencies, file extensions
3. **Current state**: from git log, README, existing docs
4. **Project structure**: from directory layout

### 3b. Create `.claude/memory/` with these files:

**PROJECT_STATE.md** - Current phase, what's done/remaining, known bugs, attention points

**ARCHITECTURE.md** - Tech stack, project structure, key components, data flow

**DECISIONS.md** - Conventions (commit format, branch naming, code style) + key decisions table

**NEXT_STEPS.md** - Immediate priority, short term, backlog

**COMMANDS.md** - Dev server, test, build, git workflow commands

### 3c. Confirm

```
Memory initialized at .claude/memory/

Created: PROJECT_STATE.md, ARCHITECTURE.md, DECISIONS.md, NEXT_STEPS.md, COMMANDS.md

Use /cc-memory:memory to reload this context in future sessions.
```

## Rules

1. **Never invent** -- only use information from actual files or project analysis
2. **Mark unknowns** as "TBD" rather than guessing
3. **Fill with real data** from project analysis, not empty templates
4. **Always conclude** with "What do we work on next?" or equivalent
5. **Respect existing** -- if some memory files exist, only create missing ones
