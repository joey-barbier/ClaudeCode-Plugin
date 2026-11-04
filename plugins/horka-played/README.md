# horka-played

`/played` for Claude Code, as in World of Warcraft: how many tokens you burned.

It reads your local transcripts (`~/.claude/projects`, 30 days by default), merges the measurements of your other machines, and opens a doc-style page:

- totals, per day, per machine, per model, subagent share, record day;
- a period picker (last day, yesterday, 7 days, free range, −1/+1 day);
- a shareable card ("POV : tu rushes tes projets perso") and a button that saves a 1080×1920 story PNG.

Read-only, no estimated number. Cloud sessions are not measurable (their transcripts vanish with the container) and the page says so.

## Use

```
/played              # this machine, 30 days
/played 7            # 7 days
/played MacBook 30   # with a readable label
```

Several machines: run `/played` on each one, copy `~/.claude/played/<label>.json` into the `~/.claude/played/` folder of the machine you open the page on, then run `/played` there.
