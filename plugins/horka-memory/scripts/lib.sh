#!/bin/bash
# Shared helpers for the horka-memory hooks and skills.
# Source this file, then call hm_status: it fills the HM_* variables below and prints nothing.
# Works with the bash 3.2 that ships with macOS: no associative arrays, no mapfile.

HM_STALE_COMMITS="${HORKA_MEMORY_STALE_COMMITS:-20}"
HM_TASK_STALE_COMMITS="${HORKA_MEMORY_TASK_STALE_COMMITS:-3}"
HM_BASE_BRANCHES="${HORKA_MEMORY_BASE_BRANCHES:-main master develop dev integration staging trunk}"

# stdin -> body of a JSON string (no surrounding quotes)
hm_json_escape() {
  awk 'BEGIN { ORS = "\\n" } { gsub(/\\/, "\\\\"); gsub(/"/, "\\\""); gsub(/\t/, "\\t"); gsub(/\r/, ""); print }' \
    | sed 's/\\n$//'
}

# Reads the hook payload on stdin and prints a file-safe session id.
# The id must be stable across the hook calls of one session: never build it from $$ (new for every call).
hm_session_id() {
  local payload id
  payload="$(cat 2>/dev/null)"
  id="$(printf '%s' "$payload" | sed -n 's/.*"session_id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)"
  id="$(printf '%s' "$id" | tr -cd 'A-Za-z0-9_-')"
  [ -n "$id" ] || id="nosession"
  printf '%s' "$id"
}

hm_state_dir() {
  local d="${TMPDIR:-/tmp}"
  d="${d%/}/horka-memory"
  mkdir -p "$d" 2>/dev/null
  printf '%s' "$d"
}

# "feature/login form" -> "feature-login-form"
hm_task_id() {
  printf '%s' "$1" | tr '/ ' '--' | tr -cd 'A-Za-z0-9._-'
}

hm_default_branch() {
  git -C "$HM_ROOT" symbolic-ref --short -q refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##'
}

hm_is_base_branch() {
  local b="$1" x
  [ -n "$b" ] || return 0            # detached HEAD: never a task branch
  [ "$b" = "$HM_DEFAULT_BRANCH" ] && return 0
  case "$b" in release/*|hotfix-base/*) return 0 ;; esac
  for x in $HM_BASE_BRANCHES; do [ "$b" = "$x" ] && return 0; done
  return 1
}

# Prints "<hash> <date>" from the marker line of a memory file, or nothing.
hm_marker() {
  [ -f "$1" ] || return 0
  grep -o 'memory-saved: [0-9a-f]\{7,40\} [0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}' "$1" 2>/dev/null | tail -1 | sed 's/^memory-saved: //'
}

# Commit a memory file was last saved against: its marker when that commit still exists,
# else the last commit that touched the file. Prints nothing when neither is known.
hm_ref_commit() {
  local file="$1" hash
  hash="$(hm_marker "$file" | cut -d' ' -f1)"
  if [ -n "$hash" ] && git -C "$HM_ROOT" cat-file -e "${hash}^{commit}" 2>/dev/null; then
    printf '%s' "$hash"; return 0
  fi
  git -C "$HM_ROOT" log -1 --format=%H -- "$file" 2>/dev/null
}

# Commits since <ref> that changed something other than the memory itself.
hm_behind() {
  [ -n "$1" ] || { printf '?'; return 0; }
  git -C "$HM_ROOT" rev-list --count "$1"..HEAD -- . ':(exclude).claude/memory' 2>/dev/null || printf '?'
}

hm_status() {
  HM_ROOT=""; HM_KIND="folder"; HM_REPOS=""; HM_REPO_COUNT=0
  HM_MEM="absent"; HM_MEM_DIR=""; HM_SAVED=""; HM_BEHIND="?"; HM_STALE="no"
  HM_BRANCH=""; HM_DEFAULT_BRANCH=""; HM_TASK_BRANCH="no"; HM_TASK_ID=""; HM_TASK_DIR=""
  HM_TASK_FILE="absent"; HM_TASK_SAVED=""; HM_TASK_BEHIND="?"; HM_TASK_STALE="no"
  HM_AHEAD="?"; HM_UNPUSHED="0"; HM_LEFTOVER=""

  if HM_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" && [ -n "$HM_ROOT" ]; then
    HM_KIND="repo"
  else
    HM_ROOT="$(pwd)"
    local d
    for d in "$HM_ROOT"/*/; do
      [ -e "${d}.git" ] || continue
      HM_REPO_COUNT=$((HM_REPO_COUNT + 1))
      HM_REPOS="$HM_REPOS $(basename "$d")"
    done
    HM_REPOS="${HM_REPOS# }"
    [ "$HM_REPO_COUNT" -ge 2 ] && HM_KIND="workspace"
  fi

  HM_MEM_DIR="$HM_ROOT/.claude/memory"
  if ls "$HM_MEM_DIR"/*.md >/dev/null 2>&1; then HM_MEM="present"; fi

  [ "$HM_KIND" = "repo" ] || return 0

  HM_BRANCH="$(git -C "$HM_ROOT" symbolic-ref --short -q HEAD 2>/dev/null)"
  HM_DEFAULT_BRANCH="$(hm_default_branch)"

  if [ "$HM_MEM" = "present" ]; then
    local state="$HM_MEM_DIR/PROJECT_STATE.md"
    HM_SAVED="$(hm_marker "$state")"
    HM_BEHIND="$(hm_behind "$(hm_ref_commit "$state")")"
    case "$HM_BEHIND" in
      ''|*[!0-9]*) ;;
      *) [ "$HM_BEHIND" -ge "$HM_STALE_COMMITS" ] && HM_STALE="yes" ;;
    esac
  fi

  if ! hm_is_base_branch "$HM_BRANCH"; then
    HM_TASK_BRANCH="yes"
    HM_TASK_ID="$(hm_task_id "$HM_BRANCH")"
    HM_TASK_DIR="$HM_MEM_DIR/in-progress/$HM_TASK_ID"
    if [ -f "$HM_TASK_DIR/TASK.md" ]; then
      HM_TASK_FILE="present"
      HM_TASK_SAVED="$(hm_marker "$HM_TASK_DIR/TASK.md")"
      HM_TASK_BEHIND="$(hm_behind "$(hm_ref_commit "$HM_TASK_DIR/TASK.md")")"
      case "$HM_TASK_BEHIND" in
        ''|*[!0-9]*) ;;
        *) [ "$HM_TASK_BEHIND" -ge "$HM_TASK_STALE_COMMITS" ] && HM_TASK_STALE="yes" ;;
      esac
    fi
    if [ -n "$HM_DEFAULT_BRANCH" ] && git -C "$HM_ROOT" rev-parse -q --verify "origin/$HM_DEFAULT_BRANCH" >/dev/null 2>&1; then
      HM_AHEAD="$(git -C "$HM_ROOT" rev-list --count "origin/$HM_DEFAULT_BRANCH"..HEAD 2>/dev/null || printf '?')"
    fi
    if git -C "$HM_ROOT" rev-parse -q --verify '@{u}' >/dev/null 2>&1; then
      HM_UNPUSHED="$(git -C "$HM_ROOT" rev-list --count '@{u}'..HEAD 2>/dev/null || printf '0')"
    else
      HM_UNPUSHED="no-upstream"
    fi
  else
    # On a base branch nothing should be left in in-progress/: a task folder there was merged by mistake.
    local t
    for t in "$HM_MEM_DIR"/in-progress/*/; do
      [ -d "$t" ] || continue
      HM_LEFTOVER="$HM_LEFTOVER $(basename "$t")"
    done
    HM_LEFTOVER="${HM_LEFTOVER# }"
  fi
  return 0
}
