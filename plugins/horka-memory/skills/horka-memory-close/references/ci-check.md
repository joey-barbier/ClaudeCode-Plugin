# CI check: no task memory on the base branch

The check lives in the project, not in the plugin: CI machines do not have the plugin installed. It is one shell test with no dependency.

## GitHub Actions

Add this job to a workflow that runs on pull requests to the base branch (adapt the branch name), or as a step of an existing job after the checkout:

```yaml
name: memory
on:
  pull_request:
    branches: [main]
permissions:
  contents: read
jobs:
  no-task-memory:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Task memory must be closed before merge
        run: |
          left="$(find .claude/memory/in-progress -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort)"
          if [ -n "$left" ]; then
            echo "Task memory still in progress. Run horka-memory-close on the branch, then push:"
            echo "$left"
            exit 1
          fi
```

A draft pull request fails this check until the task is closed: that is the intended signal. If the team prefers a green draft, add `if: github.event.pull_request.draft == false` to the job.

## Any other CI, or a local gate

```bash
test -z "$(find .claude/memory/in-progress -mindepth 1 -maxdepth 1 -type d 2>/dev/null)"
```

The plugin ships the same test with a readable message: `scripts/check-in-progress.sh [repository root]`.

## Before installing it

Look at the project's existing workflows and gate script first and add the step where the other checks live, in the project's own style. Do not create a second workflow when one already runs on pull requests.
