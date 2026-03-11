# CLAUDE.md Generation Rules

## Section Structure

Generate ONLY sections relevant to user answers. Never include empty or irrelevant sections.

**# Git Workflow** (if user uses git)
- Branch naming convention based on chosen strategy
- Commit format with examples matching chosen style
- Push rules (ask-first or auto)
- NEVER push without approval (if ask-first selected)
- For PR descriptions: analyze ALL commits in the branch, not just latest

**# Security & Stream Safety** (always include)
- If strict: NEVER use cat/echo/Bash to display passwords/secrets/tokens. ALWAYS use Read tool for sensitive files.
- If standard: Be careful with sensitive data in terminal output.

**# Communication Style** (always include)
- Tone based on choice (concise/detailed/balanced)
- No unnecessary emojis unless explicitly requested
- If developer: use markdown formatting, include file:line references

**# File Header Rules** (always include)
- NEVER put "Created by Claude" in file headers
- If custom author name: always use specified name

**# Context & Documentation** (if full context management)
- Before any action: check local docs folders for relevant guidance
- ALWAYS check local folders before using WebFetch

**# Context Restoration** (if full context management)
- At session start: read memory files
- NEVER invent information - always read files first
- After significant work: update memory files (PROJECT_STATE.md priority)

**# Code Quality Principles** (if MVP-first or balanced)
- Prioritize working result over perfect architecture
- Security and data integrity are non-negotiable
- When stuck >2h: consider manual/simpler solution

**# Work Principles** (for non-dev profiles)
- Prioritize accuracy over speed
- Always verify facts before presenting

**# Technology Stack** (if detected or specified)
- Package manager and framework conventions

## Plugin Integration

**Critical**: If user has ANY plugins, generate a dedicated section.

**# Plugins & Agents** - For each installed plugin:

| Plugin | Instructions |
|--------|-------------|
| code-review | `review-pr agent`: Invoke before any PR. NEVER create PR without review pass. |
| qa-testing | `qa-validate agent`: Challenge implementation claims. `/qa-testing:unit-test-expert`: Generate tests. |
| dev-workflow | `structured-dev-methodology agent`: Autonomous for complex implementations. `/time-check`: Over-engineering detection. `/init-docs`: Architecture docs. `/new-feature`: Git prep. |
| cc-memory | `/cc-memory:memory`: Session start context restore. Update memory after significant work. |
| analytics | `saas-analytics-architect agent`: Analytics tracking strategy. |
| openclaw | `/openclaw:compact`: Compress sessions. `/openclaw:extract`: Extract learnings. |

## PR Workflow

**# Pull Request Workflow** (if git + feature branches)

Base: 1. Changes on feature branch -> 2. Commit -> 3. Push + create PR

If `code-review` installed, expand:
1. Changes on feature branch
2. Commit with clean messages
3. User says "review PR" -> invoke review-pr agent
4. Address feedback
5. Ask: "Ready to push?"
6. Push and create PR
7. NEVER merge without user approval

## Writing Rules

1. Every instruction must be actionable -- use NEVER, ALWAYS
2. No filler prose -- bullet points only
3. Bold critical keywords: **NEVER**, **ALWAYS**
4. Keep total length under 100 lines
5. Write in the selected language
6. Do NOT include sections the user didn't select
7. No emojis in the generated file

## Quality Reference

Example output (tone/density reference -- personalize, do NOT copy verbatim):

```markdown
# Git Workflow
- NEVER push directly to main branch. Always create feature branches and PRs.
- NEVER run `git push` without explicit user approval.
- Branch naming: `feature/description` or `fix/description`
- Commit format: `add/update/fix/delete(scope) - Clear description` (NO emojis)

# Security & Stream Safety
- NEVER use cat, echo, or Bash to display passwords/secrets/tokens
- ALWAYS use Read tool for sensitive files

# Communication Style
- Direct and concise (CLI environment)
- No unnecessary emojis unless explicitly requested

# Plugins & Agents
- review-pr: Invoke before any PR. Process feedback before pushing.
- /dev-workflow:time-check: When detecting over-engineering or loops
- /cc-memory:memory: At session start to restore context
```
