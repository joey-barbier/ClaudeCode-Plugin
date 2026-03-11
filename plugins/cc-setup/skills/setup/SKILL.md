---
name: setup
description: Interactive CLAUDE.md generator. Asks about workflow, preferences, and installed plugins to generate an optimized instruction file. Use when user says "setup claude", "generate CLAUDE.md", "configure claude code", "setup", or at first project setup.
disable-model-invocation: true
allowed-tools: AskUserQuestion, Read, Write, Edit, Glob, Bash
---

# Setup

Generate a personalized `CLAUDE.md` through interactive questions and project analysis.

## Scope

This skill generates CLAUDE.md files only. It does NOT:
- Modify existing project code or configuration
- Install plugins or dependencies
- Set up git repositories

## Step 1: Detect Context

1. Check for existing CLAUDE.md files: `~/.claude/CLAUDE.md` (global), `.claude/CLAUDE.md` (project), `CLAUDE.md` (root)
2. If in a project: detect tech stack from config files and git conventions from recent commits
3. Note findings for pre-filling defaults

If existing CLAUDE.md found, ask: replace, augment, or create at different scope.

## Step 2: Questionnaire

Consult `references/questionnaire.md` for the full question tables.

Run 3 rounds via `AskUserQuestion`:
1. **Profile & Philosophy**: usage type, work philosophy, communication style, language
2. **Workflow**: git strategy, commit format, push safety, security (adapts to profile)
3. **Integration**: file headers, context management, output destination, installed plugins

## Step 3: Generate CLAUDE.md

Consult `references/generation-rules.md` for section templates, plugin integration, and quality reference.

Key rules:
- Generate ONLY sections relevant to user answers
- Every instruction must be actionable (NEVER, ALWAYS)
- No filler prose -- bullet points only
- Keep total length under 100 lines
- Include plugin section if ANY plugins selected

## Step 4: Write & Confirm

1. Show preview summary: sections generated, total line count
2. Ask for confirmation before writing
3. Write to chosen destination
4. Display final message:

```
CLAUDE.md generated at [path]
[N] sections | [M] lines | Language: [lang]

Sections: [list of generated section names]

Tip: Edit this file anytime to adjust Claude's behavior.
```

## Error Handling

- **Existing CLAUDE.md conflict**: Ask user to replace, augment, or change scope
- **No project detected**: Default to global `~/.claude/CLAUDE.md`
- **AskUserQuestion denied**: Tell user "Interactive mode requires AskUserQuestion permission. Approve to continue."
- **Write permission denied**: Show generated content in output and let user copy manually
