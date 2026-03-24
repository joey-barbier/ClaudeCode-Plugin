---
name: horka-git-new-feature
description: Prepare the git environment for starting a new feature. Switches to main/develop branch, pulls latest, cleans up merged branches, and confirms ready state. Trigger on "new feature", "GNF", "start feature", "next feature", "prepare for new work".
allowed-tools: Bash
---

# New Feature (GNF)

Prepare the git environment for starting a new feature.

## Scope

Prepares git environment only. Does NOT:
- Create feature implementations
- Modify existing code
- Push to remote (only local branch operations)

## Steps

### 1. Identify and switch to base branch

```bash
git branch -a
```

Look for `develop`, `main`, or `master` (in that priority order), then checkout:

```bash
git checkout <base-branch>
```

### 2. Pull latest

```bash
git pull origin <base-branch>
```

If pull has merge conflicts: "Merge conflicts detected on `<base-branch>`. Resolve them before starting a new feature, or stash your changes and retry."

### 3. Clean up merged branches

```bash
git branch --merged <base-branch> | grep -v "^\*" | grep -vE "^[[:space:]]*(main|master|develop)$"
```

If merged branches exist, ask: "These branches are already merged and can be deleted: [list]. Delete them?"

### 4. Confirm ready state

```bash
git status
```

If uncommitted changes: "You have uncommitted changes. Stash them (`git stash`), commit them, or discard them before proceeding?"

Output:

```
Environment ready for new feature.
Branch: <base-branch> (up to date)
Working tree: clean

What's the new feature? I'll create the branch: feature/<description>
```

### 5. Create feature branch

Wait for user to describe the feature. Sanitize the name (lowercase, hyphens, no special chars):

```bash
git checkout -b feature/<sanitized-description>
```

## Error Handling

- **Network/auth failure on pull**: "Could not pull latest. Continue on local state or fix connection?"
- **Branch already exists**: "Branch `feature/X` already exists. Switch to it or pick a new name?"
- **Detached HEAD state**: Warn and switch to base branch first
