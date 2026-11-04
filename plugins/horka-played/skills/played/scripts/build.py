#!/usr/bin/env python3
# Builds the /played page (doc-style) from one or more JSON files produced by usage.py.
# Daily numbers are embedded in the page: the period is picked in the browser.
# Usage: python3 build.py out.html machine1.json [machine2.json ...]
import base64, html, json, os, sys
from datetime import date, datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "..", "assets")
COLORS = ["#AE7AFF", "#87CEEB", "#FF8ACD", "#FFD24D", "#7AE582", "#FF9F6B"]  # doc-style palette

out_path, paths = sys.argv[1], sys.argv[2:]
if not paths:
    sys.exit("usage: build.py out.html machine1.json [machine2.json ...]")
src = {}
for p in paths:
    d = json.load(open(p))
    src[d["machine"]] = d
MACHINES = [(k, d.get("label") or k, COLORS[i % len(COLORS)]) for i, (k, d) in enumerate(src.items())]

# Window: the one of the most recent measurement (an older measurement does not widen it).
ref = max(src.values(), key=lambda d: d["window"][1])
start, end = date.fromisoformat(ref["window"][0]), date.fromisoformat(ref["window"][1])
days = [(start + timedelta(i)).isoformat() for i in range((end - start).days + 1)]

def z(): return [0, 0, 0, 0, 0]
def addv(a, v):
    for i in range(5): a[i] += v[i]
s4 = lambda v: v[0] + v[1] + v[2] + v[3]
def fr(n): return f"{n:,}".replace(",", " ")
def pct(a, b): return (f"{100*a/b:.1f}".replace(".", ",") + " %") if b else "–"
MOIS = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]
def dfr(iso, year=False):
    d = date.fromisoformat(iso)
    return f"{d.day} {MOIS[d.month-1]}" + (f" {d.year}" if year else "")
inwin = lambda day: start.isoformat() <= day <= end.isoformat()

data = {
    "days": days,
    "machines": [{"key": k, "label": lab, "color": col, "measured": True} for k, lab, col in MACHINES],
    "series": {k: {day: m for day, m in src[k]["days"].items() if inwin(day)} for k, _, _ in MACHINES},
    # Subagents per day: only for measurements that carry this detail.
    "sub": {k: {day: v for day, v in src[k]["days_sub"].items() if inwin(day)}
            for k, _, _ in MACHINES if "days_sub" in src[k]},
}

def proj_rows(d):
    merged = {}
    for name, v in d["top_projects"].items():
        if "reviewme-pr-" in name: n = "reviewme : relectures de PR (dossiers temporaires)"
        elif name.startswith(("-private-", "-tmp-", "-var-")): n = "dossiers temporaires (scratchpads)"
        else: n = name
        addv(merged.setdefault(n, z()), v)
    home = "-" + os.path.expanduser("~").strip("/").replace("/", "-")
    r = ""
    for name, v in sorted(merged.items(), key=lambda kv: -s4(kv[1]))[:8]:
        n = name
        for root in d.get("roots", []):
            pre = "-" + os.path.dirname(root.rstrip("/")).replace("/.claude", "").strip("/").replace("/", "-")
            if n.startswith(pre + "-"): n = n[len(pre) + 1:]; break
            if n == pre: n = "~ (dossier personnel)"; break
        if n == home: n = "~ (dossier personnel)"
        r += f'<tr><td><code>{html.escape(n)}</code></td><td class="num">{fr(s4(v))}</td><td class="num">{fr(v[1])}</td><td class="num">{fr(v[4])}</td></tr>'
    return r

def kind_line(d):
    sub = d["by_kind"].get("subagents", z()); pri = d["by_kind"].get("principal", z())
    return pct(s4(sub), s4(sub) + s4(pri))

cols = ""
for k, lab, _ in MACHINES:
    d = src[k]
    cols += (f'    <div class="col"><h3>{html.escape(lab)} · {len(days)} jours <span class="chip c-mut">sous-agents {kind_line(d)}</span></h3>\n'
             f'      <div class="card twrap"><table><thead><tr><th>Dossier</th><th class="r">Total</th><th class="r">Sortie</th><th class="r">Rép.</th></tr></thead><tbody>{proj_rows(d)}</tbody></table></div></div>\n')

src_rows = ""
for k, lab, _ in MACHINES:
    d = src[k]
    oldest = dfr(d["oldest_transcript_mtime"], True) if d.get("oldest_transcript_mtime") else "–"
    src_rows += (f'<tr><td>{html.escape(lab)}</td><td><code>{html.escape(", ".join(d["roots"]))}</code></td><td class="num">{fr(d["files"])}</td>'
                 f'<td>{oldest}</td><td>{html.escape(d["generated_at"].replace("T", " ")[:16])}</td></tr>')

labels = [lab for _, lab, _ in MACHINES]
# A measurement taken more than 6 hours before the most recent one leaves its later hours empty: say so.
newest = max(datetime.fromisoformat(d["generated_at"]) for d in src.values())
stale = [f'{lab} (mesuré le {dfr(src[k]["generated_at"][:10])})' for k, lab, _ in MACHINES
         if (newest - datetime.fromisoformat(src[k]["generated_at"])).total_seconds() > 6 * 3600]
n = len(MACHINES)
page = open(os.path.join(ASSETS, "template.html")).read()
for key, val in {
    "DATA": json.dumps(data, separators=(",", ":")).replace("</", "<\\/"),
    "EYEBROW": html.escape(" + ".join(labels)),
    "NMACH": "1 machine" if n == 1 else f"{n} machines",
    "MEASURED": html.escape(" et ".join(labels)),
    "MISSING": (" Mesure plus ancienne, jours suivants vides : " + ", ".join(stale) + ".") if stale else "",
    "FENETRE": f"du {dfr(days[0], True)} au {dfr(days[-1], True)}",
    "NBJ": str(len(days)),
    "POULPI": "data:image/png;base64," + base64.b64encode(open(os.path.join(ASSETS, "poulpi.png"), "rb").read()).decode(),
    "PROJ_COLS": cols.rstrip("\n"),
    "SRC_ROWS": src_rows,
}.items():
    page = page.replace("{{" + key + "}}", val)
open(out_path, "w").write(page)
print(out_path)
