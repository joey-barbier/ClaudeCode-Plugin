#!/bin/bash
# Context Monitor for OpenClaw
# Checks context usage and outputs status/alerts

# Get session status and extract context percentage
STATUS=$(openclaw gateway call status --json 2>/dev/null)

# Get current session info
SESSION_FILE="$HOME/.openclaw/agents/main/sessions/sessions.json"
if [ -f "$SESSION_FILE" ]; then
    CURRENT_SESSION=$(jq -r '.sessions["agent:main:main"].uuid // empty' "$SESSION_FILE")
    if [ -n "$CURRENT_SESSION" ]; then
        SESSION_PATH="$HOME/.openclaw/agents/main/sessions/${CURRENT_SESSION}.jsonl"
        if [ -f "$SESSION_PATH" ]; then
            SIZE_BYTES=$(stat -f%z "$SESSION_PATH" 2>/dev/null || stat -c%s "$SESSION_PATH" 2>/dev/null)
            SIZE_MB=$((SIZE_BYTES / 1024 / 1024))
            echo "SESSION_FILE_SIZE_MB=$SIZE_MB"
        fi
    fi
fi

# Output for parsing
echo "STATUS=ok"
