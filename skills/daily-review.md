---
name: daily-review
description: "Claude Code activity tracking — standup, weekly rollups, project reports, brag doc, friction tracking, goal tracking, heatmap, export."
user_invocable: true
---

# Daily Review

Comprehensive activity tracking and productivity intelligence built from Claude Code conversation history.

## User Identity Resolution

Before starting, resolve the current user's identity dynamically:
- **Full name:** Run `git config user.name`
- **Username:** Run `whoami`
- **Email:** Run `git config user.email`

Use these values everywhere the skill references the user's name or email. Never hardcode a specific user's identity.

## Subcommands

Parse the user's arguments to determine which mode to run:

| Command | Mode | Description |
|---|---|---|
| `/daily-review` | **daily** | Generate today's daily log |
| `/daily-review YYYY-MM-DD` | **daily** | Generate log for a specific date |
| `/daily-review YYYY-MM-DD YYYY-MM-DD` | **daily** | Generate logs for a date range |
| `/daily-review standup` | **standup** | Generate copy-paste standup notes |
| `/daily-review week` | **weekly** | Weekly rollup for the current week |
| `/daily-review week YYYY-MM-DD` | **weekly** | Weekly rollup for the week containing that date |
| `/daily-review project <name>` | **project** | All-time report for a specific project |
| `/daily-review compare this-week last-week` | **compare** | Compare two time periods |
| `/daily-review compare YYYY-MM-DD YYYY-MM-DD` | **compare** | Compare two specific dates |
| `/daily-review friction` | **friction** | Accumulated friction report across all days |
| `/daily-review goals` | **goals** | View/manage weekly goals |
| `/daily-review goals set <goal>` | **goals** | Add a new weekly goal |
| `/daily-review goals done <goal>` | **goals** | Mark a goal as complete |
| `/daily-review heatmap` | **heatmap** | Time-of-day activity heatmap |
| `/daily-review heatmap YYYY-MM` | **heatmap** | Heatmap for a specific month |
| `/daily-review export [date] [format]` | **export** | Export as JSON or condensed text |
| `/daily-review brag` | **brag** | Regenerate the full brag doc |

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

The `_tag` field is available on every entry and should be used to:
- Show a work/personal breakdown in the header (time and prompt counts per tag)
- Display the tag next to each project name in the Project Breakdown section (e.g., `my-api (work)` or `my-app (personal)`)
- Enable filtering: `/daily-review --work` shows only work projects, `/daily-review --personal` shows only personal projects

### Reference extraction

Extract all URLs and identifiers from prompt text:
- **GitHub PRs:** `https://github.com/.*/pull/\d+`
- **Google Docs/Slides/Sheets:** `https://docs.google.com/...`
- **Jira/Atlassian:** `https://.*.atlassian.net/...`
- **Jira tickets:** `[A-Z]+-\d{3,6}` pattern
- **Never fabricate URLs** — only extract what's actually present in the prompt text

---

## Mode: Daily (default)

Generate `~/.claude/daily-logs/YYYY-MM-DD.md` with these sections:

### Header
```markdown
# Daily Activity Log — YYYY-MM-DD (DayName)

**Total prompts:** N (across M project(s))
**Active hours:** HH:MM - HH:MM
**Estimated active time:** Xh Ym
**Work:** Xh Ym (N prompts) | **Personal:** Xh Ym (N prompts)
```

### Time Distribution

Include a time block table with a **total row** at the bottom:

```markdown
## Time Distribution
| Time Block | Duration | Activity |
|---|---|---|
| 09:21 - 10:55 | 1h 34m | Morning: Feature planning, PR reviews |
| 11:58 - 12:31 | 33m | Midday: PR fixes, API integration |
| 17:22 - 18:18 | 56m | Evening: Workflow local testing |
| **Total** | **3h 03m** | |
```

**How to calculate time blocks:**
- Group consecutive prompts into blocks. A new block starts when there's a gap of **30+ minutes** between prompts.
- Each block's duration = last prompt timestamp - first prompt timestamp in that block.
- Add a reasonable buffer (e.g., +5 min) to the last prompt in each block to account for reading/thinking time after the final prompt.
- **Total estimated active time** = sum of all block durations. This goes in both the header and the total row.
- This is an estimate — it captures time actively prompting Claude, not total work time. Note this with a footnote if needed.

### Project Breakdown
For each project (sorted by prompt count descending):
- Project name, tag (`work` or `personal`), prompt count, time range
- **Key activities** — representative prompts (cleaned up, truncated to 150 chars, max 15 per project)
- **Skills used** — any `/skill` commands detected
- **References** — all extracted URLs and Jira ticket IDs

### Impact & Accomplishments
Write **specific, concrete impact statements** derived from the actual prompts. Not generic labels.

Detect accomplishment types by analyzing prompt content:
- **PR shipped** — prompts containing "create a pr", "open a pr", `/pr-create`, plus the PR URL if present
- **PR reviewed** — prompts with "review", `/pr-review`, external PR URLs
- **PR feedback addressed** — `/pr-comments-fix` usage
- **Production issue resolved** — prompts mentioning "production", "error", "fix", "resolved", combined with commit/push prompts
- **Feature implemented** — sequences of implementation prompts followed by commit/PR
- **Testing added** — prompts about tests, mock data, test fixtures
- **Documentation** — wiki updates, doc creation, presentation work
- **Tooling/automation** — skill creation, script writing, config changes

List all **PRs**, **Docs**, **Jira tickets** with full URLs.

### Patterns & Optimization Opportunities
- **Repeated skills** — skills used more than once with counts
- **Context switches** — number of project switches during the day
- **Manual data pasting** — prompts containing `[Pasted text` or `[Image`
- **Environment friction** — prompts mentioning docker, error, setup, not working, cert, permission, etc.
- **Iterative refinement** — prompts with "how's this look", "is this correct", "what do you think"

### Transcript-derived sections (NEW — from v2 activity-db)

Before writing the daily log, trigger enrichment for today so the activity-db has fresh transcript-derived rows:

```bash
cd ~/.claude/bin/activity-db && uv run python main.py enrich-from-transcripts --date YYYY-MM-DD
```

Then query the enriched data and render these sections into the markdown (if there's any data for the day). These sections appear BELOW "Patterns & Optimization Opportunities" and BEFORE "Immutability":

**Files Touched**
```bash
cd ~/.claude/bin/activity-db && uv run python main.py query --sql "SELECT DISTINCT json_extract(metadata, '\$.file_path') AS file FROM activities WHERE date='YYYY-MM-DD' AND category='file_edit' ORDER BY file"
```
Render as a grouped list under "## Files Touched" — group by project folder where possible, show edit counts.

**Commands Run**
```bash
cd ~/.claude/bin/activity-db && uv run python main.py query --sql "SELECT json_extract(metadata, '\$.command') AS cmd, COUNT(*) AS n FROM activities WHERE date='YYYY-MM-DD' AND category='command' GROUP BY cmd ORDER BY n DESC LIMIT 20"
```
Render under "## Commands Run" — top distinct bash commands by frequency.

**Tool Usage Summary**
```bash
cd ~/.claude/bin/activity-db && uv run python main.py query --sql "SELECT json_extract(metadata, '\$.tool') AS tool, COUNT(*) AS n FROM activities WHERE date='YYYY-MM-DD' AND category IN ('tool_use','file_edit','command','mcp_call','plan') GROUP BY tool ORDER BY n DESC"
```
Render under "## Tool Usage" — inventory of tool invocations by type.

**MCP Calls by Server**
```bash
cd ~/.claude/bin/activity-db && uv run python main.py query --sql "SELECT json_extract(metadata, '\$.mcp_server') AS server, json_extract(metadata, '\$.mcp_tool') AS tool, COUNT(*) AS n FROM activities WHERE date='YYYY-MM-DD' AND category='mcp_call' GROUP BY server, tool ORDER BY n DESC LIMIT 15"
```
Render under "## MCP Calls".

Only include each section if it has rows. If enrichment returned no data for the day (e.g., transcripts were cleaned up or the sessions aren't in the DB), omit the transcript-derived sections entirely and add a one-line note at the end of the markdown: `> Transcript enrichment unavailable for this date (no session data or transcripts deleted).`

These sections get written both to the local `.md` file AND pushed to the Google Doc via the existing `--sync` path — the existing sync logic doesn't need any changes, since it just uploads whatever is in the markdown file.

### Immutability
**CRITICAL:** Before writing, check if the file already exists.
- If it exists: **DO NOT overwrite.** Tell the user and ask if they want to regenerate.
- If it doesn't exist: Write the new log.

### Auto brag doc update
After generating a daily log, **automatically** append new accomplishments to `~/.claude/daily-logs/BRAG-DOC.md`. Add entries under the appropriate project section. If a section doesn't exist for the project, create one. Update the Key Metrics table. Do NOT rewrite the entire brag doc — only append/update.

---

## Mode: Standup

Generate a copy-paste-ready standup message. Output directly to the user (don't write a file).

### Format
```
**Yesterday:**
- [concrete accomplishment 1 with project name]
- [concrete accomplishment 2]

**Today:**
- [inferred from open branches, recent PR activity, or last session's context]

**Blockers:**
- [any detected friction from yesterday — env issues, waiting on reviews]
- None (if no blockers detected)
```

### How to generate
1. Pull yesterday's prompts from history
2. Identify the top 3-5 accomplishments (PRs, commits, features, fixes)
3. For "Today": check what projects had activity late yesterday or have open PRs/branches. If unclear, list the top 2-3 projects the user has been most active on recently.
4. For "Blockers": look for unresolved friction — errors that weren't fixed, setup issues, questions left unanswered, prompts like "lets come back to this later" or "put on hold"

---

## Mode: Weekly Rollup

Generate `~/.claude/daily-logs/week-YYYY-WNN.md`.

### Content
```markdown
# Weekly Rollup — YYYY-WNN (Mon DD - Sun DD)

**Total prompts:** N across M days
**Projects touched:** list
**Peak day:** DayName (N prompts)
**Work:** Xh Ym (N prompts) | **Personal:** Xh Ym (N prompts)
```

#### Daily Summaries
One-paragraph summary per active day (pulled from existing daily logs or generated on the fly).

#### Week's Accomplishments
Aggregated from all daily Impact sections. Deduplicated. Grouped by project.

#### Cross-Day Patterns
Detect patterns that span multiple days:
- "Spent 3 days (Mar 1-3) debugging DB connection issues across project-a and project-b"
- "Context-switched between project-a and project-b every day this week"
- "Friction with Docker setup appeared on 2 separate days"

#### Week-over-Week Comparison
If previous week data exists, compare:
- Prompt volume change (%)
- Project focus shift
- New projects vs. continued projects
- Friction trend (up/down)

---

## Mode: Project Focus Report

Generate `~/.claude/daily-logs/project-<name>.md`.

### Content
```markdown
# Project Report — <project-name>

**Total prompts:** N across D days
**Date range:** first activity — last activity
**Peak day:** YYYY-MM-DD (N prompts)
```

#### Timeline
Chronological list of every day with activity on this project, with prompt count and 1-line summary.

#### All Accomplishments
Every impact item from daily logs related to this project, in chronological order.

#### All References
Every PR, Jira ticket, doc page, Google Doc ever referenced in this project's prompts.

#### Skills Used
Aggregated skill usage with counts.

#### Collaborating Projects
Other projects that were active on the same days (suggests related work or dependencies).

---

## Mode: Compare

Compare two time periods side-by-side.

### Supported comparisons
- `this-week last-week` — current vs previous week
- `this-month last-month` — current vs previous month
- `YYYY-MM-DD YYYY-MM-DD` — two specific dates
- `YYYY-WNN YYYY-WNN` — two specific weeks

### Output format (to screen, not file)
```markdown
## Comparison: [Period A] vs [Period B]

| Metric | Period A | Period B | Delta |
|---|---|---|---|
| Total prompts | N | N | +/-N (%) |
| Active days | N | N | +/-N |
| Projects touched | N | N | +/-N |
| Context switches | N | N | +/-N |
| Friction prompts | N | N | +/-N |
| Skills used | N | N | +/-N |

**Focus shift:**
- Period A top projects: X (N), Y (N), Z (N)
- Period B top projects: X (N), Y (N), Z (N)

**New in Period B:** projects that appear in B but not A
**Dropped from Period A:** projects that appear in A but not B
```

---

## Mode: Friction Tracker

Analyze ALL history for accumulated friction patterns. Write to `~/.claude/daily-logs/friction-report.md`.

### Friction categories
Scan all prompts for these friction signals:

| Category | Keywords/Patterns |
|---|---|
| **Environment setup** | docker, container, startup, install, setup, nix, devbox |
| **Auth/certs** | cert, certificate, permission, access denied, auth, credentials, token expired |
| **Build/deploy** | build fail, deploy, error, not working, still failing, CI red |
| **Data entry** | `[Pasted text`, `[Image`, manual copy-paste of logs/errors |
| **Tool issues** | MCP errors, tool not responding, plugin failed |
| **Branch/git** | wrong branch, wrong location, leaked changes, merge conflict |
| **Iteration tax** | "how's this look" repeated 3+ times in same session, back-and-forth refinement |

### Output format
```markdown
# Friction Report — Generated YYYY-MM-DD

## Top Friction Areas (by frequency)

### 1. [Category] — N occurrences across D days
**Days affected:** list of dates
**Examples:**
- [YYYY-MM-DD] "prompt excerpt showing the friction"
- [YYYY-MM-DD] "prompt excerpt"
**Suggested automation:** concrete suggestion

### 2. ...
```

### Recurring friction alert
If the same friction category appears on 3+ separate days, flag it prominently:
```
RECURRING FRICTION: [category] has appeared on N days. This is costing real time.
Suggested fix: [specific automation or runbook suggestion]
```

---

## Mode: Goals

Manage weekly goals stored in `~/.claude/daily-logs/goals.json`.

### File format
```json
{
  "weeks": {
    "2026-W13": {
      "goals": [
        {"text": "Ship API refactor PR", "status": "done", "completed": "2026-03-28"},
        {"text": "Review 3 team PRs", "status": "in-progress"},
        {"text": "Set up CI pipeline", "status": "open"}
      ]
    }
  }
}
```

### Subcommands
- `/daily-review goals` — Show current week's goals with status. Auto-detect progress by checking if related PRs were merged, commits were made, etc.
- `/daily-review goals set <text>` — Add a new goal to the current week
- `/daily-review goals done <text>` — Mark a goal as complete (fuzzy match on text)
- `/daily-review goals history` — Show goals from all weeks with completion rates

### Auto-progress detection
When showing goals, scan recent history for signals that a goal may be complete:
- If a goal mentions a PR and that PR URL appears in a "create pr" or "merge" prompt, suggest marking it done
- If a goal mentions a project and there were commits in that project, show progress indicator

---

## Mode: Heatmap

Generate a time-of-day activity visualization. Output to screen.

### Format
```
## Activity Heatmap — [period]

Hour  | Mon | Tue | Wed | Thu | Fri | Sat | Sun
------|-----|-----|-----|-----|-----|-----|-----
00-01 |  ·  |  ·  |  ·  |  ·  |  ·  |  ·  |  ·
01-02 |  ·  |  ·  |  ·  |  ·  |  ·  |  ·  |  ·
...
09-10 | ███ | ██· | ███ | ██· | █·· |  ·  |  ·
10-11 | ███ | ███ | ███ | ███ | ██· |  ·  |  ·
...
23-00 | ██· |  ·  | █·· | ██· |  ·  |  ·  | █·

Legend: · = 0  █ = 1-5  ██ = 6-15  ███ = 16+
```

Use block characters to represent density:
- ` · ` = 0 prompts
- ` █ ` = 1-5 prompts
- `██ ` = 6-15 prompts
- `███` = 16+ prompts

### Insights
Below the heatmap, add:
- **Peak hours:** "Most active 09:00-11:00 and 21:00-23:00"
- **Deep work windows:** "Longest uninterrupted blocks tend to happen [time range]"
- **Off-hours pattern:** "N% of prompts happen outside 9-6 business hours"

If a specific month is given (`/daily-review heatmap 2026-03`), scope to that month. Otherwise use all available data.

---

## Mode: Export

Output a daily log in alternative formats.

### JSON format (`/daily-review export YYYY-MM-DD json`)
```json
{
  "date": "2026-03-30",
  "total_prompts": 64,
  "projects": [
    {"name": "my-api", "prompts": 25, "first": "00:35", "last": "14:14"}
  ],
  "references": {
    "prs": ["https://..."],
    "docs": ["https://..."],
    "jira": ["PROJ-123"]
  },
  "impact": ["Created PR #123", "Fixed auth bug"],
  "friction": {"context_switches": 12, "paste_count": 5}
}
```

### Condensed format (`/daily-review export YYYY-MM-DD condensed`)
Single-line or short block suitable for Slack/Teams:
```
Mar 30: 64 prompts | 6 projects | my-api (25), my-frontend (14), shared-lib (10) | PRs: #123, #456 | Shipped: auth refactor, test fixtures
```

### Default
If no format specified, default to JSON.

---

## Mode: Brag Doc Regeneration

`/daily-review brag` regenerates the full `~/.claude/daily-logs/BRAG-DOC.md`.

Pull all data from history and existing daily logs. Structure:

1. **Executive Summary** — period, total stats, primary focus areas
2. **Major Accomplishments** — grouped by project, with PRs, Jira, details
3. **Key Metrics** — table with totals
4. **Weekly Trend** — table showing prompts/projects per week
5. **Top Skills Used** — with counts and purpose
6. **Growth & Patterns** — what went well, areas for improvement
7. **All References** — PRs, Jira, Docs, Repos

---

## Google Docs Sync

Daily review logs can be synced to a private Google Doc for cloud backup, searchability, and mobile access.

### Prerequisites

Google Docs sync requires an MCP server that provides Google Docs tools. You need tools for:
- **Creating** a Google Doc
- **Reading** a Google Doc
- **Writing/appending** to a Google Doc

Recommended MCP servers:
- [google-docs-mcp](https://github.com/nicholasoxford/google-docs-mcp) — Lightweight Google Docs MCP
- Any MCP server that exposes `create_document`, `read_document`, and `write_document` operations

If no Google Docs MCP tools are available, sync commands will be skipped with a helpful message telling the user to set up a Google Docs MCP server.

### Configuration

Doc IDs and URLs are stored in `~/.claude/daily-logs/gdoc-config.json`:
```json
{
  "daily_review": {
    "document_id": "DOC_ID_HERE",
    "title": "<full_name> - Daily Review Log",
    "url": "https://docs.google.com/document/d/DOC_ID_HERE/edit",
    "created": "2026-03-31"
  }
}
```

### Sync flags

| Flag | Description |
|---|---|
| `--sync` | After generating the daily log locally, also append it to the Google Doc |
| `--sync-all` | Bulk-push ALL existing local logs to the Google Doc (one-time backfill, skips dates already in doc) |
| `--sync-only` | Don't generate a new log, just sync an existing local log to Google Doc |
| `--force-sync` | Used with `--sync` to bypass the dedup check and sync even if the date already exists in the doc |

Examples:
- `/daily-review --sync` — generate today's log and sync to Google Doc
- `/daily-review 2026-03-28 --sync` — generate for a date and sync
- `/daily-review --sync-all` — push all existing logs to the doc
- `/daily-review standup --sync` — generate standup and append to doc
- `/daily-review week --sync` — generate weekly rollup and sync

### How sync works

1. **Check config:** Read `~/.claude/daily-logs/gdoc-config.json` for the `daily_review.document_id`
2. **Auto-create if missing:** If no doc ID exists, create one via Google Docs MCP with title `[username] - Daily Review Log`. Save the ID back to config.
3. **Read the local log:** Read the markdown content from `~/.claude/daily-logs/YYYY-MM-DD.md`
4. **Dedup check:** Before writing, read the Google Doc and check if an entry for this date already exists. Search for the header pattern `Daily Activity Log — YYYY-MM-DD` in the doc content.
   - **If the date already exists:** Skip the sync and tell the user: `"Skipped sync — entry for YYYY-MM-DD already exists in the Google Doc. Use --force-sync to overwrite."`
   - **If `--force-sync` is used and the date exists:** Proceed with the sync — insert the new content at the top.
   - **If the date does not exist:** Proceed normally with step 5.
5. **Append to Google Doc:** Write the full markdown content of the daily log with a horizontal rule separator between entries.
6. **Newest first:** Append new entries at the TOP of the doc (after the header) so the most recent day is always first.
7. **Confirm to user:** After a successful sync, print a confirmation message with the doc title and URL from `gdoc-config.json`.

### Sync-all (backfill)

When `--sync-all` is used:
1. Read all `~/.claude/daily-logs/YYYY-MM-DD.md` files
2. Sort by date (oldest first, so newest ends up on top after insertion)
3. For each file, insert its content at the top of the doc (after header)
4. Add a separator between each day
5. Report progress: "Synced N daily logs to Google Doc"

### Privacy

- Google Docs should be created as **private by default** — only the creator has access
- No sharing or link-sharing is enabled unless the user does it manually

### First-time sync for a user

If the skill runs and no doc is configured yet:
1. Check `~/.claude/daily-logs/gdoc-config.json` — if missing or no `daily_review` key
2. Create a new private Google Doc: `[their name] - Daily Review Log`
3. Save the doc ID to their local config
4. Continue with the sync

---

## File Locations

| File | Purpose | Mutable? |
|---|---|---|
| `~/.claude/daily-logs/YYYY-MM-DD.md` | Daily activity logs | Immutable (ask before overwriting) |
| `~/.claude/daily-logs/week-YYYY-WNN.md` | Weekly rollups | Immutable |
| `~/.claude/daily-logs/project-<name>.md` | Project reports | Regenerable (always overwrite) |
| `~/.claude/daily-logs/friction-report.md` | Friction analysis | Regenerable (always overwrite) |
| `~/.claude/daily-logs/goals.json` | Weekly goals | Mutable (user manages) |
| `~/.claude/daily-logs/gdoc-config.json` | Google Doc IDs for sync | Mutable (auto-managed) |
| `~/.claude/daily-logs/BRAG-DOC.md` | Consolidated brag doc | Regenerable or append-only |
| `~/.claude/history.jsonl` | Source data (read-only) | Never modify |

## Important Notes

- **Immutability:** Daily logs and weekly rollups are immutable — never modify without explicit permission
- **Real references only:** Extract URLs and Jira IDs from actual prompt text — never fabricate
- **Concrete impact:** Impact statements must be specific ("Shipped PR #652 with dry-run mode") not generic ("Created PRs")
- **Python for data:** Use Python via Bash tool for all history parsing and aggregation
- **Clean prompt text:** Remove `[Pasted text #N ...]` and `[Image #N]` markers, truncate to 150 chars
- **Dates:** Determine today's date from the system. Use the user's local timezone.
- **Google Docs sync:** When `--sync` is used, always write locally first, then sync. Local files are the source of truth. Google Doc is the backup/access layer.
