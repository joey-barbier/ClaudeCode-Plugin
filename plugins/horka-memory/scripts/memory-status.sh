#!/bin/bash
# Prints the state of the project memory as "key: value" lines. Read-only.
# Used by the skills (restore, save, close) so they start from measured facts, not from guesses.
# A value of "?" or "unknown" means it could not be measured (shallow clone, no history): say so, never guess.

. "$(dirname "$0")/lib.sh"
hm_status

echo "root: $HM_ROOT"
echo "kind: $HM_KIND"                       # repo | workspace (several repositories, not a project) | folder
if [ "$HM_KIND" = "workspace" ]; then
  printf '%s\n' "$HM_REPOS" | while IFS= read -r r; do
    [ -n "$r" ] || continue
    if [ -f "$HM_ROOT/$r/.claude/memory/PROJECT_STATE.md" ]; then echo "repository: $r (memory: present)"; else echo "repository: $r (memory: absent)"; fi
  done
fi
echo "memory: $HM_MEM"                      # present | partial (no PROJECT_STATE.md) | absent
if [ "$HM_KIND" = "repo" ]; then
  [ "$HM_SHALLOW" = "yes" ] && echo "shallow: yes"       # counts below are unknown
  echo "branch: ${HM_BRANCH:-detached}"
  echo "default_branch: ${HM_DEFAULT_BRANCH:-unknown}"
  if [ "$HM_MEM" = "present" ]; then
    echo "saved: ${HM_SAVED:-no usable marker}"           # "<commit> <date>" of the last save, when that commit is in the history
    echo "behind: $HM_BEHIND"               # commits since the memory was last updated, memory-only commits not counted
    echo "stale: $HM_STALE"                 # yes when behind >= $HM_STALE_COMMITS
  fi
  echo "task_branch: $HM_TASK_BRANCH"       # yes | no (a base branch) | detached | unknown (no base branch in this clone to compare with)
  if [ "$HM_TASK_BRANCH" = "yes" ]; then
    echo "base: ${HM_BASE_REF:-unknown}"    # the base this branch is measured against
    echo "base_source: ${HM_BASE_SOURCE:-none}"   # recorded (written in TASK.md by a save) | guessed (nearest base branch) | none
    echo "task_id: $HM_TASK_ID"
    echo "task_dir: .claude/memory/in-progress/$HM_TASK_ID"
    echo "task_file: $HM_TASK_FILE"         # present | absent | closed (deleted by a close on this branch)
    if [ "$HM_TASK_FILE" != "absent" ]; then
      [ "$HM_TASK_FILE" = "present" ] && echo "task_saved: ${HM_TASK_SAVED:-no usable marker}"
      echo "task_behind: $HM_TASK_BEHIND"   # this branch's own commits since the task file was written (or closed)
      echo "task_stale: $HM_TASK_STALE"     # yes when task_behind >= $HM_TASK_STALE_COMMITS
    fi
    echo "ahead_of_base: $HM_AHEAD"         # this branch's own work commits (merges and memory-only commits left out)
    echo "unpushed: $HM_UNPUSHED"           # a count | not-on-remote (never pushed, or deleted there) | n/a (no remote)
    echo "local_only: $HM_LOCAL_ONLY"       # commits that are on no remote branch at all | n/a (no remote)
  elif [ "$HM_TASK_BRANCH" = "no" ]; then
    [ -n "$HM_LEFTOVER" ] && echo "leftover_tasks: $HM_LEFTOVER"
  fi
  echo "uncommitted: $HM_DIRTY"             # files changed or untracked in the working tree
  echo "head: $(git -C "$HM_ROOT" rev-parse --short HEAD 2>/dev/null)"
  echo "today: $(date +%Y-%m-%d)"
fi
exit 0
