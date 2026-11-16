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
               k_time='elapsed, for {cum} of agent work ({par})', graph='Task graph',
               graph_note='A task starts as soon as the tasks it depends on are done; the others do not wait for it. A solid arrow comes from a finished task.',
               tasks='Tasks and agents', by_model='Tokens by model',
               h=['Id', 'Task', 'Role', 'Model', 'Effort', 'State', 'Agents', 'Duration', 'Turns', 'Tokens', 'Output'],
               hm=['Model', 'Agents', 'Turns', 'Tokens in all', 'Cache reads', 'Input and cache writes', 'Output'],
               model_note='The top tier orchestrates and judges, the expert tier writes and reviews, the generalist does checked mechanical work, the cheapest tier does wide lookups. Dollars are not measured here.',
               done='Done', running='Running', ready='Can start', waiting='Waits for its dependencies', user='Waits for {who}',
               failed='To redo', interrupted='Interrupted, to resume', notyet='Not started', you='you'),
    'fr': dict(title='Suivi du chantier', updated='Mis à jour le', tok_note='Jetons lus dans les transcripts, lectures de cache comprises.',
               essentials="L'essentiel", waiting_on='En attente de {who}', decisions='Décisions prises', probes="Sondes réelles : ce qu'on a relevé",
               k_tasks='tâches faites', k_run='tâches en cours', k_agents='agents lancés', k_asks='appels directs à un modèle moins cher',
               k_tok='jetons au total, dont {cr} de lectures de cache', k_out='jetons de sortie',
               k_time="écoulées, pour {cum} de travail d'agents ({par})", graph='Graphe des tâches',
               graph_note="Une tâche part dès que celles dont elle dépend sont faites ; les autres ne l'attendent pas. Une flèche pleine vient d'une tâche terminée.",
               tasks='Tâches et agents', by_model='Jetons par modèle',
               h=['Id', 'Tâche', 'Rôle', 'Modèle', 'Effort', 'État', 'Agents', 'Durée', 'Tours', 'Jetons', 'Sortie'],
               hm=['Modèle', 'Agents', 'Tours', 'Jetons au total', 'Lectures de cache', 'Entrée et écriture de cache', 'Sortie'],
               model_note="Le palier du haut orchestre et juge, le palier expert écrit et relit, le généraliste fait le mécanique vérifiable, le moins cher fait les recherches larges. Le coût en dollars n'est pas mesuré ici.",
               done='Fait', running='En cours', ready='Peut partir', waiting='Attend ses dépendances', user='Attend {who}',
               failed='À refaire', interrupted='Coupée, à reprendre', notyet='Pas encore lancée', you='toi'),
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

    # ── graph layout: one row per depth, top to bottom ──────────────────────
    N = {n['id']: n for n in G['nodes']}
    for n in G['nodes']:
        n['status'] = ALIASES.get(n['status'], n['status'])
    depth = {}

    def dep(i):
        if i not in depth:
            depth[i] = 1 + max([dep(d) for d in N[i].get('deps', [])], default=-1)
        return depth[i]

    for i in N:
        dep(i)
    rows = collections.defaultdict(list)
    for n in G['nodes']:
        rows[depth[n['id']]].append(n['id'])
    BW, BH, GX, GY, PAD = 152, 66, 14, 30, 14
    width = max(len(v) for v in rows.values())
    W = PAD * 2 + width * BW + (width - 1) * GX
    H = PAD * 2 + len(rows) * BH + (len(rows) - 1) * GY
    pos = {}
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

    svg = ['<svg viewBox="0 0 %d %d" width="%d" height="%d" role="img" aria-label="%s">' % (W, H, W, H, E(lab['graph'])),
           '<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
           '<path d="M0 0L10 5L0 10z" class="arh"/></marker></defs>']
    for n in G['nodes']:
        x2, y2 = pos[n['id']]
        for d in n.get('deps', []):
            x1, y1 = pos[d]
            a, b, c, e = x1 + BW / 2, y1 + BH, x2 + BW / 2, y2 - 3
            my = (b + e) / 2
            cls = 'edge done' if N[d]['status'] == 'done' else 'edge'
            svg.append('<path class="%s" d="M%.0f %.0fC%.0f %.0f %.0f %.0f %.0f %.0f" marker-end="url(#ar)"/>' % (cls, a, b, a, my, c, my, c, e))
    for n in G['nodes']:
        x, y = pos[n['id']]
        k = ST.get(n['status'], 'todo')
        svg.append('<g class="node %s"><title>%s</title><rect class="sh" x="%.0f" y="%.0f" width="%d" height="%d" rx="4"/>'
                   '<rect class="bx" x="%.0f" y="%.0f" width="%d" height="%d" rx="4"/>' % (k, E(n['title']), x + 4, y + 4, BW, BH, x, y, BW, BH))
        svg.append('<text class="nid" x="%.0f" y="%.0f">%s</text>' % (x + 9, y + 16, E(n['id'])))
        if n.get('model'):
            svg.append('<text class="nwho" x="%.0f" y="%.0f" text-anchor="end">%s</text>' % (x + BW - 9, y + 16, E(n['model'])))
        for j, line in enumerate(wrap(n['title'])):
            svg.append('<text class="ntt" x="%.0f" y="%.0f">%s</text>' % (x + 9, y + 35 + j * 15, E(line)))
        svg.append('</g>')
    svg.append('</svg>')

    def chip(k, t):
        return '<span class="chip %s">%s</span>' % (k, E(t))

    def label(status):
        return lab.get(status, status).format(who=who)

    trs = []
    for n in G['nodes']:
        tot, t0, t1 = collections.Counter(), None, None
        for aid in n.get('agents', []):
            a = agents.get(aid)
            if not a or not a['t0']:
                continue
            tot.update(a['tot'])
            t0 = min(filter(None, [t0, a['t0']]))
            t1 = max(filter(None, [t1, a['t1']]))
        dur = '%d min' % max(1, round((ts(t1) - ts(t0)).total_seconds() / 60)) if t0 else '—'
        trs.append('<tr><td class="mono">%s</td><td>%s%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td class="num">%s</td>'
                   '<td class="num">%s</td><td class="num">%s</td><td class="num">%s</td><td class="num">%s</td></tr>' % (
                       E(n['id']), E(n['title']), ('<div class="note">%s</div>' % E(n['note'])) if n.get('note') else '',
                       E(n.get('role', '')), E(n.get('model', '—')), E(n.get('effort', '—')),
                       chip(ST.get(n['status'], 'todo'), label(n['status'])),
                       len(n.get('agents', [])) or '—', dur, tot['turns'] or '—',
                       fmt(allin(tot)) if tot else '—', fmt(tot['output_tokens']) if tot else '—'))
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
        '{{K_ELAPSED}}': '%d min' % round(elapsed),
        '{{SVG}}': '\n'.join(svg), '{{ROWS}}': '\n'.join(trs), '{{MROWS}}': '\n'.join(mrows),
        '{{CHIPS}}': ''.join(chip(ST[s], label(s)) for s in ('done', 'running', 'waiting', 'user', 'failed')),
    }
    for k in ('tok_note', 'essentials', 'decisions', 'probes', 'k_tasks', 'k_run', 'k_agents', 'k_asks', 'k_out',
              'graph', 'graph_note', 'tasks', 'by_model', 'model_note'):
        rep['{{L_%s}}' % k.upper()] = E(lab[k])
    rep['{{L_WAITING_ON}}'] = E(lab['waiting_on'].format(who=who))
    rep['{{L_K_TOK}}'] = E(lab['k_tok'].format(cr='%d %%' % round(100 * tot_cr / tot_all) if tot_all else '—'))
    rep['{{L_K_TIME}}'] = E(lab['k_time'].format(cum='%d min' % round(cum), par=('×%.1f' % (cum / elapsed)) if elapsed else '—'))
    rep['{{L_H}}'] = ''.join('<th%s>%s</th>' % (' class="num"' if i >= 6 else '', E(h)) for i, h in enumerate(lab['h']))
    rep['{{L_HM}}'] = ''.join('<th%s>%s</th>' % (' class="num"' if i >= 1 else '', E(h)) for i, h in enumerate(lab['hm']))
    for k, v in rep.items():
        page = page.replace(k, v)
    out = os.path.join(board, 'board.html')
    open(out, 'w', encoding='utf-8').write(page)
    print('board', out, '· agents', len(agents), '· tokens', fmt(tot_all), '· session', session or 'none found')


if __name__ == '__main__':
    main()
