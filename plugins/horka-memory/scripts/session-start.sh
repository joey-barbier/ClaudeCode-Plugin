#!/bin/bash
# SessionStart hook: tells Claude what project memory exists here and how far it can be trusted.
# It measures (commits since the last save) instead of only checking that files exist:
# a memory left as an empty template after 500 commits must not be announced as "found".

. "$(dirname "$0")/lib.sh"
cat >/dev/null 2>&1   # the payload is not needed here
hm_status

MSG=""
add() { MSG="${MSG}${MSG:+
}$1"; }

case "$HM_KIND" in
  workspace)
    WITH=""
    for r in $HM_REPOS; do
      ls "$HM_ROOT/$r/.claude/memory"/*.md >/dev/null 2>&1 && WITH="$WITH $r"
    done
    add "This folder holds $HM_REPO_COUNT git repositories and is not itself a project: do not create memory files here."
    add "Project memory lives in each repository${WITH:+ (present in:$WITH)}. Restore it from the repository the task is about."
    [ "$HM_MEM" = "present" ] && add "The .claude/memory/ files of this folder are notes about the workspace as a whole: read them as an index of the repositories, not as the state of a project."
    ;;
  repo)
    if [ "$HM_MEM" = "absent" ]; then
      add "No project memory in this repository (.claude/memory/ is empty). Use the horka-memory:horka-memory-restore skill to initialize it before working on the project."
    else
      if [ "$HM_STALE" = "yes" ]; then
        add "Project memory found in .claude/memory/ but it is $HM_BEHIND commits behind the code${HM_SAVED:+ (last saved: $HM_SAVED)}. Treat it as outdated: the code wins. Use horka-memory:horka-memory-restore, which will say what to refresh."
      else
        add "Project memory found in .claude/memory/${HM_SAVED:+ (last saved: $HM_SAVED, $HM_BEHIND commits behind)}. Use horka-memory:horka-memory-restore to read it before working on the project."
      fi
      if [ "$HM_TASK_BRANCH" = "yes" ]; then
        if [ "$HM_TASK_FILE" = "present" ]; then
          add "Task in progress on branch $HM_BRANCH: .claude/memory/in-progress/$HM_TASK_ID/TASK.md${HM_TASK_SAVED:+ (last saved: $HM_TASK_SAVED, $HM_TASK_BEHIND commits behind)}. It says where the last person stopped: read it before continuing this task."
        else
          add "Branch $HM_BRANCH has no task file yet (.claude/memory/in-progress/$HM_TASK_ID/TASK.md). horka-memory:horka-memory-save creates it at the first milestone."
        fi
      elif [ -n "$HM_LEFTOVER" ]; then
        add "Task folders were left in .claude/memory/in-progress/ on $HM_BRANCH: $HM_LEFTOVER. They should have been closed before the merge (horka-memory:horka-memory-close)."
      fi
    fi
    ;;
  *)
    if [ "$HM_MEM" = "present" ]; then
      add "Project memory found in .claude/memory/. Use horka-memory:horka-memory-restore to read it before working on the project."
    fi
    ;;
esac

[ -n "$MSG" ] || exit 0
printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "$(printf '%s' "$MSG" | hm_json_escape)"
exit 0
