# Briefs — templates per role

Every brief ends with the pass-down line of `references/model-routing.md`, whatever the role:

> You may launch sub-agents. Choose their tier with `references/model-routing.md` (absolute path: <path>): judgement → your tier at most, mechanical with a check → generalist, lookup whose conclusion is all you keep → cheapest (`Explore`). Never a tier above yours: report back instead. Put this same line in every brief you write.

Every brief starts with the common brief (context, constraints, forbidden content, output schema) and the sentence:

> No number from memory. Each number has a URL you opened and a date. List what you could not find. Prefer primary sources (official docs, APIs, the company's own page, papers) dated within two years. If a page is blocked, say so and move on.

## Persona (wave 1, before any research)

```
You are <persona: e.g. CTO of a 40-person SaaS, Dependabot on, 300 alerts ignored, no security budget, wary of tools that read code>.
Read the question and the list of candidate action types (not the researchers' output).
For each action type say: would it make you try, leave you neutral, or make you flee — and under which condition.
Then list what is missing between "first contact" and "paying", and the rules you would impose.
Back each reaction with a source (survey, blog post by a peer, a documented incident) — URL and date.
```

Pick two personas on purpose: the buyer, and the third party the actions touch (a maintainer, a partner, a regulator). The second one kills the actions the first one likes.

## Real-demand probe (wave 1)

Measure, do not guess. For each topic the plan might write about:

- StackOverflow: `https://api.stackexchange.com/2.3/search/advanced?site=stackoverflow&q=<query>&filter=total` and `questions?tagged=<tag>&filter=total` (cumulative questions; throttled per IP, say when a query failed).
- Hacker News: `https://hn.algolia.com/api/v1/search?query=%22<query>%22&tags=story&advancedSyntax=true` — quoted only (unquoted "epss" matches "Epstein"); record story count and max points, and the 12-month subset with `numericFilters=created_at_i>…`.
- Google autocomplete: `https://suggestqueries.google.com/complete/search?client=firefox&hl=en&q=<query>` and `hl=fr&gl=fr`. A suggestion proves an intent exists; an empty list means "too rare to suggest". It is not a volume.
- GitHub: repository count for the words, as an order of magnitude only.

Verdict per topic: strong / medium / weak, a recommended title in each language, and the list of what could not be measured.

## Researcher (wave 2) — one brief per action type

```
Action type: <content | distribution | partnerships | product-as-marketing | community | press and regulation>.
Find 5 to 8 concrete actions of this type that a <one-founder company with N days over 90 days> can run.
For each: title, who it reaches, steps, the expected result as a number with its URL and date, cost, delay, a comparable (a company that did it, with its figures), and what could go wrong.
Look at direct competitors AND at unrelated sectors whose mechanics can be copied (say which sector).
Return the JSON schema given. End with "not found".
```

## Validator (wave 4) — never the same agent as the researcher

```
Here is a researcher's JSON. For every number, open the URL with WebFetch and report:
verified (number on the page, same context) / partial (number on the page, context differs: say how) /
unverifiable (page blocked or number absent) / false (page says something else: quote it).
Never propose a replacement number. Return the corrections list.
```

## Antagonist critic (wave 5)

```
You are the antagonist. You did not write these actions. Find: duplicates (merge them), filler,
fragile figures (ratios borrowed from players 100× bigger, one-off cases, invented rates),
brand risks (humiliating a third party, over-promising compliance, fear-based messaging),
actions that assume unshipped features. Keep 8 to 12 actions, in order, with a 90-day sequence
and two dated decision gates. Each dropped action gets one sentence of reason.
```

## Feasibility (wave 6)

```
The plan assumes this flow: <flow>. Verify every brick in official documentation and in the code:
triggers, permissions, what the tool does NOT do by default, cost under an explicit hypothesis
(state it, and say what measurement replaces it), a minimal demo project, and what the product
must change for the flow to be reproducible. Return "verified / not verified" per brick with URLs.
```

## Code variant — common brief (one file in the repo, read by every agent)

```
Question: <rewrite X in Y according to decision record Z, without changing the observable behaviour>.
Reference = the existing code on the remote main (fresh clone, read-only); never a local copy that may be behind.
The test branches and fix branches of the old code are the specification of record: each fix is a test case.
Forbidden: push, repository or PR creation, scheduling, running anything against a real service, reading any
secret file. Commits: <format>, no attribution trailer. Own worktree, own branch, own folders only.
Context economy: for any wide search, or a read of several files of which you keep only a conclusion, launch
an Explore sub-agent on the cheapest tier and keep only its answer; read in full only what you modify or port.
Do not delegate: content you need in full (it would be read twice), a single grep or ls (the sub-agent costs
more), or anything that needs exactness (a summary can be wrong; verify yourself).
Context cap: at ~150k tokens of context, stop, write a hand-over report (done, state, next steps, open questions) and let a fresh agent continue.
Proof before "done": full test run and the reference gate green, last lines pasted. No test skipped, no retry,
no assertion loosened. Report ≤ 300 words: branch, commits, done, old → new mapping, deliberate deviations,
not done or not found, questions. Do not declare yourself validated: others do that.
```

## Code variant — blind tester (wave T)

```
You write the executable specification of <target> from the reference and the architecture base only.
You never open Sources/, in your worktree or any other. The only code you read is in the base's spec extracts.
Deliverables in order: Tests/<Target>/Spec/API.md (modules, types, signatures, errors you assume; mark your
own choices "(tester's choice)"), then the test files, one suite per behaviour, each test citing its source
(file:line of the reference, or the base section, or the old test branch).
Cover: nominal, limits, errors (every error case the target can produce), real formats anonymised, the base's
invariants, the old test branches, the fixes (each fix is a case), the catalogued defects that must now pass.
Deterministic: injected clock, no network, no real service, temp dirs only.
You cannot compile against an implementation that does not exist: a throwaway stub package outside the repo
is allowed, never committed.
Report: tests and suites, coverage by theme, the riskiest API assumptions, ambiguous or buggy behaviours of
the reference (file:line), what you could not find, questions. You do not declare yourself validated.
```

## Code variant — implementer (wave I)

```
Make Tests/<Target>/Spec/ pass without changing an assertion. Allowed in Spec/: mechanical API renames strictly
needed to compile, each listed in the report with its count. A test you believe wrong stays red and is
explained with file:line of the reference. Your own tests live next to Spec/, never inside it.
You own <folders>; a type you need from another agent's area is declared locally and marked
// TEMP: reconcile at merge. Proof: full run green, reference gate green, pasted.
Report: green / red with reasons, renames, what the tester saw that you would not have coded, questions.
```

## Code variant — reconciliation (wave R)

```
Merge <branches> into integration. Resolve each duplicate type: the lowest layer's API.md is the authority;
delete every TEMP type; adapt call sites mechanically; no assertion changes. Run the full suite and the gate.
Report: what was merged, each duplicate and its resolution, types moved, what stays open.
```

## Code variant — validation thread (wave V, a separate thread, no orchestrator context)

```
You receive only: the branch, the architecture base, the validation type (code | AI behaviour | security).
Code: rerun the gate, look for what is not tested, write the missing tests red first, verdict.
AI behaviour: replay recorded inputs through old and new, list every difference.
Security: replay the walls with your own variants, exfiltration and cross-tenant scenarios, verdict
BLOCKED / WARNINGS. Never skip, retry or loosen a test to get green. Report ≤ 300 words with outputs pasted.
```

## Completeness (wave 6)

```
Read everything produced so far. What is missing? Which hypotheses are fragile? Which actions
duplicate each other? What measurement must exist before any action can be judged
(events, UTM convention, server-side attribution, baseline export, weekly external counters)?
```
