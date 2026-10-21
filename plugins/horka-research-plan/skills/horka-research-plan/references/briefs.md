# Briefs — templates per role

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

## Completeness (wave 6)

```
Read everything produced so far. What is missing? Which hypotheses are fragile? Which actions
duplicate each other? What measurement must exist before any action can be judged
(events, UTM convention, server-side attribution, baseline export, weekly external counters)?
```
