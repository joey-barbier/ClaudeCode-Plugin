---
name: extract
description: Extract learnings from the current conversation session and store them in memory files. Use before deleting large sessions or on /compact command.
allowed-tools: Read, Write, Bash, Glob
---

# Session Memory Extraction

Extract important information from the current session and archive it.

## Process

### 1. Identify the active session

```bash
ls -lhS ~/.openclaw/agents/main/sessions/*.jsonl
```

Take the most recent / largest file.

### 2. Extract messages

```bash
jq -r 'select(.type == "message") | select(.message.role == "user" or .message.role == "assistant") | .message.content[]? | select(.type == "text") | .text' SESSION.jsonl
```

### 3. Filter noise

**IGNORE:** HEARTBEAT, empty/short responses (<20 chars), system messages, greetings, raw command outputs.

**KEEP:** Decisions, configurations, problems resolved + solutions, explicit learnings, project state.

### 4. Structure learnings

```markdown
## Session Archive [START_DATE -> END_DATE]

*Session ID: xxx*
*Compacted: YYYY-MM-DD HH:MM*

### Configurations
- [Config 1]: details

### Decisions
- [Decision 1]

### Learnings
- [Problem] -> [Solution]

### Project State
- [Project]: [progress]
```

### 5. Save to memory/

1. Add summary to `~/.openclaw/memory/YYYY-MM-DD.md`
2. If learnings are generalizable, add to `~/.openclaw/memory/MEMORY.md` (cumulative knowledge base)
3. Update `~/.openclaw/memory/INDEX.md` with tagged entries (e.g., `- [2024-01-15] #config #deployment - Server setup learnings`)

### 6. Archive the .jsonl

```bash
mkdir -p ~/.openclaw/agents/main/archive
gzip -c SESSION.jsonl > ~/.openclaw/agents/main/archive/SESSION_ID_YYYY-MM-DD.jsonl.gz
# Clear session to minimal size (keep first line as header) instead of deleting
head -1 SESSION.jsonl > SESSION.jsonl.tmp && mv SESSION.jsonl.tmp SESSION.jsonl
```

Archives ALWAYS in `~/.openclaw/agents/main/archive/` (NEVER in `sessions/`).

### 7. Report

```
Session [ID] compacted
- Messages analyzed: X
- Learnings extracted: Y
- Files updated: memory/YYYY-MM-DD.md, MEMORY.md, INDEX.md
- Original size: X MB -> gzip archive
- Archive: ~/.openclaw/agents/main/archive/[file].gz
```

## Rules

1. **Only extract what's explicitly in the logs**
2. **Max 100 lines** of summary per session
3. **Priority**: Decisions > Configs > Learnings > State
4. **Deduplicate** against existing memory files
5. **Archive in the right place** - `archive/` at parent level
