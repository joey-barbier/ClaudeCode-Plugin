#!/usr/bin/env python3
# Aggregates Claude Code token usage from the local transcripts (JSONL) over N days.
# Usage:
#   python3 usage.py [label=hostname] [days=30]   -> JSON on stdout (a machine)
#   python3 usage.py --cloud DIR [days=60]        -> writes DIR/<session>.json (a cloud session)
# Cloud mode keeps one line per API response, so that the same response seen by two
# containers of one session (a session resumed in a new container) is counted once.
import json, os, sys, glob, time, socket, tempfile
from datetime import datetime, timedelta

FIELDS = ["input", "output", "cache_creation", "cache_read", "messages"]


def roots():
    r = {os.path.expanduser("~/.claude/projects"), os.path.expanduser("~/.config/claude/projects")}
    if os.environ.get("CLAUDE_CONFIG_DIR"):
        r.add(os.path.join(os.environ["CLAUDE_CONFIG_DIR"], "projects"))
    return sorted(x for x in r if os.path.isdir(x))


def scan(start, today, rts):
    """Reads the transcripts. Returns ({key: [day, model, project, sidechain, i, o, cc, cr]}, info)."""
    start_ts = time.mktime(start.timetuple())
    best = {}
    info = {"files": 0, "bad_lines": 0, "earliest": None, "oldest_file": None}
    for root in rts:
        for path in glob.glob(os.path.join(root, "**", "*.jsonl"), recursive=True):
            try:
                mt = os.path.getmtime(path)
                info["oldest_file"] = mt if info["oldest_file"] is None else min(info["oldest_file"], mt)
                if mt < start_ts:
                    continue
            except OSError:
                continue
            info["files"] += 1
            project = os.path.relpath(path, root).split(os.sep)[0]
            with open(path, encoding="utf-8", errors="replace") as f:
                for line in f:
                    if '"usage"' not in line:
                        continue
                    try:
                        e = json.loads(line)
                    except Exception:
                        info["bad_lines"] += 1; continue
                    if e.get("type") != "assistant":
                        continue
                    m = e.get("message") or {}
                    u = m.get("usage") or {}
                    model = m.get("model") or "inconnu"
                    if not u or model == "<synthetic>":
                        continue
                    ts = e.get("timestamp")
                    if not ts:
                        continue
                    try:
                        dt = datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone()
                    except Exception:
                        continue
                    d = dt.date()
                    if info["earliest"] is None or d < info["earliest"]:
                        info["earliest"] = d
                    if d < start or d > today:
                        continue
                    key = "%s:%s" % (m.get("id") or line[:80], e.get("requestId") or "")
                    rec = [d.isoformat(), model, project, bool(e.get("isSidechain")),
                           int(u.get("input_tokens") or 0), int(u.get("output_tokens") or 0),
                           int(u.get("cache_creation_input_tokens") or 0), int(u.get("cache_read_input_tokens") or 0)]
                    keep(best, key, rec)
    return best, info


def keep(best, key, rec):
    """Streaming writes the same response several times: keep the line with the most output."""
    prev = best.get(key)
    if prev is None or rec[5] > prev[5]:
        best[key] = rec


def summarize(best):
    """Per-response records -> the totals the page reads."""
    def add(acc, k, v):
        a = acc.setdefault(k, [0, 0, 0, 0, 0])
        for i in range(4):
            a[i] += v[i]
        a[4] += 1
    days, projects, side, total, days_sub = {}, {}, {}, {}, {}
    for d, model, project, sc, *v in best.values():
        add(days.setdefault(d, {}), model, v)
        if sc:
            add(days_sub, d, v)
        add(projects, project, v)
        add(side, "subagents" if sc else "principal", v)
        add(total, "total", v)
    return {
        "messages": len(best), "fields": FIELDS,
        "total": total.get("total"), "by_kind": side,
        "days": dict(sorted(days.items())), "days_sub": dict(sorted(days_sub.items())),
        "top_projects": dict(sorted(projects.items(), key=lambda kv: -sum(kv[1][:4]))[:15]),
    }


def iso_day(ts):
    return datetime.fromtimestamp(ts).date().isoformat() if ts else None


def machine_main(args):
    machine = args[0] if args and args[0] else socket.gethostname().split(".")[0]
    ndays = int(args[1]) if len(args) > 1 else 30
    today = datetime.now().astimezone().date()
    start = today - timedelta(days=ndays - 1)
    rts = roots()
    best, info = scan(start, today, rts)
    out = {"machine": machine, "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
           "window": [start.isoformat(), today.isoformat()], "roots": rts, "files": info["files"],
           "bad_lines": info["bad_lines"],
           "earliest_in_recent_files": info["earliest"].isoformat() if info["earliest"] else None,
           "oldest_transcript_mtime": iso_day(info["oldest_file"])}
    out.update(summarize(best))
    print(json.dumps(out, separators=(",", ":")))


def cloud_main(args):
    """One file per cloud session, merged with what earlier containers of the same session saw."""
    if os.environ.get("PLAYED_CLOUD") == "0":
        return
    out_dir = args[0]
    ndays = int(args[1]) if len(args) > 1 else 60
    session = (os.environ.get("CLAUDE_CODE_REMOTE_SESSION_ID") or os.environ.get("CLAUDE_CODE_SESSION_ID")
               or socket.gethostname()).replace(os.sep, "_")
    today = datetime.now().astimezone().date()
    start = today - timedelta(days=ndays - 1)
    best, info = scan(start, today, roots())
    path = os.path.join(out_dir, session + ".json")
    try:
        with open(path) as f:
            old = json.load(f).get("responses") or {}
    except (OSError, ValueError):
        old = {}
    for key, rec in old.items():
        if rec[0] >= start.isoformat():
            keep(best, key, rec)
    if not best:
        return
    out = {"machine": "cloud", "label": "Cloud", "session": session,
           "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
           "window": [start.isoformat(), today.isoformat()], "roots": ["cloud:" + session],
           "files": info["files"], "bad_lines": info["bad_lines"],
           "oldest_transcript_mtime": min(r[0] for r in best.values())}
    out.update(summarize(best))
    out["responses"] = best
    os.makedirs(out_dir, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=out_dir, prefix=".played-")
    with os.fdopen(fd, "w") as f:
        json.dump(out, f, separators=(",", ":"))
    os.replace(tmp, path)
    print(path)


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--cloud":
        cloud_main(sys.argv[2:])
    else:
        machine_main(sys.argv[1:])
