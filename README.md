# ClaudeCode-Plugin

**[FR](README.fr.md)** | **[ES](README.es.md)** | **[DE](README.de.md)**

Ready-to-use plugins that make Claude Code actually useful in real projects. Memory, code review, dev workflow, safety guards — built from months of daily usage.

> Also, to track your external libraries, CVEs and more, check out [LibTracker](https://app.libtracker.io/).

![Demo](assets/demo.gif)

## Install all plugins at once

Browse and install everything from inside Claude Code:

```bash
/plugin marketplace add joey-barbier/ClaudeCode-Plugin
```

Then use `/plugin` → **Discover** tab to browse and install what you need.

Or install plugins individually by following the steps below.

## Getting Started

Follow the steps in order. Each one builds on the previous.

### Step 1: Configure Claude Code (first time only)

Install `cc-setup` and run the setup wizard.

```bash
claude plugin add joey-barbier/ClaudeCode-Plugin/plugins/cc-setup
```
Then type `/cc-setup:setup` — it asks about your git workflow, communication style, security preferences, and installed plugins, then generates a personalized `CLAUDE.md` that tells Claude how YOU work.

### Step 2: Give Claude a memory

Install `cc-memory` so Claude remembers your project between sessions. No more re-explaining where you left off after a compact or a new conversation.

```bash
claude plugin add joey-barbier/ClaudeCode-Plugin/plugins/cc-memory
```

**What happens:** When you open Claude, it automatically detects your project files and restores full context — what's done, what's not, what to work on next. Type `/cc-memory:memory` to initialize memory on a new project (it scans your codebase and creates PROJECT_STATE, ARCHITECTURE, DECISIONS, NEXT_STEPS, and COMMANDS files) or restore context manually at session start.

### Step 3: Add the tools you need

Pick what fits your workflow. Each plugin works independently.

---

#### code-review — *Autonomous*

**Your personal Senior Tech Lead.** Activates automatically when you say "review PR" or when Claude detects code ready to push. Does a full first pass (architecture, security, quality) so when you review, you focus on what matters — not typos and misplaced ifs.

```bash
claude plugin add joey-barbier/ClaudeCode-Plugin/plugins/code-review
```

> Hook included (runs automatically, no command needed): Blocks push to main/master. Reminds you to review before pushing feature branches.

---

#### qa-testing — *Mixed (autonomous + command)*

**QA validation and test generation.** Two components — one autonomous, one manual.

```bash
claude plugin add joey-barbier/ClaudeCode-Plugin/plugins/qa-testing
```

| Component | How it works |
|---|---|
| QA validation agent | Autonomous — activates when you claim a feature is done, challenges your assertions and tests edge cases |
| `/qa-testing:unit-test-expert` | Generates business-focused unit tests: permissions, limits, data consistency. Reads your existing test conventions first, then writes tests that match your patterns. Supports any language/framework |

---

#### dev-workflow — *Commands + autonomous agent*

**Structured development methodology.** The agent activates for complex implementations. The skills are commands you type when needed.

```bash
claude plugin add joey-barbier/ClaudeCode-Plugin/plugins/dev-workflow
```

| Component | How it works |
|---|---|
| Dev methodology agent | Autonomous — activates for complex multi-layer work |
| `/dev-workflow:implement` | Launches a structured dev session: analyzes your architecture, verifies docs against code, then implements changes in the right dependency order with validation at each step |
| `/dev-workflow:new-feature` | Prepares git for a new feature: switches to main/develop, pulls latest, offers to delete merged branches, then creates a `feature/` branch |
| `/dev-workflow:time-check` | Detects when you're stuck in a loop: same error 3+ times, over-engineering, debates without decisions. Proposes the fastest working solution with a clear action plan |
| `/dev-workflow:init-docs` | Creates architecture docs (ARCHITECTURE.md, CONVENTIONS.md, etc.) from your codebase, or surgically updates existing docs when patterns change |

> Hook included (runs automatically, no command needed): Blocks dangerous git commands (force push, hard reset, checkout ., restore ., clean, branch -D).

---

#### analytics — *Autonomous*

**SaaS analytics expert.** Activates when you work on tracking, funnels, or conversion. Designs what to measure, how to set it up, and what dashboards to build.

```bash
claude plugin add joey-barbier/ClaudeCode-Plugin/plugins/analytics
```

---

#### openclaw — *Commands*

**Session management for OpenClaw gateway.** Tools for long-running AI sessions — compress context, extract learnings, maintain performance.

```bash
claude plugin add joey-barbier/ClaudeCode-Plugin/plugins/openclaw
```

| Component | How it works |
|---|---|
| `/openclaw:compact` | Compresses large AI sessions: scans for files over 20MB, extracts decisions/configs/learnings, archives the original, and clears the session to minimal size |
| `/openclaw:extract` | Extracts learnings from the current session and saves them to memory files — use before deleting sessions or when context is getting heavy |
| Shell scripts | `context-monitor.sh`, `context-guardian-daemon.sh`, `self-reboot.sh`, `clean-session-blobs.sh` |

> Hook included (runs automatically, no command needed): Warns you to save learnings before large sessions get compacted.

## How plugins work

Three types of components, three behaviors:

| Type | Behavior | Example |
|---|---|---|
| **Agents** | Autonomous — Claude activates them when relevant | Code review agent triggers on "review PR" |
| **Skills** | Commands — you type them when needed | `/cc-memory:memory` to restore context |
| **Hooks** | Silent — run in background, protect you from mistakes | Blocks `git push --force` automatically |

## Questions?

I stream live on Twitch while building with Claude Code. Come ask questions, see the plugins in action, or suggest new ones.

**[twitch.tv/horka_tv](https://twitch.tv/horka_tv)**

## License

MIT — free to use, modify, and share.
