# PixelClaw - Decisions

| Decision | Rationale | Date |
|----------|-----------|------|
| Adopt all skill-creator versions over originals | A/B test showed +3.5 avg improvement, 0 regressions | 2026-03-20 |
| Move unit-test-expert code examples to references/ | +8 pts from progressive disclosure, -17% token footprint | 2026-03-20 |
| Remove unused tools from allowed-tools (Grep, Write) | Rubric penalizes -2 per unused tool, cleaner composability | 2026-03-20 |
| Add Scope + Error Handling to all agents | Agents scored B+ without them, A with them | 2026-03-20 |
| Make horka-memory fully autonomous | User preference: no confirmation before creating memory files | 2026-03-20 |
| SessionStart hook for auto-context restore | Skills don't auto-trigger; hook injects additionalContext | 2026-03-20 |
| Pushy descriptions for better triggering | skill-creator best practice: "MUST run" + more trigger phrases | 2026-03-20 |
| Commit format: add/update/fix/delete(scope) - desc | No emojis, no Co-Authored-By footer per CLAUDE.md | 2026-03-20 |
