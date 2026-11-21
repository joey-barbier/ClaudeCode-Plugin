# horka-played

`/played` for Claude Code, as in World of Warcraft: how many tokens you burned.

It reads your local transcripts (`~/.claude/projects`, 30 days by default), merges the measurements of your other machines, and opens a doc-style page:

- totals, per day, per machine, per model, subagent share, record day;
- a period picker (last day, yesterday, 7 days, free range, −1/+1 day);
- a shareable card ("POV : tu rushes tes projets perso") and a button that saves a 1080×1920 story PNG.

Read-only, no estimated number.

## Cloud sessions

Cloud transcripts vanish with their container. With this plugin installed, a `Stop` hook saves each cloud session's usage at the end of every turn to `/mnt/project-files/played/cloud/<session>.json` (claude.ai project threads), deduplicated across the containers of one session. It does nothing on a local machine; `PLAYED_CLOUD=0` turns it off. Usage from before the install is not recovered.

To count them: run `/played` in a cloud thread (it builds the page from that folder), or copy the folder into `~/.claude/played/cloud/` on your machine.

## Use

```
/played              # this machine, 30 days
/played 7            # 7 days
/played MacBook 30   # with a readable label
```

Several machines: run `/played` on each one, copy `~/.claude/played/<label>.json` into the `~/.claude/played/` folder of the machine you open the page on, then run `/played` there.
