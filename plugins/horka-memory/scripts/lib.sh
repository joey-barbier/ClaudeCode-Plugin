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

hm_is_number() { case "$1" in ''|*[!0-9]*) return 1 ;; *) return 0 ;; esac; }

hm_is_base_branch() {
  local b="$1" x
  [ -n "$b" ] || return 1
  [ "$b" = "$HM_DEFAULT_BRANCH" ] && return 0
  case "$b" in release/*) return 0 ;; esac
  for x in $HM_BASE_BRANCHES; do [ "$b" = "$x" ] && return 0; done
  return 1
}

# Every base branch that exists in this clone, remote and local, except the current branch.
# Nothing here chooses "the" base of a task: the hooks only ask whether a commit is on some base or on none.
hm_base_refs() {
  local c out="" cands=""
  [ -n "$HM_DEFAULT_BRANCH" ] && cands="origin/$HM_DEFAULT_BRANCH"
  for c in $HM_BASE_BRANCHES; do cands="$cands origin/$c $c"; done
  for c in $cands; do
    [ "$c" = "$HM_BRANCH" ] && continue
    case " $out " in *" $c "*) continue ;; esac
    git -C "$HM_ROOT" rev-parse -q --verify "$c^{commit}" >/dev/null 2>&1 && out="$out $c"
  done
  printf '%s' "${out# }"
}

# Prints "<hash> <date>" from the last marker line of a memory file, or nothing.
hm_marker() {
  [ -f "$1" ] || return 0
  grep -o 'memory-saved: [0-9a-f]\{7,40\} [0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}' "$1" 2>/dev/null | tail -1 | sed 's/^memory-saved: //'
}

# Base recorded in a task file by a save ("<!-- task-base: main -->" on a line of its own).
# Sets HM_BASE_REF, HM_BASE_SOURCE (recorded | recorded-missing) and HM_BASE_LOCAL_DIFFERS, or leaves them empty.
# Only the skills use it (is the branch up to date, may a check command run unasked): no hook depends on it.
hm_task_base() {
  local file="$1" name remote="" loc=""
  [ -f "$file" ] || return 0
  name="$(sed -n 's/^<!-- task-base: \([A-Za-z0-9._/-]\{1,100\}\) -->[[:space:]]*$/\1/p' "$file" 2>/dev/null | tail -1)"
  case "$name" in ''|HEAD|*/HEAD) return 0 ;; esac
  [ "$name" = "$HM_BRANCH" ] && return 0
  git -C "$HM_ROOT" rev-parse -q --verify "refs/remotes/origin/$name^{commit}" >/dev/null 2>&1 && remote="origin/$name"
  git -C "$HM_ROOT" rev-parse -q --verify "refs/heads/$name^{commit}" >/dev/null 2>&1 && loc="$name"
  if [ -n "$remote" ]; then
    HM_BASE_REF="$remote"; HM_BASE_SOURCE="recorded"
    # The local branch of the same name points elsewhere (a stale fork, a local merge): the skills must ask which one counts.
    if [ -n "$loc" ] && [ "$(git -C "$HM_ROOT" rev-parse "$loc" 2>/dev/null)" != "$(git -C "$HM_ROOT" rev-parse "$remote" 2>/dev/null)" ]; then
      HM_BASE_LOCAL_DIFFERS="yes"
    fi
  elif [ -n "$loc" ]; then
    HM_BASE_REF="$loc"
    # The remote exists but no longer has this branch (merged and deleted there): the record is stale.
    if git -C "$HM_ROOT" remote get-url origin >/dev/null 2>&1; then HM_BASE_SOURCE="recorded-missing"; else HM_BASE_SOURCE="recorded"; fi
  fi
}

# Number of non-merge commits in a rev-list selection that changed something other than the memory.
# Usage: hm_work <rev-list arguments...>. Prints "?" when git cannot answer, the cap when the plain
# selection is already that large (the path-limited walk is the expensive part and is skipped then).
hm_work() {
  local all n
  all="$(git -C "$HM_ROOT" rev-list --count --max-count="$HM_COUNT_CAP" "$@" 2>/dev/null)"
  [ -n "$all" ] || { printf '?'; return 0; }
  if [ "$all" -ge "$HM_COUNT_CAP" ]; then printf '%s' "$HM_COUNT_CAP"; return 0; fi
  n="$(git -C "$HM_ROOT" rev-list --count --no-merges "$@" -- . ':(exclude).claude/memory' 2>/dev/null)"
  printf '%s' "${n:-?}"
}

# Reference commit a memory file was last updated against: the marker of the last save when that commit is
# an ancestor of HEAD (a rebase or a foreign hash does not count), and the last commit that touched the file.
# Sets HM_OUT_REFS (one or two commits, the marker first) and HM_OUT_SAVED ("<hash> <date>" when usable).
hm_refs() {
  local file="$1" firstparent="$2" mark hash last
  HM_OUT_REFS=""; HM_OUT_SAVED=""; HM_OUT_LAST=""
  mark="$(hm_marker "$file")"; hash="${mark%% *}"
  if [ -n "$hash" ] && git -C "$HM_ROOT" merge-base --is-ancestor "$hash" HEAD 2>/dev/null; then
    HM_OUT_REFS="$hash"; HM_OUT_SAVED="$mark"
  fi
  last="$(git -C "$HM_ROOT" log -1 ${firstparent:+--first-parent} --format=%H HEAD -- "$file" 2>/dev/null)"
  HM_OUT_LAST="$last"
  [ -n "$last" ] && HM_OUT_REFS="$HM_OUT_REFS $last"
  HM_OUT_REFS="${HM_OUT_REFS# }"
}

# Smallest of several counts, "?" when none is a number.
hm_min() {
  local best="?" v
  for v in "$@"; do
    hm_is_number "$v" || continue
    if [ "$best" = "?" ] || [ "$v" -lt "$best" ]; then best="$v"; fi
  done
  printf '%s' "$best"
}

# Largest of several counts, "?" when none is a number.
hm_max() {
  local best="?" v
  for v in "$@"; do
    hm_is_number "$v" || continue
    if [ "$best" = "?" ] || [ "$v" -gt "$best" ]; then best="$v"; fi
  done
  printf '%s' "$best"
}

# How far a task file is behind, without knowing the base of the branch. Since <ref>, counts the commits
# that are the branch's own: those on its first-parent line (work done here, wherever it was merged since),
# plus those that are on no base branch (a colleague's commits pulled into this branch).
hm_task_behind() {
  local ref="$1" n b mb line not=""
  # A base that already contains <ref> because the branch was merged into it would hide the commits made
  # after <ref> as well: leave it out of the "on no base" test. But a base that was merged back into the
  # branch brings its teammates' commits: that one stays in the test. The two are told apart by where the
  # base and the branch meet: on the branch's own first-parent line in the first case, off it in the second.
  line="$(git -C "$HM_ROOT" rev-list --first-parent --max-count="$HM_COUNT_CAP" HEAD 2>/dev/null)"
  for b in $HM_BASES; do
    if git -C "$HM_ROOT" merge-base --is-ancestor "$ref" "$b" 2>/dev/null; then
      mb="$(git -C "$HM_ROOT" merge-base HEAD "$b" 2>/dev/null)"
      printf '%s\n' "$line" | grep -q "^$mb\$" && continue
    fi
    not="$not $b"
  done
  n="$( { git -C "$HM_ROOT" rev-list --no-merges --first-parent --max-count="$HM_COUNT_CAP" "$ref"..HEAD -- . ':(exclude).claude/memory' 2>/dev/null
          [ -n "$not" ] && git -C "$HM_ROOT" rev-list --no-merges --max-count="$HM_COUNT_CAP" "$ref"..HEAD --not $not -- . ':(exclude).claude/memory' 2>/dev/null
        } | sort -u | grep -c . )"
  printf '%s' "${n:-?}"
}

hm_status() {
  HM_ROOT=""; HM_KIND="folder"; HM_REPOS=""; HM_REPO_COUNT=0; HM_SHALLOW="no"
  HM_MEM="absent"; HM_MEM_DIR=""; HM_SAVED=""; HM_BEHIND="?"; HM_STALE="unknown"
  HM_BRANCH=""; HM_DEFAULT_BRANCH=""; HM_BASES=""; HM_TASK_BRANCH="no"; HM_TASK_ID=""; HM_TASK_DIR=""
  HM_BASE_REF=""; HM_BASE_SOURCE=""; HM_BASE_KIND=""; HM_BASE_LOCAL_DIFFERS=""
  HM_TASK_FILE="absent"; HM_TASK_SAVED=""; HM_TASK_BEHIND="?"; HM_TASK_STALE="unknown"
  HM_OWN_WORK="?"; HM_OWN="?"; HM_CREATED=""; HM_OBASES=""; HM_HAS_WORK="no"; HM_UNPUSHED="n/a"; HM_LOCAL_ONLY="n/a"; HM_DIRTY=0; HM_LEFTOVER=""; HM_LEFTOVER_COUNT=0

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
  HM_BASES="$(hm_base_refs)"

  # What kind of branch is this? Decided by its name and by whether its own task file is there, never by
  # comparing refs: a base name is a base; any other branch is a task when the clone has a base branch to
  # tell it apart from, or when it carries its own task file; otherwise it cannot be classified.
  local own_file=""
  if [ -z "$HM_BRANCH" ]; then
    HM_TASK_BRANCH="detached"   # rebase, bisect, a commit checked out: no task, the project memory is still measured
  elif ! hm_is_base_branch "$HM_BRANCH"; then
    HM_TASK_ID="$(hm_task_id "$HM_BRANCH")"
    HM_TASK_DIR="$HM_MEM_DIR/in-progress/$HM_TASK_ID"
    own_file="$HM_TASK_DIR/TASK.md"
    if [ -n "$HM_BASES" ] || [ -f "$own_file" ]; then HM_TASK_BRANCH="yes"; else HM_TASK_BRANCH="unknown"; HM_TASK_ID=""; HM_TASK_DIR=""; fi
  fi

  # Project memory: commits since it was last updated. Seen from a task branch it is judged on the history
  # of the remote's default branch (up to where this branch shares it), so the task's own commits never
  # count, wherever the branch was merged since. Without a known default branch, the commits that are on
  # no base are subtracted instead.
  local r n own_in target=""
  if [ "$HM_TASK_BRANCH" = "yes" ] && [ -n "$HM_DEFAULT_BRANCH" ]; then
    target="$(git -C "$HM_ROOT" merge-base HEAD "origin/$HM_DEFAULT_BRANCH" 2>/dev/null)"
  fi
  if [ "$HM_MEM" = "present" ] && [ "$HM_SHALLOW" != "yes" ]; then
    hm_refs "$HM_MEM_DIR/PROJECT_STATE.md" firstparent
    HM_SAVED="$HM_OUT_SAVED"
    # The default branch's history is the yardstick only when the memory lives on it: the commit that last
    # updated the file must be part of that history. A memory kept on another base (develop) is judged the
    # other way, or it would always read as current.
    if [ -z "$HM_OUT_LAST" ] || ! git -C "$HM_ROOT" merge-base --is-ancestor "$HM_OUT_LAST" "${target:-HEAD}" 2>/dev/null; then target=""; fi
    for r in $HM_OUT_REFS; do
      if [ -n "$target" ]; then
        n="$(hm_work "$r".."$target")"
      else
        n="$(hm_work "$r"..HEAD)"
        if [ "$HM_TASK_BRANCH" = "yes" ] && [ -n "$HM_BASES" ] && hm_is_number "$n" && [ "$n" -lt "$HM_COUNT_CAP" ]; then
          own_in="$(hm_work "$r"..HEAD --not $HM_BASES)"
          hm_is_number "$own_in" && n=$((n - own_in))
        fi
      fi
      HM_BEHIND="$(hm_min "$HM_BEHIND" "$n")"
    done
    if hm_is_number "$HM_BEHIND"; then
      if [ "$HM_BEHIND" -ge "$HM_STALE_COMMITS" ]; then HM_STALE="yes"; else HM_STALE="no"; fi
    fi
  fi

  if [ "$HM_TASK_BRANCH" = "yes" ]; then
    local rel=".claude/memory/in-progress/$HM_TASK_ID/TASK.md" closed="" created="" onremote="no"
    git -C "$HM_ROOT" rev-parse -q --verify "refs/remotes/origin/$HM_BRANCH" >/dev/null 2>&1 && onremote="yes"

    # The branch's own commits, counted two ways and the larger kept, because each way has a blind spot:
    #  - commits that are on no base branch: blind to work that was merged or fast-forwarded into a local base;
    #  - for a branch that is not on the remote, commits made since it was created on this machine (oldest
    #    reflog entry), minus those the remote bases have (a rebase or a merge brings a teammate's commits
    #    into that range): blind when the branch was created after the work, or when the reflog expired.
    local obases="" b own_r="?" work_r="?" own_n="?" work_n="?"
    for b in $HM_BASES; do case "$b" in origin/*) obases="$obases $b" ;; esac; done
    [ "$onremote" = "no" ] && created="$(git -C "$HM_ROOT" reflog show --format=%H "refs/heads/$HM_BRANCH" 2>/dev/null | tail -1)"
    if [ -n "$created" ] && git -C "$HM_ROOT" merge-base --is-ancestor "$created" HEAD 2>/dev/null; then
      own_r="$(git -C "$HM_ROOT" rev-list --count --max-count="$HM_COUNT_CAP" "$created"..HEAD ${obases:+--not $obases} 2>/dev/null || printf '?')"
      work_r="$(hm_work "$created"..HEAD ${obases:+--not $obases})"
    else
      created=""
    fi
    if [ -n "$HM_BASES" ] && [ "$HM_SHALLOW" != "yes" ]; then
      own_n="$(git -C "$HM_ROOT" rev-list --count --max-count="$HM_COUNT_CAP" HEAD --not $HM_BASES 2>/dev/null || printf '?')"
      work_n="$(hm_work HEAD --not $HM_BASES)"
    fi
    HM_OWN="$(hm_max "$own_r" "$own_n")"; HM_OWN_WORK="$(hm_max "$work_r" "$work_n")"
    HM_OBASES="${obases# }"

    if [ -f "$own_file" ]; then
      HM_TASK_FILE="present"
      hm_task_base "$own_file"
      [ -n "$HM_BASE_REF" ] && { HM_BASE_KIND="other"; hm_is_base_branch "${HM_BASE_REF#origin/}" && HM_BASE_KIND="base-branch"; }
      if [ "$HM_SHALLOW" != "yes" ]; then
        hm_refs "$own_file" ""
        HM_TASK_SAVED="$HM_OUT_SAVED"
        for r in $HM_OUT_REFS; do HM_TASK_BEHIND="$(hm_min "$HM_TASK_BEHIND" "$(hm_task_behind "$r")")"; done
      fi
    elif [ "$HM_SHALLOW" != "yes" ]; then
      # Closed and waiting for its merge: a commit deleted the task file and has not reached the remote's
      # default branch yet. Only a committed deletion counts (a file removed from the working tree is just
      # missing). Without a known default branch, the commit must be on no base at all.
      # Known limits: a close that had no task folder to delete leaves no trace; once the branch is merged
      # into the default branch the close is no longer seen (the branch then has no work of its own either).
      if [ -n "$HM_DEFAULT_BRANCH" ]; then
        closed="$(git -C "$HM_ROOT" log -1 --diff-filter=D --format=%H HEAD --not "origin/$HM_DEFAULT_BRANCH" -- "$rel" 2>/dev/null)"
      elif [ -n "$HM_BASES" ]; then
        closed="$(git -C "$HM_ROOT" log -1 --diff-filter=D --format=%H HEAD --not $HM_BASES -- "$rel" 2>/dev/null)"
      fi
      if [ -n "$closed" ]; then HM_TASK_FILE="closed"; HM_TASK_BEHIND="$(hm_task_behind "$closed")"; fi
    fi
    if hm_is_number "$HM_TASK_BEHIND"; then
      if [ "$HM_TASK_BEHIND" -ge "$HM_TASK_STALE_COMMITS" ]; then HM_TASK_STALE="yes"; else HM_TASK_STALE="no"; fi
    fi

    HM_CREATED="$created"
    # Pushed means: on the remote under its own name. An upstream set to a base (git checkout -b x origin/main) says nothing.
    if [ "$onremote" = "yes" ]; then
      HM_UNPUSHED="$(git -C "$HM_ROOT" rev-list --count --max-count="$HM_COUNT_CAP" "origin/$HM_BRANCH"..HEAD 2>/dev/null || printf '0')"
    elif git -C "$HM_ROOT" remote get-url origin >/dev/null 2>&1; then
      HM_UNPUSHED="not-on-remote"
      # Its own commits that are on no remote branch at all: they exist on this machine only. Same two
      # counts as above, the larger kept.
      local lo_r="?" lo_n="?"
      [ -n "$created" ] && lo_r="$(git -C "$HM_ROOT" rev-list --count --max-count="$HM_COUNT_CAP" "$created"..HEAD --not --remotes 2>/dev/null || printf '?')"
      if [ -n "$HM_BASES" ] && [ "$HM_SHALLOW" != "yes" ]; then
        lo_n="$(git -C "$HM_ROOT" rev-list --count --max-count="$HM_COUNT_CAP" HEAD --not $HM_BASES --remotes 2>/dev/null || printf '?')"
      fi
      HM_LOCAL_ONLY="$(hm_max "$lo_r" "$lo_n")"
    fi
    # One answer for the three hooks: yes (a count is known and above 0), some (the count is unknown but
    # something is unpushed or exists on this machine only), no.
    HM_HAS_WORK="no"
    if hm_is_number "$HM_OWN_WORK"; then
      [ "$HM_OWN_WORK" -gt 0 ] && HM_HAS_WORK="yes"
    elif { hm_is_number "$HM_LOCAL_ONLY" && [ "$HM_LOCAL_ONLY" -gt 0 ]; } || { hm_is_number "$HM_UNPUSHED" && [ "$HM_UNPUSHED" -gt 0 ]; }; then
      HM_HAS_WORK="some"
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
