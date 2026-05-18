---
name: horka-agent-forge
description: "Enforced methodology for creating production-grade AI agent skills with mandatory quality gates. Orchestrates the full lifecycle: skill-creator for drafting + A/B testing, skill-evaluate for scoring + optimization, second A/B test, final validation. MANDATORY prerequisite: skill-creator:skill-creator and horka-skill-eval:horka-skill-evaluate must be installed. Use when user says 'create agent', 'new skill', 'forge skill', 'build agent', 'agent strategy', or wants to create any new skill or agent. Also invoke when user wants to improve an existing skill through the full quality pipeline."
allowed-tools: Skill, Read, Glob
---

# Agent Forge — Production-Grade Skill Creation Pipeline

This is a non-negotiable, gate-enforced methodology for creating AI skills that actually work in production. Every skill goes through 4 mandatory phases with A/B testing between each. No shortcuts. No "it looks good enough". Data-driven quality or nothing.

## Prerequisites Check (BLOCKING)

Before ANYTHING else, verify both required skills are available:

```
1. skill-creator:skill-creator — for drafting and A/B testing
2. horka-skill-eval:horka-skill-evaluate — for scoring and optimization
```

Check the available skills list in the system prompt. If EITHER skill is missing:

```
STOP. Do not proceed.

Tell the user:
"Agent Forge requires two mandatory skills that are not currently installed:
- skill-creator:skill-creator (for drafting + A/B testing)
- horka-skill-eval:horka-skill-evaluate (for scoring + optimization)

Install them first, then re-invoke /horka-agent-forge."
```

This is not a suggestion. This is a hard gate. Do NOT attempt to create skills manually without these tools. The whole point of this methodology is enforced quality — bypassing the tools defeats the purpose.

## Phase 1: Draft via skill-creator

Invoke `skill-creator:skill-creator` with the user's requirements.

skill-creator handles:
- Intent capture (what, when, output format)
- Interview for edge cases and dependencies
- Writing the SKILL.md draft
- Creating 2-3 test prompts

Let skill-creator drive this phase entirely. Do not override its process.

**Gate 1 output**: A drafted SKILL.md + test prompts ready for A/B testing.

## Example Flow

User: "I need a skill that generates changelog entries from git commits"

- **Phase 1**: skill-creator interviews, drafts `changelog-generator/SKILL.md` + 3 test prompts
- **Phase 2**: A/B test — with-skill covers 5/7 assertions vs 2/7 baseline — PASS
- **Phase 3**: skill-evaluate — 71/100 — fix description (+8), add error handling (+6) — 85/100 — PASS
- **Phase 4**: A/B retest — optimized 6/7 vs draft 5/7, 15% fewer tokens — PASS
- **Phase 5**: Report — Ready for production

## Phase 2: A/B Test — Draft vs No-Skill

This is handled by skill-creator's eval system:

1. For each test prompt, spawn 2 agents:
   - **With skill**: agent reads the drafted SKILL.md, then executes the task
   - **Without skill**: agent executes the same task with no skill (baseline)

2. Grade each run against assertions (completeness, accuracy, gotchas covered)

3. Generate the eval viewer for the user to review qualitative outputs

4. Collect user feedback

**Gate 2 criteria**:
- With-skill MUST outperform without-skill on >70% of assertions
- User feedback has no blocking issues
- If failing: revise skill in skill-creator and re-run A/B

Do NOT proceed to Phase 3 until Gate 2 passes.

## Phase 3: Optimize via skill-evaluate

Once the draft passes A/B testing, invoke `horka-skill-eval:horka-skill-evaluate` on the skill.

skill-evaluate scores 5 dimensions on 100 points:
- Structure (frontmatter, organization)
- Description (triggering accuracy)
- Instructions (clarity, progressive disclosure)
- Token efficiency (no bloat, no redundancy)
- Composability (works with other skills)

For each dimension scoring below 80/100:
1. Read the specific fix proposals from skill-evaluate
2. Apply the fixes to the SKILL.md
3. Re-run skill-evaluate to confirm improvement

**Gate 3 criteria**:
- Overall score >= 80/100
- No dimension below 70/100
- All "critical" fix proposals addressed

Do NOT proceed to Phase 4 until Gate 3 passes.

## Phase 4: A/B Test — Optimized vs Draft

Run a second round of A/B testing comparing the optimized version against the draft:

1. Same test prompts as Phase 2
2. **With optimized skill** vs **With original draft** (not without-skill — we already proved the skill helps)

3. Grade and compare:
   - Does the optimized version score equal or better on assertions?
   - Is it faster (fewer tokens, less time)?
   - Does user feedback prefer the optimized version?

**Gate 4 criteria**:
- Optimized version does not regress on any assertion
- Optimized version shows improvement on at least 1 dimension (quality, speed, or clarity)
- User approves

If the optimized version is WORSE on some metric: analyze why, decide with the user whether to keep the optimization or revert specific changes.

## Phase 5: Final Validation

Summary checklist before declaring the skill production-ready:

```
QUALITY GATES
  [x] Phase 2: A/B test passed (skill > no-skill)
  [x] Phase 3: skill-evaluate score >= 80/100
  [x] Phase 4: A/B test passed (optimized >= draft)

SKILL FILE
  [ ] SKILL.md frontmatter complete (name, description)
  [ ] Description is "pushy" (triggers on related queries, not just exact matches)
  [ ] Instructions are clear and explain WHY, not just WHAT
  [ ] Examples included for complex patterns
  [ ] Token-efficient (no redundant sections)

INTEGRATION
  [ ] Skill saved in correct location
  [ ] Plugin.json updated (if part of a plugin)
  [ ] marketplace.json updated (if in Public Marketplace)
  [ ] README updated (if applicable)
```

Present the final report to the user:

```
## Agent Forge Report

Skill: [name]
Location: [path]

Phase 2 (Draft A/B): PASS — [X]% assertion rate vs [Y]% baseline
Phase 3 (Evaluate):  PASS — [score]/100
Phase 4 (Optimized A/B): PASS — [delta] improvement

Ready for production.
```

## Quick Reference: Invocation Flow

```
User: "create a skill for X"
        |
        v
[1] /skill-creator:skill-creator  →  Draft SKILL.md + test prompts
        |
        v
[2] A/B Test: with-skill vs without-skill  →  Gate: >70% assertions
        |
        v
[3] /horka-skill-eval:horka-skill-evaluate  →  Gate: score >= 80/100
        |
        v
[4] A/B Test: optimized vs draft  →  Gate: no regression + improvement
        |
        v
[5] Final validation + report  →  Production-ready
```
