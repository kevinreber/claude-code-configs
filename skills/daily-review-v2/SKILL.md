---
name: daily-review-v2
description: "Claude Code activity tracking with SQLite/Turso storage — standup, weekly rollups, project reports, brag doc, friction tracking, goal tracking, heatmap, export. Data syncs to Turso for remote access. For full workday recap across all tools, use /daily-recap-v2 instead."
user_invocable: true
---

# Daily Review v2 (SQLite-backed)

Comprehensive activity tracking and productivity intelligence built from Claude Code conversation history. Stores all data in SQLite with Turso sync for remote access.

## Key Difference from /daily-review

This skill writes structured data to SQLite (`~/.claude/activity.db`) via the `activity-db` CLI instead of markdown files. The database syncs to Turso for remote access. Terminal output is still markdown for readability.

## User Identity Resolution

Before starting, resolve the current user's identity dynamically:
- **Full name:** Run `git config user.name`
- **Username:** Run `whoami`
- **Email:** Run `git config user.email`

## activity-db CLI

All database operations go through the CLI at `~/.claude/bin/activity-db/`. Always run commands from that directory using `uv run python main.py <command>`.

```bash
# Write an activity (device_id auto-detected from hostname; override with --device-id)
uv run python main.py write --date YYYY-MM-DD --category <category> --source <source> --title "..." [--detail "..."] [--url "..."] [--metadata '{}'] [--tag work|personal] [--device-id <hostname>]

# Write a summary (versioned — re-runs never overwrite, they append a new version; scoped by device_id)
uv run python main.py summary --date YYYY-MM-DD --period daily|weekly|monthly|project --type review|recap|standup|brag --content "..." [--device-id <hostname>]

# Query activities
uv run python main.py query --date YYYY-MM-DD
uv run python main.py query --start YYYY-MM-DD --end YYYY-MM-DD
uv run python main.py query --category <category> --source <source>
uv run python main.py query --sql "SELECT ..."
uv run python main.py query --format table

# Query summaries (defaults to latest version per (date, period, type))
uv run python main.py query-summaries --date YYYY-MM-DD --type review
uv run python main.py query-summaries --date YYYY-MM-DD --type review --all-versions   # see history
uv run python main.py query-summaries --date YYYY-MM-DD --type review --version 2      # pin a specific version

# Stats
uv run python main.py stats

# Export as markdown
uv run python main.py export-md --date YYYY-MM-DD

# Force sync
uv run python main.py sync
```

### Categories
`project_activity`, `skill_usage`, `accomplishment`, `pr`, `jira`, `gdoc`, `confluence`, `reference`, `prompt`

### Sources
`claude`, `github`, `jira`, `slack`, `confluence`, `gdocs`, `extracted`

### Tags
`work` (default), `personal`

## Subcommands

Parse the user's arguments to determine which mode to run:

| Command | Mode | Description |
|---|---|---|
| `/daily-review-v2` | **daily** | Generate today's daily log |
| `/daily-review-v2 YYYY-MM-DD` | **daily** | Generate log for a specific date |
| `/daily-review-v2 YYYY-MM-DD YYYY-MM-DD` | **daily** | Generate logs for a date range |
| `/daily-review-v2 standup` | **standup** | Generate copy-paste standup notes |
| `/daily-review-v2 week` | **weekly** | Weekly rollup for the current week |
| `/daily-review-v2 week YYYY-MM-DD` | **weekly** | Weekly rollup for the week containing that date |
| `/daily-review-v2 project <name>` | **project** | All-time report for a specific project |
| `/daily-review-v2 compare this-week last-week` | **compare** | Compare two time periods |
| `/daily-review-v2 compare YYYY-MM-DD YYYY-MM-DD` | **compare** | Compare two specific dates |
| `/daily-review-v2 friction` | **friction** | Accumulated friction report across all days |
| `/daily-review-v2 goals` | **goals** | View/manage weekly goals |
| `/daily-review-v2 goals set <goal>` | **goals** | Add a new weekly goal |
| `/daily-review-v2 goals done <goal>` | **goals** | Mark a goal as complete |
| `/daily-review-v2 heatmap` | **heatmap** | Time-of-day activity heatmap |
| `/daily-review-v2 heatmap YYYY-MM` | **heatmap** | Heatmap for a specific month |
| `/daily-review-v2 export [date] [format]` | **export** | Export as JSON or condensed text |
| `/daily-review-v2 brag` | **brag** | Regenerate the full brag doc |

**Filters** (can be combined with any subcommand):

| Flag | Description |
|---|---|
| `--work` | Only include work projects |
| `--personal` | Only include personal projects |

---

## Data Source

All modes read from `~/.claude/history.jsonl`. Each line is JSON with:
- `timestamp` (epoch ms)
- `project` (full path — extract last segment as project name)
- `display` (the user's prompt text)
- `sessionId`

Use Python via Bash tool for all data extraction. Base parsing:
```python
import json, datetime, os, re
from collections import defaultdict

def load_history():
    entries = []
    with open(os.path.expanduser('~/.claude/history.jsonl'), 'r') as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                dt = datetime.datetime.fromtimestamp(entry['timestamp'] / 1000)
                entry['_dt'] = dt
                entry['_date'] = dt.strftime('%Y-%m-%d')
                entry['_time'] = dt.strftime('%H:%M')
                entry['_hour'] = dt.hour
                entry['_dow'] = dt.strftime('%A')
                entry['_project'] = entry.get('project', 'unknown').split('/')[-1]
                entry['_project_path'] = entry.get('project', 'unknown')
                entry['_tag'] = 'personal' if '/personal/' in entry.get('project', '') else 'work'
                entry['_display'] = entry.get('display', '')
                entries.append(entry)
            except:
                continue
    return entries
```

### Project tagging

Each project is tagged as `personal` or `work` based on its path:
- **Personal:** project path contains `/personal/`
- **Work:** everything else (default)

### Reference extraction

Extract all URLs and identifiers from prompt text:
- **GitHub PRs:** `https://github.com/.*/pull/\d+`
- **Google Docs/Slides/Sheets:** `https://docs.google.com/...`
- **Jira/Atlassian:** `https://.*.atlassian.net/...`
- **Jira tickets:** `[A-Z]+-\d{3,6}` pattern
- **Never fabricate URLs** — only extract what's actually present in the prompt text

---

## Mode: Daily (default)

### Step 1: Parse history and extract activities

Parse `history.jsonl` for the target date. Extract projects, prompts, skills, references, time blocks — same logic as `/daily-review`.

### Step 2: Write structured data to SQLite

For each project found, write an activity:
```bash
uv run python main.py write \
  --date YYYY-MM-DD \
  --category project_activity \
  --source claude \
  --title "<project_name>" \
  --detail "<key activities, newline separated>" \
  --metadata '{"prompts": N, "time_range": "HH:MM - HH:MM", "total_day_prompts": N, "active_hours": "HH:MM - HH:MM", "estimated_time": "Xh Ym"}' \
  --tag work|personal
```

For each skill used:
```bash
uv run python main.py write \
  --date YYYY-MM-DD \
  --category skill_usage \
  --source claude \
  --title "<skill_name>" \
  --detail "<project_name>" \
  --tag work|personal
```

For each reference (URL, Jira ticket):
```bash
uv run python main.py write \
  --date YYYY-MM-DD \
  --category pr|jira|gdoc|confluence|reference \
  --source extracted \
  --title "<identifier>" \
  --url "<full_url>" \
  --tag work
```

For each accomplishment:
```bash
uv run python main.py write \
  --date YYYY-MM-DD \
  --category accomplishment \
  --source claude \
  --title "<specific impact statement>" \
  --tag work|personal
```

### Step 3: Generate markdown output

Generate the same markdown format as `/daily-review` and display it to the user in the terminal. The output should include:

#### Header
```markdown
# Daily Activity Log — YYYY-MM-DD (DayName)

**Total prompts:** N (across M project(s))
**Active hours:** HH:MM - HH:MM
**Estimated active time:** Xh Ym
**Work:** Xh Ym (N prompts) | **Personal:** Xh Ym (N prompts)
```

#### Time Distribution
Same time block table as `/daily-review` with 30-min gap threshold and total row.

#### Project Breakdown
For each project (sorted by prompt count descending):
- Project name, tag, prompt count, time range
- **Key activities** — representative prompts (cleaned, truncated to 150 chars, max 15 per project)
- **Skills used** — any `/skill` commands detected
- **References** — all extracted URLs and Jira ticket IDs

#### Impact & Accomplishments
Write **specific, concrete impact statements** — not echoed prompts. Every accomplishment should answer "what changed and why it matters."

Rules:
- **Never** echo back the user's prompt text as an accomplishment. "i think we have some daily recap..." is not an accomplishment.
- Detect concrete outcomes: PR shipped/reviewed, bug fixed, feature implemented, investigation completed, decision made, doc written, tooling improved.
- Each statement should follow the pattern: **What** was done + **why it matters** or **what it unblocked**.
- On light days (< 10 prompts), write 1-2 real statements or omit the section entirely. A short day with no concrete output should say "Light session — exploratory/setup work, no shipped artifacts."
- On heavy days, cap at 6-8 statements — pick the ones with real impact, not every small edit.

#### Transcript-derived sections (requires prior enrichment)

Before rendering, run `uv run python main.py enrich-from-transcripts --date YYYY-MM-DD` to ensure today's sessions have transcript-derived rows in `activities`. Then query and render the following sections. Only include each section if there's data. If no enrichment data exists, skip all of them silently.

**Files Touched**
```bash
uv run python main.py query --sql "SELECT json_extract(metadata, '$.file_path') AS file_path, COUNT(*) AS edits FROM activities WHERE date='YYYY-MM-DD' AND category='file_edit' GROUP BY file_path ORDER BY edits DESC"
```
Render as a list grouped by project/repo, with edit counts. Strip the home directory prefix for readability. Only include source code and meaningful files — skip temp files (`/tmp/*`), lock files, and `.pyc`.

**Commands Run**
```bash
uv run python main.py query --sql "SELECT json_extract(metadata, '$.command') AS cmd, COUNT(*) AS n FROM activities WHERE date='YYYY-MM-DD' AND category='command' GROUP BY cmd ORDER BY n DESC LIMIT 15"
```
Show top distinct bash commands by frequency. Cluster related commands (e.g., "17 pytest runs", "11 flake8/ruff cycles") rather than listing each invocation.

**Tool Usage Summary**
```bash
uv run python main.py query --sql "SELECT json_extract(metadata, '$.tool') AS tool, COUNT(*) AS n FROM activities WHERE date='YYYY-MM-DD' AND category IN ('tool_use','file_edit','command','mcp_call','plan') GROUP BY tool ORDER BY n DESC"
```
Show total tool invocations, broken down by tool name.

**MCP Call Summary** (cross-tool work)
```bash
uv run python main.py query --sql "SELECT json_extract(metadata, '$.mcp_server') AS server, json_extract(metadata, '$.mcp_tool') AS tool, COUNT(*) AS n FROM activities WHERE date='YYYY-MM-DD' AND category='mcp_call' GROUP BY server, tool ORDER BY n DESC LIMIT 10"
```

#### Critical Review

This is the most important section. Be **brutally honest** — the user specifically wants highly critical, insightful feedback that helps them optimize how they work. Don't sugarcoat.

Analyze the day's data across these dimensions and call out anything worth flagging:

**Time & Focus**
- How fragmented was the day? Count project switches. More than 5 switches in a 3-hour block = thrashing. Name the projects and suggest which should have been batched or deferred.
- Were there long gaps between prompts that suggest getting stuck, distracted, or blocked? Quantify them.
- Did any single project get less than 15 minutes of attention? That's too short to make real progress — was it worth the context switch?
- Was there a deep work block (2+ hours on one project)? If not, flag it. Deep work is where real output happens.

**Output vs. Effort**
- Compare prompt count to concrete output (PRs, features shipped, bugs fixed, decisions made). High prompts with low output = spinning wheels.
- Were there repeated attempts at the same thing? (e.g., 17 pytest runs, multiple "can you fix" prompts on the same issue). Identify the root cause — was the approach wrong, was there a missing skill, or was this unavoidable iteration?
- Did the user paste content that Claude could have fetched itself? (e.g., pasting error output instead of running the command, pasting docs instead of using MCP). Each paste is manual work that might be automatable.

**Decision Quality**
- Were there signs of indecision? ("should we...", "what do you think...", "i'm not sure if..."). Indecision isn't bad, but if it recurred on the same topic across multiple prompts, the user may need to timebox decisions.
- Were there scope creep moments? (started on X, ended up doing Y, Z). Flag them.
- Were there "going in circles" patterns? (asking the same question rephrased, or reverting changes).

**Automation & Process**
- What manual work was repeated that could be automated? (e.g., running the same sequence of commands, manually checking the same dashboards).
- Are there missing skills or tools that would have saved time? Be specific — "a pre-commit hook for X" or "a script that does Y" not "consider automation."
- Was the user doing work that could be delegated to a CI/CD pipeline, a cron job, or a background process?

**Compared to Recent Days** (if data available)
- Query the last 7 days from the DB: `SELECT date, COUNT(*) FROM activities WHERE date >= date('YYYY-MM-DD', '-7 days') GROUP BY date`
- Is today's output higher or lower than the trend? Is the project mix shifting?
- Are the same friction points recurring across days?

Format as a numbered list of specific, actionable observations. Each item should have:
1. **The observation** — what you noticed, with data
2. **Why it matters** — the cost of not addressing it
3. **What to do about it** — a concrete next step

Aim for 3-6 items. Quality over quantity. Skip this section entirely only if the day was under 5 prompts.

### Step 4: Store the generated summary

```bash
uv run python main.py summary \
  --date YYYY-MM-DD \
  --period daily \
  --type review \
  --content "<full markdown output>"
```

### Step 5: Write to Obsidian vault

If the brain-vault repo exists at `~/Projects/brain-vault/`, save the generated markdown to `Activity/`.

**File naming depends on device:**
- Detect device type by checking `hostname`:
  - If hostname contains `.linkedin.biz` or matches the work laptop pattern → **work** device
  - Otherwise → **personal** device
- **Work device** file names (default, no suffix):
  - `Activity/YYYY-MM-DD.md`
- **Personal device** file names (suffixed):
  - `Activity/YYYY-MM-DD-personal.md`

**Frontmatter** — always include:
```yaml
---
type: activity
date: YYYY-MM-DD
period: daily
device: work|personal
tags:
  - activity
  - daily-log
---
```

**Do NOT overwrite** — if the target file already exists, skip this step silently. The vault file is a snapshot; regeneration updates the DB summary (versioned), not the vault file.

**Wikilinks** — wrap all project names in `[[wikilinks]]` (e.g., `[[brain-vault]]`, `[[neo-workflow]]`) so Obsidian graph view and backlinks connect activity logs to project notes.

### Step 6: Enrich Project Notes

For each project that had **5+ prompts** in the day, update its project note in `~/Projects/brain-vault/Projects/`.

**If the project note doesn't exist**, create it:
```yaml
---
type: project
status: active
category: personal|work
last_seen: YYYY-MM-DD
---

## Overview

<!-- auto:daily-context:start -->
<!-- auto:daily-context:end -->

## Notes
```

**If the project note already exists**, update the `<!-- auto:daily-context:start/end -->` block. If that block doesn't exist, add it **after `## Overview`** (or after `## Auto-generated context` if that section exists). Never touch content outside the auto block.

The auto block should contain a **running log** of what was done on this project, appended to (not replaced). Format:

```markdown
<!-- auto:daily-context:start -->

### YYYY-MM-DD
- **What:** 1-2 sentence summary of what was done
- **How:** Key technical details, tools used, commands, architecture decisions
- **Problems solved:** Non-obvious solutions worth remembering (e.g., "Tika race condition on cold boot — services need staggered startup")
- **Status:** Current state (deployed, PR open, WIP, blocked on X)
- **Links:** [[related-project]], PR URLs, doc URLs

### YYYY-MM-DD (previous entry preserved)
...

<!-- auto:daily-context:end -->
```

**Also update frontmatter:**
- Set `last_seen` to today's date
- If `status: stub` and there's now real content, promote to `status: active`

This is critical for the vault's purpose as an external brain — project notes should answer "what is this project and what have I done with it?" not just "how many times was it mentioned."

### Step 7: Extract Ideas & Backlog

Scan the day's prompts for signals of ideas, future plans, or things to explore:
- "i'd like to...", "maybe we should...", "another feature i'm thinking of..."
- "we should add...", "it would be cool if...", "i want to explore..."
- "can we automate...", "is there a way to..."
- Questions about tools/services not yet used

Append any found items to `~/Projects/brain-vault/Backlog/ideas.md`. If the file doesn't exist, create it:

```yaml
---
type: backlog
---

# Ideas & Backlog

Pending ideas extracted from daily activity. Review periodically — promote to project notes or archive.
```

Each idea entry:
```markdown
## YYYY-MM-DD — <short title>
- **From:** [[project-name]] session
- **Idea:** What the user described wanting
- **Context:** Why it came up
- **Status:** open
```

**Do NOT duplicate** — check if a similar idea already exists before adding. Append only genuinely new ideas.

### Step 8: Update brag doc

Append new accomplishments to `~/.claude/daily-logs/BRAG-DOC.md` (same as `/daily-review`).

### Immutability

Before writing, check if a summary already exists for this date:
```bash
uv run python main.py query-summaries --date YYYY-MM-DD --type review
```
If it exists, **DO NOT overwrite.** Tell the user and ask if they want to regenerate.

---

## Mode: Standup

Same as `/daily-review standup`. Pull yesterday's data from the DB:
```bash
uv run python main.py query --date YYYY-MM-DD --format json
```

Generate copy-paste standup message to screen (not stored).

---

## Mode: Weekly Rollup

Same logic as `/daily-review week`. Query the full week's data:
```bash
uv run python main.py query --start YYYY-MM-DD --end YYYY-MM-DD
```

Store as:
```bash
uv run python main.py summary --date YYYY-MM-DD --period weekly --type review --content "..."
```

---

## Mode: Project Focus Report

Query all activities for a specific project:
```bash
uv run python main.py query --sql "SELECT * FROM activities WHERE title = '<project>' OR detail LIKE '%<project>%' ORDER BY date"
```

---

## Mode: Compare

Query both periods and compare metrics side-by-side. Use SQL aggregations:
```bash
uv run python main.py query --start <period_a_start> --end <period_a_end>
uv run python main.py query --start <period_b_start> --end <period_b_end>
```

---

## Mode: Friction Tracker

Same friction analysis as `/daily-review`. Scan all history for friction signals, write results:
```bash
uv run python main.py summary --date YYYY-MM-DD --period monthly --type review --content "..."
```

---

## Mode: Goals

Use the goals table in SQLite instead of `goals.json`:
```bash
# View goals
uv run python main.py query --sql "SELECT * FROM goals WHERE week = '2026-W14'"

# Add goal (use Python to insert directly)
# Mark done (update status and completed date)
```

---

## Mode: Heatmap

Same as `/daily-review heatmap`. Parse history.jsonl for time data and generate ASCII heatmap to screen.

---

## Mode: Export

```bash
# JSON export
uv run python main.py query --date YYYY-MM-DD --format json

# Markdown export
uv run python main.py export-md --date YYYY-MM-DD
```

---

## Mode: Brag Doc Regeneration

Query all accomplishments:
```bash
uv run python main.py query --category accomplishment
```

Regenerate `~/.claude/daily-logs/BRAG-DOC.md` from structured data.

---

## Important Notes

- **activity-db is the single write path** — all data goes through the CLI
- **Terminal output is still markdown** — the user sees the same format as `/daily-review`
- **SQLite is the source of truth** — not markdown files
- **Turso syncs automatically** — every write syncs to remote
- **Real references only** — never fabricate URLs or Jira IDs
- **Python for data parsing** — use Python via Bash tool for history.jsonl parsing
- **Dates:** Determine today's date from the system. Use the user's local timezone.
- **Run activity-db from its directory:** Always `cd ~/.claude/bin/activity-db && uv run python main.py <command>`
- **Summaries are versioned, not overwritten** — re-running `summary` for the same `(date, period, type)` appends a new version (v2, v3, …) instead of replacing the prior one. The `query-summaries` command defaults to the latest version; pass `--all-versions` to see history or `--version N` to pin one. Prior versions are preserved so regenerations never destroy earlier content.
