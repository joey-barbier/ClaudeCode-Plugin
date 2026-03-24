---
name: orka-skill-evaluate
description: Evaluate Claude skills against Anthropic's official best practices guide. Scores structure, description, instructions, token efficiency, and composability on a 100-point scale with fix proposals and before/after debrief. Use when user says "evaluate skill", "audit skills", "skill quality", "grade skills", "skill check", or after creating/modifying a skill.
allowed-tools: AskUserQuestion, Read, Edit, Glob, Bash
---

# Skill Evaluator

Evaluate skills against Anthropic's "The Complete Guide to Building Skills for Claude". Scores 5 categories on 100 points, proposes fixes, measures improvement.

## Scope

This skill evaluates SKILL.md files only. It does NOT:
- Test skill runtime behavior (use manual testing for that)
- Evaluate plugin.json or agent definitions
- Modify skills without explicit user approval

## Phase 1: Target Selection

### 1a. Scan for skills

Use Glob to find `**/skills/**/SKILL.md`. Exclude node_modules and .git.

If no SKILL.md found: "No skills found in this project. Nothing to evaluate." and stop.

### 1b. Ask user

Use `AskUserQuestion` with discovered skills as options. Include "All skills" if multiple found. Format: `plugin-name:skill-name`.

## Phase 2: Evaluate & Report

For each target skill:

### 2a. Gather data

1. Read the SKILL.md completely
2. Check parent folder name (kebab-case validation)
3. Check for references/, scripts/, assets/ subdirectories
4. Check for README.md presence (should NOT exist in skill folder)
5. Count words: `wc -w SKILL.md` via Bash

### 2b. Score against rubric

Read `references/rubric.md` for detailed criteria. Evaluate 5 categories:

| Category | Max | Key checks |
|----------|-----|------------|
| Structure & Technical | 20 | Frontmatter, naming, file org |
| Description Quality | 25 | WHAT + WHEN + triggers |
| Instructions Quality | 30 | Actionable steps, examples, error handling |
| Token Efficiency | 15 | Size, progressive disclosure |
| Composability | 10 | Scope clarity, allowed-tools |

Score STRICTLY. No sympathy points. Every deduction must cite a specific line or excerpt.

**Edge cases**:
- Malformed YAML: Score 0 on Structure, flag CRITICAL
- Missing `name` or `description`: Score 0 on respective category, flag CRITICAL
- Empty SKILL.md (only frontmatter): Score 0 on Instructions, flag CRITICAL

### 2c. Output report

```
## [plugin:skill-name] - Grade: [LETTER] ([SCORE]/100)

| Category              | Score | Status |
|-----------------------|-------|--------|
| Structure & Technical | XX/20 | [OK/WARN/FAIL] |
| Description Quality   | XX/25 | [OK/WARN/FAIL] |
| Instructions Quality  | XX/30 | [OK/WARN/FAIL] |
| Token Efficiency      | XX/15 | [OK/WARN/FAIL] |
| Composability         | XX/10 | [OK/WARN/FAIL] |

### Issues Found
1. **[CATEGORY]** [CRITICAL/MAJOR/MINOR] - [description]
   Line [N]: `[excerpt]`

### Strengths
- [what the skill does well]

Words: [N] | Est. tokens: [N x 1.3]
```

**Grades**: A+ (95-100), A (90-94), A- (85-89), B+ (80-84), B (75-79), B- (70-74), C+ (65-69), C (60-64), C- (55-59), D (40-54), F (0-39)

If evaluating ALL skills, append summary table with Average, Best, and Needs work.

## Phase 3: Fix Proposals

For each issue (ordered CRITICAL > MAJOR > MINOR):

```
### Fix [N]: [issue title]
Severity: [CRITICAL/MAJOR/MINOR] | Impact: +[N] pts

Before:
> [exact current text]

After:
> [exact proposed text]
```

Use `AskUserQuestion`: "Apply fixes?" with options: Apply all, Cherry-pick, Skip.

Apply approved fixes via Edit. Verify each edit succeeded.

## Phase 4: Debrief

ONLY if fixes were applied. Re-read and re-score with identical rubric.

```
## Debrief: [skill-name]

| Category              | Before | After | Delta |
|-----------------------|--------|-------|-------|
| Structure & Technical | XX/20  | XX/20 | +X    |
| ...                   | ...    | ...   | ...   |
| **TOTAL**             | **XX** | **XX**| **+X**|

Grade: [BEFORE] -> [AFTER]
Words: [BEFORE] -> [AFTER] ([+/-N])
```

## Rules

1. Score strictly -- rubric is law, no rounding up
2. Be specific -- every issue cites line number or exact excerpt
3. Fixes are concrete -- exact before/after text, never "consider improving"
4. Never invent -- if not assessable, mark N/A with reason
5. Self-applicable -- this skill must score A- or above by its own rubric
