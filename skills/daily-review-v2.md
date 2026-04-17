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
# Write an activity
uv run python main.py write --date YYYY-MM-DD --category <category> --source <source> --title "..." [--detail "..."] [--url "..."] [--metadata '{}'] [--tag work|personal]

# Write a summary
uv run python main.py summary --date YYYY-MM-DD --period daily|weekly|monthly|project --type review|recap|standup|brag --content "..."

# Query activities
uv run python main.py query --date YYYY-MM-DD
uv run python main.py query --start YYYY-MM-DD --end YYYY-MM-DD
uv run python main.py query --category <category> --source <source>
uv run python main.py query --sql "SELECT ..."
uv run python main.py query --format table

# Query summaries
uv run python main.py query-summaries --date YYYY-MM-DD --type review

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
Write **specific, concrete impact statements** derived from the actual prompts. Detect types: PR shipped, PR reviewed, PR feedback addressed, production issue resolved, feature implemented, testing added, documentation, tooling/automation.

#### Patterns & Optimization Opportunities
Same as `/daily-review`: repeated skills, context switches, manual data pasting, environment friction, iterative refinement.

#### Transcript-derived sections (NEW — requires prior enrichment)

Before rendering, run `uv run python main.py enrich-from-transcripts --date YYYY-MM-DD` to ensure today's sessions have transcript-derived rows in `activities`. Then query those rows and render:

**Files touched**
```bash
uv run python main.py query --sql "SELECT DISTINCT json_extract(metadata, '$.file_path') AS file_path FROM activities WHERE date='YYYY-MM-DD' AND category='file_edit' ORDER BY file_path"
```
Group by project/folder, show counts of edits per file.

**Commands run**
```bash
uv run python main.py query --sql "SELECT json_extract(metadata, '$.command') AS cmd, COUNT(*) AS n FROM activities WHERE date='YYYY-MM-DD' AND category='command' GROUP BY cmd ORDER BY n DESC LIMIT 15"
```
Show top distinct bash commands by frequency.

**Tool usage summary**
```bash
uv run python main.py query --sql "SELECT json_extract(metadata, '$.tool') AS tool, COUNT(*) AS n FROM activities WHERE date='YYYY-MM-DD' AND category IN ('tool_use','file_edit','command','mcp_call','plan') GROUP BY tool ORDER BY n DESC"
```
Show total tool invocations, broken down by tool name.

**MCP call summary** (for cross-tool work)
```bash
uv run python main.py query --sql "SELECT json_extract(metadata, '$.mcp_server') AS server, json_extract(metadata, '$.mcp_tool') AS tool, COUNT(*) AS n FROM activities WHERE date='YYYY-MM-DD' AND category='mcp_call' GROUP BY server, tool ORDER BY n DESC LIMIT 10"
```

Only include each section if there's data. If the day's sessions haven't been enriched (no activities with `category IN ('tool_use','file_edit','command','mcp_call')`), skip these sections silently or show a one-line note.

### Step 4: Store the generated summary

```bash
uv run python main.py summary \
  --date YYYY-MM-DD \
  --period daily \
  --type review \
  --content "<full markdown output>"
```

### Step 5: Update brag doc

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
