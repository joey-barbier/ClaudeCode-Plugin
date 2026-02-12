---
name: implement
description: Launch a structured development session with architecture-aware methodology. Use for complex features, multi-layer implementations, or when you need rigorous development practices.
argument-hint: describe the feature to implement
disable-model-invocation: true
context: fork
allowed-tools: Task
---

# Implement

Launch a structured development methodology session via the `structured-dev-methodology` agent.

## What This Does

Delegates to the `structured-dev-methodology` agent which will:
1. Ask clarifying questions about your project architecture
2. Verify documentation against actual code
3. Implement changes following the correct dependency order
4. Validate each step before proceeding

## Execution

Use the Task tool to launch the `structured-dev-methodology` agent with the user's request as the prompt. Pass the full context of what needs to be implemented.
