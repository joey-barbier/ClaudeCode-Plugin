#!/bin/bash
# Stop hook: states what would be lost if nobody came back to this session.
# It does not count interactions and does not rely on anyone remembering to save:
# it measures the gap between the code and the memory, between the branch and its remote,
# and what sits uncommitted in the working tree.
# Shown to the person as one line, at most once per kind of gap every 30 minutes per session.

. "$(dirname "$0")/lib.sh"
SESSION="$(hm_session_id)"
hm_status

[ "$HM_KIND" = "repo" ] || exit 0
[ "$HM_MEM" = "present" ] || exit 0          # the project does not use this memory: stay silent
[ "$HM_TASK_BRANCH" = "detached" ] && exit 0 # a rebase or a bisect is in progress: nothing to say

FLAGS=""; PARTS=""
flag() { FLAGS="${FLAGS}${FLAGS:+,}$1"; PARTS="${PARTS}${PARTS:+, }$2"; }
many() { if hm_is_number "$1" && [ "$1" -ge "$HM_COUNT_CAP" ]; then echo "more than $HM_COUNT_CAP"; else echo "$1"; fi; }
BR="$(hm_clean "$HM_BRANCH")"

if [ "$HM_TASK_BRANCH" = "yes" ]; then
  HAS_WORK="no"
  if hm_is_number "$HM_AHEAD"; then [ "$HM_AHEAD" -gt 0 ] && HAS_WORK="yes"; else HAS_WORK="yes"; fi
  case "$HM_TASK_FILE" in
    absent) [ "$HAS_WORK" = "yes" ] && flag "task-missing" "no task file for $(many "$HM_AHEAD") commits of work" ;;
    present) [ "$HM_TASK_STALE" = "yes" ] && flag "task-stale" "task file $(many "$HM_TASK_BEHIND") commits behind" ;;
    closed) ;;                               # closed and waiting for its merge: do not ask for a new task file
  esac
  HAS_OWN="yes"; hm_is_number "$HM_OWN" && [ "$HM_OWN" -eq 0 ] && HAS_OWN="no"     # unknown counts as yes
  case "$HM_UNPUSHED" in
    not-on-remote) [ "$HAS_OWN" = "yes" ] && flag "not-on-remote" "branch is not on the remote" ;;
    0|n/a) ;;
    *) hm_is_number "$HM_UNPUSHED" && flag "unpushed" "$HM_UNPUSHED commits not pushed" ;;
  esac
  WHERE="branch $BR"
  HINT="Run /horka-memory:horka-memory-save, then push, so someone else can take over."
else
  [ "$HM_STALE" = "yes" ] && flag "memory-stale" "project memory $(many "$HM_BEHIND") commits behind"
  [ -n "$HM_LEFTOVER" ] && flag "leftover" "task folders left after merge: $HM_LEFTOVER"
  WHERE="$BR"
  HINT="Run /horka-memory:horka-memory-save."
fi
if [ "$HM_DIRTY" -gt 0 ] 2>/dev/null; then
  if [ -n "$FLAGS" ]; then
    flag "dirty" "$HM_DIRTY files uncommitted"
  elif [ "$HM_TASK_BRANCH" = "yes" ] && [ "$HM_TASK_FILE" != "closed" ]; then
    # Nothing else is wrong: a save would not help, so the hint is its own.
    flag "dirty" "$HM_DIRTY files uncommitted on a task branch"
    HINT="Commit or stash them so they are not lost."
  fi
fi

STATE_DIR="$(hm_state_dir)" || exit 0        # no safe place to remember what was said: stay silent rather than nag
STATE="$STATE_DIR/stop-$SESSION"
if [ -z "$FLAGS" ]; then
  rm -f "$STATE" 2>/dev/null
  exit 0
fi

NOW="$(date +%s)"
LAST_TIME=0; LAST_FLAGS=""
if [ -f "$STATE" ] && [ ! -L "$STATE" ]; then
  LAST_TIME="$(cut -d' ' -f1 "$STATE" 2>/dev/null)"
  LAST_FLAGS="$(cut -d' ' -f2- "$STATE" 2>/dev/null)"
  hm_is_number "$LAST_TIME" || LAST_TIME=0
fi
if [ "$FLAGS" = "$LAST_FLAGS" ] && [ $((NOW - LAST_TIME)) -lt "${HORKA_MEMORY_REMIND_SECONDS:-1800}" ]; then
  exit 0
fi
rm -f "$STATE" 2>/dev/null
{ printf '%s %s\n' "$NOW" "$FLAGS" > "$STATE"; } 2>/dev/null

printf '{"systemMessage":"%s"}\n' "$(printf 'horka-memory, %s: %s. %s' "$WHERE" "$PARTS" "$HINT" | hm_json_escape)"
exit 0
