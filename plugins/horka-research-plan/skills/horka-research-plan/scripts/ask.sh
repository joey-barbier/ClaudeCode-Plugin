#!/usr/bin/env bash
# Delegates a read-only question to a cheaper model, without a turn of the parent agent.
# Usage: ask.sh <cheapest|generalist> <folder> "<precise question and answer format>"
# Models: ASK_CHEAPEST_MODEL and ASK_GENERALIST_MODEL override the defaults below.
# The call can only read (Read, Glob, Grep): no shell, no write, no web. Verify any answer whose exactness matters.
# BOARD_DIR set: one line per call is appended to $BOARD_DIR/asks.jsonl (model, tokens, turns, cost) for the run board.
set -euo pipefail
[ $# -eq 3 ] || { echo 'usage: ask.sh <cheapest|generalist> <folder> "<question>"' >&2; exit 2; }
case "$1" in
  cheapest|haiku) MODEL="${ASK_CHEAPEST_MODEL:-claude-haiku-5-5}" ;;
  generalist|sonnet) MODEL="${ASK_GENERALIST_MODEL:-claude-sonnet-5-5}" ;;
  *) echo "ask.sh: tier must be cheapest or generalist" >&2; exit 2 ;;
esac
cd "$2"
timeout "${ASK_TIMEOUT:-300}" claude -p "$3" --model "$MODEL" --tools Read,Glob,Grep --permission-mode default \
  --output-format json < /dev/null \
  | python3 -c '
import json, sys
d = json.load(sys.stdin)
print(d.get("result", ""))
print("[ask] %s · %.4f $" % (sys.argv[1], d.get("total_cost_usd") or 0), file=sys.stderr)
board = sys.argv[2]
if board:
    import datetime, os
    with open(os.path.join(board, "asks.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps({"t": datetime.datetime.now(datetime.timezone.utc).isoformat(), "model": sys.argv[1],
                            "usage": d.get("usage") or {}, "turns": d.get("num_turns"), "cost_usd": d.get("total_cost_usd")}) + "\n")
sys.exit(1 if d.get("is_error") else 0)' "$MODEL" "${BOARD_DIR:-}"
