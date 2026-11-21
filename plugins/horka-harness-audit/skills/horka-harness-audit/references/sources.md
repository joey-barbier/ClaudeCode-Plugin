# Sources: what the articles say, and what holds up

Checked on 2026-11-20. Every figure below was read on the page given, by a reader other than the one who first reported it. Anything marked "not found" must not be quoted as evidence.

## Contents
1. The harness article in one page
2. Figures: verified, nuanced, not found
3. Where the article departs from its own sources
4. Primary sources, by criterion
5. Reading list
6. How to treat a "resources" thread

## 1. The harness article in one page

"Unlock Opus 5.5: The Harness Guide for Agents That Actually Ship", X article by @0xTrackmind, 2026-10-23, https://x.com/0xTrackmind/status/2113644871529418857

**Thesis.** Agent = model + harness. The model reasons and proposes the next action; the harness is everything else. When an agent says "done" on red tests, edits the wrong file, forgets a decision or retries the same command, a longer prompt and a different model rarely fix it, because the missing piece is around the model.

**Find the broken layer before touching the prompt.**

| Symptom | Layer | Fix lives in |
|---|---|---|
| Misunderstands the request | prompt | the instruction |
| Fluent but wrong or out of date | context | what it is shown |
| Claims done without proof, does something unsafe, forgets between sessions | harness | checks, permissions, state |
| Repeats itself | loop | a stop or change-of-approach rule |
| Several agents duplicate or collide | graph | how the pieces coordinate |

**Seven failures and their fix.**

1. Did a different job than asked → a contract before starting: goal, constraints, deliverable, "done when", what needs approval, and what to do if blocked (stop and write down what was tried, never guess).
2. Lost in the codebase → a map, not a manual. Context is an attention budget, not storage. One short root file that says where things live; details opened only when the task needs them.
3. Says done when it is not → evidence is the gate. Deterministic tools first (types, lint, tests); one script whose success line is the only definition of done. Then split builder and verifier: the verifier did not write the change and looks for reasons to reject, criterion by criterion, with evidence quoted.
4. Did something never approved → permissions outside the model. Sort actions by how hard they are to undo: reversible runs freely with a trace, outward-facing needs approval, hard to reverse is closed. A closed lane is not a high threshold: thresholds move when someone is in a hurry.
5. Retries the same thing → classify the failure (timeout: retry with a pause; bad arguments: repair the call; missing information: fetch it; test failure: change the code, never the test; permission denied: ask a human; same failure twice with nothing changed: stop), then cap attempts, time and spend.
6. Forgot what was decided → state outside the conversation: current step, decisions and their reason, artefacts, open risks, next action.
7. Made the same mistake twice → turn the lesson into infrastructure. The ladder: explain it, checklist it, automate the check, enforce it. Every line of the agent guide should trace back to an incident.

**Levels.** 0: a prompt and a model. 1: a contract, a short map, a few well-defined tools. 2: stored state, real checks, a bounded loop. 3: permissions, traces, recovery paths, human approval gates. Add a layer only after watching the failure it prevents; keep the harness smaller than the problem it controls.

**Its own caveat.** Parts of a harness compensate for today's model weaknesses and turn into dead weight as models improve. A harness that is never pruned becomes the next thing to debug.

**Its ten questions** are criteria C1 to C10 of `grid.md`.

## 2. Figures: verified, nuanced, not found

| Claim | Source | Date | Status | Nuance |
|---|---|---|---|---|
| A coding agent went from 52.8 % to 66.5 % on Terminal Bench 2.0 with the model unchanged | https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering | 2026-02-17 | verified | The model was gpt-5.2-codex. The same page reports 59.6 % for another model on an earlier harness version that had not gone through the same improvement loop: the gain belongs to a harness-model pair, not to harnesses in general. |
| From outside the top 30 to the top 5 | same page | 2026-02-17 | verified | The ranking as stated by the vendor on its publication date. |
| "Doom loops" and a middleware that notices repeated edits to the same file | same page | 2026-02-17 | verified | It is a nudge to reconsider, with no stated threshold, and the page says the model can still continue down the same path. |
| Three engineers, about 1,500 pull requests, every line written by the agent | https://openai.com/index/harness-engineering/ | 2026-02-11 | verified | Read through an archive copy (the site refuses automated readers). Same page: five months, on the order of a million lines, team grown to seven. |
| Early slowness came from an under-specified environment, not a weak model | same page | 2026-02-11 | verified | |
| A short guide that points to deeper material beats one large instruction file | same page | 2026-02-11 | verified | About 100 lines there. The "under 40 lines" of the article's template is the author's own number. The Claude Code documentation advises staying under 200. |
| The author's experiment: 20 tasks, 8 then 16 accepted, 4.10 $ then 1.60 $ per accepted task, 41 retries in one night | the article itself | 2026-10-23 | not found | No repository, log or trace published. Do not quote it as evidence. |

## 3. Where the article departs from its own sources

1. **A hard cap of three attempts.** The source it cites describes a nudge, not a cap. Hard caps do exist on the tool side: a turn cap and a budget cap on headless runs, a turn cap on sub-agents. Recommend those, and present "three tries then a human" as a sensible default, not as a finding.
2. **Blocking every merge to the default branch.** The OpenAI team says it runs with few blocking merge gates, lets agents merge their own pull requests and treats flaky tests with follow-up runs. It can afford this because its invariants are held upstream by custom linters and structural tests, and it warns the choice does not generalise. So the audit question is not "is there a gate?" but "which regime did you choose, and is the other half of that regime in place?" A setup with structural linters that merges on red has neither regime.
3. **An adversarial verifier without limits.** The Claude Code best-practices page warns that "a reviewer that's asked to find problems will always find something", and that fixing every finding adds layers and tests for cases that cannot happen. A reviewer must be bound to the spec and to correctness, and its verdicts reread from time to time.

## 4. Primary sources, by criterion

| Source | Date | Criteria it backs |
|---|---|---|
| OpenAI, "Harness engineering: leveraging Codex in an agent-first world" · https://openai.com/index/harness-engineering/ | 2026-02-11 | C1, C2, C3, C4, C5, C10, and the optional C13 to C15 |
| LangChain, "Improving Deep Agents with harness engineering" · https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering | 2026-02-17 | C5, C8, C11, C12 |
| Claude Code docs, "Best practices" · https://code.claude.com/docs/en/best-practices | undated, read 2026-11-20 | C1, C2, C3, C5, C6, C7, C8, C9, C10, C11 |
| Claude Code docs, "Configure permissions" · https://code.claude.com/docs/en/permissions | undated | C7 |
| Claude Code docs, "Hooks reference" · https://code.claude.com/docs/en/hooks | undated | C5, C7 |
| Claude Code docs, "Sandboxing" · https://code.claude.com/docs/en/sandboxing | undated | C7 |
| Claude Code docs, "Subagents" · https://code.claude.com/docs/en/sub-agents | undated | C6, C8 |
| Claude Code docs, "Review locally with /code-review" · https://code.claude.com/docs/en/code-review-local | undated | C6 |
| Anthropic, "Effective harnesses for long-running agents" · https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents | 2025-11-26 | C4, C9 |
| Anthropic, "Harness design for long-running application development" · https://www.anthropic.com/engineering/harness-design-long-running-apps | 2026-03-24 | C1, C6, C11 |
| Anthropic, "Demystifying evals for AI agents" · https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents | 2026-01-09 | C12, optional C16 |
| Anthropic, "Writing effective tools for agents" · https://www.anthropic.com/engineering/writing-tools-for-agents | 2025-09-11 | C3 |
| Anthropic, "Effective context engineering for AI agents" · https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents | 2025-09-29 | C2 |
| Anthropic, "Building effective agents" · https://www.anthropic.com/engineering/building-effective-agents | 2024-12-19 | C6, optional C16 |

Two points these sources add to the article: the harness itself has to be measured (C12: a small suite of tasks drawn from real failures is enough to start, and an improvement seen on one task only is over-fitting), and each harness component should carry the assumption it compensates for, to be retested when the model changes (C11).

Documentation moves. Before recommending a flag or a setting name, open the page.

## 5. Reading list

For someone already at level 2 or above, in this order:

1. The four pages that cover the whole grid: the OpenAI post, the Claude Code best-practices page, "Demystifying evals for AI agents", "Harness design for long-running application development".
2. Three folders of the Anthropic cookbook (https://github.com/anthropics/claude-cookbooks): `patterns/agents/evaluator_optimizer.ipynb` (builder and verifier, C6), `tool_evaluation/` (measuring your own tools and skills, C3 and C12), `claude_agent_sdk/scheduled_repository_reviewer/` (a scheduled reviewer, C6 and optional C14).

## 6. How to treat a "resources" thread

When the user brings a list of courses and links: resolve the shortened links before judging (affiliate redirects are common), check who actually publishes each course, and sort into read / skim / skip for this user's level. On the list audited on 2026-11-20, 10 of 24 links were affiliate links, several courses filed under a vendor's name were co-productions or third-party, and one item out of 24 was worth reading in full. A quote attributed to a well-known person should be found at its source or dropped. The primary sources above were worth more than the whole list, and none of them was in it.
