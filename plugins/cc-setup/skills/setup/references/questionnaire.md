# Setup Questionnaire

Use `AskUserQuestion` in 3 rounds. Adapt questions based on user profile.

## Round 1: Profile & Philosophy

| # | Question | Options |
|---|----------|---------|
| 1 | What do you primarily use Claude Code for? | `Software development (Recommended)` - Writing code, debugging, building apps / `Project management` - Planning, tracking, documentation / `Writing & content` - Docs, articles, copywriting / `Mixed usage` - Combination of the above |
| 2 | What's your work philosophy? | `Ship fast, iterate (Recommended)` - Prioritize working results over perfect structure / `Quality first` - Thorough planning and testing before delivery / `Balanced` - Fast for new work, thorough for critical systems |
| 3 | How should Claude communicate? | `Concise & direct (Recommended)` - Short answers, bullet points, no fluff / `Detailed & explanatory` - Full context and reasoning / `Balanced` - Concise with detail when complex |
| 4 | CLAUDE.md language? | `English` / `French` |

## Round 2: Workflow

Adapt based on profile from Round 1.

### If software development:

| # | Question | Options |
|---|----------|---------|
| 1 | Git branch strategy? | `Feature branches + PRs (Recommended)` - Separate branch per feature, merge via PR / `Trunk-based` - Commit directly to main branch / `Gitflow` - develop/release/hotfix branches |
| 2 | Commit message format? | `Scoped: add/update/fix(scope) - desc (Recommended)` - Clear action + scope prefix / `Conventional: feat/fix(scope): desc` - Standard conventional commits / `Freeform` - No enforced format |
| 3 | Push to remote safety? | `Always ask before pushing (Recommended)` - Claude asks "Ready to push?" every time / `Push freely` - No confirmation needed |
| 4 | Security practices? | `Strict (Recommended)` - Never display secrets in terminal, use Read tool for sensitive files / `Standard` - Basic security awareness |

### If project management / writing / mixed:

| # | Question | Options |
|---|----------|---------|
| 1 | Do you use git in your workflow? | `Yes, regularly` / `Sometimes` / `No` |
| 2 | File organization? | `Structured` - Folders and naming conventions matter / `Flexible` - Whatever works |
| 3 | Review workflow? | `Always review before finalizing` - Claude shows work before saving / `Trust and save` - Save directly |
| 4 | Security practices? | `Strict (Recommended)` - Never display sensitive data in terminal / `Standard` - Basic awareness |

If git = yes/sometimes, follow up with git-specific questions in this round or Round 3.

## Round 3: Integration & Customization

| # | Question | Options |
|---|----------|---------|
| 1 | File headers - author name? | `No author in headers (Recommended)` - Leave empty / `Custom name` - Use Other to specify |
| 2 | Context management between sessions? | `Full (Recommended)` - Memory files + context restoration at session start / `Minimal` - Just CLAUDE.md, no memory system |
| 3 | Output destination? | `~/.claude/CLAUDE.md (global)` - Applies to all projects / `.claude/CLAUDE.md (project)` - This project only / `./CLAUDE.md (root)` - Project root |

### Plugin question:

| # | Question | Options |
|---|----------|---------|
| 4 | Which ClaudeCode-Plugin plugins do you use? (select all) | `code-review` / `qa-testing` / `dev-workflow` / `cc-memory` / `analytics` / `openclaw` |

Since AskUserQuestion supports max 4 options, split into two multiSelect questions:
- Question A: `code-review` / `qa-testing` / `dev-workflow` / `cc-memory`
- Question B: `analytics` / `openclaw` / `None of the above`
