# CLAUDE.md Generation Rules

## Section Structure

Generate ONLY sections relevant to user answers. Never include empty or irrelevant sections.

### Hierarchy Guidelines

- Use `#` for main categories
- Use `##` numbered subsections when a category groups 3+ related concerns (e.g., Workflow groups Git + Quality + Verification)
- Put critical rules (NEVER/ALWAYS) at the top of each section
- For non-absolute rules, add contextual qualifiers ("For non-trivial changes", "Skip this for obvious fixes")
- Simple sections (2-3 bullets) stay flat under `#` with no `##` subsections

### Developer Sections

**# Workflow** (if developer profile -- groups related subsections)

`## 1. Git Discipline` (if user uses git)
- Branch naming convention based on chosen strategy
- Commit format with examples matching chosen style
- Push rules (ask-first or auto)
- NEVER push without approval (if ask-first selected)
- For PR descriptions: analyze ALL commits in the branch, not just latest

`## 2. Code Quality` (if MVP-first or balanced)
- Make every change as simple as possible -- minimal code impact
- Find root causes, no temporary fixes
- For non-trivial changes: pause and consider a more elegant approach
- Skip elegance pursuit for obvious, small fixes -- don't over-engineer

`## 3. Verification` (always for dev profiles)
- Never present work as complete without demonstrating it works
- Run tests, check output, diff behavior when relevant
- Ask: "Would a senior engineer approve this?"

If `quality-first` philosophy, replace Code Quality with:

`## 2. Quality Standards` (if quality-first)
- Every change must have tests proving correctness
- Find root causes -- no temporary fixes, no workarounds
- Ask: "Would a senior engineer approve this?"
- Challenge your own work before presenting it

**# Security** (always include)
- If strict: NEVER display passwords/secrets/tokens via cat, echo, or Bash -- CLI is in stream mode. ALWAYS use Read tool for sensitive files.
- If standard: Be careful with sensitive data in terminal output.

**# Communication** (always include)
- Tone based on choice (concise/detailed/balanced)
- If developer: include `file:line` references when discussing code
- If concise: lead with the answer, skip trailing summaries

**# Context** (if full context management)
- At session start: read memory files to restore context
- Before any action: check local docs before WebFetch
- After significant work: update memory files (PROJECT_STATE.md priority)
- NEVER invent information -- always read files first

**# File Headers** (always include)
- NEVER put "Created by Claude" in file headers
- If custom author name: always use specified name

**# Technology Stack** (if detected or specified)
- Package manager and framework conventions

### Non-Developer Sections

**# Work Principles** (for non-dev profiles)
- Prioritize accuracy over speed
- Always verify facts before presenting
- Show work for validation before saving (if review-first selected)
- When uncertain, ask rather than guess

**# Organization** (if structured files selected)
- Respect existing folder and naming conventions
- Structure documents with clear headings and sections

## Plugin Integration

**Critical**: If user has ANY plugins, generate a dedicated section.

**# Plugins & Agents** -- For each installed plugin:

| Plugin | Instructions |
|--------|-------------|
| code-review | `review-pr agent`: Invoke before any PR. NEVER create PR without review pass. |
| qa-testing | `qa-validate agent`: Challenge implementation claims. `/horka-qa-testing:unit-test-generate`: Generate tests. |
| dev-workflow | `structured-dev-methodology agent`: For complex multi-file implementations. `/horka-dev-workflow:mvp-time-guardian`: Over-engineering detection. `/horka-dev-workflow:init-docs`: Architecture docs. `/horka-dev-workflow:git-new-feature`: Git prep. |
| cc-memory | `/horka-memory:restore`: Session start context restore. Update memory after significant work. |
| analytics | `saas-analytics-architect agent`: Analytics tracking strategy. |
| openclaw | `/horka-openclaw:session-compact`: Compress sessions. `/horka-openclaw:session-extract`: Extract learnings. |

## PR Workflow

**# PR Workflow** (if git + feature branches)

Base: 1. Changes on feature branch -> 2. Commit -> 3. Push + create PR

If `code-review` installed, expand to 4 steps max:
1. Changes on feature branch -> commit with clean messages
2. User says "review PR" -> invoke review-pr -> address feedback
3. Ask: "Ready to push?" -> push and create PR
4. NEVER merge without user approval

## Writing Rules

1. Every instruction must be actionable -- use NEVER, ALWAYS for absolute rules
2. Add contextual qualifiers for non-absolute rules ("For non-trivial changes", "Skip this for obvious fixes")
3. No filler prose -- bullet points only
4. Bold critical keywords: **NEVER**, **ALWAYS**
5. Put critical rules (NEVER/ALWAYS) at the top of each section
6. Keep total length under 100 lines
7. Write in the selected language
8. Do NOT include sections the user didn't select
9. Use `##` numbered subsections to group 3+ related concerns within a `#` category
10. Do NOT duplicate rules already in Claude's system prompt (e.g., "no emojis" is built-in)

## Quality Reference

Example output (tone/density reference -- personalize, do NOT copy verbatim):

```markdown
# Workflow
## 1. Git Discipline
- NEVER push directly to main -- feature branches and PRs only
- Ask before pushing: "Ready to push?"
- Branch naming: `feature/description` or `fix/description`
- Commit format: `add/update/fix/delete(scope) - Clear description`

## 2. Code Quality
- Make every change as simple as possible -- minimal code impact
- Find root causes, no temporary fixes
- For non-trivial changes: consider a more elegant approach
- Skip elegance for obvious fixes -- don't over-engineer

## 3. Verification
- Never present work as complete without proving it works
- Run tests, diff behavior against main when relevant

# Security
- NEVER display secrets via cat/echo/Bash -- CLI is in stream mode
- ALWAYS use Read tool for sensitive files

# Communication
- Direct and concise -- lead with the answer
- Include `file:line` references when discussing code

# Plugins & Agents
- `review-pr`: Before any PR -- never create without review
- `/horka-dev-workflow:mvp-time-guardian`: When detecting over-engineering or loops
- `/horka-memory:restore`: Session start context restore
```
