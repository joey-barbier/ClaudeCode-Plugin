---
name: horka-claude-setup
description: Interactive CLAUDE.md generator. Asks about workflow, preferences, and installed plugins to generate a personalized instruction file. Supports global, project, and root scopes with augment mode for existing files. Use when user says "setup claude", "generate CLAUDE.md", "configure claude code", "setup", or at first project setup. Also trigger when the user asks how to customize Claude's behavior or mentions wanting Claude to follow specific conventions.
disable-model-invocation: true
allowed-tools: AskUserQuestion, Read, Write, Edit, Glob, Bash
---

# Setup - CLAUDE.md Generator

## Scope

Generates CLAUDE.md files only. Does NOT:
- Modify existing project code or configuration
- Install plugins or dependencies
- Set up git repositories

## Step 1: Detect Context

1. Check for existing CLAUDE.md files: `~/.claude/CLAUDE.md` (global), `.claude/CLAUDE.md` (project), `CLAUDE.md` (root)
2. If in a project: detect tech stack from config files (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, etc.) and git conventions from recent commits (`git log --oneline -5`)
3. Use detected stack and git conventions as defaults in questionnaire (skip questions already answered by detection)

If existing CLAUDE.md found, ask via `AskUserQuestion`: replace, augment, or different scope.
- **Replace**: full questionnaire, overwrite existing file
- **Augment**: Read existing file, identify covered sections, ask only about missing/uncovered topics, use Edit to merge new sections
- **Different scope**: full questionnaire, write to chosen alternative location

## Step 2: Questionnaire

Consult `references/questionnaire.md` for the full question tables.

Run 3 rounds via `AskUserQuestion`:
1. **Profile & Philosophy**: usage type, work philosophy, communication style, language
2. **Workflow**: security (common for all profiles) + git/commit conventions for dev or git usage/file organization for PM/writing
3. **Integration**: file headers, context management, output destination, installed plugins

If a question is skipped or answered vaguely ("I don't know", "whatever"), re-ask once with: "This choice affects your CLAUDE.md quality. Here's what each option means: [brief impact of each]". If skipped a second time, apply the `(Recommended)` default.

## Step 3: Generate CLAUDE.md

Consult `references/generation-rules.md` for section templates, plugin integration, and quality reference.

Key rules:
- Generate ONLY sections relevant to user answers
- Every instruction must be actionable (NEVER, ALWAYS for absolute rules)
- Add contextual qualifiers for non-absolute rules ("For non-trivial changes", "Skip for obvious fixes")
- No filler prose -- bullet points only
- Put critical rules at the top of each section
- Use `##` numbered subsections to group 3+ related concerns within a `#` category
- Do NOT duplicate rules already in Claude's system prompt (e.g., "no emojis")
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

Example:
```
CLAUDE.md generated at .claude/CLAUDE.md
6 sections | 42 lines | Language: English

Sections: Workflow, Security, Communication, Context, File Headers, Plugins & Agents

Tip: Edit this file anytime to adjust Claude's behavior.
```

## Error Handling

- **Existing CLAUDE.md conflict**: Ask user to replace, augment, or change scope
- **No project detected**: Default to global `~/.claude/CLAUDE.md`
- **AskUserQuestion denied**: Tell user "Interactive mode requires AskUserQuestion permission. Approve to continue."
- **Write permission denied**: Show generated content in output and let user copy manually
