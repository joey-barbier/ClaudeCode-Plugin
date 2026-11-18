#!/bin/bash
# Shared helpers for the horka-memory hooks and skills.
# Source this file, then call hm_status: it fills the HM_* variables below and prints nothing.
# Works with the bash 3.2 that ships with macOS (no associative arrays, no mapfile) and with GNU or BSD tools.
#
# Environment (set them in the "env" of the Claude Code settings so the hooks see them):
#   HORKA_MEMORY_BASE_BRANCHES       branches that are never a task (default below; add e.g. "production")
#   HORKA_MEMORY_STALE_COMMITS       project memory is called stale from this many commits behind (20)
#   HORKA_MEMORY_TASK_STALE_COMMITS  same for a task file (3)
#   HORKA_MEMORY_REMIND_SECONDS      delay before the stop check repeats the same finding (1800)

HM_STALE_COMMITS="${HORKA_MEMORY_STALE_COMMITS:-20}"
HM_TASK_STALE_COMMITS="${HORKA_MEMORY_TASK_STALE_COMMITS:-3}"
HM_BASE_BRANCHES="${HORKA_MEMORY_BASE_BRANCHES:-main master develop dev integration staging trunk}"
HM_COUNT_CAP="${HORKA_MEMORY_COUNT_CAP:-1000}"     # counting stops here: a hook must stay fast on a very large history

# stdin -> body of a JSON string (no surrounding quotes). sed does the escaping: awk's gsub differs between awks.
hm_json_escape() {
  LC_ALL=C sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' | LC_ALL=C tr '\t\r' '  ' | LC_ALL=C tr -d '\000-\010\013\014\016-\037' \
    | awk 'BEGIN { ORS = "\\n" } { print }' | sed 's/\\n$//'
}

# A name taken from the file system or from git, made safe to print into the assistant's context:
# only plain characters, capped. A folder or branch name must never be able to carry a sentence.
hm_clean() {
  printf '%s' "$1" | LC_ALL=C tr -c 'A-Za-z0-9._/@+-' '?' | cut -c1-80
}

# Reads the hook payload on stdin and prints a file-safe session id.
# The id must be stable across the hook calls of one session: never build it from $$ (new for every call).
hm_session_id() {
  local payload id
  payload="$(cat 2>/dev/null)"
  id="$(printf '%s' "$payload" | sed -n 's/.*"session_id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)"
  id="$(printf '%s' "$id" | LC_ALL=C tr -cd 'A-Za-z0-9_-' | cut -c1-80)"
  [ -n "$id" ] || id="nosession"
  printf '%s' "$id"
}

# A private folder for the stop check's state. Fails (returns 1) when it cannot be made safe:
# it must be a real directory owned by the current user, so nobody else can plant a link in it.
hm_state_dir() {
  local d="${TMPDIR:-/tmp}"
  d="${d%/}/horka-memory-$(id -u)"
  mkdir -p -m 700 "$d" 2>/dev/null
  [ -d "$d" ] && [ ! -L "$d" ] && [ -O "$d" ] && [ -w "$d" ] || return 1
  printf '%s' "$d"
}

# Task id of a branch: "/" becomes "-", then only letters, digits, ".", "_" and "-" are kept.
# When that drops characters or leaves nothing ("é.é", a name in another script), a hash of the full
# branch name is appended so the id is never empty, never "." or "..", and stays unique.
# Known limit: "feature/login" and "feature-login" share one id.
hm_task_id() {
  local b="$1" flat id
  flat="$(printf '%s' "$b" | tr '/' '-')"
  id="$(printf '%s' "$flat" | LC_ALL=C tr -cd 'A-Za-z0-9._-' | sed 's/^[.-]*//' | cut -c1-80)"
  if [ -z "$id" ] || [ "$id" != "$flat" ]; then
    id="${id:+$id-}$(printf '%s' "$b" | git hash-object --stdin 2>/dev/null | cut -c1-8)"
  fi
  printf '%s' "$id"
}

hm_default_branch() {
  git -C "$HM_ROOT" symbolic-ref --short -q refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##'
}

# Nearest base ref of the current branch (fewest commits between it and HEAD), or nothing.
# Looks at origin/HEAD and at every base branch, remote then local, so a clone without origin/HEAD
# or a branch cut from develop is still measured against the right base.
# This is a guess, used only until the task file records the base (hm_task_base). Known limit of the
# guess: a branch already merged into one of these bases (a local staging, say) is measured against that
# one. The stop check does not rely on it alone: it also counts the commits that exist on this machine only.
hm_base_ref() {
  local best="" bestn="" c n cands=""
  [ -n "$HM_DEFAULT_BRANCH" ] && cands="origin/$HM_DEFAULT_BRANCH"
  for c in $HM_BASE_BRANCHES; do cands="$cands origin/$c $c"; done
  for c in $cands; do
    [ "$c" = "$HM_BRANCH" ] && continue
    git -C "$HM_ROOT" rev-parse -q --verify "$c^{commit}" >/dev/null 2>&1 || continue
    n="$(git -C "$HM_ROOT" rev-list --count --max-count="$HM_COUNT_CAP" "$c"..HEAD 2>/dev/null)" || continue
    if [ -z "$bestn" ] || [ "$n" -lt "$bestn" ]; then best="$c"; bestn="$n"; fi
  done
  printf '%s' "$best"
}

hm_is_base_branch() {
  local b="$1" x
  [ "$b" = "$HM_DEFAULT_BRANCH" ] && return 0
  case "$b" in release/*) return 0 ;; esac
  for x in $HM_BASE_BRANCHES; do [ "$b" = "$x" ] && return 0; done
  return 1
}

# Prints "<hash> <date>" from the last marker line of a memory file, or nothing.
hm_marker() {
  [ -f "$1" ] || return 0
  grep -o 'memory-saved: [0-9a-f]\{7,40\} [0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}' "$1" 2>/dev/null | tail -1 | sed 's/^memory-saved: //'
}

# Base recorded in a task file by its first save ("<!-- task-base: main -->"), resolved to a ref of this
# clone (the remote one first), or nothing. A recorded base replaces the guess of hm_base_ref: it does not
# move when a teammate merges the branch into another base.
hm_task_base() {
  local file="$1" name
  [ -f "$file" ] || return 0
  name="$(grep -o 'task-base: [A-Za-z0-9._/-]\{1,100\}' "$file" 2>/dev/null | tail -1 | sed 's/^task-base: //')"
  case "$name" in ''|-*|*..*) return 0 ;; esac
  [ "$name" = "$HM_BRANCH" ] && return 0
  if git -C "$HM_ROOT" rev-parse -q --verify "refs/remotes/origin/$name^{commit}" >/dev/null 2>&1; then
    printf 'origin/%s' "$name"
  elif git -C "$HM_ROOT" rev-parse -q --verify "refs/heads/$name^{commit}" >/dev/null 2>&1; then
    printf '%s' "$name"
  fi
}

# Commits between <ref> and <target> that changed something other than the memory, not counting merge
# commits nor those already on <exclude> (the base, for a task). Prints "?" when it cannot be measured.
hm_count() {
  local ref="$1" target="$2" exclude="$3" n all
  [ -n "$ref" ] || { printf '?'; return 0; }
  # A path-limited walk is the expensive part and --max-count does not shorten it. Count the plain range
  # first (cheap): past the cap, say so and skip the path-limited walk.
  all="$(git -C "$HM_ROOT" rev-list --count --max-count="$HM_COUNT_CAP" "$ref".."$target" ${exclude:+"^$exclude"} 2>/dev/null)"
  [ -n "$all" ] || { printf '?'; return 0; }
  if [ "$all" -ge "$HM_COUNT_CAP" ]; then printf '%s' "$HM_COUNT_CAP"; return 0; fi
  if [ -n "$exclude" ]; then
    n="$(git -C "$HM_ROOT" rev-list --count --no-merges --max-count="$HM_COUNT_CAP" "$ref".."$target" "^$exclude" -- . ':(exclude).claude/memory' 2>/dev/null)"
  else
    n="$(git -C "$HM_ROOT" rev-list --count --no-merges --max-count="$HM_COUNT_CAP" "$ref".."$target" -- . ':(exclude).claude/memory' 2>/dev/null)"
  fi
  printf '%s' "${n:-?}"
}

# How far <file> is behind <target>. Two references are tried and the nearer one wins:
# the marker written by the last save (only if that commit is an ancestor of the target: a rebase or a
# foreign hash does not count), and the last commit that touched the file (first-parent on a base branch,
# so a merged task that updated the memory resets the count whatever its marker says).
# Sets HM_OUT_BEHIND ("?" when unknown) and HM_OUT_SAVED ("<hash> <date>" only when the marker is usable).
hm_freshness() {
  local file="$1" target="$2" exclude="$3" firstparent="$4" mark hash a b last
  HM_OUT_BEHIND="?"; HM_OUT_SAVED=""
  [ "$HM_SHALLOW" = "yes" ] && return 0      # a shallow clone cannot count: say unknown, never a number
  mark="$(hm_marker "$file")"; hash="${mark%% *}"; a="?"; b="?"
  if [ -n "$hash" ] && git -C "$HM_ROOT" merge-base --is-ancestor "$hash" "$target" 2>/dev/null; then
    a="$(hm_count "$hash" "$target" "$exclude")"; HM_OUT_SAVED="$mark"
  fi
  last="$(git -C "$HM_ROOT" log -1 ${firstparent:+--first-parent} --format=%H "$target" -- "$file" 2>/dev/null)"
  [ -n "$last" ] && b="$(hm_count "$last" "$target" "$exclude")"
  case "$a:$b" in
    '?:?') ;;
    '?:'*) HM_OUT_BEHIND="$b" ;;
    *':?') HM_OUT_BEHIND="$a" ;;
    *) if [ "$a" -le "$b" ]; then HM_OUT_BEHIND="$a"; else HM_OUT_BEHIND="$b"; fi ;;
  esac
  return 0
}

hm_is_number() { case "$1" in ''|*[!0-9]*) return 1 ;; *) return 0 ;; esac; }

hm_status() {
  HM_ROOT=""; HM_KIND="folder"; HM_REPOS=""; HM_REPO_COUNT=0; HM_SHALLOW="no"
  HM_MEM="absent"; HM_MEM_DIR=""; HM_SAVED=""; HM_BEHIND="?"; HM_STALE="unknown"
  HM_BRANCH=""; HM_DEFAULT_BRANCH=""; HM_BASE_REF=""; HM_TASK_BRANCH="no"; HM_TASK_ID=""; HM_TASK_DIR=""
  HM_TASK_FILE="absent"; HM_TASK_SAVED=""; HM_TASK_BEHIND="?"; HM_TASK_STALE="unknown"
  HM_AHEAD="?"; HM_OWN="?"; HM_UNPUSHED="n/a"; HM_LOCAL_ONLY="n/a"; HM_BASE_SOURCE=""; HM_DIRTY=0; HM_LEFTOVER=""; HM_LEFTOVER_COUNT=0

  if HM_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" && [ -n "$HM_ROOT" ]; then
    HM_KIND="repo"
  else
    HM_ROOT="$(pwd)"
    local d
    for d in "$HM_ROOT"/*/; do
      [ -e "${d}.git" ] || continue
      HM_REPO_COUNT=$((HM_REPO_COUNT + 1))
      HM_REPOS="${HM_REPOS}${HM_REPOS:+
}$(basename "$d")"          # one name per line: a folder name may contain spaces
    done
    [ "$HM_REPO_COUNT" -ge 2 ] && HM_KIND="workspace"
  fi

  HM_MEM_DIR="$HM_ROOT/.claude/memory"
  if [ -f "$HM_MEM_DIR/PROJECT_STATE.md" ]; then
    HM_MEM="present"
  elif ls "$HM_MEM_DIR"/*.md >/dev/null 2>&1; then
    HM_MEM="partial"            # some files but no PROJECT_STATE.md: restore creates the missing ones
  fi

  [ "$HM_KIND" = "repo" ] || return 0

  [ "$(git -C "$HM_ROOT" rev-parse --is-shallow-repository 2>/dev/null)" = "true" ] && HM_SHALLOW="yes"
  HM_BRANCH="$(git -C "$HM_ROOT" symbolic-ref --short -q HEAD 2>/dev/null)"
  HM_DEFAULT_BRANCH="$(hm_default_branch)"
  HM_DIRTY="$(git -C "$HM_ROOT" status --porcelain 2>/dev/null | head -200 | grep -c .)"

  local target="HEAD"
  if [ -n "$HM_BRANCH" ] && ! hm_is_base_branch "$HM_BRANCH"; then
    local own="$HM_MEM_DIR/in-progress/$(hm_task_id "$HM_BRANCH")/TASK.md"
    HM_BASE_REF="$(hm_task_base "$own")"
    if [ -n "$HM_BASE_REF" ]; then
      HM_BASE_SOURCE="recorded"; HM_TASK_BRANCH="yes"
    else
      HM_BASE_REF="$(hm_base_ref)"
      if [ -n "$HM_BASE_REF" ]; then
        HM_BASE_SOURCE="guessed"; HM_TASK_BRANCH="yes"
      elif [ -f "$own" ]; then
        HM_TASK_BRANCH="yes"    # no base in this clone (single-branch, shallow), but the branch carries its own task file
      else
        # No base to compare with and a name that is not a base name: it may be the project's only line of
        # work or a task cloned alone. Do not guess: freshness is still measured, nothing is said about tasks.
        HM_TASK_BRANCH="unknown"
      fi
    fi
  fi
  # Detached HEAD (rebase, bisect, a commit checked out): no branch, so no task; the project memory is still measured.
  [ -n "$HM_BRANCH" ] || HM_TASK_BRANCH="detached"

  if [ "$HM_TASK_BRANCH" = "yes" ] && [ -n "$HM_BASE_REF" ]; then
    # Seen from a task branch, the project memory is judged at the point the branch left its base.
    target="$(git -C "$HM_ROOT" merge-base HEAD "$HM_BASE_REF" 2>/dev/null)"; [ -n "$target" ] || target="HEAD"
  fi
  if [ "$HM_MEM" = "present" ]; then
    hm_freshness "$HM_MEM_DIR/PROJECT_STATE.md" "$target" "" firstparent
    HM_SAVED="$HM_OUT_SAVED"; HM_BEHIND="$HM_OUT_BEHIND"
    if hm_is_number "$HM_BEHIND"; then
      if [ "$HM_BEHIND" -ge "$HM_STALE_COMMITS" ]; then HM_STALE="yes"; else HM_STALE="no"; fi
    fi
  fi

  if [ "$HM_TASK_BRANCH" = "yes" ]; then
    HM_TASK_ID="$(hm_task_id "$HM_BRANCH")"
    HM_TASK_DIR="$HM_MEM_DIR/in-progress/$HM_TASK_ID"
    local rel=".claude/memory/in-progress/$HM_TASK_ID/TASK.md" closed
    if [ -f "$HM_TASK_DIR/TASK.md" ]; then
      HM_TASK_FILE="present"
      hm_freshness "$HM_TASK_DIR/TASK.md" HEAD "$HM_BASE_REF" ""
      HM_TASK_SAVED="$HM_OUT_SAVED"; HM_TASK_BEHIND="$HM_OUT_BEHIND"
    else
      # Closed and waiting for its merge: a commit of this branch deleted the task file. Only a committed
      # deletion counts (a file removed from the working tree is just missing).
      # Known limit: a close that had no task folder to delete leaves no trace and is not recognised.
      closed=""
      [ -n "$HM_BASE_REF" ] && closed="$(git -C "$HM_ROOT" log -1 --diff-filter=D --format=%H "$HM_BASE_REF"..HEAD -- "$rel" 2>/dev/null)"
      if [ -n "$closed" ]; then
        HM_TASK_FILE="closed"
        [ "$HM_SHALLOW" = "yes" ] || HM_TASK_BEHIND="$(hm_count "$closed" HEAD "$HM_BASE_REF")"
      fi
    fi
    if hm_is_number "$HM_TASK_BEHIND"; then
      if [ "$HM_TASK_BEHIND" -ge "$HM_TASK_STALE_COMMITS" ]; then HM_TASK_STALE="yes"; else HM_TASK_STALE="no"; fi
    fi
    # Work of this branch: its own commits, merges and memory-only commits left out.
    # HM_OWN counts every commit of its own, memory included: that is what a push would send.
    if [ -n "$HM_BASE_REF" ] && [ "$HM_SHALLOW" != "yes" ]; then
      HM_AHEAD="$(hm_count "$HM_BASE_REF" HEAD "")"
      HM_OWN="$(git -C "$HM_ROOT" rev-list --count --max-count="$HM_COUNT_CAP" "$HM_BASE_REF"..HEAD 2>/dev/null || printf '?')"
    fi
    # Pushed means: on the remote under its own name. An upstream set to the base (git checkout -b x origin/main) says nothing.
    if git -C "$HM_ROOT" rev-parse -q --verify "refs/remotes/origin/$HM_BRANCH" >/dev/null 2>&1; then
      HM_UNPUSHED="$(git -C "$HM_ROOT" rev-list --count --max-count="$HM_COUNT_CAP" "origin/$HM_BRANCH"..HEAD 2>/dev/null || printf '0')"
    elif git -C "$HM_ROOT" remote get-url origin >/dev/null 2>&1; then
      HM_UNPUSHED="not-on-remote"
    fi
    # Commits that exist on this machine only, whatever the base is: on no remote branch at all.
    if git -C "$HM_ROOT" remote get-url origin >/dev/null 2>&1; then
      HM_LOCAL_ONLY="$(git -C "$HM_ROOT" rev-list --count --max-count="$HM_COUNT_CAP" HEAD --not --remotes 2>/dev/null || printf '?')"
    fi
  elif [ "$HM_TASK_BRANCH" = "no" ]; then
    # On a base branch nothing should be left in in-progress/: a task folder there was merged by mistake.
    # (Not on a detached HEAD nor on a branch we could not classify: the folder may be the branch's own.)
    local t
    for t in "$HM_MEM_DIR"/in-progress/*/; do
      [ -d "$t" ] || continue
      HM_LEFTOVER="$HM_LEFTOVER $(hm_clean "$(basename "$t")")"
      HM_LEFTOVER_COUNT=$((HM_LEFTOVER_COUNT + 1))
    done
    HM_LEFTOVER="${HM_LEFTOVER# }"
  fi
  return 0
}
