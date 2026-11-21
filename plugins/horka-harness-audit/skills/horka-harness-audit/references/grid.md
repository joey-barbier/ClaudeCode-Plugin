# The grid: twelve criteria

Ten come from the checklist that closes the harness article (see `sources.md`), the eleventh from its remark on size, the twelfth from the primary sources, which the article leaves out.

For each criterion: the question, the good level according to the primary sources, the scan lines that answer it, what to read by hand, and the cheapest wall. "Held by" is always one of: nothing · sentence · script run by hand · hook · CI that reports · CI or platform that blocks.

| # | Question | Good level | Scan lines | By hand | Cheapest wall |
|---|---|---|---|---|---|
| C1 | Is "done" defined before the work starts? | Every non-trivial task starts from a written spec with checkable acceptance lines; the verifier judges against it. | `[C1] contract artefacts` | Two recent PRs or briefs: was "done when" there before the code? | A task template with a "done when" line; a PR template. |
| C2 | A map, not a manual? | A short root file (about 100 lines at OpenAI, under 200 in the Claude Code docs) that says only what the code does not show and points to the rest. Kept true. | `[C2] map`, `last changed … commits ago` | Check one concrete claim of the map against the code. | Rewrite the map; delete what is false before adding. |
| C3 | Does each tool have a clear purpose and a clear failure message? | Few tools; each failure message says how to fix, and lands in the agent's context. | `[C3] same name defined twice` | Run one gate script on purpose-broken input and read its message. | Remove duplicates; one line "to fix: …" in each failure message. |
| C4 | Is state kept outside the conversation? | Decisions, plans, known debt and progress are versioned in the repository. | `[C4] state file … commits ago` | Does the state file still describe the current work? | A hook that reminds at session end; a freshness check. |
| C5 | Does "done" require evidence? | A pass/fail check the agent runs itself, demanded by a Stop hook or by CI, with the command output as proof. For UI, a real run of the app. | `[C5] workflow`, `test-like jobs run on…`, `local gate candidates`, `Stop hooks`, `runs ·` | Does the gate check anything (are there tests at all)? Does anything refuse "done" when it is red? | One `check` script; a Stop hook or a required CI job that runs it. |
| C6 | Is the checker someone other than the builder? | A reviewer that did not see the writing, judges against the spec, and is calibrated because a reviewer asked for problems always finds some. | `[C6] reviewer roles launched`, `merged by their own author`, `reviewer artefacts` | Does any merge wait for the reviewer's verdict? | Make the review a CI job on pull requests. |
| C7 | Are risky actions blocked by policy, not by a sentence? | The "never" rules are deny or ask rules, blocking hooks or managed settings; the default branch has a rule the agent cannot bypass; outward-facing actions need approval. | `[C7] permission rules`, `broad allow`, `rule lines written as sentences`, `probe ·`, `deploy job`, `branch … protected`, `environment`, `merged with a failing check` | Open the hook that has holes. | See below: the three free walls. |
| C8 | Does every loop have a cap on attempts and spend? | Unattended runs have a turn cap or a budget cap, sub-agents a turn cap, CI jobs a timeout; batches have a size fixed before they start. | `[C8] caps written in tracked files`, `headless agent call(s)`, `jobs without timeout-minutes` | How large was the last parallel batch, and who decided its size? | `--max-turns` / `--max-budget-usd` on headless calls; `timeout-minutes`; a batch size refused by the launching script. |
| C9 | Can a run resume after a crash? | A fresh session gets back on its feet from the repository alone: log, progress file, a test run before resuming. | `[C9] work that exists on this machine only`, `tracked files read at` | Could someone else continue from the remote alone? | Push work-in-progress branches; state file committed. |
| C10 | Does each failure leave a rule, a test or a check? | Each review comment and each bug becomes a doc update or a tooled check. Corrected twice, the rule is written; ignored despite emphasis, it becomes a hook or a lint. | `[C10] lessons files`, `structural lint rules` | In the lessons file, how many rules name a script or hook? | Move one recurring lesson one step down: sentence → checklist → check → wall. |
| C11 | Is the harness smaller than the problem? | Each component states the weakness it compensates and is retested when the model changes; guides are pruned. | `[C11] loaded in every session`, `usage`, `worktrees` | Which agents and skills never ran in the window? | Delete unused agents and merged worktrees; remove a rule once a hook enforces it. |
| C12 | Is the harness itself measured? | Changes to skills, hooks and agent prompts are judged on 20 to 50 tasks drawn from real failures; hooks have tests. | `[C12] eval suites`, `tests that exercise a hook` | Was the last skill or hook change compared with the previous version? | Five test cases for each blocking hook; an eval folder per skill. |

## C7 in detail: the three things a wall must protect

Check each one separately. A setup is at enforcement level 3 only when all three have a wall.

1. **The default branch.** Paid or public repository: branch protection with a required check. Private repository on a plan without protection (the scan prints the 403): a PreToolUse hook that reads the whole command. The probe shows whether the existing hook survives `git -C <dir> push`, a `+refspec`, a chained command. A guard that only matches the start of the command stops the honest case and nothing else.
2. **Production.** Does the deploy job wait for a test job (`needs:`)? If tests live in another workflow (a nightly end-to-end suite), nothing connects them to the deploy: it is detection, not enforcement. A required reviewer on the environment is the approval gate, where the plan allows it.
3. **Spend.** With unattended runs: turn or budget caps on every headless call, a batch size fixed before launch. Without them the only cap is the account limit, which is shared with everything else running on the account.

Two more things to look at under C7, which the scan only half shows:

- **Secrets.** `[C7] env files` says whether an env file is tracked and whether `.gitignore` covers it; the probe says whether `cat .env` meets a rule. "Never read .env" with a broad allow on `cat` or an unrestricted `Read` is a sentence.
- **Unattended agents that read strangers' text.** An agent that triages issues or answers pull request comments reads text anyone can write. If its allowed tools cover merging, calling the API or reading secrets, a planted instruction can use them. Narrow the tools to what the job needs, and give the run a token that can only do that.

Sorting actions by how hard they are to undo decides the mechanism: reversible (read, search, test, edit a working branch) runs freely; visible outside (push, deploy, send, buy) asks first; hard to reverse (delete data, rotate credentials, force push, publish) is closed.

## Reading the probe

`rules: allow by Bash(git:*)` means a broad allow rule pre-approves the command: no prompt at all. `rules: none` means the permission mode decides: a prompt in the default mode, a classifier in auto mode, nothing in bypass mode. When the scan prints "permission mode: not set", the built-in default of the installed version applies, and it is not the same in every version: say that it is not set, do not assume a prompt. `hooks: passes every hook` means every hook ran and none objected. "not run", "no answer" or "filter not understood" on a probe line means that hook was not judged: it is neither a pass nor a stop. A command is stopped only by an ask rule, a deny rule or a blocking hook. The rule matching in the scan is an approximation of the real matcher; when the answer matters, test the real command form in a throwaway repository.

## Four optional criteria (name them only when relevant)

- C13 Legible environment: the agent can start the app, drive it, read logs and metrics.
- C14 Entropy collection: scheduled background tasks compare code with the stated principles and open small cleanup changes.
- C15 Structural invariants: layering and dependency directions enforced by custom linters and structural tests.
- C16 Isolation: each agent or trial works in its own worktree or sandbox, with no shared state.
