#!/bin/bash
# SessionStart hook: tells Claude what project memory exists here and how far it can be trusted.
# It measures (commits since the last update) instead of only checking that files exist:
# a memory left as an empty template after 500 commits must not be announced as "found".
# Every name that comes from the file system or from git goes through hm_clean before it is printed.

. "$(dirname "$0")/lib.sh"
cat >/dev/null 2>&1   # the payload is not needed here
hm_status

MSG=""
add() { MSG="${MSG}${MSG:+
}$1"; }
BR="\`$(hm_clean "$HM_BRANCH")\`"     # shown as a name, in backticks, never as a sentence

behind_text() {   # <count> -> "12 commits behind" | "freshness unknown (...)"
  if hm_is_number "$1"; then
    if [ "$1" -ge "$HM_COUNT_CAP" ]; then echo "more than $HM_COUNT_CAP commits behind"; else echo "$1 commits behind"; fi
  elif [ "$HM_SHALLOW" = "yes" ]; then echo "freshness unknown (shallow clone)"
  else echo "freshness unknown (no history for it)"; fi
}

case "$HM_KIND" in
  workspace)
    WITH=""
    while IFS= read -r r; do
      [ -n "$r" ] || continue
      [ -f "$HM_ROOT/$r/.claude/memory/PROJECT_STATE.md" ] && WITH="${WITH}${WITH:+, }$(hm_clean "$r")"
    done <<EOF2
$HM_REPOS
EOF2
    add "This folder holds $HM_REPO_COUNT git repositories and is not itself a project: do not create memory files here."
    add "Project memory lives in each repository${WITH:+ (present in: $WITH)}. Use horka-memory:horka-memory-restore, which restores from the repositories that have memory."
    [ "$HM_MEM" != "absent" ] && add "The .claude/memory/ files of this folder are notes about the workspace as a whole: read them as an index of the repositories, not as the state of a project."
    ;;
  repo)
    case "$HM_MEM" in
      absent)
        if [ "$HM_TASK_BRANCH" = "yes" ]; then
          add "No project memory in this repository. It is initialized from a base branch, not from task branch $BR: say so if the work needs it."
        elif [ "$HM_TASK_BRANCH" = "unknown" ]; then
          add "No project memory in this repository, and branch $BR cannot be classified (no base branch in this clone). Ask whether it is the project's main line before initializing the memory with horka-memory:horka-memory-restore."
        else
          add "No project memory in this repository (.claude/memory/ is empty). Use the horka-memory:horka-memory-restore skill to initialize it before working on the project."
        fi ;;
      partial)
        if [ "$HM_TASK_BRANCH" = "yes" ]; then
          add "Project memory in .claude/memory/ is incomplete (no PROJECT_STATE.md). The missing files are created from a base branch, not from task branch $BR: say so if the work needs them."
        elif [ "$HM_TASK_BRANCH" = "unknown" ]; then
          add "Project memory in .claude/memory/ is incomplete (no PROJECT_STATE.md), and branch $BR cannot be classified (no base branch in this clone). Ask whether it is the project's main line before creating the missing files."
        else
          add "Project memory in .claude/memory/ is incomplete (no PROJECT_STATE.md). Use horka-memory:horka-memory-restore, which creates the missing files."
        fi ;;
      present)
        if [ "$HM_TASK_BRANCH" = "yes" ]; then
          add "Project memory found in .claude/memory/. Its freshness is measured on a base branch, not from task branch $BR: read it with horka-memory:horka-memory-restore and trust the code where they differ."
        elif [ "$HM_STALE" = "yes" ]; then
          add "Project memory found in .claude/memory/ but it is $(behind_text "$HM_BEHIND") the code. Treat it as outdated: the code wins. Use horka-memory:horka-memory-restore, which will say what to refresh."
        else
          add "Project memory found in .claude/memory/ ($(behind_text "$HM_BEHIND")). Use horka-memory:horka-memory-restore to read it before working on the project."
        fi
        case "$HM_TASK_BRANCH:$HM_TASK_FILE" in
          yes:present)
            add "Task in progress on branch $BR: .claude/memory/in-progress/$HM_TASK_ID/TASK.md ($(behind_text "$HM_TASK_BEHIND")). It says where the last person stopped: read it before continuing this task." ;;
          yes:closed)
            if [ -n "$HM_DEFAULT_BRANCH" ]; then
              add "The task of branch $BR was closed (its task folder was promoted and deleted) and has not reached origin/$(hm_clean "$HM_DEFAULT_BRANCH") yet. Commits made since the close: $HM_TASK_BEHIND."
            else
              add "The task of branch $BR was closed (its task folder was promoted and deleted) and is on no base branch yet. Commits made since the close: $HM_TASK_BEHIND."
            fi ;;
          yes:absent)
            # Only when the branch has work of its own: a fresh branch, or one already merged, has nothing to write down.
            case "$HM_HAS_WORK" in
              yes) add "Branch $BR has $HM_OWN_WORK commits of its own and no task file yet (.claude/memory/in-progress/$HM_TASK_ID/TASK.md). horka-memory:horka-memory-save creates it." ;;
              some) add "Branch $BR has work of its own and no task file yet (.claude/memory/in-progress/$HM_TASK_ID/TASK.md). horka-memory:horka-memory-save creates it." ;;
            esac ;;
          no:*)
            # The count only: a folder name is somebody else's text and does not belong in the assistant's context.
            [ "$HM_LEFTOVER_COUNT" -gt 0 ] && add "$HM_LEFTOVER_COUNT task folder(s) were left in .claude/memory/in-progress/ on $BR. They should have been closed before the merge (horka-memory:horka-memory-close lists them)." ;;
          unknown:*)
            add "Branch $BR cannot be classified (no base branch in this clone to compare with): nothing is assumed about a task." ;;
        esac ;;
    esac
    ;;
  *)
    [ "$HM_MEM" != "absent" ] && add "Project memory found in .claude/memory/. Use horka-memory:horka-memory-restore to read it before working on the project."
    ;;
esac

[ -n "$MSG" ] || exit 0
printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "$(printf '%s' "$MSG" | hm_json_escape)"
exit 0
