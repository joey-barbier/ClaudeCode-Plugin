#!/usr/bin/env bash
# Builds an offline fixture for the evals: a fake Claude Code config and two repositories
# with known, planted facts. Usage: build_fixture.sh <empty destination folder>
#
# Planted in home/.claude:  a broad allow on git, no ask or deny rule, six rules written as
#   sentences, a push guard that only matches the start of the command.
# Planted in shop-api (production):  tests on every pull request; a deploy job that waits for
#   no test job; an end-to-end suite that runs only on a schedule; a scheduled headless agent
#   call with no cap; a map that names the wrong test runner; a state file 11 commits old;
#   a local allow on git push.
# Planted in proto-lab (v1, speed first):  no CI, no tests, a fresh state file, lessons as sentences.
set -euo pipefail
DEST="${1:?usage: build_fixture.sh <destination>}"
mkdir -p "$DEST"
DEST="$(cd "$DEST" && pwd)"
G() { git -c user.name=fixture -c user.email=fixture@example.invalid -c commit.gpgsign=false "$@"; }
commit() { # commit <repo> <date> <message>
  G -C "$1" add -A
  GIT_AUTHOR_DATE="$2T10:00:00" GIT_COMMITTER_DATE="$2T10:00:00" G -C "$1" commit -q -m "$3"
}

# ---------------------------------------------------------------- fake home
H="$DEST/home/.claude"
mkdir -p "$H/hooks" "$H/agents" "$H/skills/changelog" "$H/skills/deploy-check"
cat > "$H/hooks/guard.sh" <<'EOF'
#!/usr/bin/env bash
# Naive guard: looks only at how the command starts.
cmd=$(python3 -c 'import json,sys; print((json.load(sys.stdin).get("tool_input") or {}).get("command",""))')
case "$cmd" in
  "git push --force"*|"git push -f"*|"git reset --hard"*)
    echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Destructive git command blocked."}}';;
esac
EOF
chmod +x "$H/hooks/guard.sh"
cat > "$H/settings.json" <<EOF
{
  "permissions": {
    "allow": ["Bash(git:*)", "Bash(npm:*)", "Bash(cat:*)", "Read", "Edit"],
    "ask": [],
    "deny": []
  },
  "hooks": {
    "PreToolUse": [
      {"matcher": "Bash", "hooks": [{"type": "command", "command": "bash $H/hooks/guard.sh"}]}
    ]
  }
}
EOF
cat > "$H/CLAUDE.md" <<'EOF'
# Working rules

## Git
- NEVER push directly to main. Always open a pull request.
- NEVER force push. NEVER merge a pull request without my explicit approval.

## Quality
- ALWAYS run ./check.sh before saying a task is done.
- Never deploy when the build is red.

## Secrets
- Never read or print .env files.

## Cost
- Always stop after three failed attempts on the same problem and ask me.
EOF
for a in code-reviewer release-manager seo-writer; do
cat > "$H/agents/$a.md" <<EOF
---
name: $a
description: Use this agent for $a tasks. It follows the working rules and reports in a short list.
---
You are the $a agent.
EOF
done
for s in changelog deploy-check; do
cat > "$H/skills/$s/SKILL.md" <<EOF
---
name: $s
description: $s helper. Use when the user asks for a $s.
---
# $s
Steps to follow.
EOF
done

# ---------------------------------------------------------------- shop-api (production)
R="$DEST/shop-api"
mkdir -p "$R/src" "$R/.github/workflows" "$R/.claude/memory" "$R/scripts"
G init -q -b main "$R"
cat > "$R/package.json" <<'EOF'
{
  "name": "shop-api",
  "private": true,
  "scripts": {
    "test": "vitest run",
    "lint": "eslint .",
    "e2e": "playwright test"
  }
}
EOF
cat > "$R/AGENTS.md" <<'EOF'
# AGENTS.md

## Where things live
- API routes: src/routes/
- Orders and payments: src/orders/
- Tests: next to the code, written with Jest. Run them with `npm run jest`.
- Deploy: .github/workflows/deploy.yml (every push to main goes to production)

## Hard rules
- Never push to main. Open a pull request.
- Never deploy on a red build.
- Never change a test to make it pass.

## Definition of done
- ./check.sh prints GATE: PASS. Paste the output.
EOF
cat > "$R/check.sh" <<'EOF'
#!/usr/bin/env bash
set -e
npm run lint
npm test
echo "GATE: PASS"
EOF
chmod +x "$R/check.sh"
cat > "$R/.claude/memory/PROJECT_STATE.md" <<'EOF'
# Project state
Current work: checkout v2 on branch feature/checkout-v2 (not merged yet).
Next: payment webhooks.
EOF
echo "export const health = () => 'ok'" > "$R/src/health.js"
cat > "$R/.github/workflows/ci.yml" <<'EOF'
name: CI
on:
  pull_request:
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run lint
      - run: npm test
EOF
cat > "$R/.github/workflows/deploy.yml" <<'EOF'
name: Deploy
on:
  push:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t shop-api .
  deploy-prod:
    needs: build
    runs-on: ubuntu-latest
    environment: production
    steps:
      - run: ./scripts/deploy.sh production
EOF
commit "$R" 2026-06-02 "add(api) - Initial service with CI and deploy"
cat > "$R/.github/workflows/nightly-e2e.yml" <<'EOF'
name: Nightly end-to-end
on:
  schedule:
    - cron: '0 3 * * *'
  workflow_dispatch:
jobs:
  e2e:
    runs-on: ubuntu-latest
    timeout-minutes: 40
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npx playwright test
EOF
commit "$R" 2026-06-20 "add(e2e) - Nightly end-to-end suite against staging"
cat > "$R/.github/workflows/triage.yml" <<'EOF'
name: Issue triage
on:
  schedule:
    - cron: '30 2 * * *'
jobs:
  triage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: claude -p "Triage the issues opened since yesterday, label them and comment with a first diagnosis." --allowedTools "Bash(gh:*)"
EOF
cat > "$R/scripts/night-fix.sh" <<'EOF'
#!/usr/bin/env bash
# Runs from cron at night: lets an agent try to fix the failing end-to-end tests.
cd "$(dirname "$0")/.."
claude -p "The nightly end-to-end run failed. Find the cause, fix it, open a pull request." --permission-mode acceptEdits
EOF
chmod +x "$R/scripts/night-fix.sh"
commit "$R" 2026-07-11 "add(agents) - Nightly triage and night-fix agent"
for i in 1 2 3 4 5 6 7 8 9 10; do
  echo "export const route$i = () => $i" > "$R/src/route$i.js"
  commit "$R" "2026-$(printf '%02d' $((7 + i / 3)))-$(printf '%02d' $((2 + i * 2)))" "add(routes) - Route $i"
done
sed -i.bak 's/"test": "vitest run"/"test": "vitest run --coverage"/' "$R/package.json" && rm "$R/package.json.bak"
commit "$R" 2026-11-12 "update(tests) - Coverage on the unit suite"
cat > "$R/.claude/settings.local.json" <<'EOF'
{
  "permissions": {
    "allow": ["Bash(git push:*)", "Bash(npm:*)", "Bash(gh pr create:*)"]
  }
}
EOF

# ---------------------------------------------------------------- proto-lab (v1, speed first)
P="$DEST/proto-lab"
mkdir -p "$P/src" "$P/notes"
G init -q -b main "$P"
cat > "$P/CLAUDE.md" <<'EOF'
# proto-lab

Prototype of a recipe recommender. No users yet. Speed first.

## Where things live
- Engine: src/engine.py
- Notes and decisions: STATE.md

## Rules
- Keep it small. No new dependency without a note in STATE.md.
- Never commit API keys.
EOF
cat > "$P/STATE.md" <<'EOF'
# State
Current step: 1 of 3 (scoring function)
Decisions: plain Python, no framework. Reason: throwaway prototype.
Next action: try the scoring on 20 recipes.
EOF
echo "def score(recipe): return len(recipe)" > "$P/src/engine.py"
commit "$P" 2026-11-03 "add(engine) - First scoring function"
cat > "$P/notes/lessons.md" <<'EOF'
# Lessons
- Always check the units of the dataset before scoring.
- Never trust the first run: the cache hides bugs.
- Remember to clear the cache between experiments.
EOF
for i in 1 2 3 4; do
  echo "# experiment $i" >> "$P/src/engine.py"
  sed -i.bak "s/Current step: .*/Current step: $((1 + i / 2)) of 3/" "$P/STATE.md" && rm "$P/STATE.md.bak"
  commit "$P" "2026-11-$(printf '%02d' $((5 + i * 3)))" "update(engine) - Experiment $i"
done

echo "fixture ready in $DEST"
echo "scan: python3 scripts/scan.py --home $H --repo $R --repo $P"
