# PixelClaw - Project State

## Current Branch
`fix/marketplace-sync` (14 modified files, 1 new references/ dir - uncommitted)

## Phase
Post-optimization. All 10 skills + 4 agents evaluated and upgraded via A/B test (skill-creator vs original).

## DONE

- [x] Marketplace v1.0.0 with 7 plugins
  - code-review, qa-testing, dev-workflow, cc-memory, cc-setup, analytics, openclaw
- [x] 4 READMEs (EN/FR/ES/DE) with demo GIF
- [x] skill-eval plugin added with rubric
- [x] All plugins bumped to v1.1.0
- [x] A/B test: skill-creator vs original on all 14 components (2026-03-20)
  - Average score: 89.2 -> 92.7 (+3.5)
  - Biggest wins: unit-test-expert (+8), review-pr (+8), qa-validate (+8)
  - All SC versions adopted
- [x] horka-memory made fully autonomous (no confirmation prompt)
- [x] SessionStart hook added to ~/.claude/settings.json for auto-context restore
- [x] unit-test-expert: code examples moved to references/framework-examples.md

## TODO

- [ ] Commit and push current optimization changes (14 files + 1 new)
- [ ] Create PR for the optimization work
- [ ] Test SessionStart hook in a fresh session

## Known Issues

- SessionStart hook injects context but relies on Claude deciding to invoke the skill
- Skills are installed via plugin cache, changes here need `plugin install` to propagate
