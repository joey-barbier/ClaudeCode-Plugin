---
name: compact
description: Compress large OpenClaw sessions with intelligent summarization. Extracts learnings, archives originals, clears session files. Trigger on "compact", "compress sessions", "session too large".
allowed-tools: Bash, Read, Write, Glob
---

# Session Compactor

Compress large OpenClaw/Claude session files to prevent context overflow while preserving key learnings.

## When to Use

- Session files exceed 20MB
- Context usage approaching limits (>60%)
- Before gateway restarts to preserve learnings
- Scheduled maintenance (cron)

## Process

### 1. Scan for large sessions

```bash
ls -lhS ~/.openclaw/agents/main/sessions/*.jsonl
```

Identify files above threshold (default: 20MB).

### 2. Extract meaningful messages

**IGNORE:** HEARTBEAT messages, messages <30 chars, system messages (GatewayRestart, Exec completed), raw command outputs.

**KEEP:** Decisions made, configurations performed, problems resolved + solutions, explicit learnings, project state changes.

### 3. Generate summary (max 100 lines)

```markdown
## Session Compacted [START_DATE -> END_DATE]

### Configurations
- [Config]: details

### Decisions
- [Decision 1]

### Learnings
- [Problem] -> [Solution]

### Projects
- [Project]: [progress]
```

### 4. Archive and clear

1. Save summary to `~/.openclaw/memory/YYYY-MM-DD.md`
2. Compress original: `gzip -c session.jsonl > archive/session-TIMESTAMP.jsonl.gz`
3. Clear session file to minimal size (keep header only)

Archives go to `~/.openclaw/agents/main/archive/` (NEVER in `sessions/`).

### 5. Cleanup

Move `.bak` and `.deleted` files from `sessions/` to `archive/`.

## Shell Script

Run the included `session-compactor.sh` for automated processing:

```bash
./session-compactor.sh              # Standard run
./session-compactor.sh --dry-run    # Dry run
./session-compactor.sh --threshold-mb 30  # Custom threshold
```

## Requirements

- `jq` for JSON parsing
- `claude` CLI (optional, for intelligent summaries)
- `gzip` for compression

## Rules

1. **Only extract what's explicitly in the logs** - never invent
2. **Max 100 lines** of summary per session
3. **Priority**: Decisions > Configs > Learnings > State
4. **Deduplicate** against existing memory files
