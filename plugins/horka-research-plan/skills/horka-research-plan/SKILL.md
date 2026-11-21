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

## What this skill is for, and how much of it to run

Four things matter most. The three rules above never bend in either lane; what the lane changes is how many waves and passes run around them:

1. **A third party validates before anything ships**, on proof that is real and out of reach of what it judges (section Verification).
2. **Short returns.** Six words state a problem; twenty lines hide it. Every brief imposes the report format: one verdict line, then one line per point (`file:line` or URL · blocking / minor / pre-existing · problem · fix), 15 lines at most, no account of what was done. The same holds for messages to the user.
3. **The right model for each task, inherited down the chain** (Phase 2): the top tier hands task 1 to an expert agent, which gets its lookups done by the cheapest tier.
4. **The run is a task graph, shown on a board** (next section): a task starts as soon as what it reads is done, a blocked task blocks only its descendants, and the user follows tasks, models and tokens on one page instead of progress messages.

**Size the run before Phase 0.** Pick the lane and say which in one line:

| Lane | When | What runs |
|---|---|---|
| Short | The question is about the user's own systems (one repo, one API, a config), or a change to one module or one connector | 2 or 3 agents (code, external API probe), one antagonist pass, the report in the thread. No personas, no page. Every figure still gets a validator that is not its researcher and opens the URL. In code: the four default gates below, nothing more. |
| Full | Market or marketing research; a migration or rewrite across several targets | Everything below. |

If a plan for the same question already exists in the thread or the board, do not write a second one: supply facts to it. A session launched as a probe or a helper never runs this skill on its own.

## The task graph and the board (every run, both lanes)

Read `references/task-graph.md` before Phase 0 ends. The base of every run:

1. **Write the graph before launching anything.** `graph.json` in a board folder outside the repo: one node per task (framing, probes, researchers or implementers, validators, critic, user decisions, retrospective) with its `deps`, role, model and effort, and from 15 tasks a `lane` (infra, payment, screens…) so the board draws one column per lane and shows each one advancing at its own pace. A dependency is a file or a decision the task reads, never "it came before".
2. **Launch by the graph, not by the wave.** `scripts/board/set.py <board> <id> <status> [agent-id]` after every launch and every result; it prints what can start now, and you launch those in the same turn, within the concurrency cap. Tasks that do not depend on a blocked or slow task keep going. A decision waiting on the user is a node with status `user`: only its descendants wait.
3. **Publish the board at the start and at every change that matters.** `set.py` rebuilds `board.html`: essentials, waiting on the user, the graph by status, then the debrief from the transcripts (tokens per task and per model, cache reads, wall vs cumulated agent time). On the page, a click on a task opens its detail and its links both ways, the graph zooms and goes full screen, and a sticky contents bar reaches every part: a 300-task run stays readable. One message with its link; then the board replaces progress messages.
4. **Survive a cut.** Committed work is bundled outside the session while there is no remote branch; after a restart, `running` tasks become `interrupted` and are relaunched from their last commit.

The short lane keeps the graph (five to ten nodes); it skips nothing here.

## Code mode (migration, rewrite, new foundation)

Read `references/code-variant.md` before Phase 0. In one line each: no behaviour from memory (the reference is the remote `main`, every test cites `file:line`); one worktree and branch per agent, a push only on the user's go, never a PR or merge without it; blind testers write `Spec/API.md` then the tests before any implementer, who changes no assertion; a reconciliation agent merges into `integration`, which must be green on the reference gate; validation by separate threads that receive only the branch and the base, where a BLOCKED first pass is the expected result. Probe every external dependency for real before any spec that depends on it, and run the gate as the CI will (same user, cores, runner) from wave 1.

## Verification: what counts as proof (every run, both lanes)

Checks are what let many agents run without the user reading every diff. They hold only if they are real, out of reach of what they judge, and few.

1. **Run the real thing.** Green tests are not proof; the product doing the job is. Before any push, run it end to end as a user would (a real run of the job, a browser through Playwright or Chrome, a simulator, an API harness) and paste the trace: steps, screenshot or output, what failed and why. Write the start-and-drive steps once in a `verify` script or skill next to the code and make it fast and reliable before relying on it. Research mode's equivalent: a validator opens every URL.
2. **Migrations: compare old and new.** A differential harness (old and new on the same inputs, outputs diffed) checked against the **approved-differences list** the user signed, plus property tests for pure engines (wave T of `references/code-variant.md`). Old tests drift from production; the diff does not.
3. **A change never touches the check that judges it.** Every verdict names the commit SHA it checked; a push during a review makes it stale. Review rules, specs and the lessons file are read from the base branch, never from the branch under review. "No assertion changed" is checked by a script (the diff of `Spec/` holds only the listed renames), not trusted.
4. **Three rounds, then the user.** A check still red after three fix rounds stops: one message with the check, the three attempts and the open question. A flaky test is never rerun, slept or skipped until green: find the cause, or delete it and write down why.
5. **Improve one reviewer, do not stack more.** One validator per artefact plus one antagonist; a second pass reads only the corrections and the earlier verdict. Separate validation threads (code, behaviour, security) only in code mode (wave V of `references/code-variant.md`) or when a security boundary moves.
6. **Severity on every point:** blocking / minor / pre-existing. Pre-existing (already on the base) is not fixed on this branch: it goes to the hand-over list.
7. **A new gate starts in observe mode** for one run (it logs what it would have blocked; false positives are reviewed), then enforces. Every deliverable states how it was verified, "none" included.

**Default gates (short lane):** a real probe of each external dependency; one antagonist review of the decision record (by an agent that did not write it; it covers what ships now, not the next deliveries); blind tests for pure engines and security boundaries; the verify run and a third-party validation before the push.

**Cheap checks first, in parallel, never "just to see"**: Phase 0 reads the base branch's CI status and reports a red base at once; when each check runs is in `references/code-variant.md` (Gates).

## Phase 0 — Framing and reality check (you, no agent, ~15 min)

0. **Read the lessons file** if it exists (`research-plan-lessons.md`, locations in `references/retrospective.md`). Apply the rules whose trigger matches this run and run its "Next experiment".
1. Restate the question in one sentence, and name the lane (short or full). List constraints from CLAUDE.md, project memory and neighbouring work (do not duplicate another thread's actions: name them and link to them instead).
2. **Reality check in three states.** People confuse "what is shipped" with "what is merged". Build a table with, per topic: what a visitor sees in prod today / what is merged in `develop` (or the integration branch) but not deployed / what is still in an open PR.
   - Open the live site, sitemap, robots, `llms.txt`, pricing, changelog.
   - `git fetch origin main develop --depth 200` (or the repo's branch names), then `git log --oneline origin/main..origin/develop` and a diff of the public-facing files.
   - Open PRs through the REST API (`gh api repos/{owner}/{repo}/pulls?state=open`), since GraphQL is often blocked in sandboxes.
   - **Verify in code every capability the plan will rely on** (a webhook, an endpoint, a rate limit): Glob and Grep the repo for it. Assumed features are the first thing that breaks a plan.
3. Freeze a **dated point zero**: visitors, clicks and impressions, signups, activation, paying, AI citations, stars, downloads. Unknown is written "unknown", never estimated.
4. Write the **common brief** (one page, saved to a file every agent reads): context, constraints, forbidden content (e.g. prices), output JSON schema, and the sentence "no number from memory: each number has a URL you opened and a date; list what you could not find".

## Phase 1 — Waves, short, with reading in between

A wave is 3 to 5 agents, 10 to 15 minutes, results in files (`res/<role>.json`) read in slices, never pasted whole. Between waves you read, correct the brief, decide the next one: a 50-minute wave with no correction lets one bad brief cost the whole wave.

| Wave | Agents | Purpose |
|---|---|---|
| 1 · Readers first | 2 personas (the buyer; the third party your actions touch, e.g. an open-source maintainer) + 1 real-demand probe | Know what makes each reader try or flee, and whether anyone searches the topic, **before** researching (probe method in `references/briefs.md`). |
| 2 · Researchers | 4 to 6, **one brief per action type** (content, distribution, partnerships, product-as-marketing, community, press / regulation) | Per angle (competitors, benchmarks) yields the same action four times. JSON of `references/schemas.md`, with a "not found" list. |
| 3 · Dedup | code, not an agent | Normalise titles, merge duplicates, keep the union of sources. Do this before paying validators. |
| 4 · Validators | one per researcher, a different agent | Open every URL. Per figure: verified / partial / unverifiable / false. Corrections only, never new figures. |
| 5 · Antagonist critic | 1 agent (if `horka-review:antagonist-reviewer` is installed, use that voice) | Duplicates, filler, fragile figures (ratios from players 100× bigger), brand risks, actions to drop, a 90-day sequence with two dated decision gates. |
| 6 · Feasibility and completeness | 1 agent per technical flow the plan assumes + 1 "what is missing?" agent | Docs and code per brick, cost under a stated hypothesis; fragile hypotheses and the measurement to put in place. |

Keep 8 to 12 actions. Everything dropped goes in a "what we do not do, and why" tab with the reason: several will come back once the funnel has numbers.

Waves are how you think about the run; the graph is what you execute (`references/task-graph.md`): a researcher's validator starts when that researcher is done, not when the whole wave is.

Code mode replaces waves 1 to 6 with S (spike and decision records) → T (blind testers) → I (implementers) → R (reconciliation) → V (validation threads) → M (mechanical steps); 5 to 8 agents per wave, one worktree each: table and briefs in `references/code-variant.md` and `references/briefs.md`.

With the `Workflow` tool: `pipeline()` per researcher → validator, a barrier only for dedup and the critic (`references/workflow-skeleton.md`); otherwise the `Agent` tool, one role per agent. Expect a concurrency cap.

## Phase 2 — Model and effort per role, at every level

The routing rule is recursive and mode-free: `references/model-routing.md` (give every agent its absolute path) holds the four tiers, the three questions that pick one, and the pass-down line ending every brief. An agent never launches a tier above its own; it reports back instead.

| Role | Model | Effort | Why |
|---|---|---|---|
| Orchestrator (this session), critic, personas, synthesis | the most capable model available | high (medium for pure orchestration) | Judgement. On Fable 5.1 changing effort does not break the prompt cache. |
| Researchers | the expert tier (e.g. Opus) | high | Long tool sequences. A lazy result ("skipped a source, stopped early") is an effort problem, not a model problem. |
| Validators, demand probe, counting | the generalist tier (e.g. Sonnet) | medium | Mechanical: open, compare, count. |
| Code mode: authors, blind testers, implementers, antagonist reviewers, reconciliation | the expert tier (e.g. Opus) | high | Judgement on every line; a lazy spec is an effort problem. |
| Code mode: merging a branch, rerunning the gate, "is it green?", the progress board | the generalist tier (e.g. Sonnet) | medium | Mechanical, no decision. |
| Wide lookups inside any agent ("where is X used", inventory of a folder) | a sub-agent of the cheapest tier (e.g. Haiku, the `Explore` agent type), launched by the agent that needs the answer | low | The cost is the context the parent re-reads on every later turn (500 M of 566 M tokens on the Guild run were cache reads), not the output. |

**How an agent delegates** (`references/model-routing.md`; put its rule and losing cases in every brief). With a shell: `scripts/ask.sh <tier> <folder> "<question and answer format>"` (a read-only `claude -p` on a cheaper model; give its absolute path). Without: one line `ASK PARENT: <tier> · <question> · <answer format>`, then hand back. A single command, it runs itself; a lookup or mechanical check of two turns or more, it delegates; never delegate content needed in full or anything that needs exactness. Dry-run it for 30 s first: sub-agents often cannot launch agents (14/11/2026: 379 agents, none launched by another). A sub-agent inherits its parent's model unless the brief says otherwise. Measure with tokens per model and cache reads per agent.

Cost is not measured beyond the scorecard: write the real cost of each wave and adjust next time.

## Phase 3 — The page

One doc-style HTML page, hash-routed, with a sidebar; no Markdown copy (one deliverable, no legacy). If the project has a design system or a `doc-style` skill, use it; otherwise follow `references/page-structure.md` (cream background, white cards with a 2 px black border and hard shadow, colour chips with meaning, "The essentials" box on every tab, tables over paragraphs, SVG block diagrams).

Tabs: Essentials · Where we really are · Big picture · 90 days · one tab per action ("Where we are / Why / What we expect", diagram, steps, expectations with status chips) · What we do not do · Rules and risks · Real demand · Personas · Reference figures · To hand over · Method and limits (details in `references/page-structure.md`).

Expectations borrowed from bigger players are presented as orders of magnitude with a dated stop threshold, never as forecasts. Mobile: no horizontal scroll at 400 px (check with Playwright: `document.documentElement.scrollWidth` ≤ viewport on every tab).

Code variant: no page. The deliverable is the `integration` branch green on the gate, the `Spec/` folders, and the board (tests green, verify trace and validation verdicts with their SHA in its essentials).

## Phase 4 — Before delivering

- [ ] No price, no unsourced figure, no action that redefines a feature owned by another thread (needs go to the hand-over tab).
- [ ] Nothing created or scheduled (code variant: nothing pushed, merged or scheduled without the user's go in the thread; commits carry no attribution trailer).
- [ ] Rendering checked on desktop and phone; links point to the right domain.
- [ ] Summary in the thread under 80 words: link, verdict, what waits on the user.
- [ ] Board up to date and published: every node in its true end state, last debrief rebuilt.
- [ ] Proof attached: verify trace (or validator report), every verdict with its SHA and severities, "how verified" stated.
- [ ] Phase 5 done: lessons file rewritten, three lines "what I learned" in the summary.

## Phase 5 — Step back, then write the lessons file (mandatory, ~15 min)

The run is not finished when the page is delivered. It is finished when the next run can start smarter. Full method and templates in `references/retrospective.md`; the short version:

1. **Facts (you).** The scorecard of `references/retrospective.md`, filled from the board: tokens per model from the transcripts (cache reads included), times, figures by status, late discoveries, and how each reviewer did: what it found, what it missed that someone found later, what it flagged wrongly.
2. **Judgement (a fresh agent, not you).** Rule 2 applies to the orchestrator too: a critic agent that did not write the page reads the brief, the scorecard, the page and the previous lessons file, and returns at most five lessons (`situation → what we did → next time`), a verdict on the previous run's experiment (kept or dropped, why), and **one** experiment for the next run with the measure that will tell if it worked.
3. **Merge (you).** Rewrite the lessons file in full: next experiment, rules (each with a trigger, a check and its origin; a rule enters after two occurrences and leaves when it stops firing), last 10 scorecard lines. Under 4 KB, no secret. Three lines "what I learned" go in the delivery summary, with the file's path.

One experiment per run, never two: a change that is not measured alone cannot be kept or dropped on evidence.

## What you say when something is not available

- The local `doc-style`, `marketingSkills` or `Jean-Pierre` skills are not reachable from a cloud session: say that their roles were played by agents.
- Reddit, socket.dev, PageSpeed and similar may be blocked: say which figures are therefore secondary.
- No search-volume tool: demand is measured with indices, not volumes, and the page says so.
- No memory folder and no repository: the lessons file goes to `~/.claude/research-plan-lessons.md`, and the summary says so.
