#!/bin/bash
# Unified review guard: block push to default branch, enforce review order on feature branches
# Triggers on: git push, gh pr create

if ! command -v jq &>/dev/null; then exit 0; fi

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // ""')

# Only trigger on git push or gh pr create
echo "$COMMAND" | grep -qE 'git\s+push|gh\s+pr\s+create' || exit 0

# Must be in a git repo
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null) || exit 0

# Detect default branch (main, master, trunk, develop, etc.)
DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
if [ -z "$DEFAULT_BRANCH" ]; then
  # Fallback: check common names
  for candidate in main master trunk; do
    if git show-ref --verify --quiet "refs/heads/$candidate" 2>/dev/null || \
       git show-ref --verify --quiet "refs/remotes/origin/$candidate" 2>/dev/null; then
      DEFAULT_BRANCH="$candidate"
      break
    fi
  done
fi
[ -z "$DEFAULT_BRANCH" ] && DEFAULT_BRANCH="main"

# Block push to default branch
if echo "$COMMAND" | grep -qE 'git\s+push'; then
  if [ "$BRANCH" = "$DEFAULT_BRANCH" ]; then
    jq -n --arg branch "$DEFAULT_BRANCH" '{
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason: ("Push to " + $branch + " blocked. Create a feature branch and open a PR instead.")
      }
    }'
    exit 0
  fi
fi

# Skip if on default branch (nothing to review)
[ "$BRANCH" = "$DEFAULT_BRANCH" ] && exit 0

# Remind review order on feature branches
DIFF_STAT=$(git diff --stat "$DEFAULT_BRANCH"...HEAD 2>/dev/null | tail -1)

jq -n --arg branch "$BRANCH" --arg stats "$DIFF_STAT" '{
  hookSpecificOutput: {
    hookEventName: "PreToolUse",
    additionalContext: ("REVIEW ORDER for branch \u0027" + $branch + "\u0027 (" + $stats + "): 1) Run /antagonist-reviewer FIRST (finds flaws, security holes, architecture issues), 2) Fix issues found, 3) THEN run tech lead review via /horka-review-changes (clean validation). If neither review was done this session, ask the user before proceeding.")
  }
}'
