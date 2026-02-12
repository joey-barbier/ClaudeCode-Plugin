#!/bin/bash
# Guard git push: deny on main/master, remind review on feature branches

if ! command -v jq &>/dev/null; then exit 0; fi

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // ""')

# Only trigger on git push commands
if echo "$COMMAND" | grep -qE 'git\s+push'; then
  BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)

  # Block push to main/master
  if [ "$BRANCH" = "main" ] || [ "$BRANCH" = "master" ]; then
    jq -n '{
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason: "Push to main/master blocked. Create a feature branch and open a PR instead."
      }
    }'
    exit 0
  fi

  # Remind review on feature branches
  if [ "$BRANCH" != "develop" ]; then
    jq -n --arg branch "$BRANCH" '{
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        additionalContext: ("REVIEW REMINDER: Pushing feature branch \u0027" + $branch + "\u0027. Ensure review-pr agent has reviewed these changes. If no review was done in this session, ask the user before proceeding.")
      }
    }'
    exit 0
  fi
fi

exit 0
