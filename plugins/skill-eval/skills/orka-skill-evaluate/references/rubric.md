# Skill Evaluation Rubric

Detailed scoring criteria from Anthropic's "The Complete Guide to Building Skills for Claude".

## 1. Structure & Technical Compliance (20 pts)

### File & Folder (8 pts)

| Check | Pts | Pass | Fail |
|-------|-----|------|------|
| SKILL.md exists (exact case) | 2 | Named exactly `SKILL.md` | Any variation |
| Folder is kebab-case | 2 | `my-skill-name` | Spaces, underscores, capitals |
| No README.md in skill folder | 2 | Absent | Present |
| references/ for supplementary docs | 2 | Used when skill has detailed content | Large SKILL.md with no references/ |

### YAML Frontmatter (12 pts)

| Check | Pts | Pass | Fail |
|-------|-----|------|------|
| `---` delimiters present | 3 | Opens and closes with `---` | Missing or malformed |
| `name`: kebab-case only | 3 | `my-skill` | Spaces, underscores, capitals |
| `name` matches folder name | 2 | Exact match | Mismatch |
| No XML tags in frontmatter | 4 | Clean | Any `<` or `>` found |

### Scoring notes

- `description` field is scored in Category 2, not here
- `argument-hint` is optional but gets +1 bonus if present and useful (cap at 20)
- Optional frontmatter fields (`license`, `compatibility`, `metadata`): +1 bonus per present and useful field, max +2 (cap at 20)

### allowed-tools validation (auto-detect)

If `allowed-tools` is present, cross-reference instructions against the tool list. Score: +0/-2 per mismatch.

**Pattern detection** -- scan instructions for these signals and verify the matching tool is declared:

| Signal in instructions | Required tool |
|---|---|
| "ask the user", "confirm with user", "get user input", `AskUserQuestion` | AskUserQuestion |
| ````bash` blocks, "run via Bash", "Run:", `git`, `wc`, `ls`, `sed` | Bash |
| "Read the file", "Use Read", "read all found files" | Read |
| "Use Write", "Write to", "create file", "save to" | Write |
| "Use Edit", "surgical update", "modify", "augment" | Edit |
| "Use Glob", "scan for", "find files", `**/*.md` glob patterns | Glob |
| "Use Grep", "search for", "find pattern" | Grep |
| "Use LSP", "type checking", "symbol resolution" | LSP |
| "Use WebFetch", "fetch URL" | WebFetch |
| "Use WebSearch", "search the web" | WebSearch |

**Mismatch types**:
- **Tool declared but never used**: -2 (bloats permissions for no reason)
- **Tool needed but not declared**: -2 (skill will fail at runtime)
- **Implicit tool use** (e.g., "augment" implies Edit): -0 if the action is clearly described, -1 if ambiguous

## 2. Description Quality (25 pts)

### Content (17 pts)

| Check | Pts | How to score |
|-------|-----|-------------|
| States WHAT the skill does | 5 | Clear capability statement. 0 if vague ("helps with things") |
| States WHEN to use it | 5 | Trigger conditions present. 0 if no "Use when" or "Trigger on" |
| Includes user phrases | 5 | Specific things users say in quotes. 0 if no quoted triggers |
| Not vague / not too technical | 2 | Balanced for human understanding. 0 if jargon-only or too generic |

### Format (8 pts)

| Check | Pts | How to score |
|-------|-----|-------------|
| Under 1024 characters | 3 | Count characters. 0 if over |
| No XML tags | 2 | No `<` or `>` in description. 0 if present |
| Follows `[What it does] + [When to use it] + [Key capabilities]` pattern | 3 | Structured per Anthropic's formula. 1 if partial, 0 if random |

### Bonuses

- Includes negative triggers ("Do NOT use for...", scope limitations): +1 bonus (cap at 25) -- prevents overtriggering
- Mentions relevant file types when applicable: +1 bonus (cap at 25)

### Red flags (auto-deduct)

- "Helps with projects" -> -5 (too vague)
- "Implements the X entity model" -> -3 (too technical, no user triggers)
- No "Use when" / "Trigger on" phrase -> -5

## 3. Instructions Quality (30 pts)

### Structure (10 pts)

| Check | Pts | Criteria |
|-------|-----|---------|
| ## / ### heading hierarchy | 3 | Clean Markdown levels, max 4 deep. Critical instructions at top of sections. |
| Step-by-step workflow | 4 | Numbered steps or clear phases |
| Response format defined | 3 | Template or example output shown |

### Actionability (12 pts)

| Check | Pts | Criteria |
|-------|-----|---------|
| Specific commands/actions | 5 | Concrete: `Run python scripts/validate.py`. Not: `validate the data` |
| Decision criteria (IF/THEN) | 4 | Clear branching logic for different scenarios |
| Real-world examples | 3 | At least 1 concrete example with input/output |

### Robustness (8 pts)

| Check | Pts | Criteria |
|-------|-----|---------|
| Error handling / troubleshooting | 4 | What to do when things fail |
| Edge cases addressed | 2 | Boundary conditions, empty inputs, etc. |
| References linked | 2 | `consult references/X.md` pattern if references exist |

### Scoring guidelines

- **5/5 actionability**: Every instruction is a concrete verb + target. "Run X", "Check Y", "If Z then W". Non-absolute rules include contextual qualifiers.
- **3/5 actionability**: Mix of concrete and vague. "Process the data" alongside specific commands
- **1/5 actionability**: Mostly vague. "Handle errors appropriately", "Validate things"
- **0/5 actionability**: No actionable instructions at all

### Instruction quality signals (from Anthropic's troubleshooting guide)

- **Instructions too verbose**: Prose-heavy instructions get buried. Prefer bullet points and numbered lists.
- **Instructions buried**: Critical rules should be at the top of sections, use ## Important or ## Critical headers if needed.
- **Ambiguous language**: "Make sure to validate things properly" is bad. "CRITICAL: Before calling X, verify: [list]" is good.
- **No redundancy**: Do NOT include instructions that duplicate Claude's built-in system prompt behavior.

## 4. Token Efficiency (15 pts)

| Check | Pts | Criteria |
|-------|-----|---------|
| SKILL.md under 5000 words | 5 | Word count. -1 per 500 words over |
| Progressive disclosure | 5 | Core in SKILL.md, details in references/. 0 if all content inlined |
| Concise style | 5 | Lists and tables over prose. No filler words |

### Conciseness scoring

- **5**: Bullet points, tables, code blocks. Zero prose padding
- **4**: Mostly structured with occasional explanatory sentences
- **3**: Mix of prose and structure
- **2**: Prose-heavy with some lists
- **1**: Wall of text with redundancy
- **0**: Extremely verbose, duplicated content across sections

### Progressive disclosure scoring

- **5**: SKILL.md has core workflow, references/ has detailed docs, clear links between them
- **3**: Some separation but could move more to references/
- **1**: Everything in SKILL.md, no references/ used
- **0**: SKILL.md is enormous with no structure. Or: references/ exists but is never linked

### Word count benchmarks

- Under 500 words: Possibly too thin (check if instructions are complete)
- 500-1500 words: Ideal range for most skills
- 1500-3000 words: Acceptable if using progressive disclosure
- 3000-5000 words: Needs references/ offloading
- Over 5000 words: Automatic -5 penalty

## 5. Composability & Design (10 pts)

| Check | Pts | Criteria |
|-------|-----|---------|
| Clear scope boundaries | 4 | States what it does AND what it does NOT handle |
| No exclusivity assumption | 3 | Works alongside other skills. No "I am the only..." |
| allowed-tools appropriate | 3 | Cross-reference with pattern detection table in Category 1. All declared tools used, all needed tools declared. |

### Composability red flags

- Overly broad description that could conflict with other skills -> -3
- Tool needed but not in allowed-tools (detected via pattern table) -> -2
- Instructions that override or conflict with system behavior -> -3
- `disable-model-invocation: true` but description uses auto-trigger language without "Use when" framing -> -1

## Grade Scale

| Grade | Range | Meaning |
|-------|-------|---------|
| A+ | 95-100 | Exemplary, marketplace-ready |
| A | 90-94 | Production-ready |
| A- | 85-89 | Very good, minor polish |
| B+ | 80-84 | Good, few improvements |
| B | 75-79 | Solid foundation, some gaps |
| B- | 70-74 | Functional, needs attention |
| C+ | 65-69 | Below average, multiple issues |
| C | 60-64 | Significant improvements needed |
| C- | 55-59 | Barely functional |
| D | 40-54 | Major structural issues |
| F | 0-39 | Needs complete rewrite |

## Status Thresholds (per category)

- **OK**: Score >= 80% of category max
- **WARN**: Score 50-79% of category max
- **FAIL**: Score < 50% of category max
