#!/bin/bash
# Lists the current branch's own commits, newest first: those made since the branch was created here
# (a branch that never left this machine), or those that are on no base branch. Read-only.
# Used by the skills to rebuild what a task did when it has no task file.

. "$(dirname "$0")/lib.sh"
hm_status
[ "$HM_KIND" = "repo" ] || { echo "not a git repository"; exit 0; }
if [ -n "$HM_CREATED" ]; then
  git -C "$HM_ROOT" log --oneline --max-count=200 "$HM_CREATED"..HEAD
elif [ -n "$HM_BASES" ] && [ "$HM_TASK_BRANCH" = "yes" ]; then
  git -C "$HM_ROOT" log --oneline --max-count=200 HEAD --not $HM_BASES
else
  echo "cannot tell which commits are this branch's own (no base branch in this clone, or not a task branch)"
fi
exit 0
