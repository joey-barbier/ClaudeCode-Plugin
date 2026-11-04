---
name: played
allowed-tools: Bash, Read
description: >
  /played for Claude Code, as in World of Warcraft: shows how many tokens the user burned.
  Measures the local Claude Code transcripts (30 days by default), merges the measurements of
  the user's other machines, and builds a doc-style HTML page: totals, per day, per machine,
  per model, subagent share, record day, a shareable card and a 9:16 story PNG.
  Invoke on "/played", "combien de tokens j'ai consommé", "ma conso Claude Code", "ma conso de tokens",
  "how many tokens did I use", "token usage", "token page", "page de conso".
  Do NOT use for API billing or costs in euros/dollars: the page counts tokens, not money.
---

# /played — token usage page

Arguments (all optional, any order): a machine label (default: the hostname, e.g. `MacBook`) and a number of days (default `30`). Examples: `/played`, `/played 7`, `/played MacBook 30`.

The scripts live in this skill's base directory: `scripts/usage.py`, `scripts/build.py`, `assets/template.html`, `assets/poulpi.png`. Data lives in `~/.claude/played/`.

## Steps

1. **Measure this machine** (read-only on the transcripts):
   ```bash
   mkdir -p ~/.claude/played
   python3 "<skill dir>/scripts/usage.py" "<label>" <days> > ~/.claude/played/"<label>".json
   ```
   If python3 is missing, say so and stop. Never edit the transcripts.

2. **Merge the other machines.** Every other `*.json` in `~/.claude/played/` is a measurement from another machine (the user ran `/played` there and copied the file here). Keep those measured in the last 30 days; list the ones you skip. Never fetch them yourself from another machine.

3. **Build and open the page:**
   ```bash
   python3 "<skill dir>/scripts/build.py" ~/.claude/played/played.html ~/.claude/played/"<label>".json [other files…]
   open ~/.claude/played/played.html   # macOS; xdg-open on Linux
   ```
   Put this machine's file first: its color leads the chart.

4. **Reply in three lines:** total tokens and period, the machine and the model that weigh most, the subagent share. Then the path of the page. Every number comes from the JSON files: never estimate, never round into something else.

## What the page holds

- Period picker (last day, yesterday, since yesterday, 7 days, all, free range, −1/+1 day arrows).
- Share card ("POV : tu rushes tes projets perso", totals only, no folder names) with a button that saves a 1080×1920 story PNG.
- KPIs, per-day chart by machine (with or without cache reads), per-machine and per-model tables, day-by-day detail, top folders per machine, method and limits.

## Rules

- Cloud sessions (Claude Code on the web, claude.ai project threads) cannot be measured: their transcripts vanish with the container. Say so if asked; never estimate them.
- The JSON files contain folder names: do not paste them into a public place or send them anywhere. The share card and the story PNG only carry totals.
- To count another machine, the user runs `/played` on it and copies `~/.claude/played/<label>.json` into this machine's `~/.claude/played/`.
