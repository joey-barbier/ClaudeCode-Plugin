# Task graph and run board

Every run, short or full, research or code, is driven by a task graph and shown on a board. The graph is how the orchestrator decides what to launch; the board is how the user follows the run without progress messages, and how the scorecard of Phase 5 gets its numbers.

## Why a graph, not a list of waves

A list of waves makes every task of wave 2 wait for the slowest task of wave 1. A graph makes each task wait only for what it really reads. On a real code run (53 tasks, 45 agents), tasks without a link to a blocked one kept going while a review held three others, and the parallelism factor (cumulated agent time / wall time) stayed above ×3. Waves remain a way to *think* about the run; the graph is what you execute.

Rules:

1. **A task starts as soon as all its dependencies are done**, within the concurrency cap of the machine (often 3 to 5 agents at once). Nothing waits "for the wave".
2. **A dependency is a file or a decision the task reads**, never "it came before". If B only needs the brief, B depends on the framing task, not on A.
3. **A blocked task blocks only its descendants.** A review that comes back BLOCKED creates a correction task; the tasks that do not read the reviewed code keep running.
4. **A decision that waits on the user is a task of its own** (status `user`). It sits in the graph like any other: what depends on it waits, the rest goes on.
5. **Gates and validators are tasks too**, with their own model and effort. A validator depends on the work it checks, never on its author's own say-so.
6. **Adding a task mid-run is normal** (a correction, a probe that a review asked for). Add it with its dependencies before launching it; never launch an agent that is not on the graph.

## `graph.json`

Kept by the orchestrator in a board folder outside the repository (scratchpad or project files). One writer: the orchestrator, through `scripts/board/set.py`.

```jsonc
{
  "title": "Checkout rewrite: run board",
  "lang": "en",                         // or "fr": labels of the board
  "user": "Sam",                        // shown in "Waits for Sam"
  "utc_offset": 1,                      // hour shown on the board
  "start": "2026-11-16T19:17:46Z",
  "session": "/root/.claude/projects/<slug>/<session-id>.jsonl",   // optional: main transcript
  "essentials": ["<b>Goal.</b> …", "<b>Where we are.</b> …"],    // 3 to 5 lines, rewritten as the run moves
  "waiting_on_user": ["…"],
  "decisions": ["…"],
  "probes": ["<b>Payment API.</b> what the real call returned …"],
  "lanes": [["infra", "Infra"], ["pay", "Payment"], ["data", "Data and rights"], ["ship", "Delivery"]],  // optional: columns
  "nodes": [
    {"id": "P0", "title": "Framing and common brief", "role": "orchestrator", "model": "Fable", "effort": "—", "status": "done", "deps": []},
    {"id": "S1", "title": "Probe the payment API", "role": "probe", "model": "Sonnet", "effort": "medium", "status": "done", "deps": ["P0"], "agents": ["a3f2…"], "lane": "pay"},
    {"id": "A1", "title": "Antagonist review of the decision record", "role": "antagonist", "model": "Opus", "effort": "high", "status": "waiting", "deps": ["D1"]}
  ]
}
```

Statuses: `ready` (can start), `waiting` (a dependency is not done), `running`, `done`, `user` (waits for the user), `failed` (to redo: add the correction task), `interrupted` (the agent was cut by a restart or a limit: its committed work stays, relaunch it with "resume from your last commit").

**Lanes (recommended as soon as the run has 15 tasks or more).** Give `graph.json` a `lanes` list and each node a `lane`: the board then draws one column per lane (infra, payment, data, screens, delivery…), rows still by depth. Lanes make the point of the graph visible at a glance: a fast lane is finished while a slow one is still on its second task, and a lane stopped on a user decision does not hold the others. A lane-less root (the framing task) is centred on top; any other lane-less task goes to a last column. Group by what a task reads, so that most arrows stay inside their column and only the delivery lane gathers them. Without `lanes`, the board draws one row per depth.

Ids are short and stable (`S1`, `D2`, `T1`, `I3`, `V1`): they are what you write in the thread and in commit messages.

## Commands

```bash
B=<board folder>; S=<absolute path of this skill>/scripts
python3 -I $S/board/set.py $B S1 running a3f2c1      # agent id from the Agent / Workflow result
python3 -I $S/board/set.py $B S1 done note="API returns 429 above 10 req/s"
python3 -I $S/board/build.py $B                        # set.py already rebuilds; use this after editing essentials
```

`set.py` prints the tasks that can start now: launch them in the same turn. `build.py` writes `$B/board.html`. Give agents `BOARD_DIR=$B` in the common brief so that `scripts/ask.sh` logs their direct calls to `$B/asks.jsonl`.

Publish the board where the user can open it (an Artifact page, or a file in the project) at the start of the run, then republish it at each status change that matters: a task done, a review verdict, a task waiting on the user. The thread gets one message with the link, then nothing until a result or a question.

## What the board shows (the consumption debrief)

Read from the transcripts (`message.usage` per assistant message, deduplicated by message id, cache reads included), never from the harness counters:

- Tasks done / running, agents launched, direct calls to a cheaper model.
- Tokens in all and the share of cache reads (usually above 90 %: the cost of an agent is the context it re-reads every turn), output tokens.
- Wall time vs cumulated agent time, and their ratio: the parallelism factor. Below ×1.5 on a run of more than 10 tasks, the graph has too many false dependencies.
- The graph itself: one column per lane when lanes are set (else one row per depth), coloured by status, model of each task in its corner, solid arrows from finished tasks.
- Navigation, so that a run of several hundred tasks stays usable: a click on a card (or Enter / Space) opens its detail beside the graph: full title, state, lane, role, model and effort, note, agents, duration, tokens, then the whole chain that led to it (every ancestor, not only the direct dependencies: "114 tasks upstream, 5 of them direct"), in work order, numbered, grouped by lane in a list that scrolls inside the panel, direct ones marked; then its direct dependents, and its whole descent on demand (what it blocks). Every entry is a link to its card. In the graph the chain stays lit with the direct arrows thicker, dependents in the focus colour, the rest fades; Fit then frames the chain instead of the whole graph; Escape or the close button restores the graph. Buttons zoom in, zoom out, fit the window and go full screen (a layer of the page itself, since the browser API can be refused inside a sandboxed frame; Escape leaves it); Ctrl + wheel or a pinch zooms, a drag pans. A contents bar stays on top while scrolling, marks the current part and folds into one button on a phone. Without script the graph scrolls in its box and a card leads to its row in the task table. `examples/task-graph-demo.html` shows the same click on a fictional run.
- Per task: role, model, effort, state, agents, duration, turns, tokens, output.
- Per model: agents, turns, tokens in all, cache reads, input and cache writes, output. This is the check that routing worked: if the top model carries more than the orchestration and the judgement, the briefs did not route.

Dollars are not on the board: tokens are not a price. When the user wants a cost, compute it from the per-model rows with the published prices and say which date the prices are from.

## Surviving an interruption

A session can be cut (machine restart, usage limit). Before the first implementer starts, and after each merge into the integration branch, save the committed work outside the session when there is no remote branch yet (`git bundle create <project files>/backup.bundle --all`). After a cut: mark the `running` tasks `interrupted`, check their commits, relaunch them. The graph tells you exactly what to resume; nothing else needs to be remembered.

## At the end

The board is the source of the Phase 5 scorecard: copy its per-model rows, the parallelism factor, the agents relaunched and why. Leave the last version of the board published: it is the record of the run.
