---
name: horka-project-index
description: Global index of Claude Code projects that disambiguates a command when it does not say which project it targets (e.g. "write the changelog"). Resolves a name/alias to a path, knows which folder owns a skill/command (changelog, release, deploy…), detects parent workspaces, and creates + indexes a new project in the right place. Trigger on "index projects", "reindex", "project catalog", "list my projects", "which project", "new project", "start a project", "do X" without naming a project, or any generic command from a multi-project view / Agent View. Do NOT use when the current project is already unambiguous (act directly), nor to index anything other than Claude Code projects.
allowed-tools: Read, Edit, Write, Bash, Grep, AskUserQuestion
---

# Project Index

Global project registry for Claude Code's **multi-project view** (Agent View /
"FleetView"). Claude identifies a project by its `cwd`, but has no native way to
name/describe a project, nor to tie a generic command ("write the changelog") to
the right folder. This skill fills that gap.

**Scope**: multi-project by design, but stays quiet if you only have one project
(nothing to disambiguate → act on the current project). Requires Python ≥ 3.7 and
`git` on PATH (macOS / Linux / WSL / Windows). Honors `CLAUDE_CONFIG_DIR`.

## Files

Let **`$SKILL`** be this skill's own directory — its absolute path is given at
skill-load time as *"Base directory for this skill: …"*, and equals
`${CLAUDE_PLUGIN_ROOT}/skills/horka-project-index` when installed as a plugin. Always
call the script with that absolute path; never assume a hardcoded location.

- **Builder**: `$SKILL/build_index.py` (no hardcoded user paths)
- **Canonical index**: `<config>/projects-index.json`
- **Readable view**: `<config>/PROJECTS.md`

`<config>` = `$CLAUDE_CONFIG_DIR` else `~/.claude`. Use `--status` for the exact paths.

## Data model

Two entry types:
- **`project`** — a folder actually opened with Claude (source: the real `cwd`
  read from the transcripts `<config>/projects/*/*.jsonl`; folder names are never
  decoded — ambiguous: `dev-cc` ≠ `dev/cc`).
- **`workspace`** — a **parent** folder containing a `.claude/` and ancestor of at
  least one project (e.g. a monorepo `LibTracker/` hosting API + front + sdk). It
  may have no history but can own **shared skills/commands** — that is often the
  level that should run a cross-cutting action.

Each entry carries: `name`, `path`, `type`, `exists`, `aliases`, `stack`,
`description`, **`skills`**, **`commands`** (what the folder provides via its
`.claude/`), `git_remote`, `branch`, `last_active`, and `members` (workspaces).

---

## §A — Resolve a command's target

Goal: go from a fuzzy command to the **right folder**, never by guessing.
Golden rule: **nominal first, and when in doubt → ask** (`AskUserQuestion`).

1. **Current project obvious?** If the session `cwd` is already a clear project and
   the command concerns it, act on it. This skill matters when the project is
   **absent, ambiguous, or explicitly named**.

2. **Load the index.** `python3 "$SKILL/build_index.py" --status`; if `empty: true`
   → bootstrap first (§B). Read `projects-index.json`.

3. **Nominal match (priority).** Does the user name a project ("picsou's changelog",
   "LibTracker's API")? Match the reference, fuzzy and case-insensitive, against
   `name` / `name_override` / `aliases` / `path` segments.
   - **1 match** → target. Go to 5.
   - **Several matches** → `AskUserQuestion` with the candidates (name + path +
     stack). Do not guess.

4. **Capability signal (if no project named, or to pick the right level).**
   Does the command map to a skill/command (changelog, release, deploy, bump,
   test…)? Build the list of **providers** = entries whose `skills` or `commands`
   contain a match of the keyword.
   - **0 provider** → no dedicated capability: treat as a normal action on the
     current / named project.
   - **1 provider** → that is the target (often a parent workspace). Confirm.
   - **≥2 providers** → **AMBIGUOUS → ask** (`AskUserQuestion`), listing each
     provider (name, type project/workspace, path). Never fire the action at
     random: the same skill present in 5 projects = a deliberate block until the
     user decides.
   - If the user ALSO named a project (step 3), filter providers to that project
     **and its ancestor workspaces** before counting.

5. **No lead** → list the 5–8 most recent entries (already sorted) and ask which,
   or offer to create a new project (§C).

6. **Act** in the resolved path (`git -C <path>`, `cd <path>`…). State the chosen
   target in one line and why ("Target: **LibTracker** (workspace) — it owns the
   `changelog` skill; running there.").

> Why workspace vs subproject: a cross-cutting action (changelog, monorepo release)
> lives at the level that **owns** the skill/command. The `skills`/`commands` field
> decides, not folder depth.

---

## §B — Bootstrap / refresh / list / maintain

```bash
python3 "$SKILL/build_index.py"            # smart
python3 "$SKILL/build_index.py" --prune    # drop dead entries
python3 "$SKILL/build_index.py" --status   # state + paths
```

- **Empty index → ACTION A (bootstrap)**: scans all history + detects workspaces.
- **Existing index → refresh**: updates metadata and **auto-detects new projects**
  (lists them).
- If the builder warns "folders exist but no `cwd` extracted", the transcript
  format has likely changed: do not force it, tell the user.

For "list my projects": present `PROJECTS.md` (sorted by activity). Only rebuild if
the index is missing/stale.

### Refine an entry
`notes`, `name_override`, `description_override` are **preserved** on rebuild. Edit
`projects-index.json` on the entry (keyed by `path`), then rerun the builder to
regenerate the `.md`. Never hand-edit `PROJECTS.md` — it is regenerated.

---

## §C — New project: where to create it, then index it

Triggers: "start a new project <name>", or starting a conversation in a `cwd`
**absent from the index**.

1. **Where to create it (no hardcoded paths).**
   ```bash
   python3 "$SKILL/build_index.py" --roots
   ```
   Roots sorted by frequency.
   - Obvious root → propose it ("Create `my-project` in `~/dev/Orka`?").
   - Ambiguous → `AskUserQuestion` (2–3 roots + "other path").
   - Empty index → ask for the base folder, or propose the current `cwd`'s parent.
   - If the project belongs to an existing **workspace** (monorepo), create it
     **under that workspace** to inherit its skills/commands.

2. **Create** the folder `<root>/<kebab-name>`, `git init` if relevant, then the
   requested scaffold (follow the parent workspace's stack/conventions if any;
   do not assume a template).

3. **Index it immediately** (ABSOLUTE path — the shell `cwd` may be reset in the
   harness, so `.` is fragile):
   ```bash
   python3 "$SKILL/build_index.py" --ensure /absolute/path
   ```
   `--ensure` adds/refreshes **that one project**, even without a transcript.

> If you just start a conversation in an unknown `cwd` without creating anything,
> offer to index it (`--ensure <absolute cwd>`) so it becomes resolvable later.

---

## Guardrails

- **Never** decode a project from a `<config>/projects/` folder name (ambiguous).
  Always go through the builder / the transcripts' `cwd`.
- **Never** act on a guessed target. Ambiguity (name or capability) → ask.
- The builder only writes `projects-index.json` and `PROJECTS.md` (atomic writes)
  — never a project's code.
- Generic and shareable: no hardcoded user data; everything is derived from the
  local history of whoever runs it. Unknown stack/description → empty fields, never
  an error.

## What this skill does NOT do

- Edit/scaffold a project's **code** (it only touches the index) — delegate that to
  the normal flow once the target is resolved.
- Replace an already-obvious current project — in that case, act directly.
- Index anything other than Claude Code projects (not a task manager or a CMDB).
