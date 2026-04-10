# horka-review

Complete code review toolkit for Claude Code. Two complementary review passes that catch issues before they reach production.

## What's included

### Skills

| Skill | Trigger | Role |
|-------|---------|------|
| `/antagonist-reviewer` | "roast", "critique", "what's wrong", "find flaws", "challenge" | Ruthless flaw finder. Zero compliments, zero bullshit. Outputs BLOCKED/WARNINGS/WASTE/VERDICT/NEXT. |
| `/horka-review-changes` | "review changes", "review my code", "code review" | Senior Tech Lead PR review. Structured feedback with APPROVED/CHANGES REQUIRED/REJECTED verdict. |

### Hook: review-guard

Fires on `git push` and `gh pr create`:

- **Push to default branch** → blocked (create a feature branch instead)
- **Push/PR on feature branch** → reminds the review order

### Review order

```
Code → Antagonist review (find flaws) → Fix → Tech Lead review (validate) → Push/PR
```

The antagonist finds problems. You fix them. The tech lead validates the clean version. Not the other way around.

## Requirements

- `jq` (for hook scripts — gracefully skipped if missing)
- `git` (auto-detects default branch: main, master, trunk)

## Install

```bash
claude install-plugin /path/to/horka-review
```
