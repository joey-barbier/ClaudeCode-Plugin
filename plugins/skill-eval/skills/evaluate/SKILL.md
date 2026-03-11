---
name: evaluate
description: Evaluate Claude skills against Anthropic's official best practices guide. Scores structure, description, instructions, token efficiency, and composability on a 100-point scale with fix proposals and before/after debrief. Use when user says "evaluate skill", "audit skills", "skill quality", "grade skills", or "skill check".
allowed-tools: AskUserQuestion, Read, Write, Edit, Glob, Grep, Bash
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

If no SKILL.md found: tell user "No skills found in this project. Nothing to evaluate." and stop.

### 1b. Ask user

Use `AskUserQuestion` with discovered skills as options. Include "All skills" if multiple found. If only 1 skill exists, confirm and proceed.

Format options as: `plugin-name:skill-name` (derived from path).

## Phase 2: Evaluate & Report

For each target skill:

### 2a. Gather data

1. Read the SKILL.md completely
2. Check parent folder name (kebab-case validation)
3. Check for references/, scripts/, assets/ subdirectories
4. Check for README.md presence (should NOT exist in skill folder)
5. Count words: `wc -w SKILL.md`

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
- Malformed YAML (missing `---`, broken syntax): Score 0 on Structure, flag as CRITICAL
- Missing `name` or `description` field: Score 0 on respective category, flag CRITICAL
- Empty SKILL.md (only frontmatter, no instructions): Score 0 on Instructions, flag CRITICAL

### 2c. Output report

For each skill, use this exact format:

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

**Status**: OK (>= 80% of max), WARN (50-79%), FAIL (< 50%)

**Grades**: A+ (95-100), A (90-94), A- (85-89), B+ (80-84), B (75-79), B- (70-74), C+ (65-69), C (60-64), C- (55-59), D (40-54), F (0-39)

**Concrete example** (abbreviated):

```
## dev-workflow:new-feature - Grade: B+ (82/100)

| Category              | Score | Status |
|-----------------------|-------|--------|
| Structure & Technical | 18/20 | OK     |
| Description Quality   | 22/25 | OK     |
| Instructions Quality  | 24/30 | WARN   |
| Token Efficiency      | 12/15 | OK     |
| Composability         | 6/10  | WARN   |

### Issues Found
1. **Instructions** MAJOR - No error handling for git conflicts
   Line 31: `git branch --merged...`
2. **Composability** MINOR - No explicit scope boundary
```

If evaluating ALL skills, append a summary:

```
## Summary

| Skill | Grade | Score | Top Issue |
|-------|-------|-------|-----------|
| ... | ... | .../100 | ... |

Average: [N]/100 | Best: [name] | Needs work: [name]
```

## Phase 3: Fix Proposals

For each issue (ordered CRITICAL > MAJOR > MINOR):

### 3a. Show fix

```
### Fix [N]: [issue title]
Severity: [CRITICAL/MAJOR/MINOR] | Impact: +[N] pts

Before:
> [exact current text]

After:
> [exact proposed text]
```

### 3b. Ask user

Use `AskUserQuestion`: "Apply fixes?" with options:
- Apply all fixes
- Cherry-pick (then ask which ones, max 4 per question)
- Skip fixes

### 3c. Apply

Use Edit tool to apply approved fixes. Verify each edit succeeded.

## Phase 4: Debrief

ONLY run this phase if fixes were applied in Phase 3.

### 4a. Re-evaluate

Re-read modified SKILL.md files. Re-score with identical rubric.

### 4b. Comparison report

```
## Debrief: [skill-name]

| Category              | Before | After | Delta |
|-----------------------|--------|-------|-------|
| Structure & Technical | XX/20  | XX/20 | +X    |
| Description Quality   | XX/25  | XX/25 | +X    |
| Instructions Quality  | XX/30  | XX/30 | +X    |
| Token Efficiency      | XX/15  | XX/15 | +X    |
| Composability         | XX/10  | XX/10 | +X    |
| **TOTAL**             | **XX** | **XX**| **+X**|

Grade: [BEFORE] -> [AFTER]
Words: [BEFORE] -> [AFTER] ([+/-N])
Est. tokens: [BEFORE] -> [AFTER] ([+/-N])
Fixes applied: [N] | Skipped: [N]
Remaining issues: [list or "None"]
```

## Rules

1. **Score strictly** -- rubric is law, no rounding up
2. **Be specific** -- every issue cites line number or exact excerpt
3. **Fixes are concrete** -- exact before/after text, never "consider improving"
4. **Never invent** -- if a criterion is not assessable, mark N/A with reason
5. **Self-applicable** -- this skill must score A- or above by its own rubric
