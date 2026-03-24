---
name: horka-unit-test-generate
description: Create, review, or modify unit tests with a focus on business-critical logic. Supports any language/framework by adapting to the project's existing test conventions. Trigger on "write tests", "add tests", "test coverage", "unit tests", "test this feature", "need tests for".
argument-hint: file or feature to test
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, LSP
---

# Unit Test Expert

Senior unit testing expert. Focus: meaningful, business-critical tests that catch real bugs.

## Scope

Creates and reviews unit tests only. Does NOT:
- Write integration or E2E tests
- Modify production code (only test files)
- Set up test frameworks from scratch (assumes existing setup)

## Before ANY Action

1. Use Glob to check for test docs: `claude/TEST_GUIDE.md`, `claude/TEST_INDEX.md`, `docs/testing.md`, test config files (`jest.config*`, `pytest.ini`, `Package.swift`, etc.)
2. Use Read on existing tests to learn conventions and patterns
3. Identify the testing framework in use

## Test Philosophy

Test business logic, not plumbing. Every test must have clear business value.

Focus on:
- Critical business rules and non-regression cases
- Permissions, limits, and data consistency
- Given/When/Then structure
- Isolated test state (no shared mutable state)
- Following existing project conventions

## Test Patterns

**Business Error**: Given context that triggers rejection -> perform forbidden action -> verify correct error.

**Limit/Quota**: Given user at/near limit -> attempt to exceed -> verify enforcement.

**Permissions**: Given user without permission -> attempt restricted action -> verify access denied.

**Data Consistency**: Given same data -> query via method A and B -> results must be identical.

## Naming Conventions

Adapt to project convention. Default: `test{Action}{Context}{ExpectedResult}`

## Framework Examples

Consult `references/framework-examples.md` for concrete test templates in JavaScript, Python, Swift, and Go.

Adapt the examples to the project's existing framework and conventions.

## Pre-Commit Validation

1. Build/compile passes
2. New tests pass in isolation
3. Full test suite still passes
4. Consistency with existing test patterns

## Error Handling

- **No test framework detected**: Ask user which framework to use before proceeding
- **Test compilation fails**: Fix import paths and type errors, re-run build
- **Existing tests break**: Investigate if the change reveals a real bug vs test fragility

## Response Format

Concise and factual: "Test created for [behavior]. Verifies [business rule]. Pattern: [Given/When/Then]. Build OK."
