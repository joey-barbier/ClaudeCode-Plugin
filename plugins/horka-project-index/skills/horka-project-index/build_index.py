#!/usr/bin/env python3
"""
build_index.py — Global index of Claude Code projects (generic, shareable).

Source of truth: the transcripts <config>/projects/*/*.jsonl.
Each session records its real `cwd` — we extract it instead of decoding the
folder name (dash-encoding is ambiguous: `dev-cc` vs `dev/cc`).

On top of projects (folders actually opened with Claude), we detect WORKSPACES:
any ANCESTOR folder containing a `.claude/` and parent of at least one indexed
project (e.g. a monorepo `LibTracker/` hosting API + front + sdk). Workspaces do
not necessarily have history but may own shared skills/commands — that is where a
command like "write the changelog" should land.

Output (inside the Claude config dir, CLAUDE_CONFIG_DIR honored):
  - projects-index.json   (canonical, structured, atomic write)
  - PROJECTS.md           (generated readable view)

Modes:
  python3 build_index.py                # smart: bootstrap if empty, else refresh
  python3 build_index.py --ensure PATH  # add/refresh ONE project (ABSOLUTE path preferred)
  python3 build_index.py --roots        # inferred roots (where to put a new project)
  python3 build_index.py --prune        # drop entries whose path no longer exists
  python3 build_index.py --status       # index state (JSON)
  (option --json-only: do not regenerate the .md)

Portability: Python >= 3.7 and git on PATH; macOS / Linux / WSL / Windows.
Monorepos outside HOME (/Volumes, /mnt…) are covered. Stack/description
heuristics target common ecosystems; an unknown stack simply yields stack:[]
(graceful degradation, never an error).

Known limitation: concurrent `--ensure` (two sessions at once) is an unlocked
read-modify-write — the write is atomic (no corruption) but the last writer may
overwrite the other's addition. A full rebuild recovers everything from history.
"""
import json
import os
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

if sys.version_info < (3, 7):
    sys.exit("Python 3.7+ required (subprocess capture_output/text, dict ordering).")

HOME = Path.home()


def resolve_config_dir() -> Path:
    """Honor CLAUDE_CONFIG_DIR (may be a list separated by ',' or os.pathsep)."""
    raw = os.environ.get("CLAUDE_CONFIG_DIR", "").strip()
    if raw:
        # List separator: ',' + os.pathsep (';' on Windows, ':' on POSIX).
        # We do NOT split on ':' unconditionally, else 'C:\\Users\\x' breaks on Windows.
        seps = "," + os.pathsep
        first = re.split("[" + re.escape(seps) + "]", raw)[0].strip()
        if first:
            return Path(first).expanduser()
    return HOME / ".claude"


CONFIG_DIR = resolve_config_dir()
PROJECTS_DIR = CONFIG_DIR / "projects"
INDEX_JSON = CONFIG_DIR / "projects-index.json"
INDEX_MD = CONFIG_DIR / "PROJECTS.md"

MANUAL_FIELDS = ("notes", "name_override", "description_override")

# basenames too generic to identify a project on their own.
# Deliberately conservative: we do NOT include site/public/core/main/mobile,
# which are often real project names.
GENERIC = {
    "api", "app", "web", "www", "front", "frontend", "back", "backend",
    "server", "client", "src", "ios", "android",
}

# template README openings → no value, ignored (best-effort, English)
BOILERPLATE = (
    "to make it easy for you to get started",
    "look at the",
    "this is a next.js project",
    "welcome to your new",
    "get started with",
    "see the folder",
    "this template should help",
    "npm install",
    "yarn install",
)


# --------------------------------------------------------------------------- #
# Discovery
# --------------------------------------------------------------------------- #
def latest_jsonl(project_dir: Path):
    # Guarded stat(): a .jsonl may vanish (session rotation) between the glob and
    # the stat while another Claude session is running.
    best = None
    for p in project_dir.glob("*.jsonl"):
        try:
            m = p.stat().st_mtime
        except OSError:
            continue
        if best is None or m > best[0]:
            best = (m, p)
    return best[1] if best else None


def extract_cwd(jsonl: Path):
    """First `cwd` found in the transcript (reliable, unambiguous method)."""
    try:
        with jsonl.open(encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                if '"cwd"' not in line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(obj, dict) and obj.get("cwd"):
                    return obj["cwd"]
    except OSError:
        return None
    return None


def discover_history():
    """Return {cwd_path: last_active_iso} from the transcripts."""
    found = {}
    if not PROJECTS_DIR.is_dir():
        return found
    for d in sorted(PROJECTS_DIR.iterdir()):
        if not d.is_dir():
            continue
        jsonl = latest_jsonl(d)
        if not jsonl:
            continue
        cwd = extract_cwd(jsonl)
        if not cwd:
            continue
        try:
            mtime = jsonl.stat().st_mtime
        except OSError:
            continue
        iso = datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat(timespec="seconds")
        if cwd not in found or iso > found[cwd]:
            found[cwd] = iso
    return found


def count_project_dirs() -> int:
    """Number of folders in projects/ — used to detect a broken schema
    (folders exist but no cwd could be extracted)."""
    if not PROJECTS_DIR.is_dir():
        return 0
    return sum(1 for d in PROJECTS_DIR.iterdir() if d.is_dir())


def discover_workspaces(project_paths, max_up=8):
    """{workspace_path: set(member_project_paths)}.
    A workspace = an ancestor of a project, containing a `.claude/`, that is
    neither HOME, nor the global config dir, nor an already-indexed project.
    We walk up to the FS root (bounded to `max_up` levels), so monorepos outside
    HOME (/Volumes, /mnt, WSL) are covered. HOME and the global `.claude` are
    explicitly excluded."""
    proj_set = {str(p) for p in project_paths}
    config_str = str(CONFIG_DIR)
    workspaces = {}
    for p in project_paths:
        a = Path(p).parent
        steps = 0
        while a != a.parent and steps < max_up:   # up to the root, bounded
            steps += 1
            sa = str(a)
            if a != HOME and sa != config_str and sa not in proj_set \
                    and (a / ".claude").is_dir():
                workspaces.setdefault(sa, set()).add(str(p))
            a = a.parent
    return workspaces


# --------------------------------------------------------------------------- #
# Enrichment
# --------------------------------------------------------------------------- #
def git(path: Path, *args):
    try:
        out = subprocess.run(
            ["git", "-C", str(path), *args],
            capture_output=True, text=True, timeout=5,
        )
        if out.returncode == 0:
            return out.stdout.strip()
    except (subprocess.SubprocessError, OSError):
        pass
    return None


def prettify(name: str) -> str:
    s = re.sub(r"[-_]+", " ", name).strip()
    return s[:1].upper() + s[1:] if s else name


def friendly_name(path: Path) -> str:
    """If the basename is generic (api, web…), walk up to the first distinctive
    ancestor: /Orka/LibTracker/APP/API -> 'LibTracker API'."""
    base = path.name
    if base.lower() not in GENERIC:
        return prettify(base)
    anchor = path.parent
    while anchor.name and anchor.name.lower() in GENERIC and anchor.parent != anchor:
        anchor = anchor.parent
    if anchor.name:
        return f"{prettify(anchor.name)} {prettify(base)}"
    return prettify(base)


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, RecursionError, ValueError):
        # RecursionError: pathologically nested JSON (not a ValueError).
        return None


def is_boilerplate(desc: str) -> bool:
    low = re.sub(r"[\[\]`*_]", "", desc.lower()).strip()
    return any(low.startswith(b) for b in BOILERPLATE)


def first_sentence(text: str, limit: int = 160) -> str:
    lines = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith(("#", "!", "<")):
            continue
        if line.startswith("[") and "http" in line:  # badge/link only
            continue
        lines.append(line)
        if len(" ".join(lines)) > 40:
            break
    blob = re.sub(r"[*_`>#]", "", " ".join(lines)).strip()
    if not blob:
        return ""
    m = re.match(r".{0," + str(limit) + r"}(?:[.!?]|$)", blob)
    return (m.group(0) if m else blob[:limit]).strip()


def scan_capabilities(path: Path):
    """Skills and commands a folder provides via its `.claude/`.
    This is the key signal to route an action (changelog, release, deploy…)."""
    skills, commands = [], []
    sk_dir = path / ".claude" / "skills"
    if sk_dir.is_dir():
        for item in sorted(sk_dir.iterdir()):
            if item.is_dir():
                skills.append(item.name)
            elif item.suffix == ".md":
                skills.append(item.stem)
    cmd_dir = path / ".claude" / "commands"
    if cmd_dir.is_dir():
        for item in sorted(cmd_dir.rglob("*.md")):
            commands.append(item.stem)
    return skills, commands


def detect(path: Path):
    """Return (stack:list, description:str) by sniffing manifests."""
    stack, desc = [], ""

    pkg = path / "package.json"
    if pkg.exists():
        data = read_json(pkg) or {}
        deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
        if "nuxt" in deps:
            stack.append("Nuxt")
        elif "next" in deps:
            stack.append("Next.js")
        elif "vue" in deps:
            stack.append("Vue")
        elif "react" in deps:
            stack.append("React")
        else:
            stack.append("Node")
        if data.get("description"):
            desc = data["description"].strip()

    if (path / "Package.swift").exists():
        stack.append("Swift")
    if list(path.glob("*.xcodeproj")) or list(path.glob("*.xcworkspace")):
        stack.append("iOS/Xcode")
    if (path / "pubspec.yaml").exists():
        stack.append("Flutter/Dart")
        if not desc:
            try:
                for line in (path / "pubspec.yaml").read_text(errors="ignore").splitlines():
                    if line.startswith("description:"):
                        desc = line.split(":", 1)[1].strip().strip('"\'')
                        break
            except OSError:
                pass
    if (path / "Cargo.toml").exists():
        stack.append("Rust")
    if (path / "go.mod").exists():
        stack.append("Go")
    if (path / "pyproject.toml").exists() or (path / "requirements.txt").exists():
        stack.append("Python")
    if (path / "Gemfile").exists():
        stack.append("Ruby")
    if (path / "composer.json").exists():
        stack.append("PHP")

    if not desc:
        for readme in ("README.md", "readme.md", "README.MD", "Readme.md"):
            rp = path / readme
            if rp.exists():
                try:
                    desc = first_sentence(rp.read_text(encoding="utf-8", errors="ignore"))
                except OSError:
                    pass
                break

    if desc and is_boilerplate(desc):
        desc = ""

    seen = set()
    stack = [s for s in stack if not (s in seen or seen.add(s))]
    return stack, desc


def make_entry(cwd: str, last_active: str, previous: dict,
               entry_type: str = "project", members=None) -> dict:
    """Build an index entry for a path, preserving manual fields."""
    path = Path(cwd)
    exists = path.is_dir()

    stack, desc, remote, branch, skills, commands = [], "", None, None, [], []
    if exists:
        stack, desc = detect(path)
        remote = git(path, "remote", "get-url", "origin")
        branch = git(path, "rev-parse", "--abbrev-ref", "HEAD")
        skills, commands = scan_capabilities(path)

    # path.parts (not str.split("/")) to stay correct on Windows (\\).
    parts = [s for s in path.parts if s not in ("/", "\\")]
    two = "/".join(parts[-2:]).lower() if len(parts) >= 2 else path.name.lower()
    aliases = sorted({path.name.lower(), two})

    entry = {
        "name": friendly_name(path),
        "path": str(path),
        "type": entry_type,
        "exists": exists,
        "aliases": aliases,
        "stack": stack,
        "description": desc,
        "skills": skills,
        "commands": commands,
        "git_remote": remote,
        "branch": branch,
        "last_active": last_active,
    }
    if members is not None:
        entry["members"] = sorted(members)
    old = previous.get(str(path), {})
    for f in MANUAL_FIELDS:
        if old.get(f):
            entry[f] = old[f]
    return entry


# --------------------------------------------------------------------------- #
# Index I/O
# --------------------------------------------------------------------------- #
def load_index():
    return read_json(INDEX_JSON) or {"projects": []}


def is_empty(index) -> bool:
    return not index.get("projects")


def now_iso():
    return datetime.now(tz=timezone.utc).isoformat(timespec="seconds")


def atomic_write(path: Path, text: str):
    """Atomic write: tmp + os.replace. Avoids corruption if two Claude sessions
    write the index at the same time."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f".tmp.{os.getpid()}")
    try:
        tmp.write_text(text, encoding="utf-8")
        os.replace(tmp, path)
    finally:
        try:
            tmp.unlink()      # no-op after a successful replace; cleans up on early crash
        except OSError:
            pass


def save_index(entries, json_only=False):
    # Sort by activity, descending; a workspace, whose last_active = max of its
    # members, naturally lands just above its most recent member.
    entries.sort(key=lambda p: p.get("last_active", ""), reverse=True)
    index = {"generated_at": now_iso(), "count": len(entries), "projects": entries}
    atomic_write(INDEX_JSON, json.dumps(index, indent=2, ensure_ascii=False))
    if not json_only:
        render_md(index)
    return index


def infer_roots(entries):
    """Roots where the user stores projects, derived from the index.
    Ignores workspaces (we want the storage folders)."""
    counter = Counter()
    for p in entries:
        if p.get("type") == "workspace":
            continue
        counter[str(Path(p["path"]).parent)] += 1
    return counter.most_common()


# --------------------------------------------------------------------------- #
# Markdown rendering
# --------------------------------------------------------------------------- #
def render_md(index):
    lines = [
        "# Projects — global Claude Code index",
        "",
        f"_Generated {index['generated_at']} · {index['count']} entries · "
        "source: transcripts + `.claude/` workspaces_",
        "",
        "> Generated by the `horka-project-index` skill. The `notes`, `name_override`, "
        "`description_override` fields you add in `projects-index.json` are "
        "preserved on rebuild. Do not hand-edit this .md (regenerated).",
        "",
    ]
    for p in index["projects"]:
        title = p.get("name_override") or p.get("name") or p.get("path", "?")
        badge = " 🗂️ _workspace_" if p.get("type") == "workspace" else ""
        flag = "" if p.get("exists", True) else " ⚠️ _(path not found)_"
        lines.append(f"## {title}{badge}{flag}")
        desc = p.get("description_override") or p.get("description") or ""
        if desc:
            lines.append(desc)
        meta = [f"`{p.get('path', '?')}`"]
        if p.get("stack"):
            meta.append("**" + " · ".join(p["stack"]) + "**")
        lines += ["", " — ".join(meta)]
        if p.get("skills") or p.get("commands"):
            caps = []
            if p.get("skills"):
                caps.append("skills: " + ", ".join(f"`{s}`" for s in p["skills"]))
            if p.get("commands"):
                caps.append("commands: " + ", ".join(f"`/{c}`" for c in p["commands"]))
            lines.append("🧩 " + " · ".join(caps))
        if p.get("members"):
            lines.append("members: " + ", ".join(f"`{Path(m).name}`" for m in p["members"]))
        details = []
        if p.get("aliases"):
            details.append("aliases: " + ", ".join(f"`{a}`" for a in p["aliases"]))
        if p.get("branch"):
            details.append(f"branch: `{p['branch']}`")
        if p.get("git_remote"):
            details.append(f"remote: {p['git_remote']}")
        details.append(f"active: {(p.get('last_active') or '')[:10]}")
        if p.get("notes"):
            details.append(f"📝 {p['notes']}")
        lines += ["<sub>" + " · ".join(details) + "</sub>", ""]
    atomic_write(INDEX_MD, "\n".join(lines))


# --------------------------------------------------------------------------- #
# Shared construction
# --------------------------------------------------------------------------- #
def build_entries(prev_by_path):
    """Projects (history + still-on-disk 'ensured') + workspaces (ancestors with
    .claude). Returns (entries, added_paths, history_count).

    Projects added via --ensure have no transcript: a rebuild must PRESERVE them
    as long as they exist on disk, otherwise the 'new project' flow would be wiped
    on the next refresh. Projects gone from disk are naturally dropped
    (self-cleaning)."""
    history = discover_history()
    known = set(prev_by_path)

    # path -> last_active, starting from history…
    proj_paths = dict(history)
    # …then preserve 'ensured' projects (outside history) that still exist.
    for path, e in prev_by_path.items():
        if e.get("type") == "project" and path not in proj_paths and Path(path).is_dir():
            proj_paths[path] = e.get("last_active") or now_iso()

    entries, added = [], []
    for path, last_active in proj_paths.items():
        entries.append(make_entry(path, last_active, prev_by_path, "project"))
        if path not in known:
            added.append(path)

    # workspaces computed over ALL projects (history + ensured)
    workspaces = discover_workspaces(list(proj_paths.keys()))
    for ws_path, members in workspaces.items():
        la = max((proj_paths[m] for m in members if m in proj_paths), default=now_iso())
        entries.append(make_entry(ws_path, la, prev_by_path, "workspace", members))
        if ws_path not in known:
            added.append(ws_path)
    return entries, added, len(history)


# --------------------------------------------------------------------------- #
# Commands
# --------------------------------------------------------------------------- #
def cmd_rebuild(json_only=False):
    index = load_index()
    was_empty = is_empty(index)
    prev_by_path = {p["path"]: p for p in index["projects"]}

    entries, added, history_count = build_entries(prev_by_path)

    # guardrail: folders exist but no cwd extracted → schema changed?
    dir_count = count_project_dirs()
    if history_count == 0 and dir_count > 0:
        print(f"⚠️  {dir_count} folders in {PROJECTS_DIR} but no `cwd` extracted "
              "from the transcripts. The Claude Code transcript format may have "
              "changed — the index would be empty. Nothing written.", file=sys.stderr)
        return 1

    saved = save_index(entries, json_only)
    n_ws = sum(1 for e in entries if e.get("type") == "workspace")
    n_proj = saved["count"] - n_ws
    if was_empty:
        print(f"⚡ ACTION A — bootstrap: empty index → {n_proj} projects + {n_ws} workspaces.")
    else:
        print(f"✓ refresh: {n_proj} projects + {n_ws} workspaces.")
        if added:
            print(f"  + {len(added)} new: " + ", ".join(Path(a).name for a in added))
        else:
            print("  no new entry detected.")
    print(f"  {INDEX_JSON}")
    if not json_only:
        print(f"  {INDEX_MD}")
    return 0


def cmd_ensure(target: str, json_only=False):
    """Ensure ONE project is in the index. Works without a transcript ('new
    project' case). Pass an ABSOLUTE path: in the Claude harness the shell cwd may
    be reset, so `.` is fragile."""
    # abspath (not resolve): does NOT resolve symlinks, to match the raw `cwd`
    # style of the transcripts and avoid duplicate entries.
    path = Path(os.path.abspath(os.path.expanduser(target)))
    index = load_index()
    was_empty = is_empty(index)
    prev_by_path = {p["path"]: p for p in index["projects"]}

    already = str(path) in prev_by_path
    last_active = prev_by_path.get(str(path), {}).get("last_active") \
        or discover_history().get(str(path)) or now_iso()

    entry = make_entry(str(path), last_active, prev_by_path, "project")
    others = [p for p in index["projects"] if p["path"] != str(path)]
    saved = save_index(others + [entry], json_only)

    verb = "already present — refreshed" if already else "ADDED to the index"
    warn = "" if entry["exists"] else "  ⚠️ path not found on disk"
    print(f"✓ {entry['name']} ({path}): {verb}.{warn}")
    if was_empty and not already:
        print("  (empty index — consider a full bootstrap: build_index.py)")
    print(f"  total: {saved['count']} entries")
    return 0


def cmd_prune(json_only=False):
    index = load_index()
    kept = [p for p in index["projects"] if Path(p["path"]).is_dir()]
    removed = len(index["projects"]) - len(kept)
    saved = save_index(kept, json_only)
    print(f"✓ prune: {removed} dead entry(ies) removed, {saved['count']} remaining.")
    return 0


def cmd_roots():
    index = load_index()
    roots = infer_roots(index["projects"])
    print(json.dumps({
        "empty": is_empty(index),
        "count": len(index["projects"]),
        "roots": [{"path": r, "projects": n} for r, n in roots],
    }, indent=2, ensure_ascii=False))
    return 0


def cmd_status():
    index = load_index()
    entries = index["projects"]
    print(json.dumps({
        "config_dir": str(CONFIG_DIR),
        "index_json": str(INDEX_JSON),
        "exists": INDEX_JSON.exists(),
        "empty": is_empty(index),
        "count": len(entries),
        "projects": sum(1 for e in entries if e.get("type") != "workspace"),
        "workspaces": sum(1 for e in entries if e.get("type") == "workspace"),
        "generated_at": index.get("generated_at"),
    }, indent=2, ensure_ascii=False))
    return 0


def main(argv):
    json_only = "--json-only" in argv
    argv = [a for a in argv if a != "--json-only"]

    if "--roots" in argv:
        return cmd_roots()
    if "--status" in argv:
        return cmd_status()
    if "--prune" in argv:
        return cmd_prune(json_only)
    if "--ensure" in argv or "--add" in argv:
        flag = "--ensure" if "--ensure" in argv else "--add"
        i = argv.index(flag)
        if i + 1 >= len(argv):
            print(f"usage: build_index.py {flag} <path>", file=sys.stderr)
            return 2
        return cmd_ensure(argv[i + 1], json_only)
    return cmd_rebuild(json_only)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
