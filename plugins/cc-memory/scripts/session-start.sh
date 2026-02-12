#!/bin/bash
# Auto-detect memory files at session start and inject context restoration reminder

MEMORY_DIR=".claude/memory"
DOCS_ARCH="docs-architecture"

FOUND=""

if [ -d "$MEMORY_DIR" ] && [ "$(ls -A "$MEMORY_DIR" 2>/dev/null)" ]; then
  FILES=$(ls "$MEMORY_DIR"/*.md 2>/dev/null | xargs -I{} basename {} | tr '\n' ', ' | sed 's/,$//')
  FOUND="Memory files found in $MEMORY_DIR/: $FILES."
fi

if [ -d "$DOCS_ARCH" ] && [ "$(ls -A "$DOCS_ARCH" 2>/dev/null)" ]; then
  FOUND="$FOUND Architecture docs found in $DOCS_ARCH/."
fi

if [ -f ".claude/CLAUDE.md" ] || [ -f "CLAUDE.md" ]; then
  FOUND="$FOUND Project CLAUDE.md found."
fi

if [ -n "$FOUND" ]; then
  echo "$FOUND Read these files to restore project context before proceeding."
fi

exit 0
