# ClaudeCode-Plugin

**[FR](README.fr.md)** | **[ES](README.es.md)** | **[DE](README.de.md)**

A collection of ready-to-use plugins for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) that enhance your AI assistant with best practices, safety guardrails, and productivity tools.

> Built by the team behind [LibTracker](https://app.libtracker.io/) — battle-tested workflows from building a real SaaS product with Claude Code.

## What Are Plugins?

Claude Code plugins extend what Claude can do in your terminal. They add:

- **Skills** — Commands you type (like `/memory` or `/setup`) to trigger specific workflows
- **Agents** — Specialized AI personas that activate automatically when relevant (like a code reviewer)
- **Hooks** — Automatic safety checks that run behind the scenes (like blocking accidental data loss)

You install only what you need. Each plugin works independently.

## Available Plugins

### code-review

**Your personal Senior Tech Lead.**
Reviews your code changes before they go live, catching bugs, security issues, and quality problems.

| What you get | How to use |
|---|---|
| PR review agent | Say "review PR" or activates automatically |

> Hook: Reminds you to review code before pushing changes on feature branches.

---

### qa-testing

**Quality assurance and testing.**
Validates your work like a Product Owner would, and generates tests for your code in any language.

| What you get | How to use |
|---|---|
| QA validation agent | Activates when validating features |
| Test generator | Type `/qa-testing:unit-test-expert` |

---

### dev-workflow

**Structured development methodology.**
Keeps you organized, prevents time waste, and protects against accidental data loss.

| What you get | How to use |
|---|---|
| Development methodology agent | Activates for complex implementations |
| Start implementation | Type `/dev-workflow:implement` |
| Time waste detector | Type `/dev-workflow:time-check` |
| Documentation setup | Type `/dev-workflow:init-docs` |
| New feature prep | Type `/dev-workflow:new-feature` |

> Hook: Blocks dangerous git commands (force push, hard reset, clean) to prevent data loss.

---

### cc-memory

**Session memory and context.**
Remembers your project between sessions so Claude never loses track of where you left off.

| What you get | How to use |
|---|---|
| Context restore / init | Type `/cc-memory:memory` |

> Hook: Automatically detects project memory files when a session starts and restores context.

---

### cc-setup

**Interactive setup assistant.**
Generates a personalized configuration file (CLAUDE.md) through a simple questionnaire. Works for developers, project managers, writers — anyone using Claude Code.

| What you get | How to use |
|---|---|
| CLAUDE.md generator | Type `/cc-setup:setup` |

---

### analytics

**SaaS analytics expert.**
Designs tracking strategies for web applications — what to measure, how to set it up, and what dashboards to build.

| What you get | How to use |
|---|---|
| Analytics architect agent | Activates for analytics-related tasks |

---

### openclaw

**Session management for OpenClaw gateway.**
Tools to manage long-running AI sessions — compress context, extract learnings, and maintain performance.

| What you get | How to use |
|---|---|
| Session compressor | Type `/openclaw:compact` |
| Learning extractor | Type `/openclaw:extract` |
| Context monitor | Run `context-monitor.sh` |
| Context guardian | Run `context-guardian-daemon.sh` |
| Gateway restart | Run `self-reboot.sh` |
| Blob cleaner | Run `clean-session-blobs.sh` |

> Hook: Reminds you to save learnings before large sessions get compressed.

## Installation

### Install a single plugin

Pick only what you need:

```bash
claude plugin add github:joey-barbier/ClaudeCode-Plugin/plugins/code-review
```

### Try before installing

Test a plugin temporarily:

```bash
claude --plugin-dir ./plugins/dev-workflow
```

### Install from a local copy

```bash
git clone https://github.com/joey-barbier/ClaudeCode-Plugin.git
claude plugin add ./ClaudeCode-Plugin/plugins/cc-memory
```

## Quick Start

1. **Install the plugins you want** (see above)
2. **Agents work automatically** — they activate when Claude detects a relevant situation
3. **Skills are commands** — type them when needed:
   ```
   /cc-setup:setup              # Set up your Claude Code preferences
   /cc-memory:memory            # Restore project context
   /dev-workflow:new-feature    # Prepare for a new feature
   /dev-workflow:implement      # Start building
   /dev-workflow:time-check     # Check if you're over-engineering
   /dev-workflow:init-docs      # Set up project documentation
   /qa-testing:unit-test-expert # Generate tests
   /openclaw:compact            # Compress a large session
   /openclaw:extract            # Save learnings from a session
   ```
4. **Hooks run silently** — protecting you from mistakes in the background

## Recommended Setups

| Profile | Recommended plugins |
|---|---|
| **Just starting with Claude Code** | `cc-setup` → run `/cc-setup:setup` |
| **Solo developer** | `cc-memory` + `dev-workflow` + `code-review` |
| **Team with code reviews** | `code-review` + `qa-testing` + `dev-workflow` |
| **Project manager or writer** | `cc-setup` + `cc-memory` |
| **OpenClaw gateway operator** | `openclaw` + `cc-memory` |

## Structure

```
plugins/
├── code-review/     # PR review agent + push guard hook
├── qa-testing/      # QA validation + test generation
├── dev-workflow/    # Dev methodology + git safety hook
├── cc-memory/       # Context restoration + auto-detect hook
├── cc-setup/        # Interactive CLAUDE.md generator
├── analytics/       # SaaS analytics tracking
└── openclaw/        # Session management + pre-compact hook
```

## License

MIT — free to use, modify, and share.
