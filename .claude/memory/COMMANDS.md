# PixelClaw - Useful Commands

## Evaluation
- `/skill-eval:orka-skill-evaluate` - Run skill evaluator on all SKILL.md files
- `/skill-creator:skill-creator` - Generate or improve skills with A/B testing

## Memory
- `/cc-memory:orka-memory` - Restore or init project context
- `/cc-memory:orka-save` - Save session progression

## Development
- `/dev-workflow:orka-git-new-feature` (or `GNF`) - Prepare git for new feature
- `wc -w plugins/*/skills/*/SKILL.md` - Word count all skills

## Git
- `git diff --stat HEAD~N HEAD` - See changes in last N commits
- `gh pr create --title "..." --body "$(cat <<'EOF' ... EOF)"` - Create PR
