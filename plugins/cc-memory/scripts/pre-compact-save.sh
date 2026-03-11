#!/bin/bash
# Pre-compact hook: remind Claude to save memory before context is compressed.
# Context compaction means conversation history will be summarized, so saving now is critical.

MEMORY_DIR=".claude/memory"

# No memory dir = nothing to save
if [ ! -d "$MEMORY_DIR" ]; then
  exit 0
fi

# Check if memory files exist
if [ ! -f "$MEMORY_DIR/PROJECT_STATE.md" ]; then
  exit 0
fi

# Check if there's meaningful session work to save
GIT_CHANGES=$(git diff --stat HEAD 2>/dev/null | tail -1)
GIT_NEW_COMMITS=$(git log --oneline --since="2 hours ago" 2>/dev/null | wc -l | tr -d ' ')

if [ -n "$GIT_CHANGES" ] || [ "$GIT_NEW_COMMITS" -gt 0 ]; then
  echo "IMPORTANT: Context is about to be compacted. Run /cc-memory:orka-save NOW to persist session progress before context is lost. ($GIT_NEW_COMMITS recent commits, changes: $GIT_CHANGES)"
else
  echo "Context compaction starting. Memory files exist at $MEMORY_DIR/ but no significant git changes detected since last save."
fi

exit 0
