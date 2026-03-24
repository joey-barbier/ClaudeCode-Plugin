---
name: orka-memory-save
description: Save current session progression to project memory files. Updates PROJECT_STATE, ARCHITECTURE, DECISIONS, NEXT_STEPS based on work done in this session. Use when user says "save progress", "update memory", "save state", "checkpoint", or before ending a productive session. Also use proactively after significant implementations, bug fixes, or architectural changes.
allowed-tools: Read, Write, Edit, Glob, Bash
---

# Save Session Progression

## Scope

Updates existing memory files only. Does NOT:
- Create memory files from scratch (use `/cc-memory:orka-memory-restore` for that)
- Modify project source code
- Push changes to remote

## Step 1: Verify memory exists

Use Glob to find `.claude/memory/**/*.md`.

If no memory files exist: tell the user "No memory files found. Run `/cc-memory:orka-memory-restore` first to initialize." and stop.

Read all found files to understand the current documented state.

## Step 2: Analyze what happened

### Git analysis

Run via Bash:
```bash
git log --oneline -20
git status
git diff --stat HEAD~5 HEAD 2>/dev/null || git diff --stat
```

### Conversation analysis

Review the current conversation for:
- Features completed (code written, tested, merged)
- Decisions made (architecture choices, conventions)
- Problems solved (bugs fixed, blockers resolved)
- Files created/modified
- Next steps discussed but not yet done
- Known issues discovered

## Step 3: Apply surgical updates

Use Edit for precise changes -- don't rewrite entire files.

**PROJECT_STATE.md**: Move completed items to DONE, add new completions with detail, remove from TODO, update known issues and key files.

**ARCHITECTURE.md**: Only update if new modules were created, data flow changed, or dependencies were added.

**DECISIONS.md**: Add new technical choices with rationale and date:
```
| Decision | Rationale | Date |
|----------|-----------|------|
| [What] | [Why] | YYYY-MM-DD |
```

**NEXT_STEPS.md**: Rewrite priorities based on current state:
```
## Immediate (next session)
- [ ] Task 1

## Short Term
- [ ] Task 2

## Backlog
- [ ] Task 3
```

**COMMANDS.md**: Add any new useful commands discovered.

## Step 4: Report

```
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

## Error Handling

- **No memory files found**: Tell user "No memory files found. Run `/cc-memory:orka-memory-restore` first to initialize." and stop.
- **Git not available**: Skip git analysis, rely on conversation context only. Note "Git unavailable" in report.
- **Write permission denied on memory files**: Show proposed updates in output and let user apply manually.
- **No changes detected**: "No significant changes found in this session. Nothing to save."

## Rules

1. Never invent -- only save information from the actual session (conversation + git)
2. Preserve history -- don't delete past completed items, only add new ones
3. Deduplicate -- check existing content before adding
4. Date entries -- use current date for new decisions
5. Be concise -- scannable content, not verbose narratives
