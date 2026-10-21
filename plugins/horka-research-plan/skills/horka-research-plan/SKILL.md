---
name: horka-research-plan
allowed-tools: Agent, Workflow, Bash, Read, Write, Edit, Glob, Grep, WebFetch, WebSearch
description: >
  Multi-agent research that ends in a sourced action plan, delivered as one doc-style HTML page.
  Runs a reality check in three states (prod / develop / open PRs), then short waves of agents:
  personas and a real-demand probe FIRST, researchers briefed per action type, code-level dedup,
  independent validators that open every URL, an antagonist critic, then feasibility and completeness.
  Every number carries a source URL, a date and a status chip; nothing is created or scheduled.
  Ends with a retrospective that rewrites a lessons file, read again at the start of the next run.
  Invoke when the user asks for "a full check and a plan", "how do we get discovered", "which channel",
  "a go-to-market", "a sourced plan", "un check complet et un plan", "plan sourcé", "fais-moi un plan
  chiffré", or any strategy / marketing / product question that needs evidence rather than opinion.
  Do NOT use for: code changes, a quick factual lookup, a document with no decisions to make.
---

# Research Plan — sourced action plan by a team of agents

You are the orchestrator. Agents do the reading; you do the briefing, the dedup, the reading between waves, and the page. The output is a plan someone can act on tomorrow morning: for each action, where we are, why we do it, what we expect back (a number, its source, a stop threshold), a diagram, dated steps.

Three rules that never bend:

1. **No number from memory.** Every figure has a URL that was opened, a date, and a status: verified / partial / hypothesis / not found. A figure that is not on the cited page is removed, not "fixed".
2. **No agent grades its own work.** Validators are never the researcher they check. The critic never wrote an action. Personas never saw the researchers' output before judging it.
3. **Nothing is created or scheduled.** No cron, no board change, no CI change, no PR to a product repo. Product needs and tasks go in a "to hand over" tab.

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

If the `Workflow` tool is available, use `pipeline()` per researcher (researcher → validator) and a barrier only for dedup and the critic; see `references/workflow-skeleton.md`. Without it, use the `Agent` tool with one role per agent and the same schemas. Expect a concurrency cap: plan the waves, do not wait on a monolith.

## Phase 2 — Model and effort per role

| Role | Model | Effort | Why |
|---|---|---|---|
| Orchestrator (this session), critic, personas, synthesis | the most capable model available | high (medium for pure orchestration) | Judgement. On Fable 5.1 changing effort does not break the prompt cache. |
| Researchers | the expert tier (e.g. Opus) | high | Long tool sequences. A lazy result ("skipped a source, stopped early") is an effort problem, not a model problem. |
| Validators, demand probe, counting | the generalist tier (e.g. Sonnet) | medium | Mechanical: open, compare, count. |

Cost is not measured for this split: write the real cost of each wave in the orchestration scorecard and adjust next time.

## Phase 3 — The page

One doc-style HTML page, hash-routed, with a sidebar; no Markdown copy (one deliverable, no legacy). If the project has a design system or a `doc-style` skill, use it; otherwise follow `references/page-structure.md` (cream background, white cards with a 2 px black border and hard shadow, colour chips with meaning, "The essentials" box on every tab, tables over paragraphs, SVG block diagrams).

Tabs: Essentials (actions table: first datable step, effort, sourced expectation) · Where we really are (three states) · Big picture diagram · 90 days · one tab per action (meta chips effort / result / cost / product need / when; "Where we are / Why / What we expect"; diagram; steps; expectations with status chips) · What we do not do · Rules and risks · Real demand · Personas · Reference figures · Product needs and tasks to hand over · Method and limits.

Expectations borrowed from bigger players are presented as orders of magnitude with a dated stop threshold, never as forecasts. Mobile: no horizontal scroll at 400 px (check with Playwright: `document.documentElement.scrollWidth` ≤ viewport on every tab).

## Phase 4 — Before delivering

- [ ] No price, no unsourced figure, no action that redefines a feature owned by another thread (needs go to the hand-over tab).
- [ ] Nothing created or scheduled.
- [ ] Rendering checked on desktop and phone; links point to the right domain.
- [ ] Summary in the thread under 80 words: link, verdict, what waits on the user.
- [ ] Phase 5 done: lessons file rewritten, three lines "what I learned" in the summary.

## Phase 5 — Step back, then write the lessons file (mandatory, ~15 min)

The run is not finished when the page is delivered. It is finished when the next run can start smarter. Full method and templates in `references/retrospective.md`; the short version:

1. **Facts (you).** Write the scorecard: per wave, agents, models and effort, minutes, failures, what you changed in the brief mid-run; candidates → kept actions; figures opened / verified / partial / false / not found; what was discovered late; cost only if the harness reported it, otherwise `unknown`.
2. **Judgement (a fresh agent, not you).** Rule 2 applies to the orchestrator too: a critic agent that did not write the page reads the brief, the scorecard, the page and the previous lessons file, and returns at most five lessons (`situation → what we did → next time`), a verdict on the previous run's experiment (kept or dropped, why), and **one** experiment for the next run with the measure that will tell if it worked.
3. **Merge (you).** Rewrite the lessons file in full: next experiment, rules that held, rules that changed, mistakes to watch, last 10 scorecard lines. Under 4 KB, no secret, nothing the user could not read. Then put three lines "what I learned" in the delivery summary, with the file's path.

One experiment per run, never two: a change that is not measured alone cannot be kept or dropped on evidence.

## What you say when something is not available

- The local `doc-style`, `marketingSkills` or `Jean-Pierre` skills are not reachable from a cloud session: say that their roles were played by agents.
- Reddit, socket.dev, PageSpeed and similar may be blocked: say which figures are therefore secondary.
- No search-volume tool: demand is measured with indices, not volumes, and the page says so.
- No memory folder and no repository: the lessons file goes to `~/.claude/research-plan-lessons.md`, and the summary says so.
