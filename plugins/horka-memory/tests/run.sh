#!/bin/bash
# Tests of the horka-memory hooks, on throwaway git repositories. No network, nothing outside a temp folder.
# Usage: bash plugins/horka-memory/tests/run.sh
# Each test names the behaviour it protects; a test fails if that behaviour changes.

SCRIPTS="$(cd "$(dirname "$0")/../scripts" && pwd)"
WORK="$(mktemp -d)"
export TMPDIR="$WORK/tmp"; mkdir -p "$TMPDIR"
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@example.invalid GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@example.invalid
trap 'rm -rf "$WORK"' EXIT

PASS=0; FAIL=0
ok()   { PASS=$((PASS + 1)); echo "  ok    $1"; }
ko()   { FAIL=$((FAIL + 1)); echo "  FAIL  $1"; [ -n "$2" ] && echo "        got: $2"; }
has()  { case "$2" in *"$3"*) ok "$1" ;; *) ko "$1" "$2" ;; esac; }
hasnt(){ case "$2" in *"$3"*) ko "$1" "$2" ;; *) ok "$1" ;; esac; }
empty(){ [ -z "$2" ] && ok "$1" || ko "$1" "$2"; }

start() { echo '{"session_id":"s1"}' | bash "$SCRIPTS/session-start.sh"; }
stop()  { echo "{\"session_id\":\"${1:-s1}\",\"hook_event_name\":\"Stop\"}" | bash "$SCRIPTS/stop-check.sh"; }
status(){ bash "$SCRIPTS/memory-status.sh"; }
commit(){ echo "$RANDOM$RANDOM" >> "${1:-code.txt}"; git add -A >/dev/null; git commit -qm "${2:-work}"; }
commits(){ local i=0; while [ "$i" -lt "$1" ]; do commit code.txt "work $i"; i=$((i + 1)); done; }
mark()  { printf '# State\n\n<!-- memory-saved: %s %s -->\n' "$(git rev-parse --short HEAD)" "$(date +%Y-%m-%d)" > "$1"; }

new_repo() {   # a repository with a bare remote, main pushed, origin/HEAD set
  local name="$1"
  git init -q --bare -b main "$WORK/$name.git"
  git init -q -b main "$WORK/$name"; cd "$WORK/$name" || exit 1
  git remote add origin "$WORK/$name.git"
  commit code.txt init; git push -q -u origin main; git remote set-head origin main >/dev/null
}

echo "workspace of several repositories"
mkdir -p "$WORK/ws/a" "$WORK/ws/b"; git init -q "$WORK/ws/a"; git init -q "$WORK/ws/b"
mkdir -p "$WORK/ws/b/.claude/memory"; echo x > "$WORK/ws/b/.claude/memory/PROJECT_STATE.md"
cd "$WORK/ws" || exit 1
OUT="$(start)"
has   "says it is not a project and forbids creating memory there" "$OUT" "not itself a project: do not create memory files here"
has   "names the repository that already has memory" "$OUT" "present in: b"
echo "$OUT" | jq -e '.hookSpecificOutput.additionalContext' >/dev/null 2>&1 && ok "output is valid hook JSON" || ko "output is valid hook JSON" "$OUT"
has   "status reports kind workspace" "$(status)" "kind: workspace"
empty "stop hook is silent outside a repository" "$(stop)"
hasnt "no workspace notes: none are mentioned" "$OUT" "index of the repositories"
mkdir -p .claude/memory; echo notes > .claude/memory/PROJECT_STATE.md
has   "workspace notes are presented as an index, not as a project state" "$(start)" "index of the repositories, not as the state of a project"

echo "repository without memory"
new_repo r1
has   "asks to initialize" "$(start)" "No project memory in this repository"
empty "stop hook is silent when the project has no memory" "$(stop)"

echo "fresh memory on the base branch"
mkdir -p .claude/memory; mark .claude/memory/PROJECT_STATE.md
git add -A >/dev/null; git commit -qm "memory"
OUT="$(start)"
has   "announces the memory with its save point" "$OUT" "last saved:"
hasnt "does not call it outdated" "$OUT" "outdated"
has   "a commit that only touches the memory does not count as behind" "$(status)" "behind: 0"
empty "stop hook is silent when memory is current" "$(stop)"

echo "memory that fell behind"
commits 19
has   "19 commits: one below the threshold, not stale" "$(status)" "stale: no"
commits 1
has   "20 commits: stale" "$(status)" "stale: yes"
has   "session start says the code wins" "$(start)" "20 commits behind the code"
has   "stop hook states the gap" "$(stop)" "project memory 20 commits behind"

echo "memory without a save marker (empty template left behind)"
new_repo r2
mkdir -p .claude/memory; echo "# State - not started" > .claude/memory/PROJECT_STATE.md
git add -A >/dev/null; git commit -qm "scaffold"; commits 25
has   "falls back to the last commit that touched the file" "$(status)" "behind: 25"
has   "and reports it stale" "$(start)" "25 commits behind the code"

echo "stop hook: one reminder per session, not per call (the counter used to be keyed by process id)"
OUT1="$(stop s-a)"; OUT2="$(stop s-a)"; OUT3="$(stop s-b)"
has   "first call of a session speaks" "$OUT1" "systemMessage"
empty "second call of the same session is silent" "$OUT2"
has   "another session gets its own reminder" "$OUT3" "systemMessage"
[ -f "$TMPDIR/horka-memory/stop-s-a" ] && ok "state file is named after the session id" || ko "state file is named after the session id" "$(ls "$TMPDIR/horka-memory")"
OUT4="$(HORKA_MEMORY_REMIND_SECONDS=0 stop s-a)"
has   "speaks again once the delay has passed" "$OUT4" "systemMessage"
echo "$OUT1" | jq -e '.systemMessage' >/dev/null 2>&1 && ok "stop output is valid hook JSON" || ko "stop output is valid hook JSON" "$OUT1"

echo "task branch without a task file"
new_repo r3
mkdir -p .claude/memory; mark .claude/memory/PROJECT_STATE.md; git add -A >/dev/null; git commit -qm memory; git push -q
git checkout -q -b feature/login-form
ST="$(status)"
has   "task id comes from the branch name" "$ST" "task_id: feature-login-form"
has   "task file is absent" "$ST" "task_file: absent"
empty "no work yet: stop hook is silent" "$(stop t1)"
commit code.txt "first step"
OUT="$(stop t1)"
has   "work without a task file is stated" "$OUT" "no task file for 1 commits of work"
has   "a branch never pushed is stated" "$OUT" "branch never pushed"
has   "session start says the branch has no task file" "$(start)" "has no task file yet"

echo "task branch with a task file"
mkdir -p .claude/memory/in-progress/feature-login-form; mark .claude/memory/in-progress/feature-login-form/TASK.md
git add -A >/dev/null; git commit -qm "task memory"; git push -q -u origin feature/login-form
empty "current task file and pushed branch: silent" "$(stop t2)"
[ ! -f "$TMPDIR/horka-memory/stop-t2" ] && ok "no state kept when nothing is wrong" || ko "no state kept when nothing is wrong"
has   "session start points to the task file" "$(start)" "in-progress/feature-login-form/TASK.md"
commits 2
OUT="$(stop t3)"
has   "unpushed commits are counted" "$OUT" "2 commits not pushed"
hasnt "2 commits: task file not yet called behind" "$OUT" "task file 2 commits behind"
commits 1
has   "3 commits: task file is behind" "$(stop t4)" "task file 3 commits behind"
has   "the global memory is not this branch's job" "$(status)" "task_stale: yes"
hasnt "stop hook does not blame global memory on a task branch" "$(HORKA_MEMORY_STALE_COMMITS=1 stop t5)" "project memory"

echo "task folder merged by mistake"
git checkout -q main; git merge -q --no-edit feature/login-form
has   "session start reports the leftover" "$(start)" "left in .claude/memory/in-progress/ on main: feature-login-form"
has   "stop hook reports the leftover" "$(stop t6)" "task folders left after merge: feature-login-form"
OUT="$(bash "$SCRIPTS/check-in-progress.sh" . 2>&1)"; CODE=$?
[ "$CODE" = "1" ] && ok "CI check fails with a task folder present" || ko "CI check fails with a task folder present" "$CODE $OUT"
git rm -rq .claude/memory/in-progress; git commit -qm "close task"
bash "$SCRIPTS/check-in-progress.sh" . >/dev/null 2>&1 && ok "CI check passes once the folder is gone" || ko "CI check passes once the folder is gone"

echo "helpers"
. "$SCRIPTS/lib.sh"
[ "$(hm_task_id 'fix/a b/c')" = "fix-a-b-c" ] && ok "task id replaces slashes and spaces" || ko "task id replaces slashes and spaces" "$(hm_task_id 'fix/a b/c')"
ESC="$(printf 'a"b\\c\nd' | hm_json_escape)"
printf '{"x":"%s"}' "$ESC" | jq -e '.x == "a\"b\\c\nd"' >/dev/null 2>&1 && ok "JSON escaping round-trips quotes, backslashes and newlines" || ko "JSON escaping round-trips quotes, backslashes and newlines" "$ESC"
[ "$(echo '{"session_id":"../../etc"}' | hm_session_id)" = "etc" ] && ok "session id cannot escape the state folder" || ko "session id cannot escape the state folder"

echo
echo "$PASS passed, $FAIL failed"
[ "$FAIL" = "0" ]
