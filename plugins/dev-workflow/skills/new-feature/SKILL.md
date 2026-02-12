---
name: new-feature
description: Prepare the environment for a new feature. Switches to main/develop branch, pulls latest, cleans up merged branches, and confirms ready state. Trigger on "new feature", "GNF", "start feature", "next feature".
allowed-tools: Bash
---

# New Feature (GNF)

Prepare the git environment for starting a new feature.

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

### 3. Clean up merged branches
```bash
git branch --merged <base-branch> | grep -v "^\*" | grep -vE "^[[:space:]]*(main|master|develop)$"
```
If merged branches exist, ask before deleting: "These branches are already merged and can be deleted: [list]. Delete them?"

### 4. Confirm ready state
```bash
git status
```
If uncommitted changes exist, warn the user and suggest: "You have uncommitted changes. Stash them (`git stash`), commit them, or discard them before proceeding?"

Output:
```
Environment ready for new feature.
Branch: <base-branch> (up to date)
Working tree: clean

What's the new feature? I'll create the branch: feature/<description>
```

Wait for user to describe the feature, then sanitize the name (lowercase, replace spaces with hyphens, remove special characters):
```bash
git checkout -b feature/<sanitized-description>
```
