#!/usr/bin/env python3
"""Harness scan: facts about what holds an AI-assisted workflow. It edits nothing.

For the global Claude Code config and for each repository given, prints what exists
(map, state, checks, reviewers, caps) and what enforces it (permission rules, hooks,
CI dependencies, branch protection). Each line is tagged with a criterion of the grid
(references/grid.md) and carries its source.

What it does and does not do:
- It never pushes, merges, fetches, edits or deletes, and it writes one file: --json FILE.
- The only file content it quotes is rule lines (sentences of the map, permission rules,
  auto mode entries), truncated and passed through a best-effort mask for credential
  shapes. Hook command lines are never quoted: a hook is named by its script.
- The risky commands of the probe are never run. The PreToolUse hooks of the user's own
  config ARE run, once per probe command, with that command as input, from an empty
  temporary folder: a hook that logs or notifies will do so for each of them.
  --no-hook-probe skips this.
- Hooks defined by a scanned repository are listed and NOT run, because their command
  line comes from that repository, and no hook is run from inside a scanned repository.
  --probe-repo-hooks lifts both, for a repository the user trusts.

Usage:
  scan.py [--repo PATH ...] [--home DIR] [--no-network] [--no-hook-probe]
          [--probe-repo-hooks] [--usage-days N] [--json FILE]
"""
import argparse
import atexit
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path

HOME = Path.home()
FACTS = []          # every fact, for --json
NOT_MEASURED = []   # what the scan could not see, for the "limits" section


# ---------------------------------------------------------------- helpers

def run(cmd, cwd=None, timeout=30, stdin=None, env=None, shell=False):
    try:
        p = subprocess.run(cmd, cwd=cwd, input=stdin, capture_output=True, text=True,
                           timeout=timeout, env=env, shell=shell, errors="replace")
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"
    except (OSError, ValueError) as e:
        return 127, "", str(e)


def short(path):
    s, h = str(path), str(HOME)
    return "~" + s[len(h):] if s.startswith(h) else s


# Shapes of well-known credentials. In tracked files, hits are reported as file:line only.
# POSIX-safe on purpose: the same pattern goes to `git grep -E` and to Python.
SECRET_RX = (r"hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|"
             r"gh[pousr]_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{30,}|glpat-[A-Za-z0-9_-]{20,}|"
             r"xox[baprs]-[A-Za-z0-9-]{20,}|sk-ant-[A-Za-z0-9_-]{20,}|sk_live_[A-Za-z0-9]{20,}|"
             r"AIza[0-9A-Za-z_-]{35}|BEGIN [A-Z ]*PRIVATE KEY")
# Masking of the text the scan quotes from the user's files (rule lines, permission rules, auto mode entries,
# error messages). Best effort: it knows shapes, not secrets. This is why hook command lines are never
# quoted at all (see hook_label) and why tracked-file hits are reported as file:line only.
_VALUE = r"(\"[^\"]*\"|'[^']*'|[^\s,;)]+)"
_MASKS = [
    (re.compile(SECRET_RX), "***"),
    (re.compile(r"\b(gh[pousr]_|github_pat_|glpat-|xox[baprs]-|sk-|sk_|pk_|rk_|npm_|hf_|dop_v1_|shpat_|AKIA|AIza)"
                r"[A-Za-z0-9_-]{12,}"), "***"),
    (re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}(\.[A-Za-z0-9_-]+)?"), "***"),
    # a URL keeps its host only when it carries credentials, a query string or a long opaque path segment
    (re.compile(r"([A-Za-z][A-Za-z0-9+.-]*://)[^/\s:@]+:[^/\s@]+@"), r"\1***:***@"),        # any scheme
    (re.compile(r"(https?://[^/\s?#]+)(/[^\s?#]*)?\?\S+"), r"\1/***"),
    (re.compile(r"(?i)(https?://[^/\s?#]+)/\S*(webhook|hooks?/|bot\d|token|secret|[A-Za-z0-9_-]{20,})\S*"), r"\1/***"),
    (re.compile(r"(?i)\b(authorization)(\s*[:=]\s*)(?:(?:bearer|basic|token)\s+)?" + _VALUE), r"\1\2***"),
    (re.compile(r"(?i)\b(bearer|basic)(\s+)[A-Za-z0-9+/=_.-]{8,}"), r"\1\2***"),
    (re.compile(r"\b([A-Z][A-Z0-9_]{1,})(=)" + _VALUE), r"\1\2***"),                       # every NAME=value
    (re.compile(r"(?i)\b([\w-]*(?:token|secret|passw(?:or)?d|passphrase|pwd|key|pat|auth|credentials?)[\w-]*)"
                r"(\s*[=:]\s*)" + _VALUE), r"\1\2***"),
    (re.compile(r"(?i)\b(token|secret|passw(?:or)?d|passphrase|api[ _-]?key)\b([^\n:=]{0,25}?(?:\s+is\s+|\s*[:=]\s*))"
                r"(\"[^\"]{4,}\"|'[^']{4,}'|[^\s,;)*]{6,})"), r"\1\2***"),
    (re.compile(r"(?i)((?:^|\s)(?:-u|--user|-p|--password|--token|--api-key|--secret|--header|-H)[= ]\s*)" + _VALUE),
     r"\1***"),
    (re.compile(r"((?:^|\s)-p)[^\s-]\S{5,}"), r"\1***"),                                    # mysql -pVALUE
]


def scrub(s):
    for rx, repl in _MASKS:
        s = rx.sub(repl, s)
    return s


def mask(s, n=130):
    """For every string quoted from a file the scan did not write: masked, on one line, truncated."""
    s = " ".join(scrub(str(s)).split())
    return s if len(s) <= n else s[: n - 1] + "…"


def fact(scope, crit, text, source="", data=None):
    FACTS.append({"scope": scope, "criterion": crit, "fact": text, "source": source, "data": data})
    print(f"[{crit}] {text}" + (f"  ({source})" if source else ""))


def missing(scope, text):
    NOT_MEASURED.append(f"{scope}: {text}")


def load_json(path):
    try:
        return json.loads(Path(path).read_text(errors="replace"))
    except (OSError, ValueError):
        return None


def load_settings(path):
    """A settings file as a dict, or None when absent, unreadable or not a JSON object."""
    s = load_json(path)
    return s if isinstance(s, dict) else None


def rule_list(settings, kind):
    perms = (settings or {}).get("permissions")
    v = perms.get(kind) if isinstance(perms, dict) else None
    return v if isinstance(v, list) else []


# ---------------------------------------------------------------- permission rules

BROAD = {"git", "git push", "git merge", "git reset", "gh", "gh pr merge", "gh api", "rm", "sudo",
         "curl", "wget", "ssh", "scp", "docker", "kubectl", "npm publish", "terraform", "*", ""}

PROBES = [
    ("plain push", "git push"),
    ("push to the default branch", "git push origin {b}"),
    ("force push", "git push --force origin {b}"),
    ("force push with -f", "git push -f origin {b}"),
    ("force push with the flag at the end", "git push origin {b} --force"),
    ("force push with a +refspec", "git push origin +{b}"),
    ("force push through git -C", "git -C /tmp/x push --force origin {b}"),
    ("force push chained after another command", "echo ok && git push --force origin {b}"),
    ("hard reset", "git reset --hard HEAD~1"),
    ("hard reset through git -C", "git -C /tmp/x reset --hard HEAD~1"),
    ("merge a pull request", "gh pr merge 1 --merge"),
    ("recursive delete", "rm -rf ./build"),
    ("read an env file", "cat .env"),
]


def bash_rules(settings):
    return {k: [r for r in rule_list(settings, k) if isinstance(r, str)] for k in ("allow", "ask", "deny")}


def rule_prefix(rule):
    """'Bash(git push:*)' -> 'git push:*' ; 'Bash' -> '' ; not a Bash rule -> None."""
    if rule == "Bash":
        return ""
    m = re.match(r"^Bash\((.*)\)$", rule)
    return m.group(1) if m else None


def is_broad(rule):
    body = rule_prefix(rule)
    if body is None:
        return False
    for suffix in (":*", " *"):
        if body.endswith(suffix):
            body = body[: -len(suffix)]
    return body in BROAD


def rule_matches(rule, part):
    body = rule_prefix(rule)
    if body is None:
        return False
    if body in ("", "*"):
        return True
    for suffix in (":*", " *"):     # both forms also match the bare command, without arguments
        if body.endswith(suffix):
            pre = body[: -len(suffix)]
            if "*" in pre:
                return fnmatch.fnmatchcase(part, pre) or fnmatch.fnmatchcase(part, pre + " *")
            return part == pre or part.startswith(pre + " ")
    if "*" in body:
        return fnmatch.fnmatchcase(part, body)
    return part == body


def rules_verdict(rules, command):
    """Approximation of the matcher: each chained part is judged; deny > ask > no rule > allow."""
    parts = [p.strip() for p in re.split(r"&&|\|\||;|\|", command) if p.strip()]
    verdicts = []
    for part in parts:
        v = ("none", "")
        for kind in ("deny", "ask", "allow"):
            hit = next((r for r in rules[kind] if rule_matches(r, part)), None)
            if hit:
                v = (kind, hit)
                break
        verdicts.append(v)
    for kind in ("deny", "ask", "none"):
        for v in verdicts:
            if v[0] == kind:
                return v
    return verdicts[-1] if verdicts else ("none", "")


def merge_rules(*rule_sets):
    out = {"allow": [], "ask": [], "deny": []}
    for rs in rule_sets:
        for k in out:
            out[k] += rs[k]
    return out


# ---------------------------------------------------------------- hooks

def settings_hooks(settings, source, root=None, from_repo=False):
    """Command hooks of a settings object. `from_repo` marks a command line written by a scanned repository."""
    out = []
    table = (settings or {}).get("hooks") if isinstance(settings, dict) else None
    for event, groups in (table.items() if isinstance(table, dict) else []):
        for g in (groups if isinstance(groups, list) else []):
            if not isinstance(g, dict):
                continue
            for h in (g.get("hooks") if isinstance(g.get("hooks"), list) else []):
                if not isinstance(h, dict) or not isinstance(h.get("command"), str) or not h["command"].strip():
                    continue
                if h.get("type", "command") != "command":
                    continue
                matcher = g.get("matcher") if isinstance(g.get("matcher"), str) else ""
                out.append({"event": str(event), "matcher": matcher, "command": h["command"], "n": len(out) + 1,
                            "if": h.get("if") if isinstance(h.get("if"), str) else None,
                            "source": source, "root": root, "from_repo": from_repo})
    return out


def plugin_parts(home, enabled):
    """Hooks, skills and agents brought by the enabled plugins."""
    hooks, skills, agents = [], [], []
    reg = load_json(home / "plugins" / "installed_plugins.json")
    installed = reg.get("plugins") if isinstance(reg, dict) else None
    installed = installed if isinstance(installed, dict) else {}
    for key, on in (enabled.items() if isinstance(enabled, dict) else []):
        if not on:
            continue
        entries = installed.get(key)
        entries = [entries] if isinstance(entries, dict) else entries if isinstance(entries, list) else []
        last = entries[-1] if entries and isinstance(entries[-1], dict) else {}
        path = Path(last["installPath"]) if isinstance(last.get("installPath"), str) else None
        if not path or not path.is_dir():
            continue
        name = str(key).split("@")[0]
        hj = load_json(path / "hooks" / "hooks.json")
        if isinstance(hj, dict):
            hooks += settings_hooks(hj, f"plugin {name}", root=str(path))
        skills += [(p.parent.name, name) for p in path.glob("skills/*/SKILL.md")]
        agents += [(p.stem, name) for p in path.glob("agents/*.md")]
    return hooks, skills, agents


def bash_pretool(hooks):
    res = []
    for h in hooks:
        if h["event"] != "PreToolUse":
            continue
        m = h["matcher"] or "*"
        try:
            ok = m in ("*", "") or re.fullmatch(m, "Bash") is not None
        except re.error:
            ok = m == "Bash"
        if ok:
            res.append(h)
    return res


HOOK_TIMEOUT = 8        # seconds; Claude Code waits much longer, the scan does not
_NOT_AGAIN = set()      # hook commands that timed out once: not run again


def hook_applies(hook, command):
    """The optional `if` filter of a hook, written as a permission rule: True, False, or None when not understood."""
    cond = hook.get("if")
    if not cond:
        return True
    if not re.match(r"^[A-Za-z_]+(\(.*\))?$", cond.strip()):
        return None
    cond = cond.strip()
    if rule_prefix(cond) is None:
        return False                # a filter on another tool: the hook never runs for a Bash command
    parts = [p.strip() for p in re.split(r"&&|\|\||;|\|", command) if p.strip()]
    return any(rule_matches(cond, p) for p in [command] + parts)


_SEEN = {}              # (hook command, probe command, folder) -> verdict: a hook runs once per probe command
_PROBE_DIR = []         # the empty temporary folder the hooks are run from


def probe_dir():
    if not _PROBE_DIR:
        _PROBE_DIR.append(tempfile.mkdtemp(prefix="harness-scan-"))
        atexit.register(shutil.rmtree, _PROBE_DIR[0], ignore_errors=True)
    return _PROBE_DIR[0]


def probe_hook(hook, command, cwd=None):
    """Run one hook of the user's config with a fabricated command as input. The command itself is never run.

    Without `cwd`, the hook runs from an empty temporary folder, and CLAUDE_PROJECT_DIR points there: neither the
    working directory nor the project variable leads into a scanned repository, so a hook that loads a file
    "from the project" cannot load one written by that repository. `cwd` is given only with --probe-repo-hooks.
    """
    key = (hook["command"], command, str(cwd))
    if key in _SEEN:
        return _SEEN[key]
    if hook["command"] in _NOT_AGAIN:
        return "not run again after its timeout"
    where = str(cwd) if cwd else probe_dir()
    payload = json.dumps({"session_id": "harness-scan", "hook_event_name": "PreToolUse", "tool_name": "Bash",
                          "tool_input": {"command": command}, "cwd": where, "permission_mode": "default"})
    env = dict(os.environ)
    env["CLAUDE_PROJECT_DIR"] = where
    if hook.get("root"):
        env["CLAUDE_PLUGIN_ROOT"] = hook["root"]
    rc, out, _ = run(hook["command"], cwd=where, timeout=HOOK_TIMEOUT, stdin=payload, env=env, shell=True)
    if rc == 124:
        _NOT_AGAIN.add(hook["command"])
        return f"no answer in {HOOK_TIMEOUT} s"
    try:
        j = json.loads(out) if out.startswith("{") else {}
    except ValueError:
        j = {}
    j = j if isinstance(j, dict) else {}
    spec = j.get("hookSpecificOutput")
    d = spec.get("permissionDecision") if isinstance(spec, dict) else None
    if rc == 2 or j.get("decision") == "block":
        d = "deny"
    elif d not in ("deny", "ask"):
        d = "pass" if rc == 0 else f"error (exit {rc}, which does not block)"
    _SEEN[key] = d
    return d


def hook_name(h):
    """The script a hook calls, never its command line: a command line can carry a credential."""
    scripts = re.findall(r"([\w.-]+\.(?:sh|bash|zsh|py|js|mjs|cjs|ts|rb|pl|php))(?![\w.-])", h["command"])
    return scripts[-1] if scripts else f"inline hook #{h.get('n', '?')}"


def hook_label(h):
    return f"{hook_name(h)} [{h['source']}]"


def probe_stack(scope, rules, hooks, branch, cwd, do_probe, mode, baseline=None, repo_hooks_ok=False):
    """Probe the stack. With a baseline (the GLOBAL result), print only the lines that differ.

    `cwd` is None except for a repository probed with --probe-repo-hooks (see probe_hook).
    """
    pre = bash_pretool(hooks)
    held = [h for h in pre if h.get("from_repo") and not repo_hooks_ok]     # never run without the opt-in
    if not do_probe:
        how = "not run (--no-hook-probe)"
    else:
        how = (f"{len(pre) - len(held)} run once per command, with the command as input, from "
               + ("this repository (--probe-repo-hooks)" if cwd else "an empty temporary folder"))
        if held:
            how += (f"; {len(held)} defined by the repository and NOT run, because their command line comes from "
                    "the repository (--probe-repo-hooks to run them)")
    print(f"  probe of {len(PROBES)} risky commands: the commands themselves are never run. Rules: approximation "
          f"of the matcher. Hooks: {len(pre)} PreToolUse hook(s) on Bash, {how}")
    for h in held:
        print(f"      not run: {hook_label(h)}")
    holes, result, same, blind = [], {}, 0, 0
    no_rule = "(no rule: the permission mode decides" + ("" if mode == "not set" else f", here `{mode}`") + ")"
    for label, tpl in PROBES:
        cmd = tpl.format(b=branch)
        kind, rule = rules_verdict(rules, cmd)
        rule = mask(rule, 80) if rule else rule
        rv = kind + (f" by {rule}" if rule else f" {no_rule}")
        hv, blockers, named, notes, ran, unknown = "not probed", [], [], [], 0, len(held)
        if do_probe:
            for h in pre:
                if h in held:
                    continue
                applies = hook_applies(h, cmd)
                if applies is False:
                    continue
                if applies is None:
                    unknown += 1
                    notes.append(f"`if` filter not understood, hook not run: {hook_label(h)}")
                    continue
                d = probe_hook(h, cmd, cwd)
                ran += 1
                if d in ("deny", "ask"):
                    blockers.append(f"{d} by {hook_label(h)}")
                    named.append({"decision": d, "name": hook_name(h), "source": h["source"]})
                elif d != "pass":
                    unknown += 1        # no answer, or an error: this hook did not judge the command
                    notes.append(f"{d}: {hook_label(h)}")
            if blockers:
                hv = "; ".join(blockers)
            elif not pre:
                hv = "no hook"
            elif not ran and not notes and not held:
                hv = "no hook runs for this command"
            else:
                hv = "passes every hook" if not notes and not held else "no hook that ran stops it"
            if held:
                hv += f"; {len(held)} repository hook(s) not run"
            if notes:
                hv += "; " + "; ".join(notes)
        stopped = kind in ("deny", "ask") or bool(blockers)
        if not stopped:
            holes.append(label)
            blind += bool(unknown)
        result[label] = (rv, hv)
        if baseline is not None and baseline.get(label) == (rv, hv):
            same += 1
            continue
        fact(scope, "C7", f"probe · {label}: `{cmd}` → rules: {rv} · hooks: {hv}",
             "scan probe", {"command": cmd, "rules": kind, "rule": rule, "hooks": named, "stopped": stopped,
                            "hooks_unknown": unknown if do_probe else len(pre)})
    if same:
        print(f"  {same} of {len(PROBES)} probes answer exactly as in GLOBAL (not repeated)")
    if holes:
        fact(scope, "C7", f"{len(holes)} of {len(PROBES)} risky commands met no ask rule, no deny rule and no "
             "blocking hook" + (" among the hooks that ran" if blind or not do_probe else "") + ": " + "; ".join(holes)
             + (f". For {blind} of them at least one hook could not be judged (not run, no answer, or filter not "
                "understood): read that hook before writing that nothing stops them" if blind else ""), "scan probe")
    else:
        fact(scope, "C7", f"all {len(PROBES)} risky commands are stopped by a rule or a hook", "scan probe")
    return result


# ---------------------------------------------------------------- prose rules, agents, skills

RULE_WORDS = re.compile(r"(?i)\b(never|always|must not|must|do not|don't|forbidden|jamais|toujours|interdit|"
                        r"ne pas|obligatoire)\b")


def prose_rules(scope, name, text, source, limit=25):
    lines = text.splitlines()
    hits = [(i + 1, l.strip()) for i, l in enumerate(lines) if RULE_WORDS.search(l) and len(l.strip()) > 12]
    fact(scope, "C2", f"map: {name} has {len(lines)} lines, {len(text.encode())} bytes", source)
    if hits:
        fact(scope, "C7", f"{len(hits)} rule line(s) written as sentences (never / always / must) in {name}: "
             "each one needs an enforcer, or it is a wish", source)
        for n, l in hits[:limit]:
            print(f"      L{n}: {mask(l.lstrip('-* '), 120)}")
        if len(hits) > limit:
            print(f"      … {len(hits) - limit} more")


def frontmatter_bytes(path):
    try:
        text = path.read_text(errors="replace")
    except OSError:
        return 0
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    return len(m.group(1).encode()) if m else 0


def transcript_usage(home, days, cap_mb, known):
    root = home / "projects"
    cutoff = time.time() - days * 86400
    files = []
    for p in root.rglob("*.jsonl") if root.is_dir() else []:
        try:
            st = p.stat()
        except OSError:
            continue
        if st.st_mtime >= cutoff:
            files.append((st.st_mtime, st.st_size, p))
    files.sort(reverse=True)
    ra = re.compile(rb'"subagent_type"\s*:\s*"([^"\\]+)"')
    rs = re.compile(rb'"name"\s*:\s*"Skill".{0,200}?"skill"\s*:\s*"([^"\\]+)"', re.S)
    rc = re.compile(rb"<command-name>/?([\w:.-]+)</command-name>")
    agents, skills, read, skipped, done = Counter(), Counter(), 0, 0, 0
    for _, size, p in files:
        if read + size > cap_mb * 1024 * 1024:
            skipped += 1
            continue
        try:
            data = p.read_bytes()
        except OSError:
            continue
        read += size
        done += 1
        agents.update(m.decode(errors="replace") for m in ra.findall(data))
        skills.update(m.decode(errors="replace") for m in rs.findall(data))
        typed = (m.decode(errors="replace") for m in rc.findall(data))
        skills.update(t for t in typed if t in known or t.split(":")[-1] in known)
    return agents, skills, done, read, skipped


# ---------------------------------------------------------------- workflows (line parser, no YAML dependency)

KEY = re.compile(r'^(\s*)(?:"([^"]+)"|\'([^\']+)\'|([A-Za-z0-9_.\-]+))\s*:(?:\s+(.*))?$')
TESTY = re.compile(r"(?i)(tests?\b|lint|typecheck|e2e|tnr|gate|verify|judge|\bqa\b|\bunit\b)")
TEST_CMD = re.compile(r"(?i)\b(pytest|jest|vitest|playwright|swift test|go test|cargo test|(npm|pnpm|yarn|bun)"
                      r"( run)? (test|lint|typecheck|check)|phpunit|rspec|eslint|ruff|swiftlint|tsc\b|make (test|check))")
DEPLOYY = re.compile(r"(?i)(deploy|release|publish|promote|\bship\b)")
PROD_ENV = re.compile(r"(?i)(prod|live|stag|preprod|recette|\brec\b)")
# POSIX-safe on purpose: the same pattern goes to `git grep -E` and to Python.
AGENT_CALL_RX = r"(^|[^A-Za-z0-9_./-])(claude|codex|gemini) (.* )?(-p|--print|exec)( |$)"
AGENT_TIMED_RX = r"timeout +(-[a-zA-Z-]+ +)*[0-9]+[smh]? .*(claude|codex|gemini) "
AGENT_CAPPED_RX = r"(^|[^A-Za-z0-9_./-])(claude|codex|gemini) .*(--max-turns|--max-budget-usd)"


def ind(line):
    return len(line) - len(line.lstrip(" "))


def children(lines):
    ls = [l for l in lines if l.strip() and not l.lstrip().startswith("#")]
    if not ls:
        return []
    base = min(ind(l) for l in ls)
    out, cur = [], None
    for l in ls:
        if ind(l) == base:
            m = KEY.match(l)
            if m:
                val = (m.group(5) or "").strip()
                if '"' not in val and "'" not in val:
                    val = re.sub(r"\s+#.*$", "", val)
                cur = [m.group(2) or m.group(3) or m.group(4), val, []]
                out.append(cur)
                continue
        if cur is not None:
            cur[2].append(l)
    return out


def as_list(inline, body):
    if inline:
        v = inline.strip()
        if v.startswith("["):
            return [x.strip().strip("\"'") for x in v.strip("[]").split(",") if x.strip()]
        return [v.strip("\"'")]
    return [l.strip()[2:].strip().strip("\"'") for l in body if l.strip().startswith("- ")]


def parse_workflow(text):
    wf = {"name": None, "events": {}, "jobs": {}}
    for k, inline, body in children(text.splitlines()):
        if k == "name":
            wf["name"] = inline.strip("\"'")
        elif k in ("on", "true"):
            if inline:
                for e in as_list(inline, []):
                    wf["events"][e] = {}
                continue
            ch = children(body)
            if not ch:
                for e in as_list("", body):
                    wf["events"][e] = {}
            for ek, _, eb in ch:
                info = {}
                for sk, sin, sb in children(eb):
                    if sk in ("branches", "branches-ignore", "paths", "paths-ignore", "types", "workflows"):
                        info[sk] = as_list(sin, sb)
                if ek == "schedule":
                    info["cron"] = [c.strip() for c in re.findall(r"cron:\s*['\"]?([^'\"\n#]+)", "\n".join(eb))]
                wf["events"][ek] = info
        elif k == "jobs":
            for jk, _, jb in children(body):
                job = {"needs": [], "environment": None, "timeout": None, "continue_on_error": False,
                       "name": None, "uses": None, "body": "\n".join(jb)}
                for fk, fin, fb in children(jb):
                    if fk == "needs":
                        job["needs"] = as_list(fin, fb)
                    elif fk == "environment":
                        job["environment"] = fin.strip("\"'") if fin else next(
                            (nin.strip("\"'") for nk, nin, _ in children(fb) if nk == "name"), "set")
                    elif fk == "timeout-minutes":
                        job["timeout"] = fin
                    elif fk == "continue-on-error":
                        job["continue_on_error"] = fin.lower() == "true"
                    elif fk == "name":
                        job["name"] = fin.strip("\"'")
                    elif fk == "uses":
                        job["uses"] = fin
                wf["jobs"][jk] = job
    return wf


def event_text(name, info):
    bits = []
    for k in ("branches", "paths", "paths-ignore", "workflows", "cron"):
        if info.get(k):
            bits.append(f"{k}: {', '.join(info[k][:4])}" + ("…" if len(info[k]) > 4 else ""))
    return name + (f" ({'; '.join(bits)})" if bits else "")


def is_test(jid, job):
    return bool(TESTY.search(jid + " " + (job["name"] or "")) or TEST_CMD.search(job["body"]))


def is_deploy(jid, job):
    if DEPLOYY.search(jid + " " + (job["name"] or "")):
        return True
    env = job["environment"] or ""
    return bool(env and "${{" not in env and PROD_ENV.search(env) and not TESTY.search(jid))


def upstream(jobs, jid, seen=None):
    seen = seen if seen is not None else set()
    for n in jobs.get(jid, {}).get("needs", []):
        if n not in seen:
            seen.add(n)
            upstream(jobs, n, seen)
    return seen


def scan_workflows(scope, tree):
    files = [f for f in tree.files if re.match(r"\.github/workflows/[^/]+\.ya?ml$", f)]
    deploy_branches = set()
    if not files:
        other = [n for n in (".gitlab-ci.yml", ".circleci/config.yml", "bitbucket-pipelines.yml", "Jenkinsfile",
                             "bitrise.yml", "azure-pipelines.yml", ".buildkite/pipeline.yml", "codemagic.yaml",
                             ".travis.yml", "fastlane/Fastfile") if n in tree.fileset]
        if other:
            fact(scope, "C5", f"CI config found but NOT PARSED by this scan: {', '.join(other)}. Read it by hand: "
                 "which pipelines run tests, on which branches, and whether the delivery waits for them", tree.where)
            missing(scope, f"CI not parsed ({', '.join(other)}): tests, deploy dependencies and unattended agent "
                    "calls in it were read by hand or not at all")
        else:
            fact(scope, "C5", "no CI workflow in the repository", f".github/workflows absent at {tree.where}")
        return deploy_branches
    pr_tests, pr_filtered, other_tests = [], [], []
    for rel in files:
        text = tree.read(rel) or ""
        wf = parse_workflow(text)
        name = rel.split("/")[-1]
        evs = [event_text(e, i) for e, i in wf["events"].items()] or ["triggers not parsed"]
        jobs = wf["jobs"]
        tests = [j for j in jobs if is_test(j, jobs[j])]
        fact(scope, "C5", f"workflow {name} · triggers: {' | '.join(evs)} · jobs: {', '.join(jobs) or 'not parsed'}"
             + (f" · test-like: {', '.join(tests)}" if tests else " · no test-like job"), rel)
        if tests:
            pr = next((wf["events"][e] for e in ("pull_request", "pull_request_target") if e in wf["events"]), None)
            if pr is None:
                other_tests.append(f"{name} on {', '.join(wf['events']) or '?'}")
            elif pr.get("paths"):
                pr_filtered.append(f"{name} (paths: {', '.join(pr['paths'][:3])})")
            else:
                pr_tests.append(name)
        soft = [j for j in jobs if jobs[j]["continue_on_error"]]
        if soft:
            fact(scope, "C5", f"{name}: job(s) with continue-on-error, a red result does not fail the run: "
                 + ", ".join(soft), rel)
        pr_only = "push" not in wf["events"] and any(e.startswith("pull_request") for e in wf["events"])
        for jid, job in jobs.items():
            if pr_only or not is_deploy(jid, job):
                continue
            gate = [u for u in upstream(jobs, jid) if u in jobs and is_test(u, jobs[u])]
            own = bool(TEST_CMD.search(job["body"]))
            for e in ("push", "workflow_run"):
                deploy_branches.update(wf["events"].get(e, {}).get("branches") or [])
            how = (f"waits for test-like job(s) {', '.join(gate)}" if gate else
                   "runs test commands in its own steps" if own else
                   "NO test-like job upstream in this workflow")
            fact(scope, "C7", f"deploy job `{jid}` in {name}"
                 + (f" (environment {job['environment']})" if job["environment"] else "")
                 + f" · triggers: {', '.join(wf['events']) or '?'} · needs: {', '.join(job['needs']) or 'nothing'} · {how}"
                 + (f" · calls {job['uses']} (not followed)" if job["uses"] else ""), rel,
                 {"job": jid, "needs": job["needs"], "gated_by_tests": bool(gate or own)})
        no_timeout = [j for j in jobs if not jobs[j]["timeout"] and not jobs[j]["uses"]]
        if jobs and no_timeout:
            fact(scope, "C8", f"{name}: {len(no_timeout)} of {len(jobs)} jobs without timeout-minutes", rel)
    if pr_tests:
        fact(scope, "C5", f"test-like jobs run on every pull request: {', '.join(pr_tests)}", "workflow triggers")
    if pr_filtered:
        fact(scope, "C5", "test-like jobs run on pull requests ONLY when these paths change: "
             + "; ".join(pr_filtered), "workflow triggers")
    if other_tests:
        fact(scope, "C5", "test-like jobs that never see a pull request: " + "; ".join(other_tests), "workflow triggers")
    if not pr_tests and not pr_filtered:
        fact(scope, "C5", "no workflow runs a test-like job on pull_request", "workflow triggers")
    return deploy_branches


# ---------------------------------------------------------------- repository

def git(repo, *args, timeout=30):
    # --no-optional-locks: a read such as `git status` must not rewrite the index of the repository.
    # core.fsmonitor=false: that setting of a scanned folder's own .git/config names a command git would run.
    return run(["git", "--no-optional-locks", "-c", "core.fsmonitor=false", "-C", str(repo), *args], timeout=timeout)


class Tree:
    """Tracked files of a repository at one ref, or plain files when there is no git."""

    def __init__(self, repo, ref):
        self.repo, self.ref = repo, ref
        if ref:
            self.where = ref
            rc, out, _ = git(repo, "ls-tree", "-r", "--name-only", ref, timeout=60)
            self.files = out.splitlines() if rc == 0 else []
        else:
            self.where = "working files"
            self.files = []
            for base, dirs, names in os.walk(repo):
                dirs[:] = [d for d in dirs if d not in (".git", "node_modules", ".build", "dist", "vendor", ".venv")]
                for n in names:
                    self.files.append(os.path.relpath(os.path.join(base, n), repo))
                if len(self.files) > 20000:
                    break
        self.fileset = set(self.files)

    def read(self, rel):
        if self.ref:
            rc, out, _ = git(self.repo, "show", f"{self.ref}:{rel}")
            return out if rc == 0 else None
        try:
            return (self.repo / rel).read_text(errors="replace")
        except OSError:
            return None

    def age(self, rel):
        if not self.ref:
            return None, None
        rc, out, _ = git(self.repo, "log", "-1", "--format=%H %cs", self.ref, "--", rel)
        if rc or not out:
            return None, None
        sha, date = out.split()
        rc, n, _ = git(self.repo, "rev-list", "--count", f"{sha}..{self.ref}")
        return date, (int(n) if rc == 0 and n.isdigit() else None)

    def grep(self, pattern, names_only=False):
        """file:line hits (or file names) for an extended regex, lock files excluded."""
        if self.ref:
            rc, out, _ = git(self.repo, "grep", "-lIE" if names_only else "-nIE", "-e", pattern, self.ref,
                             "--", ".", ":!*.lock", ":!*lock.json", timeout=60)
            hits = [l[len(self.ref) + 1:] for l in out.splitlines()] if rc == 0 else []
            return hits if names_only else [":".join(h.split(":")[:2]) for h in hits]
        rx, hits = re.compile(pattern), []
        for rel in self.files:
            if rel.endswith((".lock", "lock.json")):
                continue
            try:
                p = self.repo / rel
                if p.stat().st_size > 1_000_000:
                    continue
                for i, line in enumerate(p.read_text(errors="replace").splitlines(), 1):
                    if rx.search(line):
                        hits.append(rel if names_only else f"{rel}:{i}")
                        if names_only:
                            break
            except OSError:
                continue
        return hits


def gh_json(args, timeout=40):
    rc, out, err = run(["gh", *args], timeout=timeout)
    if rc:
        return None, (err or out)
    try:
        return json.loads(out), ""
    except ValueError:
        return None, "unreadable answer"


RED = {"FAILURE", "TIMED_OUT", "ERROR", "STARTUP_FAILURE", "ACTION_REQUIRED"}


def scan_github(scope, slug, info, branches):
    default = info.get("default_branch", "main")
    fact(scope, "C7", f"GitHub {slug}: {'private' if info.get('private') else 'PUBLIC'}, default branch {default}",
         "gh api repos")
    for b in [default] + [x for x in sorted(branches) if x != default and "*" not in x][:2]:
        prot, err = gh_json(["api", f"repos/{slug}/branches/{b}/protection"])
        # rulesets protect a branch without a classic protection rule: ask which rules apply to it
        eff, _ = gh_json(["api", f"repos/{slug}/rules/branches/{b}"])
        kinds = sorted({str(r.get("type")) for r in eff if isinstance(r, dict)}) if isinstance(eff, list) else None
        if kinds:
            fact(scope, "C7", f"branch {b}: rules applied by rulesets: {', '.join(kinds[:8])}",
                 "gh api rules/branches")
        if prot is not None and not isinstance(prot, dict):
            missing(scope, f"protection of {b}: unexpected answer from GitHub")
        elif prot is None and "not protected" in err.lower() and kinds:
            fact(scope, "C7", f"branch {b} has no classic protection rule; the ruleset rules above are what "
                 "protects it", "gh api branches/protection → 404")
        elif prot is None and "not protected" in err.lower() and kinds is None:
            fact(scope, "C7", f"branch {b} has no classic protection rule, and its rulesets could not be read: "
                 "not known whether a ruleset protects it", "gh api branches/protection → 404")
        elif prot is not None:
            checks = (prot.get("required_status_checks") or {}).get("contexts") or []
            reviews = (prot.get("required_pull_request_reviews") or {}).get("required_approving_review_count")
            admins = (prot.get("enforce_admins") or {}).get("enabled")
            fact(scope, "C7", f"branch {b} is protected · required checks: {', '.join(checks) or 'none'} · "
                 f"required approvals: {reviews if reviews is not None else 'none'} · applies to admins: {admins}",
                 "gh api branches/protection")
        elif "not protected" in err.lower():
            fact(scope, "C7", f"branch {b} is NOT protected: whoever can write, agents included, can push to it",
                 "gh api branches/protection → 404")
        elif "upgrade" in err.lower():
            fact(scope, "C7", f"branch {b}: protection is not offered by this plan for a private repository "
                 "(hooks and job dependencies are the free walls left)", "gh api branches/protection → 403")
        else:
            missing(scope, f"protection of {b} not readable ({mask(err, 80)})")
    rs, _ = gh_json(["api", f"repos/{slug}/rulesets"])
    if isinstance(rs, list):
        active = [r.get("name") for r in rs if r.get("enforcement") == "active"]
        fact(scope, "C7", f"rulesets: {len(active)} active" + (f" ({', '.join(active[:4])})" if active else ""),
             "gh api rulesets")
    envs, _ = gh_json(["api", f"repos/{slug}/environments"])
    if envs is not None:
        for e in envs.get("environments", []):
            rules = [r.get("type") for r in e.get("protection_rules") or []]
            fact(scope, "C7", f"environment {e.get('name')}: " + (f"protection rules: {', '.join(rules)}" if rules
                 else "NO protection rule (no required reviewer, no wait timer)"), "gh api environments")
    prs, err = gh_json(["pr", "list", "-R", slug, "--state", "merged", "--limit", "30", "--json",
                        "number,author,mergedBy,reviewDecision,statusCheckRollup,mergedAt"])
    if prs is None:
        missing(scope, f"merged pull requests not readable ({mask(err, 80)})")
    elif prs:
        red, nocheck, selfm, names = [], [], [], Counter()
        for p in prs:
            roll = p.get("statusCheckRollup") or []
            bad = [c.get("name") or c.get("context") for c in roll
                   if (c.get("conclusion") or c.get("state") or "").upper() in RED]
            if bad:
                red.append(p["number"])
                names.update(set(bad))
            if not roll:
                nocheck.append(p["number"])
            a, m = (p.get("author") or {}).get("login"), (p.get("mergedBy") or {}).get("login")
            if a and a == m and p.get("reviewDecision") != "APPROVED":
                selfm.append(p["number"])
        span = f"{prs[-1]['mergedAt'][:10]} to {prs[0]['mergedAt'][:10]}"
        fact(scope, "C7", f"last {len(prs)} merged PRs ({span}): {len(red)} merged with a failing check"
             + (f" (#{', #'.join(map(str, red[:8]))}{'…' if len(red) > 8 else ''}; most often: "
                f"{', '.join(n for n, _ in names.most_common(3))})" if red else "")
             + f" · {len(nocheck)} with no check at all", "gh pr list --state merged",
             {"red": red, "no_check": nocheck})
        fact(scope, "C6", f"last {len(prs)} merged PRs: {len(selfm)} merged by their own author without an approving "
             "review (normal for a solo developer: the second pair of eyes is then a check or an agent)",
             "gh pr list --state merged")
    else:
        fact(scope, "C6", "no merged pull request: work lands by direct push", "gh pr list --state merged")
    runs, err = gh_json(["run", "list", "-R", slug, "--limit", "200", "--json",
                         "workflowName,event,conclusion,createdAt"])
    if runs is None:
        missing(scope, f"workflow runs not readable ({mask(err, 80)})")
        return
    groups = {}
    for r in runs:
        groups.setdefault((r["workflowName"], r["event"]), []).append(r)
    for (wname, event), rr in sorted(groups.items(), key=lambda kv: -len(kv[1]))[:10]:
        done = [r for r in rr if r.get("conclusion")]
        if len(done) < 3:
            continue
        c = Counter(r["conclusion"] for r in done)
        streak = 0
        for r in done:
            if r["conclusion"] != "failure":
                break
            streak += 1
        last_ok = next((r["createdAt"][:10] for r in done if r["conclusion"] == "success"), None)
        txt = (f"runs · {wname} on {event}: {c.get('success', 0)} success, {c.get('failure', 0)} failure, "
               f"{c.get('cancelled', 0)} cancelled (last {len(rr)}, {done[-1]['createdAt'][:10]} to "
               f"{done[0]['createdAt'][:10]})")
        if streak >= 3:
            txt += f" · RED for the last {streak} runs, last green: {last_ok or 'not in the sample'}"
        fact(scope, "C5", txt, "gh run list")


def scan_repo(path, home_rules, home_hooks, args, mode, baseline):
    repo = Path(path).expanduser().resolve()
    if not repo.is_dir():
        print(f"\n== REPO {repo.name}  ({short(repo)}) ==\npath not found or not a folder: nothing scanned.")
        missing(repo.name, f"{short(repo)} does not exist or is not a folder: nothing scanned for it")
        return
    rc, top, _ = git(repo, "rev-parse", "--show-toplevel")
    inside = rc == 0 and top and Path(top).resolve() != repo
    if inside:
        print(f"\n{short(repo)} is a subfolder of the repository {short(top)}: the whole repository is scanned.")
        repo = Path(top).resolve()
    scope = repo.name
    print(f"\n== REPO {scope}  ({short(repo)}) ==")
    is_git = git(repo, "rev-parse", "--git-dir")[0] == 0 and (repo / ".git").exists()
    if not is_git:
        subs = sorted(p.parent.name for p in repo.glob("*/.git"))
        if subs:
            print(f"not a git repository: a workspace holding {len(subs)} repositories ({', '.join(subs[:12])}). "
                  "Pass each one with --repo.")
            return
        print("not a git repository: file checks only, no history, no platform.")
        missing(scope, "not a git repository: freshness, run history and platform walls unknown")
    default, slug, info, ref = "main", None, None, None
    if is_git:
        rc, url, _ = git(repo, "remote", "get-url", "origin")
        # github.com exactly (not notgithub.com, not github.company.com), or an SSH host alias such as
        # git@github.com-work:owner/repo.git
        m = re.search(r"(?:^|[@/])github\.com(?:-[\w.-]+)?[:/]([^/:]+)/([^/]+?)(?:\.git)?/?$", url) if rc == 0 else None
        slug = f"{m.group(1)}/{m.group(2)}" if m else None
        if slug and not args.no_network:
            if run(["gh", "auth", "status"], timeout=15)[0] == 0:
                info, err = gh_json(["api", f"repos/{slug}"])
                if info is None:
                    missing(scope, f"GitHub not readable for {slug} ({mask(err, 80)}): branch protection, merges "
                            "and run history unknown")
            else:
                missing(scope, "gh is absent or not signed in: branch protection, merges on red and run history unknown")
        elif slug:
            missing(scope, "network probes skipped (--no-network): branch protection, merges on red and run "
                    "history unknown")
        else:
            missing(scope, "no GitHub remote: platform walls (branch protection, environments) not measured")
        rc, out, _ = git(repo, "symbolic-ref", "--short", "refs/remotes/origin/HEAD")
        if info:
            default = info.get("default_branch", "main")
        elif rc == 0 and "/" in out:
            default = out.split("/", 1)[1]
        else:
            default = next((c for c in ("main", "master", "develop")
                            if git(repo, "rev-parse", "--verify", "-q", c)[0] == 0), "main")
        ref = f"origin/{default}" if git(repo, "rev-parse", "--verify", "-q", f"origin/{default}")[0] == 0 else "HEAD"
        _, cur, _ = git(repo, "branch", "--show-current")
        _, date, _ = git(repo, "log", "-1", "--format=%cs", ref)
        _, fh, _ = git(repo, "rev-parse", "--git-path", "FETCH_HEAD")
        fetched = "never"
        fp = Path(fh) if os.path.isabs(fh) else repo / fh
        if fp.exists():
            fetched = time.strftime("%Y-%m-%d", time.localtime(fp.stat().st_mtime))
        fresh = ""
        if ref != "HEAD":
            fresh = (", fetched today" if fetched == time.strftime("%Y-%m-%d")
                     else f", LAST FETCH {fetched}: run `git fetch` for fresh facts")
        fact(scope, "C9", f"tracked files read at {ref} (last commit {date or 'none'}{fresh}) · working tree on "
             f"{cur or 'a detached commit'}"
             + (f" · remote {slug}" if slug else " · no GitHub remote")
             + (" · default branch taken from the local origin/HEAD, which may be stale" if slug and not info else ""),
             "git")
    tree = Tree(repo, ref)

    # C2 map
    maps = [n for n in ("CLAUDE.md", "AGENTS.md", ".claude/CLAUDE.md", ".cursorrules", "GEMINI.md") if n in tree.fileset]
    for name in maps:
        prose_rules(scope, name, tree.read(name) or "", f"{name} at {tree.where}", limit=12)
        date, behind = tree.age(name)
        if date:
            fact(scope, "C2", f"{name} last changed {date}, {behind} commits ago", "git log")
    if not maps:
        fact(scope, "C2", "no map file (CLAUDE.md / AGENTS.md) at the root", tree.where)

    # C4 state
    state_rx = re.compile(r"^(\.claude/memory/[^/]+\.md|\.claude/memory/in-progress/[^/]+/TASK\.md|(docs/)?"
                          r"(STATE|PROGRESS|DECISIONS|NEXT_STEPS)\.md)$")
    states = [f for f in tree.files if state_rx.match(f)]
    for rel in states[:8]:
        date, behind = tree.age(rel)
        fact(scope, "C4", f"state file {rel}" + (f" last changed {date}, {behind} commits ago" if date else ""),
             f"git log at {tree.where}" if date else tree.where)
    local_state = [str(p.relative_to(repo)) for pat in (".claude/memory/*.md", "STATE.md", "PROGRESS.md")
                   for p in repo.glob(pat) if str(p.relative_to(repo)) not in tree.fileset]
    if local_state:
        fact(scope, "C4", f"state files present on this machine but absent from {tree.where}: "
             + ", ".join(local_state[:6]), "file presence")
    if not states and not local_state:
        fact(scope, "C4", "no state file outside the conversation (STATE.md, .claude/memory/…)", tree.where)

    # C1 contracts
    specs = [f for f in tree.files if re.search(r"(?i)(^|/)(specs?/[^/]+\.md|SPEC\.md|adr/[^/]+\.md)$", f)]
    tmpl = [f for f in tree.files if re.match(r"(?i)\.github/(pull_request_template\.md|ISSUE_TEMPLATE/)", f)]
    fact(scope, "C1", f"contract artefacts: {len(specs)} spec or ADR file(s)"
         + (f" (e.g. {', '.join(specs[:3])})" if specs else "") + f", {len(tmpl)} PR or issue template(s)"
         + ("" if specs or tmpl else " — read two recent PRs or task briefs to see whether `done when` is written "
            "before the work"), tree.where)

    # C5 local gate
    gates = [f for f in tree.files if re.search(
        r"(?i)(^|/)((check|gate|verify|preflight)[^/]*\.(sh|py|js|ts)|Makefile|justfile|\.pre-commit-config\.yaml|"
        r"lefthook\.yml)$|^\.husky/[^/]+$|^package\.json$", f)]
    fact(scope, "C5", "local gate candidates: " + (", ".join(gates[:8]) if gates else "none"), tree.where)

    # C7 rules and hooks active in this checkout
    rules, hooks, own = home_rules, list(home_hooks), False
    for name in (".claude/settings.json", ".claude/settings.local.json"):
        s = load_settings(repo / name)
        if s is None:
            if (repo / name).is_file():
                missing(scope, f"{name} is not a readable JSON object: its rules and hooks are unknown")
            continue
        r, h = bash_rules(s), settings_hooks(s, name, from_repo=True)
        n = {k: len(rule_list(s, k)) for k in ("allow", "ask", "deny")}
        broad = [x for x in r["allow"] if is_broad(x)]
        fact(scope, "C7", f"{name}: allow {n['allow']} · ask {n['ask']} · deny {n['deny']}"
             + (f" · broad allow: {', '.join(broad[:8])}" if broad else "")
             + (f" · hooks: {', '.join(sorted({x['event'] for x in h}))}" if h else ""), name)
        own = own or any(n.values()) or bool(h)
        rules = merge_rules(rules, r)
        hooks += h
    stop = [h for h in hooks if h["event"] in ("Stop", "SubagentStop")]
    fact(scope, "C5", f"Stop hooks (the place where a proof can be demanded before `done`): {len(stop)}"
         + (f" — {'; '.join(hook_label(h) for h in stop[:4])}" if stop else ""), "settings + plugins")
    if own:
        probe_stack(scope, rules, hooks, "main", repo if args.probe_repo_hooks else None, not args.no_hook_probe,
                    mode, baseline, repo_hooks_ok=args.probe_repo_hooks)
    else:
        print("  permission rules and hooks: same stack as GLOBAL (no repository-level rule or hook)")

    deploy_branches = scan_workflows(scope, tree)

    # C7 secrets in the tree
    env_tracked = [f for f in tree.files if re.search(r"(^|/)\.env(\.[^/]+)?$", f)
                   and not re.search(r"(?i)\.(example|sample|template|dist)$", f)]
    ignore = tree.read(".gitignore") if ".gitignore" in tree.fileset else None
    fact(scope, "C7", "env files: " + (f"{len(env_tracked)} TRACKED in the repository ({', '.join(env_tracked[:4])})"
         if env_tracked else "none tracked") + " · .gitignore "
         + ("absent" if ignore is None else "covers .env" if re.search(r"(?m)^\s*\*?\.env", ignore)
            else "does not mention .env"), tree.where)
    hard = [h for h in tree.grep(SECRET_RX) if not h.split(":")[0].endswith((".md", ".mdx"))]
    if hard:
        fact(scope, "C7", f"{len(hard)} line(s) in tracked files look like a hard-coded secret ({', '.join(hard[:5])}"
             f"{'…' if len(hard) > 5 else ''}); the value is not printed here, do not print it either. Rotate it and "
             "move it to the secret store", f"pattern match at {tree.where}")
    # C6 reviewers
    rev = [f for f in tree.files if re.search(r"(?i)(^|/)(CODEOWNERS|\.claude/agents/[^/]*(review|verif|qa|antagon)[^/]*)$", f)]
    fact(scope, "C6", "reviewer artefacts in the repository: " + (", ".join(rev[:6]) if rev else "none"), tree.where)
    # C8 caps
    caps = tree.grep(r"--max-turns|--max-budget-usd|maxTurns|max_turns|MAX_ATTEMPTS")
    fact(scope, "C8", f"turn, budget or attempt caps written in tracked files: {len(caps)}"
         + (f" ({', '.join(caps[:5])})" if caps else " (no --max-turns, --max-budget-usd, maxTurns, MAX_ATTEMPTS)"),
         f"grep at {tree.where}")
    hits = [h for h in tree.grep(AGENT_CALL_RX) if not h.split(":")[0].endswith((".md", ".mdx", ".txt"))]
    launchers = re.compile(r"(\.(sh|bash|zsh|ya?ml|plist|service|timer)|(^|/)(Makefile|justfile|crontab|package\.json))$")
    calls = [h for h in hits if launchers.search(h.split(":")[0])]
    mentions = sorted({h.split(":")[0] for h in hits if h not in calls})
    if calls:
        capped = set(tree.grep(AGENT_CAPPED_RX)) | set(tree.grep(AGENT_TIMED_RX))
        bare = [c for c in calls if c not in capped]
        fact(scope, "C8", f"{len(calls)} headless agent call(s) in scripts and CI files, {len(bare)} with no turn or "
             "budget flag and no `timeout` on the same line" + (f" ({', '.join(bare[:5])}{'…' if len(bare) > 5 else ''})" if bare else ""),
             f"grep at {tree.where}")
    if mentions:
        fact(scope, "C8", f"headless agent calls also appear in {len(mentions)} source file(s) "
             f"({', '.join(mentions[:4])}{'…' if len(mentions) > 4 else ''}): the program launches agents itself, "
             "open the launcher to see how each run is capped", f"grep at {tree.where}")
    # C10 lessons and structural checks
    lessons = [f for f in tree.files if re.search(
        r"(?i)(^|[/_.-])(lessons?|post-?mortems?|incidents?|retro(spective)?s?|learnings?)[^/]*\.(md|mdx|txt)$", f)]
    lint = tree.grep(r"no-restricted-imports|no-restricted-paths|dependency-cruiser|custom_rules|ArchUnit|import-linter",
                     names_only=True)
    fact(scope, "C10", f"lessons files: {len(lessons)}" + (f" ({', '.join(lessons[:4])})" if lessons else "")
         + f" · structural lint rules (a past failure turned into a check): {len(lint)} file(s)"
         + (f" ({', '.join(lint[:4])})" if lint else ""), tree.where)
    # C12 measuring the harness
    evals = sorted({re.sub(r"/evals?/.*$", "", f) for f in tree.files if re.search(r"(^|/)evals?/", f)})
    hook_tests = [f for f in tree.files if re.search(r"(?i)hook[^/]*(test|spec)|(test|spec)[^/]*hook", f)]
    fact(scope, "C12", f"eval suites in the repository: {len(evals)} · tests that exercise a hook: {len(hook_tests)}",
         tree.where)

    if not is_git:
        return
    # C5 git hooks that are versioned but may not run here
    hook_dirs = sorted({f.split("/")[0] for f in tree.files if re.match(r"(\.githooks|\.husky|githooks)/[^/]+$", f)})
    if hook_dirs:
        _, hp, _ = git(repo, "config", "--get", "core.hooksPath")
        active = [d for d in hook_dirs if hp.rstrip("/").endswith(d)]
        fact(scope, "C5", f"git hooks versioned in {', '.join(hook_dirs)} · core.hooksPath on this machine: "
             f"{hp or 'not set (.git/hooks)'}" + ("" if active else " → these hooks do NOT run here"), "git config")
    # C9 recovery
    rc, n, _ = git(repo, "rev-list", "--count", "@{u}..HEAD")
    _, refs, _ = git(repo, "for-each-ref", "--format=%(refname:short)|%(upstream)", "refs/heads")
    local_only = [l.split("|")[0] for l in refs.splitlines() if l.endswith("|")]
    _, dirty, _ = git(repo, "status", "--porcelain")
    if git(repo, "remote")[1]:
        fact(scope, "C9", "work that exists on this machine only: "
             + (f"{n} unpushed commit(s) on the current branch" if rc == 0 else "current branch has no upstream")
             + f", {len(local_only)} local-only branch(es), {len(dirty.splitlines())} uncommitted file(s)", "git")
    else:
        fact(scope, "C9", f"no remote at all: every commit of the {len(refs.splitlines())} branch(es) "
             f"({', '.join(l.split('|')[0] for l in refs.splitlines()[:4])}) exists on this machine only, "
             f"{len(dirty.splitlines())} uncommitted file(s)", "git")
    # C11 entropy
    _, wt, _ = git(repo, "worktree", "list", "--porcelain")
    branches = re.findall(r"^branch refs/heads/(.+)$", wt, re.M)
    n_wt = len(re.findall(r"^worktree ", wt, re.M))
    if n_wt > 1:
        merged = [b for b in branches if b != default and git(repo, "merge-base", "--is-ancestor", b, ref)[0] == 0]
        fact(scope, "C11", f"{n_wt} worktrees, {len(merged)} whose branch is already contained in {ref} "
             "(squash merges are not seen by this test)", "git worktree list")
    if info:
        scan_github(scope, slug, info, deploy_branches)


# ---------------------------------------------------------------- global

def scan_global(home, args):
    scope = "GLOBAL"
    print(f"== GLOBAL  ({short(home)}) ==")
    settings = load_settings(home / "settings.json")
    if settings is None:
        print("no readable settings.json here (absent, or not a JSON object).")
        missing(scope, f"{short(home)}/settings.json not readable: global rules and hooks unknown")
        settings = {}
    # settings.local.json in this folder is the local file of a project rooted in the home folder: it applies to
    # sessions started there only, so it is not merged into the global stack.
    local = load_settings(home / "settings.local.json")
    if local and (any(rule_list(local, k) for k in ("allow", "ask", "deny")) or settings_hooks(local, "")):
        print("  settings.local.json here holds rules or hooks: they apply only to sessions started in the home "
              "folder and are not counted as global.")
    rules = bash_rules(settings)
    perms = settings.get("permissions") if isinstance(settings.get("permissions"), dict) else {}
    n = {k: len(rule_list(settings, k)) for k in ("allow", "ask", "deny")}
    mode = perms.get("defaultMode") or settings.get("defaultMode")
    mode = mode if isinstance(mode, str) and mode else "not set"
    fact(scope, "C7", f"permission rules: allow {n['allow']} · ask {n['ask']} · deny {n['deny']} · permission mode: "
         + (mode if mode != "not set" else "not set (the built-in default of the installed version applies; it is "
                                            "not the same in every version, check it before relying on a prompt)"),
         "settings.json")
    broad = [x for x in rules["allow"] if is_broad(x)]
    if broad:
        fact(scope, "C7", "broad allow rules: " + ", ".join(broad[:12]) + ". Each pre-approves a whole family of "
             "commands, the reversible ones (commit) and the others (push, reset) alike, unless an ask rule, a deny "
             "rule or a hook catches those", "settings.json")
    enabled = settings.get("enabledPlugins") if isinstance(settings.get("enabledPlugins"), dict) else {}
    p_hooks, p_skills, p_agents = plugin_parts(home, enabled)
    hooks = settings_hooks(settings, "settings.json") + p_hooks
    by_event = Counter(h["event"] for h in hooks)
    fact(scope, "C7", f"hooks: {len(hooks)} (" + (", ".join(f"{e} {c}" for e, c in by_event.most_common()) or "none")
         + f") · enabled plugins: {sum(1 for v in enabled.values() if v)}", "settings.json + plugins")
    for h in [h for h in hooks if h["event"] in ("PreToolUse", "Stop", "SubagentStop")][:12]:
        print(f"      {h['event']}[{h['matcher'] or '*'}] {hook_label(h)}  ← an event that can block")
    auto = settings.get("autoMode")
    if isinstance(auto, dict):
        for k, v in auto.items():
            if isinstance(v, list) and v and re.search(r"deny|allow|ask", k):
                fact(scope, "C7", f"auto mode `{k}`: {len(v)} entr{'y' if len(v) == 1 else 'ies'}, judged by a "
                     "classifier model (a filter, not a deterministic wall): "
                     + " | ".join(mask(str(x), 50) for x in v[:5]), "settings.json autoMode")
    if (home / "CLAUDE.md").is_file():
        prose_rules(scope, "CLAUDE.md", (home / "CLAUDE.md").read_text(errors="replace"), short(home / "CLAUDE.md"))
    baseline = probe_stack(scope, rules, hooks, "main", None, not args.no_hook_probe, mode)

    # C11: weight of what is loaded in every session, and what is actually launched
    agents = [p for p in sorted((home / "agents").glob("*.md")) if frontmatter_bytes(p)] \
        if (home / "agents").is_dir() else []
    skills = sorted(p.parent.name for p in (home / "skills").glob("*/SKILL.md")) if (home / "skills").is_dir() else []
    weight = sum(frontmatter_bytes(p) for p in agents)
    fact(scope, "C11", f"loaded in every session: {len(agents)} personal agents ({weight} bytes of frontmatter), "
         f"{len(skills)} personal skills, {len(p_skills)} plugin skills, {len(p_agents)} plugin agents",
         "agents, skills, plugins")
    lessons = sorted({p for pat in ("*lesson*.md", "memory/*lesson*.md", "projects/*/memory/*lesson*.md")
                      for p in home.glob(pat)})
    fact(scope, "C10", f"lessons files in the global config: {len(lessons)}"
         + (f" ({', '.join(short(p) for p in lessons[:3])})" if lessons else ""), "file names")
    dup = sorted(set(skills) & {s for s, _ in p_skills}) + sorted({a.stem for a in agents} & {a for a, _ in p_agents})
    if dup:
        fact(scope, "C3", f"same name defined twice (personal and plugin): {', '.join(dup[:8])}", "name comparison")
    if args.usage_days > 0:
        a_use, s_use, nfiles, nbytes, skipped = transcript_usage(
            home, args.usage_days, args.usage_cap_mb, set(skills) | {s for s, _ in p_skills})
        if nfiles:
            idle = [a.stem for a in agents if a_use.get(a.stem, 0) == 0]
            idle_s = [s for s in skills if s_use.get(s, 0) == 0]
            cover = (f"last {args.usage_days} days, {nfiles} transcripts, {nbytes // 1048576} MB"
                     + (f", {skipped} older ones skipped over the size cap" if skipped else "") + ", approximate")
            fact(scope, "C11", f"usage ({cover}): {len(idle)} of {len(agents)} personal agents never launched"
                 + (f" ({', '.join(idle[:9])})" if idle else "")
                 + f" · {len(idle_s)} of {len(skills)} personal skills never invoked", "session transcripts")
            top = ", ".join(f"{k} {v}" for k, v in (a_use + s_use).most_common(6))
            if top:
                fact(scope, "C11", f"most launched: {top}", "session transcripts")
            rev = {k: v for k, v in (a_use + s_use).items() if re.search(r"(?i)review|verif|antagon|\bqa\b|valid", k)}
            fact(scope, "C6", "reviewer roles launched: " + (", ".join(
                f"{k} {v}" for k, v in sorted(rev.items(), key=lambda kv: -kv[1])[:6]) or "none"), "session transcripts")
        else:
            missing(scope, "no transcript in the window: agent and skill usage unknown")
    return rules, hooks, mode, baseline


def main():
    ap = argparse.ArgumentParser(description="Scan of what holds an AI-assisted workflow. Edits nothing; runs your own "
                                             "PreToolUse hooks on fabricated commands unless --no-hook-probe.")
    ap.add_argument("--repo", action="append", default=[], help="repository to scan (repeatable)")
    ap.add_argument("--home", default=str(HOME / ".claude"), help="Claude Code config folder (default ~/.claude)")
    ap.add_argument("--no-network", action="store_true", help="skip the GitHub probes")
    ap.add_argument("--no-hook-probe", action="store_true", help="run no hook at all")
    ap.add_argument("--probe-repo-hooks", action="store_true",
                    help="also run the hooks defined by the scanned repositories (only for repositories you trust)")
    ap.add_argument("--usage-days", type=int, default=30, help="window for agent and skill usage (0 to skip)")
    ap.add_argument("--usage-cap-mb", type=int, default=3000, help="stop reading transcripts after this many MB")
    ap.add_argument("--json", metavar="FILE", help="also write the facts as JSON to FILE")
    args = ap.parse_args()

    print(f"HARNESS SCAN · {time.strftime('%Y-%m-%d')} · reads only; runs git, gh and, unless --no-hook-probe, "
          "your own PreToolUse hooks · criteria C1 to C12 in references/grid.md\n")
    rules, hooks, mode, baseline = scan_global(Path(args.home).expanduser(), args)
    for r in args.repo:
        scan_repo(r, rules, hooks, args, mode, baseline)
    print("\n== NOT MEASURED (say so in the report, never fill these in from memory) ==")
    for m in NOT_MEASURED:
        print(f"- {m}")
    print("- C3 (tools with clear failure messages) and the quality of specs, reviews and lessons: the scan only "
          "shows that the files exist, read them")
    print("- the size of parallel agent batches, and what fixes it: invisible to the scan, ask or read the "
          "orchestration instructions")
    if not args.repo:
        print("- no repository given: CI, deploy dependencies and platform walls not scanned (--repo PATH)")
    if args.json:
        Path(args.json).write_text(json.dumps({"date": time.strftime("%Y-%m-%d"), "facts": FACTS,
                                               "not_measured": NOT_MEASURED}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
