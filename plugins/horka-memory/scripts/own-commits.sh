#!/bin/bash
# Lists the current branch's own commits, newest first, the same way the hooks count them: the commits
# that are on no base branch, plus, for a branch that is not on the remote, those made since it was
# created on this machine that the remote bases do not have. Read-only.
# Used by the skills to rebuild what a task did when it has no task file.

. "$(dirname "$0")/lib.sh"
hm_status
[ "$HM_KIND" = "repo" ] || { echo "not a git repository"; exit 0; }
if [ "$HM_TASK_BRANCH" != "yes" ] || { [ -z "$HM_CREATED" ] && [ -z "$HM_BASES" ]; }; then
  echo "cannot tell which commits are this branch's own (no base branch in this clone, or not a task branch)"
  exit 0
fi
{ [ -n "$HM_CREATED" ] && git -C "$HM_ROOT" rev-list --max-count=200 "$HM_CREATED"..HEAD ${HM_OBASES:+--not $HM_OBASES}
  [ -n "$HM_BASES" ] && [ "$HM_SHALLOW" != "yes" ] && git -C "$HM_ROOT" rev-list --max-count=200 HEAD --not $HM_BASES
} 2>/dev/null | awk '!seen[$0]++' | head -200 | git -C "$HM_ROOT" log --no-walk=unsorted --oneline --stdin
exit 0
