#!/usr/bin/env python3
"""Update one task of graph.json, then rebuild the board.

Usage: python3 -I set.py <board-dir> <TASK_ID> <status> [agent_id ...] [key=value ...]
Status: ready | running | done | waiting | user | failed | interrupted
A bare word is an agent id (appended to the task); key=value sets a field (model=Sonnet, note=...).
"""
import json
import os
import subprocess
import sys

STATUSES = {'ready', 'running', 'done', 'waiting', 'user', 'failed', 'interrupted'}

if len(sys.argv) < 4:
    sys.exit(__doc__)
board, tid, status = sys.argv[1], sys.argv[2], sys.argv[3]
if status not in STATUSES:
    sys.exit('set.py: unknown status %r (one of %s)' % (status, ', '.join(sorted(STATUSES))))
path = os.path.join(board, 'graph.json')
g = json.load(open(path, encoding='utf-8'))
node = next((n for n in g['nodes'] if n['id'] == tid), None)
if node is None:
    sys.exit('set.py: no task %r in %s' % (tid, path))
node['status'] = status
for arg in sys.argv[4:]:
    if '=' in arg:
        k, v = arg.split('=', 1)
        node[k] = v
    elif arg not in node.setdefault('agents', []):
        node['agents'].append(arg)
tmp = path + '.tmp'
json.dump(g, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
os.replace(tmp, path)

# Which tasks can start now: every dependency done, not started yet.
by = {n['id']: n for n in g['nodes']}
ready = [n['id'] for n in g['nodes'] if n['status'] in ('ready', 'waiting')
         and all(by[d]['status'] == 'done' for d in n.get('deps', []))]
print('ok %s -> %s · can start now: %s' % (tid, status, ' '.join(ready) or 'none'), flush=True)
subprocess.run([sys.executable, '-I', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build.py'), board], check=False)
