#!/usr/bin/env python3
"""Progress board of a multi-agent run: python3 -I build.py <board-dir> [--session <main transcript .jsonl>]

Reads <board-dir>/graph.json (the task graph kept by the orchestrator), the session transcripts
(tokens per agent and per model, read from message.usage) and <board-dir>/asks.jsonl (direct calls
made through scripts/ask.sh). Writes <board-dir>/board.html. Read-only on everything else.
"""
import collections
import datetime
import glob
import html
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KEYS = ('input_tokens', 'output_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens')
E = html.escape

# Status key -> (css class, label key). French keys are accepted for older graphs.
ALIASES = {'fait': 'done', 'en-cours': 'running', 'pret': 'ready', 'attente': 'waiting', 'horka': 'user',
           'echec': 'failed', 'coupe': 'interrupted'}
ST = {'done': 'ok', 'running': 'run', 'ready': 'todo', 'waiting': 'todo', 'user': 'you', 'failed': 'ko', 'interrupted': 'ko'}

L = {
    'en': dict(title='Run board', updated='Updated', tok_note='Tokens read from the transcripts, cache reads included.',
               essentials='The essentials', waiting_on='Waiting on {who}', decisions='Decisions taken', probes='Real probes: what we found',
               k_tasks='tasks done', k_run='tasks running', k_agents='agents launched', k_asks='direct calls to a cheaper model',
               k_tok='tokens in all, {cr} of them cache reads', k_out='output tokens',
               k_time='elapsed, for {cum} of agent work ({par})', u_day='d', graph='Task graph',
               graph_note='A task starts as soon as the tasks it depends on are done; the others do not wait for it. A solid arrow comes from a finished task.',
               tasks='Tasks and agents', by_model='Tokens by model',
               h=['Id', 'Task', 'Role', 'Model', 'Effort', 'State', 'Agents', 'Duration', 'Turns', 'Tokens', 'Output'],
               hm=['Model', 'Agents', 'Turns', 'Tokens in all', 'Cache reads', 'Input and cache writes', 'Output'],
               model_note='The top tier orchestrates and judges, the expert tier writes and reviews, the generalist does checked mechanical work, the cheapest tier does wide lookups. Dollars are not measured here.',
               done='Done', running='Running', ready='Can start', waiting='Waits for its dependencies', user='Waits for {who}',
               failed='To redo', interrupted='Interrupted, to resume', notyet='Not started', you='you',
               toc='Contents', n_ess='Essentials', n_kpi='Figures and time', n_wait='Waits for {who}', n_dec='Decisions',
               n_probes='Probes', n_graph='Graph', n_tasks='Tokens per task', n_models='Tokens per model',
               tools='Graph controls', z_in='Zoom in', z_out='Zoom out', z_fit='Fit to window', z_full='Full screen',
               z_exit='Exit full screen', z_hint='Drag to move · Ctrl + wheel or pinch to zoom · Esc to leave',
               graph_hint='Click a task to light the whole chain that leads to it, thicker for its direct dependencies, and what depends on it.',
               p_label='Task detail', p_close='Close', p_role='Role', p_model='Model', p_effort='effort',
               p_agents='Agents', p_dur='Duration', p_turns='Turns', p_tok='Tokens', p_out='output',
               p_deps='What it took to get here', p_kids='Depends on it', p_none='None',
               p_up_n='{n} upstream, {d}', p_down_n='{d}, {n} in the whole descent',
               p_task='task|tasks', p_dir='direct|direct', p_direct='direct', p_all='Show the whole descent ({n})',
               p_less='Fold the descent ({n})', p_nolane='No lane', p_row='Its row in the task table'),
    'fr': dict(title='Suivi du chantier', updated='Mis à jour le', tok_note='Jetons lus dans les transcripts, lectures de cache comprises.',
               essentials="L'essentiel", waiting_on='En attente de {who}', decisions='Décisions prises', probes="Sondes réelles : ce qu'on a relevé",
               k_tasks='tâches faites', k_run='tâches en cours', k_agents='agents lancés', k_asks='appels directs à un modèle moins cher',
               k_tok='jetons au total, dont {cr} de lectures de cache', k_out='jetons de sortie',
               k_time="de temps écoulé, pour {cum} de travail d'agents ({par})", u_day='j', graph='Graphe des tâches',
               graph_note="Une tâche part dès que celles dont elle dépend sont faites ; les autres ne l'attendent pas. Une flèche pleine vient d'une tâche terminée.",
               tasks='Tâches et agents', by_model='Jetons par modèle',
               h=['Id', 'Tâche', 'Rôle', 'Modèle', 'Effort', 'État', 'Agents', 'Durée', 'Tours', 'Jetons', 'Sortie'],
               hm=['Modèle', 'Agents', 'Tours', 'Jetons au total', 'Lectures de cache', 'Entrée et écriture de cache', 'Sortie'],
               model_note="Le palier du haut orchestre et juge, le palier expert écrit et relit, le généraliste fait le mécanique vérifiable, le moins cher fait les recherches larges. Le coût en dollars n'est pas mesuré ici.",
               done='Fait', running='En cours', ready='Peut partir', waiting='Attend ses dépendances', user='Attend {who}',
               failed='À refaire', interrupted='Coupée, à reprendre', notyet='Pas encore lancée', you='toi',
               toc='Sommaire', n_ess="L'essentiel", n_kpi='Chiffres et temps', n_wait='Attend {who}', n_dec='Décisions',
               n_probes='Sondes', n_graph='Graphe', n_tasks='Jetons par tâche', n_models='Jetons par modèle',
               tools='Commandes du graphe', z_in='Zoom avant', z_out='Zoom arrière', z_fit='Ajuster à la fenêtre', z_full='Plein écran',
               z_exit='Quitter le plein écran', z_hint='Glisser pour déplacer · Ctrl + molette ou pincement pour zoomer · Échap pour sortir',
               graph_hint="Touche une tâche : toute la chaîne qui y mène s'allume, en trait épais pour ses dépendances directes, avec ce qui dépend d'elle.",
               p_label="Détail d'une tâche", p_close='Fermer', p_role='Rôle', p_model='Modèle', p_effort='effort',
               p_agents='Agents', p_dur='Durée', p_turns='Tours', p_tok='Jetons', p_out='de sortie',
               p_deps="Ce qu'il a fallu pour y arriver", p_kids="Ce qui dépend d'elle", p_none='Aucune',
               p_up_n='{n} en amont, dont {d}', p_down_n='{d}, {n} dans toute la descendance',
               p_task='tâche|tâches', p_dir='directe|directes', p_direct='directe', p_all='Voir toute la descendance ({n})',
               p_less='Replier la descendance ({n})', p_nolane='Sans couloir', p_row='Sa ligne dans le tableau des tâches'),
}


def ts(s):
    return datetime.datetime.fromisoformat(s.replace('Z', '+00:00'))


def usage(path):
    """Sum message.usage per assistant message id (last chunk wins), per model."""
    seen, t0, t1 = {}, None, None
    for line in open(path, encoding='utf-8', errors='replace'):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get('timestamp'):
            t0 = t0 or d['timestamp']
            t1 = d['timestamp']
        m = d.get('message') or {}
        u = m.get('usage')
        if d.get('type') == 'assistant' and u and m.get('id'):
            seen[m['id']] = (m.get('model') or '?', {k: u.get(k) or 0 for k in KEYS})
    by = collections.defaultdict(collections.Counter)
    for model, u in seen.values():
        by[model].update(u)
        by[model]['turns'] += 1
    return by, t0, t1


def short(model):
    for k in ('fable', 'opus', 'sonnet', 'haiku'):
        if k in model:
            return k.capitalize()
    return model


def fmt(n):
    if n >= 1e6:
        return '%.1f M' % (n / 1e6)
    if n >= 1e3:
        return '%d k' % round(n / 1e3)
    return str(n)


def span(minutes, day='d'):
    """A duration given in minutes, as text: minutes under an hour ("45 min"), hours and minutes under a day ("2 h 15"),
    days and hours beyond ("2 d 16 h"). Non-breaking spaces, so that a line never cuts a duration in two."""
    m = max(0, int(round(minutes)))
    if m < 60:
        s = '%d min' % m
    elif m < 1440:
        s = ('%d h %02d' % divmod(m, 60)) if m % 60 else '%d h' % (m // 60)
    else:
        d, h = divmod(int(round(m / 60)), 24)
        s = ('%d %s %d h' % (d, day, h)) if h else '%d %s' % (d, day)
    return s.replace(' ', '\u00a0')


def allin(c):
    return sum(c[k] for k in KEYS)


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    board = args[0]
    G = json.load(open(os.path.join(board, 'graph.json'), encoding='utf-8'))
    lab = L.get(G.get('lang', 'en'), L['en'])
    who = G.get('user') or lab['you']

    def label(status):
        return lab.get(status, status).format(who=who)
    tz = datetime.timezone(datetime.timedelta(hours=float(G.get('utc_offset', 0))))
    start = ts(G['start'])
    now = datetime.datetime.now(datetime.timezone.utc)

    # Main transcript: --session, then graph.json "session", then the newest transcript touched since the start.
    session = args[args.index('--session') + 1] if '--session' in args else G.get('session')
    if not session:
        cands = [p for p in glob.glob(os.path.expanduser('~/.claude/projects/*/*.jsonl'))
                 if os.path.getmtime(p) >= start.timestamp()]
        session = max(cands, key=os.path.getmtime) if cands else None

    agents, orch = {}, {}
    if session and os.path.exists(session):
        orch, _, _ = usage(session)
        for p in glob.glob(session[:-6] + '/subagents/**/agent-*.jsonl', recursive=True):
            by, t0, t1 = usage(p)
            tot = collections.Counter()
            for c in by.values():
                tot.update(c)
            agents[os.path.basename(p)[6:-6]] = dict(by=by, tot=tot, t0=t0, t1=t1)

    models = collections.defaultdict(collections.Counter)
    for m, c in orch.items():
        models[short(m)].update(c)
    for a in agents.values():
        for m, c in a['by'].items():
            models[short(m)].update(c)
        if a['by']:
            models[short(max(a['by'], key=lambda m: allin(a['by'][m])))]['agents'] += 1
    n_asks = 0
    asks_path = os.path.join(board, 'asks.jsonl')
    if os.path.exists(asks_path):
        for line in open(asks_path, encoding='utf-8'):
            try:
                d = json.loads(line)
            except ValueError:
                continue
            n_asks += 1
            c = collections.Counter({k: (d.get('usage') or {}).get(k) or 0 for k in KEYS})
            c['turns'] += d.get('turns') or 1
            models[short(d.get('model', '?'))].update(c)
    if orch:
        models[short(max(orch, key=lambda m: allin(orch[m])))]['agents'] += 1

    elapsed = (now - start).total_seconds() / 60
    cum = sum((ts(a['t1']) - ts(a['t0'])).total_seconds() for a in agents.values() if a['t0']) / 60
    tot_all = sum(allin(c) for c in models.values())
    tot_out = sum(c['output_tokens'] for c in models.values())
    tot_cr = sum(c['cache_read_input_tokens'] for c in models.values())

    # ── graph layout: lanes as columns when graph.json has "lanes", else one row per depth ──
    N = {n['id']: n for n in G['nodes']}
    for n in G['nodes']:
        n['status'] = ALIASES.get(n['status'], n['status'])
    depth = {}

    def dep(i):
        if i not in depth:
            depth[i] = 0   # placeholder first: a cycle in faulty data ends here instead of recursing forever
            depth[i] = 1 + max([dep(d) for d in N[i].get('deps', []) if d in N], default=-1)
        return depth[i]

    for i in N:
        dep(i)
    BW, BH, GX, GY, PAD = 152, 66, 14, 30, 14
    nrows = max(depth.values()) + 1
    pos, lane_boxes = {}, []
    lanes = [l if isinstance(l, list) else [l, l] for l in G.get('lanes', [])]
    lane_names = {k: v for k, v in lanes}
    if lanes:
        # One column per lane, sub-columns when a lane has several tasks at one depth; a lane-less
        # root (the framing task) is centred on top. Lanes advance at their own pace, which is the point.
        HEAD, LG = 28, 24
        keys = [k for k, _ in lanes]
        if any(n.get('lane') not in keys and depth[n['id']] > 0 for n in G['nodes']):
            lanes.append(['_', '—'])
            keys.append('_')
        cells = collections.defaultdict(lambda: collections.defaultdict(list))
        top = []
        for n in G['nodes']:
            k = n.get('lane') if n.get('lane') in keys else ('_' if depth[n['id']] > 0 else None)
            (cells[k][depth[n['id']]] if k else top).append(n['id'])
        lw = {k: max([len(v) for v in cells[k].values()] or [1]) for k in keys}
        lx, x = {}, PAD
        for k in keys:
            lx[k] = x
            x += lw[k] * BW + (lw[k] - 1) * GX + LG
        W = x - LG + PAD
        # Lanes that start at depth 0 would share the top row with the centred root: push them one row down.
        shift = 1 if top and any(0 in cells[k] for k in keys) else 0
        H = PAD * 2 + HEAD + (nrows + shift) * BH + (nrows + shift - 1) * GY
        for j, i in enumerate(top):
            pos[i] = (W / 2 - BW / 2 + (j - (len(top) - 1) / 2) * (BW + GX), PAD + HEAD)
        for k, lname in lanes:
            w = lw[k] * BW + (lw[k] - 1) * GX
            lane_boxes.append((lx[k] - 7, PAD, w + 14, H - PAD * 2, lx[k] + w / 2, lname))
            for d, ids in cells[k].items():
                off = (lw[k] - len(ids)) * (BW + GX) / 2
                for j, i in enumerate(ids):
                    pos[i] = (lx[k] + off + j * (BW + GX), PAD + HEAD + (d + shift) * (BH + GY))
    else:
        # One row per depth, top to bottom.
        rows = collections.defaultdict(list)
        for n in G['nodes']:
            rows[depth[n['id']]].append(n['id'])
        width = max(len(v) for v in rows.values())
        W = PAD * 2 + width * BW + (width - 1) * GX
        H = PAD * 2 + nrows * BH + (nrows - 1) * GY
        for r, ids in rows.items():
            off = (width - len(ids)) * (BW + GX) / 2
            for k, i in enumerate(ids):
                pos[i] = (PAD + off + k * (BW + GX), PAD + r * (BH + GY))

    def wrap(t, n=22):
        out, cur = [], ''
        for w in t.split():
            if len(cur) + len(w) + 1 > n and cur:
                out.append(cur)
                cur = w
            else:
                cur = (cur + ' ' + w).strip()
        out.append(cur)
        if len(out) > 2:
            out = [out[0], out[1][:n - 1].rstrip() + '…']
        return out

    # Natural size in width/height: without script the graph scrolls in its box; the script turns
    # the box into a pan and zoom view by moving the viewBox.
    svg = ['<svg id="graph" viewBox="0 0 %d %d" width="%d" height="%d" data-w="%d" data-h="%d" aria-label="%s">'
           % (W, H, W, H, W, H, E(lab['graph'])),
           '<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
           '<path d="M0 0L10 5L0 10z" class="arh"/></marker></defs>']
    for x, y, w, h, cx, lname in lane_boxes:
        svg.append('<rect class="lane" x="%.0f" y="%.0f" width="%.0f" height="%.0f" rx="4"/>'
                   '<text class="lane-t" x="%.0f" y="%.0f" text-anchor="middle">%s</text>' % (x, y, w, h, cx, y + 18, E(lname)))
    for n in G['nodes']:
        x2, y2 = pos[n['id']]
        for d in n.get('deps', []):
            x1, y1 = pos[d]
            a, b, c, e = x1 + BW / 2, y1 + BH, x2 + BW / 2, y2 - 3
            my = (b + e) / 2
            cls = 'edge done' if N[d]['status'] == 'done' else 'edge'
            svg.append('<path class="%s" data-f="%s" data-t="%s" d="M%.0f %.0fC%.0f %.0f %.0f %.0f %.0f %.0f" marker-end="url(#ar)"/>'
                       % (cls, E(d), E(n['id']), a, b, a, my, c, my, c, e))
    for n in G['nodes']:
        x, y = pos[n['id']]
        k = ST.get(n['status'], 'todo')
        # A link to the task's table row: the card still leads to its detail when script is off.
        svg.append('<a class="node %s" href="#t-%s" tabindex="0" data-id="%s" data-x="%.0f" data-y="%.0f" aria-label="%s">'
                   '<title>%s</title><rect class="sh" x="%.0f" y="%.0f" width="%d" height="%d" rx="4"/>'
                   '<rect class="bx" x="%.0f" y="%.0f" width="%d" height="%d" rx="4"/>' % (
                       k, E(n['id']), E(n['id']), x, y, E('%s · %s · %s' % (n['id'], n['title'], label(n['status']))),
                       E(n['title']), x + 4, y + 4, BW, BH, x, y, BW, BH))
        svg.append('<text class="nid" x="%.0f" y="%.0f">%s</text>' % (x + 9, y + 16, E(n['id'])))
        if n.get('model'):
            svg.append('<text class="nwho" x="%.0f" y="%.0f" text-anchor="end">%s</text>' % (x + BW - 9, y + 16, E(n['model'])))
        for j, line in enumerate(wrap(n['title'])):
            svg.append('<text class="ntt" x="%.0f" y="%.0f">%s</text>' % (x + 9, y + 35 + j * 15, E(line)))
        svg.append('</a>')
    svg.append('</svg>')

    def chip(k, t):
        return '<span class="chip %s">%s</span>' % (k, E(t))

    trs, data = [], []
    for n in G['nodes']:
        tot, t0, t1 = collections.Counter(), None, None
        for aid in n.get('agents', []):
            a = agents.get(aid)
            if not a or not a['t0']:
                continue
            tot.update(a['tot'])
            t0 = min(filter(None, [t0, a['t0']]))
            t1 = max(filter(None, [t1, a['t1']]))
        dur = span(max(1, (ts(t1) - ts(t0)).total_seconds() / 60), lab['u_day']) if t0 else '—'
        trs.append('<tr id="t-%s"><td class="mono"><a href="#graph-section" data-go="%s">%s</a></td><td>%s%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td class="num">%s</td>'
                   '<td class="num">%s</td><td class="num">%s</td><td class="num">%s</td><td class="num">%s</td></tr>' % (
                       E(n['id']), E(n['id']), E(n['id']), E(n['title']), ('<div class="note">%s</div>' % E(n['note'])) if n.get('note') else '',
                       E(n.get('role', '')), E(n.get('model', '—')), E(n.get('effort', '—')),
                       chip(ST.get(n['status'], 'todo'), label(n['status'])),
                       len(n.get('agents', [])) or '—', dur, tot['turns'] or '—',
                       fmt(allin(tot)) if tot else '—', fmt(tot['output_tokens']) if tot else '—'))
        # What the detail panel shows; plain text, set with textContent by the page script.
        data.append(dict(id=n['id'], t=n['title'], k=ST.get(n['status'], 'todo'), s=label(n['status']),
                         l=lane_names.get(n.get('lane'), ''), r=n.get('role', ''), m=n.get('model', ''), e=n.get('effort', ''),
                         n=n.get('note', ''), a=n.get('agents', []), d=n.get('deps', []), h=depth[n['id']], du=dur if t0 else '',
                         tu=tot['turns'] or '', to=fmt(allin(tot)) if tot else '', o=fmt(tot['output_tokens']) if tot else ''))
    mrows = []
    for m in sorted(models, key=lambda m: -allin(models[m])):
        c = models[m]
        mrows.append('<tr><td><b>%s</b></td><td class="num">%s</td><td class="num">%s</td><td class="num">%s</td><td class="num">%s</td>'
                     '<td class="num">%s</td><td class="num">%s</td></tr>' % (
                         E(m), c['agents'], c['turns'], fmt(allin(c)), fmt(c['cache_read_input_tokens']),
                         fmt(c['cache_creation_input_tokens'] + c['input_tokens']), fmt(c['output_tokens'])))
    count = collections.Counter(n['status'] for n in G['nodes'])

    def lis(*keys):
        for k in keys:
            if G.get(k):
                return ''.join('<li>%s</li>' % x for x in G[k])  # orchestrator-written HTML, trusted
        return '<li>—</li>'

    page = open(os.path.join(HERE, 'page.tpl.html'), encoding='utf-8').read()
    rep = {
        '{{TITLE}}': E(G.get('title', lab['title'])), '{{STAMP}}': '%s %s' % (lab['updated'], now.astimezone(tz).strftime('%d/%m %H:%M')),
        '{{ESSENTIALS}}': lis('essentials', 'essentiel'), '{{WAITING}}': lis('waiting_on_user', 'attente_horka'),
        '{{DECISIONS}}': lis('decisions'), '{{PROBES}}': lis('probes', 'sondes'),
        '{{K_TASKS}}': '%d / %d' % (count['done'], len(G['nodes'])), '{{K_RUN}}': str(count['running']),
        '{{K_AGENTS}}': str(len(agents)), '{{K_ASKS}}': str(n_asks), '{{K_TOK}}': fmt(tot_all), '{{K_OUT}}': fmt(tot_out),
        '{{K_ELAPSED}}': span(elapsed, lab['u_day']),
        '{{SVG}}': '\n'.join(svg), '{{ROWS}}': '\n'.join(trs), '{{MROWS}}': '\n'.join(mrows),
        '{{CHIPS}}': ''.join(chip(ST[s], label(s)) for s in ('done', 'running', 'waiting', 'user', 'failed')),
    }
    for k in ('tok_note', 'essentials', 'decisions', 'probes', 'k_tasks', 'k_run', 'k_agents', 'k_asks', 'k_out',
              'graph', 'graph_note', 'tasks', 'by_model', 'model_note'):
        rep['{{L_%s}}' % k.upper()] = E(lab[k])
    rep['{{L_WAITING_ON}}'] = E(lab['waiting_on'].format(who=who))
    rep['{{L_K_TOK}}'] = E(lab['k_tok'].format(cr='%d %%' % round(100 * tot_cr / tot_all) if tot_all else '—'))
    rep['{{L_K_TIME}}'] = E(lab['k_time'].format(cum=span(cum, lab['u_day']), par=('×%.1f' % (cum / elapsed)) if elapsed else '—'))
    rep['{{L_H}}'] = ''.join('<th%s>%s</th>' % (' class="num"' if i >= 6 else '', E(h)) for i, h in enumerate(lab['h']))
    rep['{{L_HM}}'] = ''.join('<th%s>%s</th>' % (' class="num"' if i >= 1 else '', E(h)) for i, h in enumerate(lab['hm']))
    for k in ('toc', 'tools', 'z_in', 'z_out', 'z_fit', 'z_full', 'z_hint', 'graph_hint', 'p_label', 'p_close'):
        rep['{{L_%s}}' % k.upper()] = E(lab[k])
    rep['{{LANG}}'] = E(G.get('lang', 'en'))
    nav = [('essentials', 'n_ess'), ('figures', 'n_kpi'), ('graph-section', 'n_graph'), ('waiting', 'n_wait'), ('decisions', 'n_dec'),
           ('probes', 'n_probes'), ('models', 'n_models'), ('tasks', 'n_tasks')]   # page order
    rep['{{NAV}}'] = ''.join('<li><a href="#%s">%s</a></li>' % (a, E(lab[k].format(who=who))) for a, k in nav)
    # Data of the detail panel and its labels. "</" is escaped so that no note can close the script element.
    ui = {k: lab[k].replace('{who}', who) for k in lab if k[:2] in ('p_', 'z_')}
    rep['{{DATA}}'] = json.dumps({'nodes': data, 'lab': ui}, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    for k, v in rep.items():
        page = page.replace(k, v)
    out = os.path.join(board, 'board.html')
    open(out, 'w', encoding='utf-8').write(page)
    print('board', out, '· agents', len(agents), '· tokens', fmt(tot_all), '· session', session or 'none found')


if __name__ == '__main__':
    main()
