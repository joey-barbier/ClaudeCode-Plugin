---
name: setup
description: Interactive CLAUDE.md generator. Asks about your workflow, preferences, and installed plugins, then generates an optimized instruction file for Claude Code. Works for developers, PMs, writers, and anyone using Claude Code.
disable-model-invocation: true
allowed-tools: AskUserQuestion, Read, Write, Edit, Glob, Bash
---

# Setup

Generate a personalized `CLAUDE.md` through interactive questions and project analysis.

## Step 1: Detect Context

1. Check for existing CLAUDE.md files: `~/.claude/CLAUDE.md` (global), `.claude/CLAUDE.md` (project), `CLAUDE.md` (root)
2. If in a project: detect tech stack from config files and git conventions from recent commits
3. Note findings for pre-filling defaults

If existing CLAUDE.md found, ask: replace, augment, or create at different scope.

## Step 2: Questionnaire

Use `AskUserQuestion` in 3 rounds. Adapt questions based on the user's profile. Use clear, jargon-free descriptions for each option.

### Round 1: Profile & Philosophy

| # | Question | Options |
|---|----------|---------|
| 1 | What do you primarily use Claude Code for? | `Software development (Recommended)` - Writing code, debugging, building apps / `Project management` - Planning, tracking, documentation / `Writing & content` - Docs, articles, copywriting / `Mixed usage` - Combination of the above |
| 2 | What's your work philosophy? | `Ship fast, iterate (Recommended)` - Prioritize working results over perfect structure / `Quality first` - Thorough planning and testing before delivery / `Balanced` - Fast for new work, thorough for critical systems |
| 3 | How should Claude communicate? | `Concise & direct (Recommended)` - Short answers, bullet points, no fluff / `Detailed & explanatory` - Full context and reasoning / `Balanced` - Concise with detail when complex |
| 4 | CLAUDE.md language? | `English` / `French` |

### Round 2: Workflow

**Adapt based on profile from Round 1.**

**If software development:**

| # | Question | Options |
|---|----------|---------|
| 1 | Git branch strategy? | `Feature branches + PRs (Recommended)` - Separate branch per feature, merge via PR / `Trunk-based` - Commit directly to main branch / `Gitflow` - develop/release/hotfix branches |
| 2 | Commit message format? | `Scoped: add/update/fix(scope) - desc (Recommended)` - Clear action + scope prefix / `Conventional: feat/fix(scope): desc` - Standard conventional commits / `Freeform` - No enforced format |
| 3 | Push to remote safety? | `Always ask before pushing (Recommended)` - Claude asks "Ready to push?" every time / `Push freely` - No confirmation needed |
| 4 | Security practices? | `Strict (Recommended)` - Never display secrets in terminal, use Read tool for sensitive files / `Standard` - Basic security awareness |

**If project management / writing / mixed:**

| # | Question | Options |
|---|----------|---------|
| 1 | Do you use git in your workflow? | `Yes, regularly` / `Sometimes` / `No` |
| 2 | File organization? | `Structured` - Folders and naming conventions matter / `Flexible` - Whatever works |
| 3 | Review workflow? | `Always review before finalizing` - Claude shows work before saving / `Trust and save` - Save directly |
| 4 | Security practices? | `Strict (Recommended)` - Never display sensitive data in terminal / `Standard` - Basic awareness |

If git = yes/sometimes, follow up with git-specific questions (branch strategy, commit format) in this round or Round 3.

### Round 3: Integration & Customization

| # | Question | Options |
|---|----------|---------|
| 1 | File headers - author name? | `No author in headers (Recommended)` - Leave empty / `Custom name` - Use Other to specify |
| 2 | Context management between sessions? | `Full (Recommended)` - Memory files + context restoration at session start / `Minimal` - Just CLAUDE.md, no memory system |
| 3 | Output destination? | `~/.claude/CLAUDE.md (global)` - Applies to all projects / `.claude/CLAUDE.md (project)` - This project only / `./CLAUDE.md (root)` - Project root |

Then ask about plugins:

| # | Question | Options |
|---|----------|---------|
| 4 | Which ClaudeCode-Plugin plugins do you use? (select all) | `code-review` - PR review agent / `qa-testing` - QA validation + test generation / `dev-workflow` - Structured dev methodology / `cc-memory` - Context restoration & memory / `analytics` - SaaS analytics tracking / `openclaw` - Session management |

**Note:** This question uses `multiSelect: true`. Since AskUserQuestion supports max 4 options, split into two questions if needed:
- Question A: `code-review` / `qa-testing` / `dev-workflow` / `cc-memory` (multiSelect)
- Question B: `analytics` / `openclaw` / `None of the above` (multiSelect)

## Step 3: Generate CLAUDE.md

Compose the file based on all answers. Follow these rules:

### Section Structure

Generate ONLY sections relevant to the user's answers. Never include empty or irrelevant sections.

**# Git Workflow** (if user uses git)
- Branch naming convention based on chosen strategy
- Commit format with examples matching chosen style
- Push rules (ask-first or auto)
- NEVER push without approval (if ask-first selected)
- For PR descriptions: analyze ALL commits in the branch, not just latest

**# Security & Stream Safety** (always include)
- If strict: NEVER use cat/echo/Bash to display passwords/secrets/tokens. ALWAYS use Read tool for sensitive files. Require explicit approval before showing sensitive data.
- If standard: Be careful with sensitive data in terminal output.

**# Communication Style** (always include)
- Tone based on choice (concise/detailed/balanced)
- No unnecessary emojis unless explicitly requested
- If developer: use markdown formatting, include file:line references when discussing code

**# File Header Rules** (always include)
- NEVER put "Created by Claude" in file headers
- If custom author name: always use specified name

**# Context & Documentation** (if full context management selected)
- Before any action: check local docs folders for relevant guidance
- ALWAYS check local folders before using WebFetch
- Prioritize understanding existing patterns before suggesting changes

**# Context Restoration** (if full context management selected)
- At session start or when losing context: read memory files
- NEVER invent information about a project - always read files first
- If no memory files found: ask user to describe context or offer to create them
- After significant work: update memory files
- Standard memory structure: PROJECT_STATE.md, ARCHITECTURE.md, DECISIONS.md, NEXT_STEPS.md, COMMANDS.md

**# Code Quality Principles** (if MVP-first or balanced)
- Prioritize working result over perfect architecture
- Security and data integrity are non-negotiable
- Defer optimization/DRY to V2 if time-consuming
- When stuck >2h: consider manual/simpler solution as valid approach

**# Work Principles** (for non-dev profiles, if quality-first or balanced)
- Prioritize accuracy over speed
- Always verify facts before presenting
- Structure information clearly with headings and lists

**# Technology Stack** (if detected or specified)
- Package manager and framework conventions
- Project-specific tooling from README or docs

### Plugin Integration Section

**Critical: If the user has installed ANY plugins, generate a dedicated section.** This is high-value -- it tells Claude when and how to use each installed plugin.

**# Plugins & Agents** (if any plugins selected)

For each installed plugin, add usage instructions:

**If `code-review` installed:**
```
- review-pr agent: Invoke before any PR for quality review. User says "review PR" → run review → process feedback → then tell user "PR ready for your review"
- NEVER create PR without review-pr pass
```

**If `qa-testing` installed:**
```
- qa-validate agent: Use to challenge implementation claims and validate features before release
- /qa-testing:unit-test-expert: Generate business-focused unit tests. Invoke after implementing features.
```

**If `dev-workflow` installed:**
```
- structured-dev-methodology agent: For complex multi-step implementations. Follows code-over-docs philosophy.
- /dev-workflow:implement: Launch structured dev session for feature implementation
- /dev-workflow:time-check: Invoke when detecting over-engineering, loops, or >2 failed attempts on same issue
- /dev-workflow:init-docs: Initialize or update architecture documentation
- /dev-workflow:new-feature: Prepare git environment for a new feature (checkout base, pull, clean branches)
```

**If `cc-memory` installed:**
```
- /cc-memory:memory: Use at session start to restore context, or to initialize memory files for a new project
- After significant work: update memory files (PROJECT_STATE.md is priority)
```

**If `analytics` installed:**
```
- saas-analytics-architect agent: For designing, auditing, and optimizing SaaS analytics tracking strategies
```

**If `openclaw` installed:**
```
- /openclaw:compact: Compress large sessions with intelligent summarization when context is getting large
- /openclaw:extract: Extract learnings from sessions before deletion
```

### PR Workflow Section

**# Pull Request Workflow** (if user uses git + feature branches)

Generate a numbered workflow. Adapt based on installed plugins:

Base workflow:
1. Make changes on feature branch
2. Commit with clean messages
3. Push and create PR with description covering ALL commits

If `code-review` installed, expand:
1. Make changes on feature branch
2. Commit with clean messages
3. User says "review PR" → invoke review-pr agent
4. Address all feedback
5. Ask user: "PR reviewed and feedback addressed. Ready to push?"
6. Only after approval: push and create PR
7. NEVER merge without user's explicit approval

### Writing Rules

1. Every instruction must be actionable -- use NEVER, ALWAYS, specific behaviors
2. No filler prose -- bullet points only
3. Bold critical keywords: **NEVER**, **ALWAYS**
4. Keep total length under 100 lines
5. Write in the selected language
6. Do NOT include sections the user didn't select features for
7. No emojis in the generated file

## Step 4: Write & Confirm

1. Show a preview summary: which sections were generated, total line count
2. Ask for confirmation before writing
3. Write to the chosen destination
4. Display final message:

```
CLAUDE.md generated at [path]
[N] sections | [M] lines | Language: [lang]

Sections: [list of generated section names]

Tip: Edit this file anytime to adjust Claude's behavior.
```

## Quality Reference

Example of well-structured CLAUDE.md output (tone and density reference -- personalize based on answers, do NOT copy verbatim):

```markdown
# Git Workflow
- NEVER push directly to main branch. Always create feature branches and PRs.
- NEVER run `git push` without explicit user approval. Ask first: "Ready to push to remote?"
- Branch naming: `feature/description` or `fix/description`
- Commit format: `add/update/fix/delete(scope) - Clear description` (NO emojis)

# Security & Stream Safety
- NEVER use cat, echo, or Bash to display passwords/secrets/tokens
- ALWAYS use Read tool for sensitive files (doesn't expose in terminal stream)
- If must show sensitive data: ask explicit user approval first

# Communication Style
- Direct and concise (CLI environment)
- No unnecessary emojis unless explicitly requested
- Use markdown for formatting, include file:line references when discussing code

# Context Restoration
- At session start: read memory files before acting
- NEVER invent information about a project - always read files first
- After significant work: update memory files (PROJECT_STATE.md is priority)

# Code Quality Principles
- Prioritize working MVP over perfect architecture
- Security and data integrity are non-negotiable
- When stuck >2h: consider manual solution as valid approach

# Plugins & Agents
- review-pr: Invoke before any PR. Process feedback before pushing.
- /dev-workflow:time-check: When detecting over-engineering or loops
- /cc-memory:memory: At session start to restore context
```
