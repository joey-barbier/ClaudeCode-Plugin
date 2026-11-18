#!/bin/bash
# PreCompact hook: the conversation is about to be summarized, so what is not in the memory files may be lost.
# Says which file is behind, measured against the code, instead of a generic reminder.

. "$(dirname "$0")/lib.sh"
cat >/dev/null 2>&1
hm_status

[ "$HM_KIND" = "repo" ] || exit 0
[ "$HM_MEM" = "present" ] || exit 0
[ "$HM_TASK_BRANCH" = "detached" ] && exit 0

BR="$(hm_clean "$HM_BRANCH")"
DIRTY=""; [ "$HM_DIRTY" -gt 0 ] 2>/dev/null && DIRTY=" and there are uncommitted changes"
gap() {   # <count> -> "is 3 commits behind" | "may be behind (freshness unknown)" | "" when current
  if hm_is_number "$1"; then [ "$1" -gt 0 ] && echo "is $1 commits behind"; else echo "may be behind (freshness unknown)"; fi
}

if [ "$HM_TASK_BRANCH" = "yes" ]; then
  case "$HM_TASK_FILE" in
    absent)
      # Only when the branch has work of its own or uncommitted changes: otherwise there is no stopping point to write down.
      if { hm_is_number "$HM_OWN_WORK" && [ "$HM_OWN_WORK" -gt 0 ]; } || [ -n "$DIRTY" ]; then
        echo "IMPORTANT: context is about to be compacted and branch $BR has no task file. Run /horka-memory:horka-memory-save NOW so the stopping point of this task is written down."
      fi ;;
    present)
      G="$(gap "$HM_TASK_BEHIND")"
      if [ -n "$G" ] || [ -n "$DIRTY" ]; then
        echo "IMPORTANT: context is about to be compacted. The task file of $BR ${G:-is current}$DIRTY. Run /horka-memory:horka-memory-save NOW."
      fi ;;
    closed) ;;
  esac
else
  G="$(gap "$HM_BEHIND")"
  if [ -n "$G" ] || [ -n "$DIRTY" ]; then
    echo "IMPORTANT: context is about to be compacted. Project memory ${G:-is current}$DIRTY. Run /horka-memory:horka-memory-save NOW."
  fi
fi
exit 0
