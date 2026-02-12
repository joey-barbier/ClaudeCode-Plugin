#!/bin/bash
# Remind to extract learnings before context compaction on large sessions

if ! command -v jq &>/dev/null; then exit 0; fi

INPUT=$(cat)
TRANSCRIPT=$(echo "$INPUT" | jq -r '.transcript_path // ""')

if [ -n "$TRANSCRIPT" ] && [ -f "$TRANSCRIPT" ]; then
  MSG_COUNT=$(wc -l < "$TRANSCRIPT" 2>/dev/null | tr -d ' ')
  if [ "$MSG_COUNT" -gt 50 ]; then
    echo "Large session ($MSG_COUNT entries) about to be compacted. Consider using /openclaw:extract to save learnings before context is reduced."
  fi
fi

exit 0
