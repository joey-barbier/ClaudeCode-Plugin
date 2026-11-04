#!/usr/bin/env python3
# Aggregates Claude Code token usage from the local transcripts (JSONL) over N days.
# Usage: python3 usage.py [label=hostname] [days=30]  -> JSON on stdout
import json, os, sys, glob, time, socket
from datetime import datetime, timedelta, timezone

machine = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else socket.gethostname().split(".")[0]
ndays = int(sys.argv[2]) if len(sys.argv) > 2 else 30
today = datetime.now().astimezone().date()
start = today - timedelta(days=ndays - 1)
start_ts = time.mktime(start.timetuple())

roots = {os.path.expanduser("~/.claude/projects"), os.path.expanduser("~/.config/claude/projects")}
if os.environ.get("CLAUDE_CONFIG_DIR"):
    roots.add(os.path.join(os.environ["CLAUDE_CONFIG_DIR"], "projects"))
roots = [r for r in roots if os.path.isdir(r)]

best = {}  # message.id:requestId -> (day, model, project, sidechain, usage)
files = 0; lines_bad = 0; earliest = None; oldest_file = None
for root in roots:
    for path in glob.glob(os.path.join(root, "**", "*.jsonl"), recursive=True):
        try:
            mt = os.path.getmtime(path)
            oldest_file = mt if oldest_file is None else min(oldest_file, mt)
            if mt < start_ts:
                continue
        except OSError:
            continue
        files += 1
        project = os.path.relpath(path, root).split(os.sep)[0]
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                if '"usage"' not in line:
                    continue
                try:
                    e = json.loads(line)
                except Exception:
                    lines_bad += 1; continue
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
                if earliest is None or d < earliest:
                    earliest = d
                if d < start or d > today:
                    continue
                key = "%s:%s" % (m.get("id") or line[:80], e.get("requestId") or "")
                vals = [int(u.get("input_tokens") or 0), int(u.get("output_tokens") or 0),
                        int(u.get("cache_creation_input_tokens") or 0), int(u.get("cache_read_input_tokens") or 0)]
                prev = best.get(key)
                if prev is None or vals[1] > prev[4][1]:
                    best[key] = (d.isoformat(), model, project, bool(e.get("isSidechain")), vals)

def add(acc, k, v):
    a = acc.setdefault(k, [0, 0, 0, 0, 0])
    for i in range(4):
        a[i] += v[i]
    a[4] += 1

days, projects, side, total, days_sub = {}, {}, {}, {}, {}
for d, model, project, sc, v in best.values():
    add(days.setdefault(d, {}), model, v)
    if sc:
        add(days_sub, d, v)
    add(projects, project, v)
    add(side, "subagents" if sc else "principal", v)
    add(total, "total", v)

top = dict(sorted(projects.items(), key=lambda kv: -sum(kv[1][:4]))[:15])
print(json.dumps({
    "machine": machine, "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    "window": [start.isoformat(), today.isoformat()], "roots": roots, "files": files,
    "messages": len(best), "bad_lines": lines_bad,
    "earliest_in_recent_files": earliest.isoformat() if earliest else None,
    "oldest_transcript_mtime": datetime.fromtimestamp(oldest_file).date().isoformat() if oldest_file else None,
    "fields": ["input", "output", "cache_creation", "cache_read", "messages"],
    "total": total.get("total"), "by_kind": side, "days": dict(sorted(days.items())), "days_sub": dict(sorted(days_sub.items())), "top_projects": top,
}, separators=(",", ":")))
