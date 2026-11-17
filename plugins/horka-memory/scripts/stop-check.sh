#!/bin/bash
# Stop hook: states what would be lost if nobody came back to this session.
# It does not count interactions and does not rely on anyone remembering to save:
# it measures the gap between the code and the memory, and between the branch and its remote.
# Shown to the person as one line, at most once per kind of gap every 30 minutes per session.

. "$(dirname "$0")/lib.sh"
SESSION="$(hm_session_id)"
hm_status

[ "$HM_KIND" = "repo" ] || exit 0
[ "$HM_MEM" = "present" ] || exit 0      # the project does not use this memory: stay silent

FLAGS=""; PARTS=""
flag() { FLAGS="${FLAGS}${FLAGS:+,}$1"; PARTS="${PARTS}${PARTS:+, }$2"; }

if [ "$HM_TASK_BRANCH" = "yes" ]; then
  HAS_WORK="no"
  case "$HM_AHEAD" in ''|*[!0-9]*) HAS_WORK="unknown" ;; 0) ;; *) HAS_WORK="yes" ;; esac
  if [ "$HM_TASK_FILE" = "absent" ]; then
    [ "$HAS_WORK" = "yes" ] && flag "task-missing" "no task file for $HM_AHEAD commits of work"
  elif [ "$HM_TASK_STALE" = "yes" ]; then
    flag "task-stale" "task file $HM_TASK_BEHIND commits behind"
  fi
  case "$HM_UNPUSHED" in
    no-upstream) [ "$HAS_WORK" = "yes" ] && flag "no-upstream" "branch never pushed" ;;
    ''|*[!0-9]*|0) ;;
    *) flag "unpushed" "$HM_UNPUSHED commits not pushed" ;;
  esac
  WHERE="branch $HM_BRANCH"
  HINT="Run /horka-memory:horka-memory-save, then push, so someone else can take over."
else
  [ "$HM_STALE" = "yes" ] && flag "memory-stale" "project memory $HM_BEHIND commits behind"
  [ -n "$HM_LEFTOVER" ] && flag "leftover" "task folders left after merge: $HM_LEFTOVER"
  WHERE="${HM_BRANCH:-detached HEAD}"
  HINT="Run /horka-memory:horka-memory-save."
fi

STATE="$(hm_state_dir)/stop-$SESSION"
if [ -z "$FLAGS" ]; then
  rm -f "$STATE" 2>/dev/null
  exit 0
fi

NOW="$(date +%s)"
LAST_TIME=0; LAST_FLAGS=""
if [ -f "$STATE" ]; then
  LAST_TIME="$(cut -d' ' -f1 "$STATE" 2>/dev/null)"
  LAST_FLAGS="$(cut -d' ' -f2- "$STATE" 2>/dev/null)"
  case "$LAST_TIME" in ''|*[!0-9]*) LAST_TIME=0 ;; esac
fi
if [ "$FLAGS" = "$LAST_FLAGS" ] && [ $((NOW - LAST_TIME)) -lt "${HORKA_MEMORY_REMIND_SECONDS:-1800}" ]; then
  exit 0
fi
printf '%s %s\n' "$NOW" "$FLAGS" > "$STATE" 2>/dev/null

printf '{"systemMessage":"%s"}\n' "$(printf 'horka-memory, %s: %s. %s' "$WHERE" "$PARTS" "$HINT" | hm_json_escape)"
exit 0
