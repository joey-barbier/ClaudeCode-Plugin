#!/bin/bash
# Block destructive git commands that can cause data loss

if ! command -v jq &>/dev/null; then exit 0; fi

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // ""')

# Force push - overwrites remote history (allow --force-with-lease)
if echo "$COMMAND" | grep -qE 'git\s+push\s+.*(-f|--force)\b'; then
  if ! echo "$COMMAND" | grep -qE '\-\-force-with-lease'; then
    jq -n '{
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason: "Force push blocked. This overwrites remote history and can destroy teammates work. Use --force-with-lease if necessary, only after explicit user approval."
      }
    }'
    exit 0
  fi
fi

# Hard reset - discards all uncommitted changes
if echo "$COMMAND" | grep -qE 'git\s+reset\s+--hard'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "Hard reset blocked. This permanently discards all uncommitted changes. Ask the user for explicit confirmation first."
    }
  }'
  exit 0
fi

# Clean -f - permanently deletes untracked files
if echo "$COMMAND" | grep -qE 'git\s+clean\s+-[a-zA-Z]*f'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "git clean blocked. This permanently deletes untracked files. Ask the user for explicit confirmation first."
    }
  }'
  exit 0
fi

# Branch -D - force delete branch (may lose unmerged work)
if echo "$COMMAND" | grep -qE 'git\s+branch\s+-D\b'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "Force branch delete blocked. Branch may contain unmerged work. Use -d (lowercase) for safe delete, or ask user for confirmation."
    }
  }'
  exit 0
fi

# Checkout . - discards all unstaged changes
if echo "$COMMAND" | grep -qE 'git\s+checkout\s+\.\s*$'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "git checkout . blocked. This discards all unstaged changes. Ask the user for explicit confirmation first."
    }
  }'
  exit 0
fi

# Restore . - discards all unstaged changes
if echo "$COMMAND" | grep -qE 'git\s+restore\s+\.\s*$'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "git restore . blocked. This discards all unstaged changes. Ask the user for explicit confirmation first."
    }
  }'
  exit 0
fi

exit 0
