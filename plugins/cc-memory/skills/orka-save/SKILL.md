---
name: orka-save
description: Save current session progression to project memory files. Updates PROJECT_STATE, ARCHITECTURE, DECISIONS, NEXT_STEPS based on work done. Use when user says "save progress", "update memory", "save state", "checkpoint", or before ending a productive session.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Orka Save - Save Progression

Analyze the current session and update memory files with what was accomplished.

## Scope

Updates existing memory files only. Does NOT:
- Create memory files from scratch (use `/cc-memory:orka-memory` for that)
- Modify project source code
- Push changes to remote

## Step 1: Read Current Memory Files

Use Glob to find existing memory files:
- `.claude/memory/**/*.md`

Read all existing files to understand the current documented state.

**If no memory files exist**: tell the user to run `/cc-memory:orka-memory` first to initialize.

## Step 2: Analyze Current Session

Gather information about what happened in this session:

### 2a. Git Analysis

```bash
# Current branch and recent commits
git log --oneline -20
git status
git diff --stat HEAD~5 HEAD 2>/dev/null || git diff --stat
```

### 2b. Conversation Analysis

Review the current conversation to identify:
- **Features completed** (code written, tested, merged)
- **Decisions made** (architecture choices, conventions adopted)
- **Problems solved** (bugs fixed, blockers resolved)
- **Files created/modified** (new modules, configs changed)
- **Commands discovered** (useful dev commands, workflows)
- **Next steps discussed** (what was planned but not done yet)
- **Known issues** (bugs found, limitations identified)

## Step 3: Update Memory Files

For each memory file, apply **surgical updates** -- don't rewrite entire files, only add/modify/remove what changed.

### PROJECT_STATE.md

Update these sections:
- **Current Branch**: update if changed
- **DONE**: move completed items, add new completions with details
- **TODO**: remove completed items, add newly identified tasks
- **Known Issues**: add/remove bugs and limitations
- **Key Files**: add newly created files

Format for done items:
```markdown
- [x] Feature description
  - Detail 1
  - Detail 2
```

### ARCHITECTURE.md

Only update if:
- New modules/components were created
- Data flow changed
- New dependencies were added
- Project structure changed significantly

### DECISIONS.md

Add new entries for:
- Technical choices made during session (with rationale)
- Conventions established or changed
- Trade-offs discussed and resolved

Format:
```markdown
| Decision | Rationale | Date |
|----------|-----------|------|
| [What] | [Why] | YYYY-MM-DD |
```

### NEXT_STEPS.md

Rewrite priorities based on current state:
```markdown
## Immediate (next session)
- [ ] Task 1

## Short Term
- [ ] Task 2

## Backlog
- [ ] Task 3
```

### COMMANDS.md

Add any new useful commands discovered during the session.

## Step 4: Report

After updating, provide a concise summary:

```markdown
## Memory Saved

**Files updated**:
- PROJECT_STATE.md: [what changed]
- NEXT_STEPS.md: [what changed]
- [other files if modified]

**Session highlights**:
- [Key accomplishment 1]
- [Key accomplishment 2]

**Next session priority**: [Most important next task]
```

## Rules

1. **Never invent** -- only save information from the actual session (conversation + git)
2. **Surgical updates** -- don't rewrite entire files, only modify what changed
3. **Preserve history** -- don't delete past completed items from PROJECT_STATE, only add new ones
4. **Deduplicate** -- check existing content before adding to avoid repetition
5. **Date entries** -- use current date for new decisions and state changes
6. **Be concise** -- memory files should be scannable, not verbose narratives
7. **Respect structure** -- maintain the existing file format and section headers
