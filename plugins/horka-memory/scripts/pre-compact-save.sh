#!/bin/bash
# PreCompact hook: the conversation is about to be summarized, so what is not in the memory files may be lost.
# Says which file is behind, measured against the code, instead of a generic reminder.

. "$(dirname "$0")/lib.sh"
cat >/dev/null 2>&1
hm_status

[ "$HM_KIND" = "repo" ] || exit 0
[ "$HM_MEM" = "present" ] || exit 0

DIRTY="$(git -C "$HM_ROOT" status --porcelain 2>/dev/null | grep -v ' \.claude/memory/' | head -1)"

if [ "$HM_TASK_BRANCH" = "yes" ]; then
  if [ "$HM_TASK_FILE" = "absent" ]; then
    echo "IMPORTANT: context is about to be compacted and branch $HM_BRANCH has no task file. Run /horka-memory:horka-memory-save NOW so the stopping point of this task is written down."
  elif [ "$HM_TASK_BEHIND" != "0" ] || [ -n "$DIRTY" ]; then
    echo "IMPORTANT: context is about to be compacted. The task file of $HM_BRANCH is $HM_TASK_BEHIND commits behind${DIRTY:+ and there are uncommitted changes}. Run /horka-memory:horka-memory-save NOW."
  fi
elif [ "$HM_BEHIND" != "0" ] || [ -n "$DIRTY" ]; then
  echo "IMPORTANT: context is about to be compacted. Project memory is $HM_BEHIND commits behind${DIRTY:+ and there are uncommitted changes}. Run /horka-memory:horka-memory-save NOW."
fi
exit 0
