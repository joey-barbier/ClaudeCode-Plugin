#!/bin/bash
# Fails when anything is still present in .claude/memory/in-progress/.
# Run it on pull requests that target the base branch: a task folder must be closed
# (horka-memory-close) before the merge, never merged.
# Usage: check-in-progress.sh [a path inside the repository]   (default: current directory)
# Exit codes: 0 nothing left, 1 task memory left, 2 not a git repository (the check could not run).

ROOT="$(git -C "${1:-.}" rev-parse --show-toplevel 2>/dev/null)"
if [ -z "$ROOT" ]; then
  echo "check-in-progress: ${1:-.} is not inside a git repository, nothing was checked." >&2
  exit 2
fi
LEFT="$(find "$ROOT/.claude/memory/in-progress" -mindepth 1 -maxdepth 1 2>/dev/null | sort)"
if [ -n "$LEFT" ]; then
  echo "Task memory still in progress, close it before merging:"
  printf '%s\n' "$LEFT" | sed 's/^/  /'
  exit 1
fi
echo "No task memory left in progress."
exit 0
