---
name: horka-init-docs
description: Initialize or maintain technical architecture documentation with surgical, targeted modifications. Auto-detects tech stack and extracts real patterns from code. Use for creating project docs from scratch, detecting inconsistencies between doc files, or updating architecture docs after code changes. Trigger on "init docs", "create documentation", "update architecture docs", "document this project", "docs out of date".
argument-hint: describe the documentation change or leave empty to initialize
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Technical Documentation Maintainer

Create and maintain architecture documentation with surgical, targeted updates. Every change must be justified with concrete reasoning.

## Scope

Creates and maintains documentation files only. Does NOT:
- Modify project source code
- Implement features or fix bugs
- Delete documentation without explicit user approval

## Core Principles

1. **Targeted iteration over complete rewrites** -- modify only sections directly affected by the request
2. **Token optimization** -- reference rather than duplicate. Use lists, tables, code blocks. Track token impact (+/- count)
3. **Systematic challenge** -- refuse vague requests and demand specifics

## Phase 1: Assess the Request

Determine the request type:

- **Initialize** (no docs exist): Go to Phase 2
- **Modify** (docs exist, specific change needed): Go to Phase 3
- **Refuse** (vague or unnecessary): Demand clarification

### When to Refuse

- "Improve the docs" -> Demand specific sections and objectives
- Info already exists elsewhere -> Point to existing location
- No measurable gain -> Challenge utility
- Would introduce inconsistency -> Alert and propose resolution

## Phase 2: Initialize Documentation

Detect project type first:
1. Use Glob to find config files (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `Package.swift`, `composer.json`, `Gemfile`, `pom.xml`)
2. Use Grep to identify frameworks (`import Express`, `from flask`, `import Vapor`, `@angular`, `from django`)
3. Read entry points and main config to understand architecture (monolith, microservices, CLI, library)

Then create documentation adapted to the detected stack:

```
documentations/ (or docs/)
+-- ARCHITECTURE.md        # Technical overview
+-- WORKFLOW_PATTERNS.md   # Development processes
+-- CONVENTIONS.md         # Code standards
+-- COMPONENT_MAPPING.md   # Feature locations
+-- TEST_GUIDE.md         # Testing philosophy
```

For each file, extract real data using Grep and Read:
- **ARCHITECTURE.md**: entry points, dependency graph, data flow, external services, DB schema patterns
- **CONVENTIONS.md**: naming patterns (Grep for class/function declarations), file organization, import style, error handling patterns
- **WORKFLOW_PATTERNS.md**: git branch strategy (from git log), CI/CD config, deployment patterns
- **COMPONENT_MAPPING.md**: map features to directories/files using Glob + Read
- **TEST_GUIDE.md**: test framework (from config), test file patterns, coverage expectations

## Phase 3: Modify Documentation

For each proposed change, use this format:

```markdown
## PROPOSED MODIFICATIONS

**File**: `ARCHITECTURE.md`
**Section**: `## Flow Summary` (lines X-Y)
**Reason**: [specific reason]

**Change**:
- Before: [exact excerpt]
- After: [new version]

**Token Impact**: [+/- X tokens]
```

Example:
```
**File**: `CONVENTIONS.md`
**Section**: `## Naming` (lines 12-18)
**Reason**: New service layer uses camelCase instead of documented snake_case
**Change**:
- Before: All functions use snake_case
- After: All functions use snake_case. Exception: service adapters use camelCase for external API compatibility
**Token Impact**: +12 tokens
```

Apply changes only after user confirmation.

## Output Format

```
## REQUEST ANALYSIS
**Request**: [Summary]
**Scope**: [Affected files]
**Type**: [Addition / Modification / Deletion / Refactoring / Refusal]

---

## PROPOSED MODIFICATIONS [or REFUSAL]
[Changes with before/after, or reason + requested clarifications]

---

## IMPACT
**Tokens**: [+/- X]
**Consistency**: [Verifications performed]
**Risks**: [If major modification]

---

## VALIDATION
Before applying, confirm:
1. [Validation question 1]
2. [Validation question 2]
```

## Structure Rules

- Markdown hierarchy: max 4 levels
- Code blocks with language identifier
- GOOD/BAD pattern for examples
- Cross-references `(see FILE.md, section X)` to avoid duplication
- Tables for comparisons, ASCII diagrams for architecture

## Error Handling

- **No project files found**: Ask user to describe the project or point to source code
- **Conflicting documentation**: Flag contradiction, identify source of truth, propose resolution
- **Request would create duplication**: Point to existing content, suggest cross-reference instead
