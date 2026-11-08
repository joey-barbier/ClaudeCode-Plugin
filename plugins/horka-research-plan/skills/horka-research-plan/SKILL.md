---
name: horka-research-plan
allowed-tools: Agent, Workflow, Bash, Read, Write, Edit, Glob, Grep, WebFetch, WebSearch
description: >
  Right model, right effort, right moment, at every level: routes each sub-task to the cheapest tier
  that can do it (top tier judges, expert tier researches or codes, generalist validates and merges,
  cheapest tier does lookups), and every agent launched receives the same rule for its own sub-agents.
  Runs any multi-agent job in short waves with independent validators, an antagonist critic and a
  retrospective lessons file. Research mode ends in a sourced action plan (doc-style page, every number
  with URL and date); code mode runs a migration or rewrite with blind test writers before implementers,
  an integration branch green on a gate, and separate validation threads. Use when the user wants work
  split across agents or asks "a full check and a plan", "plan sourcé", "fais-moi un plan chiffré",
  "migre X vers Y avec plein d'agents", "lance plein d'agents", "quel modèle pour quelle tâche".
  Do NOT use for a single bug fix, a quick lookup, or a document with no decision to make.
---

# Research Plan — sourced action plan by a team of agents

You are the orchestrator. Agents do the reading; you do the briefing, the dedup, the reading between waves, and the page. The output is a plan someone can act on tomorrow morning: for each action, where we are, why we do it, what we expect back (a number, its source, a stop threshold), a diagram, dated steps.

Three rules that never bend:

1. **No number from memory.** Every figure has a URL that was opened, a date, and a status: verified / partial / hypothesis / not found. A figure that is not on the cited page is removed, not "fixed".
2. **No agent grades its own work.** Validators are never the researcher they check. The critic never wrote an action. Personas never saw the researchers' output before judging it.
3. **Nothing is created or scheduled.** No cron, no board change, no CI change, no PR to a product repo. Product needs and tasks go in a "to hand over" tab.

## Code mode (migration, rewrite, new foundation)

Same orchestrator, same "no agent grades its own work". Read `references/code-variant.md` before Phase 0 when the request is a migration or rewrite run by many agents. The five changes, in one line each:

1. Rule 1 becomes **no behaviour from memory**: the reference is the existing code on the remote `main`; every test cites `file:line`.
2. Rule 3 relaxes to **branches**: one worktree and branch per agent; a push only on the user's go in the thread; never a PR or merge without it.
3. The deliverable is an **integration branch green on the reference gate** plus the executable specs and a local progress board, not a page.
4. **Two-hand TDD**: blind testers (never open `Sources/`) write `Spec/API.md` then the tests; implementers make them pass without changing an assertion; a reconciliation agent resolves the drift between specs.
5. **Validation by separate threads** (code, AI behaviour, security) that receive only the branch and the base; a BLOCKED first pass is the expected result.

## Phase 0 — Framing and reality check (you, no agent, ~15 min)

0. **Read the lessons file** if it exists (`research-plan-lessons.md`, locations in `references/retrospective.md`). Apply its "Rules that held" to the common brief and run its "Next experiment". This is how the skill improves: the previous run wrote it for you.
1. Restate the question in one sentence. List constraints from CLAUDE.md, project memory and neighbouring work (do not duplicate another thread's actions: name them and link to them instead).
2. **Reality check in three states.** People confuse "what is shipped" with "what is merged". Build a table with, per topic: what a visitor sees in prod today / what is merged in `develop` (or the integration branch) but not deployed / what is still in an open PR.
   - Open the live site, sitemap, robots, `llms.txt`, pricing, changelog.
   - `git fetch origin main develop --depth 200` (or the repo's branch names), then `git log --oneline origin/main..origin/develop` and a diff of the public-facing files.
   - Open PRs through the REST API (`gh api repos/{owner}/{repo}/pulls?state=open`), since GraphQL is often blocked in sandboxes.
   - **Verify in code every capability the plan will rely on** (a webhook, an endpoint, a rate limit). Assumed features are the first thing that breaks a plan.
3. Freeze a **dated point zero**: visitors, clicks and impressions, signups, activation, paying, AI citations, stars, downloads. Unknown is written "unknown", never estimated.
4. Write the **common brief** (one page, saved to a file every agent reads): context, constraints, forbidden content (e.g. prices), output JSON schema, and the sentence "no number from memory: each number has a URL you opened and a date; list what you could not find".

## Phase 1 — Waves, short, with reading in between

A wave is 3 to 5 agents, 10 to 15 minutes, results written to files (`res/<role>.json`), never pasted whole into your context: read them in slices. Between waves you read, correct the brief, and decide the next wave. A 50-minute wave with no course correction is the failure mode to avoid: one bad brief costs the whole wave.

| Wave | Agents | Purpose |
|---|---|---|
| 1 · Readers first | 2 personas (the buyer; the third party your actions touch, e.g. an open-source maintainer) + 1 real-demand probe | Know what makes each reader try or flee **before** researching, and whether anyone searches the topic. See `references/briefs.md` for the probe method (StackOverflow API, HN Algolia with quoted queries, Google autocomplete EN and FR; GitHub as order of magnitude; no Google volumes: say so). |
| 2 · Researchers | 4 to 6, **one brief per action type** (content, distribution, partnerships, product-as-marketing, community, press / regulation) | Briefing per angle (competitors, benchmarks, other sectors) produces the same action four times. Each researcher returns the JSON in `references/schemas.md` with a "not found" list. |
| 3 · Dedup | code, not an agent | Normalise titles, merge duplicates, keep the union of sources. Do this before paying validators. |
| 4 · Validators | one per researcher, a different agent | Open every URL with WebFetch. Status per figure: verified / partial (exact figure, context to add) / unverifiable / false. Return corrections, never new figures. |
| 5 · Antagonist critic | 1 agent (if `horka-review:antagonist-reviewer` is installed, use that voice) | Duplicates, filler, fragile figures (ratios borrowed from players 100× bigger), brand risks, actions to drop with the reason, a 90-day sequence with two dated decision gates. |
| 6 · Feasibility and completeness | 1 agent per technical flow the plan assumes + 1 "what is missing?" agent | Check official docs and the code, cost under an explicit hypothesis, a demo plan; list fragile hypotheses and the measurement to put in place. |

Keep 8 to 12 actions. Everything dropped goes in a "what we do not do, and why" tab with the reason: several will come back once the funnel has numbers.

Code mode replaces waves 1 to 6 with S (spike and decision records) → T (blind testers) → I (implementers) → R (reconciliation) → V (validation threads) → M (mechanical steps); 5 to 8 agents per wave, one worktree each: table and briefs in `references/code-variant.md` and `references/briefs.md`.

If the `Workflow` tool is available, use `pipeline()` per researcher (researcher → validator) and a barrier only for dedup and the critic; see `references/workflow-skeleton.md`. Without it, use the `Agent` tool with one role per agent and the same schemas. Expect a concurrency cap: plan the waves, do not wait on a monolith.

## Phase 2 — Model and effort per role, at every level

The routing rule is general and recursive, not tied to a mode: `references/model-routing.md` gives the four tiers (top, expert, generalist, cheapest), the three questions that pick a tier for any sub-task, and the pass-down line to put at the end of every brief so that an expert agent launches generalist or cheapest sub-agents for its own mechanical steps and lookups, and a generalist agent still launches cheapest ones. An agent never launches a tier above its own; it reports back instead. Give every agent the absolute path of that file.

| Role | Model | Effort | Why |
|---|---|---|---|
| Orchestrator (this session), critic, personas, synthesis | the most capable model available | high (medium for pure orchestration) | Judgement. On Fable 5.1 changing effort does not break the prompt cache. |
| Researchers | the expert tier (e.g. Opus) | high | Long tool sequences. A lazy result ("skipped a source, stopped early") is an effort problem, not a model problem. |
| Validators, demand probe, counting | the generalist tier (e.g. Sonnet) | medium | Mechanical: open, compare, count. |
| Code mode: authors, blind testers, implementers, antagonist reviewers, reconciliation | the expert tier (e.g. Opus) | high | Judgement on every line; a lazy spec is an effort problem. |
| Code mode: merging a branch, rerunning the gate, "is it green?", the progress board | the generalist tier (e.g. Sonnet) | medium | Mechanical, no decision. |
| Wide lookups inside any agent ("where is X used", inventory of a folder) | a sub-agent of the cheapest tier (e.g. Haiku, the `Explore` agent type), launched by the agent that needs the answer | low | The cost is the context the parent re-reads on every later turn (500 M of 566 M tokens on the Guild run were cache reads), not the output. |

Nothing picks the model automatically: a sub-agent inherits its parent's model unless the brief says otherwise. Put the delegation rule, with its losing cases, in every brief (text in `references/model-routing.md`): delegate a wide search whose conclusion is all you keep; never delegate content you need in full, a single `grep`, or anything that needs exactness. Measure it with tokens per model and cache-read tokens per agent in the scorecard.

Cost is not measured beyond the scorecard: write the real cost of each wave and adjust next time.

## Phase 3 — The page

One doc-style HTML page, hash-routed, with a sidebar; no Markdown copy (one deliverable, no legacy). If the project has a design system or a `doc-style` skill, use it; otherwise follow `references/page-structure.md` (cream background, white cards with a 2 px black border and hard shadow, colour chips with meaning, "The essentials" box on every tab, tables over paragraphs, SVG block diagrams).

Tabs: Essentials (actions table: first datable step, effort, sourced expectation) · Where we really are (three states) · Big picture diagram · 90 days · one tab per action (meta chips effort / result / cost / product need / when; "Where we are / Why / What we expect"; diagram; steps; expectations with status chips) · What we do not do · Rules and risks · Real demand · Personas · Reference figures · Product needs and tasks to hand over · Method and limits.

Expectations borrowed from bigger players are presented as orders of magnitude with a dated stop threshold, never as forecasts. Mobile: no horizontal scroll at 400 px (check with Playwright: `document.documentElement.scrollWidth` ≤ viewport on every tab).

Code variant: no page. The deliverable is the `integration` branch green on the reference gate, the `Spec/` folders, and the local progress board (doc-style HTML regenerated from the worktrees and the transcripts: tokens per model all-in and output, wall time vs cumulated agent time, parallelism factor, tests green, verdicts of the validation threads). The board replaces progress messages in the thread.

## Phase 4 — Before delivering

- [ ] No price, no unsourced figure, no action that redefines a feature owned by another thread (needs go to the hand-over tab).
- [ ] Nothing created or scheduled (code variant: nothing pushed, merged or scheduled without the user's go in the thread; commits carry no attribution trailer).
- [ ] Rendering checked on desktop and phone; links point to the right domain.
- [ ] Summary in the thread under 80 words: link, verdict, what waits on the user.
- [ ] Phase 5 done: lessons file rewritten, three lines "what I learned" in the summary.

## Phase 5 — Step back, then write the lessons file (mandatory, ~15 min)

The run is not finished when the page is delivered. It is finished when the next run can start smarter. Full method and templates in `references/retrospective.md`; the short version:

1. **Facts (you).** Write the scorecard: per wave, agents, models and effort, minutes, failures, what you changed in the brief mid-run; candidates → kept actions; figures opened / verified / partial / false / not found; what was discovered late; tokens per model (all-in and output, read from the transcripts: the harness count ignores cache reads), wall time vs cumulated agent time; code variant: tests green on the gate, blocking points found by reviewers and validation threads, agents relaunched and why.
2. **Judgement (a fresh agent, not you).** Rule 2 applies to the orchestrator too: a critic agent that did not write the page reads the brief, the scorecard, the page and the previous lessons file, and returns at most five lessons (`situation → what we did → next time`), a verdict on the previous run's experiment (kept or dropped, why), and **one** experiment for the next run with the measure that will tell if it worked.
3. **Merge (you).** Rewrite the lessons file in full: next experiment, rules that held, rules that changed, mistakes to watch, last 10 scorecard lines. Under 4 KB, no secret, nothing the user could not read. Then put three lines "what I learned" in the delivery summary, with the file's path.

One experiment per run, never two: a change that is not measured alone cannot be kept or dropped on evidence.

## What you say when something is not available

- The local `doc-style`, `marketingSkills` or `Jean-Pierre` skills are not reachable from a cloud session: say that their roles were played by agents.
- Reddit, socket.dev, PageSpeed and similar may be blocked: say which figures are therefore secondary.
- No search-volume tool: demand is measured with indices, not volumes, and the page says so.
- No memory folder and no repository: the lessons file goes to `~/.claude/research-plan-lessons.md`, and the summary says so.
