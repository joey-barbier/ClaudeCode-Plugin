---
name: horka-review-changes
description: Launch a Tech Lead review on current changes (uncommitted, staged, or branch commits). Delegates entirely to the review-pr agent for context isolation. Trigger on "review changes", "review my code", "check my changes", "TL review", "code review".
allowed-tools: Agent
---

## Instructions

Launch the `review-pr` agent (subagent_type: `pr-tech-lead-reviewer`) with the following prompt:

> Review all current changes in this repository. Follow this order:
> 1. Run `git diff --stat` and `git diff --cached --stat` to check for uncommitted changes
> 2. Run `git log --oneline main..HEAD` to check for branch commits
> 3. If uncommitted changes exist, review `git diff` + `git diff --cached`
> 4. If no uncommitted changes but branch has commits, review `git diff main...HEAD`
> 5. If nothing found, report "No changes detected." and stop
> 6. Search for documentation folders at the repo root (any folder whose name suggests docs, architecture, or conventions). Read all `.md` files found for project context before reviewing

Do NOT gather the diff yourself. The agent handles everything in its own isolated context.
