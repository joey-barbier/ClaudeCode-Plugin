#!/usr/bin/env python3
# Builds the /played page (doc-style) from one or more JSON files produced by usage.py.
# Daily numbers are embedded in the page: the period is picked in the browser.
# Usage: python3 build.py out.html machine1.json [machine2.json ...]
import base64, glob, html, json, os, sys
from datetime import date, datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "..", "assets")
COLORS = ["#AE7AFF", "#87CEEB", "#FF8ACD", "#FFD24D", "#7AE582", "#FF9F6B"]  # doc-style palette

sys.path.insert(0, HERE)
from usage import keep, summarize

out_path, args = sys.argv[1], sys.argv[2:]
if not args:
    sys.exit("usage: build.py out.html machine1.json [machine2.json | cloud_dir ...]")
# A folder stands for every *.json inside it (the cloud folder holds one file per session).
paths = []
for a in args:
    paths += sorted(glob.glob(os.path.join(a, "*.json"))) if os.path.isdir(a) else [a]
groups = {}
for p in paths:
    if os.path.abspath(p) == os.path.abspath(out_path):
        continue
    try:
        d = json.load(open(p))
    except (OSError, ValueError):
        print("ignoré (illisible) : " + p, file=sys.stderr); continue
    if "machine" in d and "days" in d:
        groups.setdefault(d["machine"], []).append(d)

def merge(ds):
    """Several files under one label: cloud sessions, deduplicated response by response."""
    if len(ds) == 1:
        return ds[0]
    if not all("responses" in d for d in ds):  # two measurements of one machine: the newest wins
        return max(ds, key=lambda d: d["generated_at"])
    best = {}
    for d in ds:
        for key, rec in d["responses"].items():
            keep(best, key, rec)
    m = {"machine": ds[0]["machine"], "label": ds[0].get("label"),
         "generated_at": max(d["generated_at"] for d in ds),
         "window": [min(d["window"][0] for d in ds), max(d["window"][1] for d in ds)],
         "roots": ["cloud : %d sessions" % len(ds)], "files": sum(d["files"] for d in ds),
         "oldest_transcript_mtime": min(d["oldest_transcript_mtime"] for d in ds)}
    m.update(summarize(best))
    return m

src = {k: merge(v) for k, v in groups.items()}
if not src:
    sys.exit("aucune mesure lisible")
CLOUD = "cloud" in src
MACHINES = [(k, d.get("label") or k, COLORS[i % len(COLORS)]) for i, (k, d) in enumerate(src.items())]

# Window: the one of the most recent measurement (an older measurement does not widen it).
ref = max(src.values(), key=lambda d: d["window"][1])
if len(src) > 1 and CLOUD:  # the cloud keeps 60 days: the machines' window frames the page
    ref = max((d for k, d in src.items() if k != "cloud"), key=lambda d: d["window"][1])
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
    "cloud": CLOUD,
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
    "CLOUD_NOTE": ("Les sessions cloud sont comptées à partir des relevés qu'elles déposent elles-mêmes, une ligne par réponse, sans doublon."
                   if CLOUD else "Les sessions cloud ne sont pas comptées : aucun relevé cloud fourni."),
    "CLOUD_BOX": ('<span class="chip c-ok">Cloud compté</span> Chaque session cloud dépose son relevé à la fin de chaque tour '
                  "(hook du plugin). Les réponses sont dédoublonnées entre les conteneurs d'une même session. "
                  "Seules les sessions qui ont tourné avec ce plugin depuis son installation sont comptées : le passé n'est pas reconstitué."
                  if CLOUD else
                  '<span class="chip c-ko">Cloud non mesuré</span> Aucun relevé cloud fourni. Les sessions cloud (Claude Code sur le web, '
                  "fils de projet claude.ai) tournent dans des conteneurs éphémères : avec ce plugin installé, elles déposent leur relevé "
                  "dans <code>/mnt/project-files/played/cloud/</code>. Copie ce dossier dans <code>~/.claude/played/cloud/</code> pour les compter ici."),
}.items():
    page = page.replace("{{" + key + "}}", val)
open(out_path, "w").write(page)
print(out_path)
