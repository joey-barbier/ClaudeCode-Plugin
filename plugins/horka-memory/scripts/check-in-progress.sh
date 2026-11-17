#!/bin/bash
# Fails when a task folder is still present in .claude/memory/in-progress/.
# Run it on pull requests that target the base branch: a task folder must be closed
# (horka-memory-close) before the merge, never merged.
# Usage: check-in-progress.sh [repository root]   (default: current directory)

ROOT="${1:-.}"
LEFT="$(find "$ROOT/.claude/memory/in-progress" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort)"
if [ -n "$LEFT" ]; then
  echo "Task memory still in progress, close it before merging:"
  echo "$LEFT" | sed 's/^/  /'
  exit 1
fi
echo "No task memory left in progress."
exit 0
