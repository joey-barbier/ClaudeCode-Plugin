# PixelClaw - Architecture

## Overview
Claude Code plugin marketplace. Collection of plugins providing skills (user-invocable) and agents (subagent-invocable) for Claude Code.

## Tech Stack
- Markdown-based skills (SKILL.md) and agents (.md)
- JSON config (plugin.json, marketplace.json, hooks.json)
- Shell scripts for automation (hooks, cron)
- Git/GitHub for distribution

## Structure
```
PixelClaw/
+-- .claude-plugin/marketplace.json    # Marketplace registry
+-- plugins/
|   +-- cc-memory/                     # Context persistence (2 skills)
|   +-- cc-setup/                      # CLAUDE.md generator (1 skill + references/)
|   +-- code-review/                   # PR review (1 agent)
|   +-- dev-workflow/                  # Dev tools (3 skills + 1 agent)
|   +-- analytics/                     # SaaS analytics (1 agent)
|   +-- openclaw/                      # Session management (2 skills + scripts/)
|   +-- qa-testing/                    # QA & testing (1 skill + references/ + 1 agent)
|   +-- skill-eval/                    # Skill evaluator (1 skill + references/)
+-- README.md (+ .fr/.es/.de)
```

## Plugin Anatomy
Each plugin: `.claude-plugin/plugin.json` + `skills/*/SKILL.md` + `agents/*.md` + optional `hooks/`, `scripts/`, `references/`

## Totals
- 10 skills, 4 agents, 8 shell scripts
- 2 plugins use references/ for progressive disclosure (cc-setup, skill-eval, qa-testing)
