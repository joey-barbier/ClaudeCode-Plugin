#!/bin/bash
# Auto-save reminder: triggers after significant work in a session.
# Uses a counter file to track Claude responses and only reminds periodically.
# Anti-loop: won't remind if memory was recently saved or if already reminded.

MEMORY_DIR=".claude/memory"
TMPDIR="${TMPDIR:-/tmp}"
SESSION_COUNTER="$TMPDIR/cc-memory-stop-counter-$$"
REMINDER_FLAG="$TMPDIR/cc-memory-reminded-$$"
THRESHOLD=15

# No memory dir = no reminder (user hasn't initialized yet)
if [ ! -d "$MEMORY_DIR" ]; then
  exit 0
fi

# If we already reminded and haven't been reset, stay silent
if [ -f "$REMINDER_FLAG" ]; then
  exit 0
fi

# Increment counter
COUNT=0
if [ -f "$SESSION_COUNTER" ]; then
  COUNT=$(cat "$SESSION_COUNTER" 2>/dev/null || echo 0)
fi
COUNT=$((COUNT + 1))
echo "$COUNT" > "$SESSION_COUNTER"

# Only remind at threshold crossings
if [ "$COUNT" -ge "$THRESHOLD" ]; then
  # Check if memory was recently updated (within last 5 minutes)
  if [ -f "$MEMORY_DIR/PROJECT_STATE.md" ]; then
    LAST_MOD=$(stat -f %m "$MEMORY_DIR/PROJECT_STATE.md" 2>/dev/null || stat -c %Y "$MEMORY_DIR/PROJECT_STATE.md" 2>/dev/null || echo 0)
    NOW=$(date +%s)
    DIFF=$((NOW - LAST_MOD))
    if [ "$DIFF" -lt 300 ]; then
      # Memory was saved recently, reset counter
      echo "0" > "$SESSION_COUNTER"
      exit 0
    fi
  fi

  # Check if meaningful work happened (git changes)
  GIT_CHANGES=$(git diff --stat HEAD 2>/dev/null | tail -1)
  GIT_NEW_COMMITS=$(git log --oneline --since="1 hour ago" 2>/dev/null | wc -l | tr -d ' ')

  if [ -n "$GIT_CHANGES" ] || [ "$GIT_NEW_COMMITS" -gt 0 ]; then
    echo "Significant work detected ($COUNT interactions, $GIT_NEW_COMMITS recent commits). Consider running /cc-memory:orka-save to persist progress."
    touch "$REMINDER_FLAG"
    echo "0" > "$SESSION_COUNTER"
  fi
fi

exit 0
