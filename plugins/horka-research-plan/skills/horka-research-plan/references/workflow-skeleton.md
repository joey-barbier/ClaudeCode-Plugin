# Workflow skeleton (when the `Workflow` tool is available)

Three scripts, one per wave group, so you read between them. Each agent writes its result to a file and returns the JSON; the orchestrator reads files in slices, never the whole result in context.

## Wave 1 — readers first

```js
export const meta = {
  name: 'research-plan-wave1',
  description: 'Personas and real-demand probe before any research',
  phases: [{ title: 'Readers' }],
}
const BRIEF = args.brief            // path of the common brief
const out = await parallel([
  () => agent(`Read ${BRIEF}. ${args.persona1}`, { label: 'persona:buyer', phase: 'Readers', schema: args.schemas.persona }),
  () => agent(`Read ${BRIEF}. ${args.persona2}`, { label: 'persona:third-party', phase: 'Readers', schema: args.schemas.persona }),
  () => agent(`Read ${BRIEF}. Measure real demand for these topics: ${args.topics.join('; ')}. Method: StackOverflow API, HN Algolia quoted, Google autocomplete en+fr, GitHub repo count as order of magnitude. No Google volumes: say so.`, { label: 'demand', phase: 'Readers', schema: args.schemas.demand }),
])
return out
```

## Wave 2 + 4 — researchers piped into validators

```js
export const meta = {
  name: 'research-plan-wave2',
  description: 'Researchers per action type, each validated by a different agent',
  phases: [{ title: 'Research' }, { title: 'Validate' }],
}
const results = await pipeline(
  args.actionTypes,                                        // [{key, brief}]
  t => agent(`Read ${args.brief}. ${t.brief}`, { label: `research:${t.key}`, phase: 'Research', schema: args.schemas.researcher }),
  (r, t) => r && agent(`Read ${args.brief}. Validate every number in this JSON by opening its URL. Never propose a replacement number.\n${JSON.stringify(r)}`,
                       { label: `validate:${t.key}`, phase: 'Validate', schema: args.schemas.validator }).then(v => ({ research: r, validation: v })),
)
log(`${results.filter(Boolean).length}/${args.actionTypes.length} action types researched and validated`)
return results.filter(Boolean)
```

Dedup between wave 2 and the critic is plain code in the orchestrator (normalise titles, merge, union of sources), not an agent.

## Wave 5 + 6 — critic, then feasibility and completeness

```js
export const meta = {
  name: 'research-plan-wave3',
  description: 'Antagonist critic, then feasibility and completeness',
  phases: [{ title: 'Critic' }, { title: 'Feasibility' }],
}
const critic = await agent(`Read ${args.brief} and ${args.dedupFile}. You are the antagonist (Jean-Pierre). ${args.criticBrief}`, { label: 'critic', phase: 'Critic', schema: args.schemas.critic })
const checks = await parallel([
  ...args.flows.map(f => () => agent(`Read ${args.brief}. ${f.brief}`, { label: `feasibility:${f.key}`, phase: 'Feasibility' })),
  () => agent(`Read ${args.brief}, ${args.dedupFile} and the critic result ${JSON.stringify(critic.kept)}. What is missing, which hypotheses are fragile, what measurement must exist first?`, { label: 'completeness', phase: 'Feasibility' }),
])
return { critic, checks: checks.filter(Boolean) }
```

Notes:
- Pass file paths and schemas through `args`; scripts cannot read the filesystem themselves.
- Concurrency is capped by the machine (often 2 to 4 agents at once): size waves accordingly and read the journal (`journal.jsonl` in the workflow transcript dir) if a result looks empty.
- Set `model` and `effort` per `agent()` call following the table in SKILL.md.
