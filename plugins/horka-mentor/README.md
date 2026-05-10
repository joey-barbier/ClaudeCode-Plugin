# Mentor — Teaching AI for Junior Devs

An AI mentor that teaches you while you code — instead of coding for you.

## The Problem

Claude Code is powerful. Too powerful for a junior dev. Ask it to implement JWT auth and you get working code in 30 seconds. But you didn't learn anything. Next time you hit an auth problem, you're back at zero.

The Mentor changes the dynamic: it accompanies you, checks your understanding, teaches concepts before coding, and builds with you step-by-step. It takes longer. But you actually learn.

## What It Does

| Feature | How |
|---------|-----|
| **Detects new concepts** | Analyzes your request, checks your profile, identifies what you haven't seen before |
| **Assesses understanding** | Open questions only — predict output, spot the bug, explain in your words. Never yes/no |
| **Teaches before coding** | Analogies, examples from official docs (via Context7), exercises |
| **Builds step-by-step** | Codes WITH you, explains decisions as they happen, checks comprehension at each stage |
| **Tracks your progress** | Per-topic skill levels (unknown → learning → understood → confident) in ~/.claude/mentor/ |
| **Quizzes with spaced repetition** | Reviews topics at increasing intervals (D+1, D+3, D+7, D+14, D+30) |
| **Adapts to your profile** | Language, learning speed, prior stacks (cross-stack translation), security topics get directive mode |

## Requires Context7

**The Mentor refuses to start without Context7 MCP server installed.** This is intentional.

A mentor that teaches outdated APIs or deprecated patterns does more harm than good. Context7 provides access to official, current documentation. Without it, the Mentor cannot guarantee the quality of its teaching.

Install Context7 MCP server following the official instructions: https://github.com/upstash/context7

Bypass for pure concept work (no code examples): `/mentor --no-context7`

## Install

```bash
claude plugin install horka-mentor
```

## Two Skills

### `/mentor` — Teaching Mode

Two modes, same goal: you learn.

**Build mode (default)** — code together, learn by doing:
```
> /mentor
> I need to add WebSocket notifications when an order status changes

Mentor: Before we build this — in your own words, what's the difference
between WebSockets and regular HTTP requests?

[you answer]

Mentor: Good. One thing to add: [brief clarification].
Let's build this step by step. First, the connection setup...

[codes incrementally, explains at each step, checks comprehension]
```

**Learn mode** — full exploration before coding:
```
> /mentor learn
> I need to implement a task queue with Celery

Mentor: Task queues are a big topic. Let me check where you're at.

1. What happens when your web server receives a request that takes
   60 seconds to process? What does the user see?
2. Can you explain the difference between doing something synchronously
   vs. in the background?

[deeper exploration, analogies, examples, exercises, THEN coding]
```

### `/mentor-quiz` — Review & Retention

```
> /mentor-quiz

QUIZ — Async/Await (level: learning)

What does this code print, and in what order?

  async function foo() {
    console.log(1);
    await Promise.resolve();
    console.log(2);
  }
  foo();
  console.log(3);

Take your time.
```

Modes:
- `/mentor-quiz` — spaced repetition (reviews what's due today)
- `/mentor-quiz async` — quiz on a specific topic
- `/mentor-quiz all` — full review of all covered topics

## Proactive Mode

When enabled (default), the Mentor can intervene during regular Claude Code usage — not just when invoked explicitly.

If you ask Claude Code to implement something involving a concept you haven't demonstrated understanding of, the Mentor steps in:

```
[MENTOR] This request involves database transactions. We haven't covered that.
Before we code: what happens if step 2 of a 3-step database operation fails?

(type "skip" to bypass, or "/mentor proactif off" to disable proactive mode)
```

**Throttled**: max 2 interventions per session, cooldown after skip, never on trivial concepts.

## Memory

All stored in `~/.claude/mentor/` (global, shared across projects):

```
~/.claude/mentor/
├── dev-profile.md      # Your profile, language, stack, learning speeds
├── quiz-log.md         # Quiz history + spaced repetition schedule
└── topics/
    ├── async-await.md
    ├── jwt-auth.md
    ├── database-transactions.md
    └── ...
```

- **Private.** Never exposed to anyone but you.
- **Per-topic tracking.** Not a single "junior/senior" label — each concept has its own level.
- **Spaced repetition.** Topics are scheduled for review at increasing intervals.

## Security-Critical Topics

For auth, crypto, input validation, and other security topics: the Mentor switches to **directive mode**. No Socratic method — too dangerous to learn by failing.

1. Explains the correct approach first
2. Shows a vulnerable example and explains why it's dangerous
3. Shows the secure pattern
4. THEN quizzes to verify understanding

## Commands

| Command | What it does |
|---------|-------------|
| `/mentor` | Start mentor in build mode (default) |
| `/mentor learn` | Start mentor in learn mode |
| `/mentor --no-context7` | Start without Context7 (concepts only, no code examples) |
| `/mentor proactif on/off` | Enable/disable proactive interventions |
| `/mentor profil` | Show your current profile |
| `/mentor topics` | List all covered topics with levels |
| `/mentor-quiz` | Run spaced repetition quiz |
| `/mentor-quiz [topic]` | Quiz on a specific topic |
| `/mentor-quiz all` | Full review of all topics |

## Philosophy

The Mentor makes you slower today so you're faster tomorrow.

It doesn't code for you. It doesn't let you skip understanding. It doesn't pretend you know something when you don't. And it never asks a yes/no question — because "yes I know" teaches nothing.

Your profile is yours. Your progress is tracked. Your gaps are addressed. And when you're ready, the Mentor gets out of your way.

---

Built by [HORKA_TV](https://twitch.tv/horka_tv). Free. MIT.
