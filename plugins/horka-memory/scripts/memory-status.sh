#!/bin/bash
# Prints the state of the project memory as "key: value" lines. Read-only.
# Used by the skills (restore, save, close) so they start from measured facts, not from guesses.

. "$(dirname "$0")/lib.sh"
hm_status

echo "root: $HM_ROOT"
echo "kind: $HM_KIND"                       # repo | workspace (several repositories, not a project) | folder
[ "$HM_KIND" = "workspace" ] && echo "repositories: $HM_REPOS"
echo "memory: $HM_MEM"
if [ "$HM_KIND" = "repo" ]; then
  echo "branch: ${HM_BRANCH:-detached}"
  echo "default_branch: ${HM_DEFAULT_BRANCH:-unknown}"
  if [ "$HM_MEM" = "present" ]; then
    echo "saved: ${HM_SAVED:-no marker}"    # "<commit> <date>" written by the last save
    echo "behind: $HM_BEHIND"               # commits since that save, memory-only commits not counted
    echo "stale: $HM_STALE"                 # yes when behind >= $HM_STALE_COMMITS
  fi
  echo "task_branch: $HM_TASK_BRANCH"
  if [ "$HM_TASK_BRANCH" = "yes" ]; then
    echo "task_id: $HM_TASK_ID"
    echo "task_dir: .claude/memory/in-progress/$HM_TASK_ID"
    echo "task_file: $HM_TASK_FILE"
    if [ "$HM_TASK_FILE" = "present" ]; then
      echo "task_saved: ${HM_TASK_SAVED:-no marker}"
      echo "task_behind: $HM_TASK_BEHIND"
      echo "task_stale: $HM_TASK_STALE"     # yes when task_behind >= $HM_TASK_STALE_COMMITS
    fi
    echo "ahead_of_default: $HM_AHEAD"
    echo "unpushed: $HM_UNPUSHED"           # a count, or no-upstream when the branch was never pushed
  else
    [ -n "$HM_LEFTOVER" ] && echo "leftover_tasks: $HM_LEFTOVER"
  fi
  echo "head: $(git -C "$HM_ROOT" rev-parse --short HEAD 2>/dev/null)"
  echo "today: $(date +%Y-%m-%d)"
fi
exit 0
