---
name: daily-recap-v2
description: "Full workday recap across all tools — Jira, GitHub, Slack, Confluence, Google Docs, and Claude Code activity. Stores all data in SQLite with Turso sync for remote access. For Claude-only activity tracking, use /daily-review-v2 instead."
user_invocable: true
---

# Daily Recap v2 (SQLite-backed)

Generate a comprehensive workday recap by pulling activity from all available sources — Jira, GitHub, Slack, Confluence, Google Docs, and Claude Code. Stores all collected data in SQLite with Turso sync for remote access.

## Key Difference from /daily-recap

This skill writes structured data to SQLite (`~/.claude/activity.db`) via the `activity-db` CLI instead of markdown files. Every activity from every source gets a database row, making cross-source and cross-time queries possible from any device.

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
uv run python main.py summary --date YYYY-MM-DD --period daily --type recap --content "..."

# Query activities
uv run python main.py query --date YYYY-MM-DD
uv run python main.py query --start YYYY-MM-DD --end YYYY-MM-DD --source jira
uv run python main.py query --sql "SELECT * FROM activities WHERE source = 'github' AND date = '2026-04-03'"

# Stats
uv run python main.py stats
```

### Categories
`project_activity`, `skill_usage`, `accomplishment`, `pr`, `pr_review`, `commit`, `jira`, `jira_comment`, `gdoc`, `confluence`, `slack_thread`, `alert`, `reference`, `prompt`

### Sources
`claude`, `github`, `jira`, `slack`, `confluence`, `gdocs`, `extracted`

## Prerequisites

- **MCP servers** for Jira, Slack, Confluence, and Google Docs are optional but recommended (see MCP Setup below)
- **GitHub CLI (`gh`)** for PR and commit activity (install via `brew install gh` or [cli.github.com](https://cli.github.com))
- Falls back gracefully — if a source fails, skip it and note the gap
- Claude Code history (`~/.claude/history.jsonl`) is always available as baseline

## MCP Setup (Optional)

To get the full cross-tool experience, configure MCP servers for the tools you use. Add them to your `~/.claude/mcp_servers.json` or Claude Desktop config.

**Recommended MCP servers:**
- **Jira:** Any MCP server that provides `search_jira_issues` and `get_jira_issue` tools
- **Slack:** Any MCP server that provides `search_slack` or `search_messages` tools
- **Confluence:** Any MCP server that provides `search_confluence` or `search_confluence_content` tools
- **Google Docs:** Any MCP server that provides `create_document`, `read_document`, and `write_document` tools

Without MCP servers, the recap will use GitHub CLI + Claude Code history, which still provides significant value.

## Subcommands

| Command | Description |
|---|---|
| `/daily-recap-v2` | Full recap for today |
| `/daily-recap-v2 YYYY-MM-DD` | Full recap for a specific date |
| `/daily-recap-v2 YYYY-MM-DD YYYY-MM-DD` | Recap for a date range |
| `/daily-recap-v2 sources` | Show which sources are available and authenticated |
| `/daily-recap-v2 insights` | Cross-tool optimization insights from recent recaps |

**Filters:**

| Flag | Description |
|---|---|
| `--work` | Only include work projects |
| `--personal` | Only include personal projects |

---

## How It Works

### Phase 1: Gather from all sources (parallel)

Fan out data collection across all sources **in parallel** using the Agent tool or sequential tool calls. For the target date(s), collect and write to DB:

#### Source 1: Claude Code (local — always available)

Read `~/.claude/history.jsonl` and filter for the target date. For each project:
```bash
uv run python main.py write \
  --date YYYY-MM-DD \
  --category project_activity \
  --source claude \
  --title "<project_name>" \
  --detail "<key activities>" \
  --metadata '{"prompts": N, "time_range": "HH:MM-HH:MM"}' \
  --tag work|personal
```

If a daily review already exists in DB, read it instead of regenerating:
```bash
uv run python main.py query-summaries --date YYYY-MM-DD --type review
```

#### Source 2: Jira (via MCP — optional)

If a Jira MCP server is available, search for tickets you interacted with. Use whichever Jira MCP tool is available (e.g., `search_jira_issues`) with JQL:
```
(assignee = currentUser() OR reporter = currentUser()) AND updated >= "YYYY-MM-DD" AND updated < "YYYY-MM-DD+1" ORDER BY updated DESC
```

For each ticket returned:
```bash
uv run python main.py write \
  --date YYYY-MM-DD \
  --category jira \
  --source jira \
  --title "<TICKET-KEY>: <summary>" \
  --detail "<action: created|updated|commented|transitioned>" \
  --url "<ticket_url>" \
  --metadata '{"status": "<status>", "priority": "<priority>", "action": "<action>"}' \
  --tag work
```

If the Jira MCP is not configured or the query fails, skip and continue.

#### Source 3: GitHub (via `gh` CLI)

Use the `gh` CLI via Bash tool:
```bash
# PRs created
gh pr list --author @me --state all --json number,title,state,url,createdAt,updatedAt,repository

# PRs reviewed
gh api search/issues --method GET -f q="is:pr reviewed-by:@me updated:YYYY-MM-DD"

# Commits per active project
cd <project-path> && git log --author="<full_name>" --since="YYYY-MM-DD" --until="YYYY-MM-DD+1" --oneline
```

For each PR:
```bash
uv run python main.py write \
  --date YYYY-MM-DD \
  --category pr \
  --source github \
  --title "#<number>: <title>" \
  --detail "<state>" \
  --url "<pr_url>" \
  --metadata '{"repo": "<repo>", "state": "<state>"}' \
  --tag work
```

For each commit:
```bash
uv run python main.py write \
  --date YYYY-MM-DD \
  --category commit \
  --source github \
  --title "<commit message>" \
  --detail "<repo>" \
  --metadata '{"repo": "<repo>", "sha": "<hash>"}' \
  --tag work|personal
```

#### Source 4: Confluence (via MCP — optional)

If a Confluence MCP server is available, search for pages you created or edited. Use whichever Confluence MCP tool is available (e.g., `search_confluence_content`):
```
query: "<full_name>" OR "<username>"
limit: 10
```

For each page:
```bash
uv run python main.py write \
  --date YYYY-MM-DD \
  --category confluence \
  --source confluence \
  --title "<page_title>" \
  --detail "<space> — <action: created|edited|viewed>" \
  --url "<page_url>" \
  --tag work
```

If Confluence MCP is not configured, skip and continue.

#### Source 5: Slack (via MCP — optional)

If a Slack MCP server is available, search for threads you participated in. Use whichever Slack MCP tool is available (e.g., `search_slack`):
```
query: "<username>"
limit: 15
```

For each thread:
```bash
uv run python main.py write \
  --date YYYY-MM-DD \
  --category slack_thread \
  --source slack \
  --title "<channel>: <topic summary>" \
  --detail "<role: initiated|responded>" \
  --tag work
```

If Slack MCP is not configured, skip and continue.

#### Source 6: Google Docs (via MCP — optional)

Check Claude history for Google Doc URLs. For each:
```bash
uv run python main.py write \
  --date YYYY-MM-DD \
  --category gdoc \
  --source gdocs \
  --title "<document_title>" \
  --detail "<action: created|edited>" \
  --url "<doc_url>" \
  --tag work
```

If Google Docs MCP is not configured, just list the URLs found in prompts without fetching titles.

---

### Phase 2: Build unified timeline from DB

Query all activities for the date:
```bash
uv run python main.py query --date YYYY-MM-DD --format json
```

Merge into chronological timeline. Each entry has: Time, Source, Action, Details, URL.

---

### Phase 3: Generate the recap

Generate markdown output for the terminal AND store as summary.

```markdown
# Daily Recap — YYYY-MM-DD (DayName)

**Sources queried:** Jira [check] | GitHub [check] | Slack [check] | Confluence [check] | Google Docs [check] | Claude Code [check]
**Total activities:** N across M sources
**Work:** Xh Ym (N prompts) | **Personal:** Xh Ym (N prompts)

---

## Unified Timeline

### Morning (before 12:00)
| Time | Source | Activity |
|---|---|---|
| 09:21 | Claude | Discussed auth refactor in my-api |
| 09:35 | Jira | Updated PROJ-123 — changed status to In Progress |
| 09:42 | Slack | Posted in #engineering about API changes |

### Afternoon (12:00 - 17:00)
...

### Evening (after 17:00)
...

---

## By Source

### Jira
| Ticket | Summary | Action | Status |
|---|---|---|---|
| [PROJ-123](url) | Auth middleware refactor | Updated, commented | In Progress |

### GitHub
| PR/Commit | Repo | Action | Status |
|---|---|---|---|

### Confluence / Slack / Google Docs / Claude Code
(same format as /daily-recap)

---

## Impact & Accomplishments

Cross-tool impact statements connecting activities across sources.

---

## Cross-Tool Insights

### Workflow Efficiency
### Automation Candidates
### Time Allocation
```

### Phase 4: Store the recap summary

```bash
uv run python main.py summary \
  --date YYYY-MM-DD \
  --period daily \
  --type recap \
  --content "<full markdown output>"
```

### Phase 5: Immutability check

Before writing, check if a recap summary already exists:
```bash
uv run python main.py query-summaries --date YYYY-MM-DD --type recap
```
If exists, ask before overwriting.

### Phase 6: Update brag doc

Append cross-tool accomplishments to `~/.claude/daily-logs/BRAG-DOC.md`.

---

## Subcommand: Sources

`/daily-recap-v2 sources` — Check which sources are available:

1. Test GitHub: `gh auth status`
2. Test Jira: Check if a Jira MCP tool is available, run a simple query
3. Test Slack: Check if a Slack MCP tool is available, run a simple query
4. Test Confluence: Check if a Confluence MCP tool is available, run a simple query
5. Test Google Docs: Check if a Google Docs MCP tool is available
6. Claude Code: always available (local file)

Output:
```
Source Status:
  Claude Code  [check] always available
  GitHub       [check] authenticated (gh cli)
  Jira         [check] MCP server configured
  Slack        [x] no MCP server found
  Google Docs  [x] no MCP server found
  Confluence   [x] no MCP server found
```

---

## Subcommand: Insights

`/daily-recap-v2 insights` — Query recent activities across sources for cross-tool patterns:

```bash
uv run python main.py query --start <7_days_ago> --end <today> --format json
```

Analyze for:
1. Repeated cross-tool workflows
2. Tool underutilization
3. Context fragmentation
4. Jira hygiene
5. Communication patterns

---

## Error Handling

- If no external MCP servers are available and `gh` is not installed, fall back to Claude-only mode and suggest running `/daily-review-v2` instead
- If individual sources fail, skip and mark with [x] in output
- Never let a single source failure block the entire recap
- Report which sources succeeded and which failed

## Important Notes

- **activity-db is the single write path** — all source data goes through the CLI
- **Every source activity gets its own row** — this is the key advantage over markdown
- **Terminal output is still markdown** — same format as `/daily-recap`
- **SQLite is the source of truth** — queryable, syncable, structured
- **Parallel collection** — fan out tool calls in parallel where possible
- **Graceful degradation** — always produce output even if some sources fail
- **Real data only** — never fabricate activity
- **Privacy aware** — only include Slack threads where the user participated
- **Run activity-db from its directory:** Always `cd ~/.claude/bin/activity-db && uv run python main.py <command>`
