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
# Write an activity (device_id auto-detected from hostname; override with --device-id)
uv run python main.py write --date YYYY-MM-DD --category <category> --source <source> --title "..." [--detail "..."] [--url "..."] [--metadata '{}'] [--tag work|personal] [--device-id <hostname>]

# Write a summary (versioned — re-runs append a new version instead of overwriting; scoped by device_id)
uv run python main.py summary --date YYYY-MM-DD --period daily --type recap --content "..." [--device-id <hostname>]

# Query activities
uv run python main.py query --date YYYY-MM-DD
uv run python main.py query --start YYYY-MM-DD --end YYYY-MM-DD --source jira
uv run python main.py query --sql "SELECT * FROM activities WHERE source = 'github' AND date = '2026-04-03'"

# Query summaries (defaults to latest version; use --all-versions for history, --version N for a specific one)
uv run python main.py query-summaries --date YYYY-MM-DD --type recap

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

### Transcript-derived sections (requires prior enrichment)

Before rendering, run `uv run python main.py enrich-from-transcripts --date YYYY-MM-DD` to ensure today's sessions have transcript-derived rows. Then include the following sections. Only include each if there's data. If no enrichment data exists, skip all silently.

**Files Touched**
```bash
uv run python main.py query --sql "SELECT json_extract(metadata, '$.file_path') AS file_path, COUNT(*) AS edits FROM activities WHERE date='YYYY-MM-DD' AND category='file_edit' GROUP BY file_path ORDER BY edits DESC"
```
Render as a list grouped by project/repo, with edit counts. Strip the home directory prefix for readability. Only include source code and meaningful files — skip temp files (`/tmp/*`), lock files, and `.pyc`. Correlate with GitHub PRs / commits touching the same files when possible.

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
Correlate with Jira/Confluence/Google Docs actions seen from the respective MCP sources — this connects "what Claude did locally" with "what shows up in external systems."

---

## Impact & Accomplishments

Write **specific, concrete impact statements** — not echoed prompts. Every accomplishment should answer "what changed and why it matters."

Rules:
- **Never** echo back the user's prompt text as an accomplishment.
- Detect concrete outcomes: PR shipped/reviewed, bug fixed, feature implemented, investigation completed, decision made, doc written, tooling improved.
- Each statement should follow the pattern: **What** was done + **why it matters** or **what it unblocked**.
- On light days (< 10 prompts), write 1-2 real statements or omit the section entirely. A short day with no concrete output should say "Light session — exploratory/setup work, no shipped artifacts."
- On heavy days, cap at 6-8 statements — pick the ones with real impact, not every small edit.
- Cross-reference across sources when possible: "Shipped PR #428 (GitHub) to resolve MI-18790 (Jira) after debugging via Observe dashboard".

---

## Critical Review

This is the most important section. Be **brutally honest** — the user specifically wants highly critical, insightful feedback that helps them optimize how they work. Don't sugarcoat.

Since the recap has cross-tool data, this review should be richer than the daily-review version. Analyze across all sources:

**Time & Focus**
- How fragmented was the day? Count project switches across all tools (Claude, GitHub, Jira, Slack). More than 5 switches in a 3-hour block = thrashing.
- Were there long gaps between activities? Did Slack interrupt deep work? Did PR reviews break flow?
- Did any project get less than 15 minutes? Was the context switch worth it?
- Was there a deep work block (2+ hours)? If not, flag it.

**Output vs. Effort**
- Compare total activity count to concrete output (PRs shipped, tickets closed, decisions made). High activity with low output = spinning wheels.
- Were there repeated attempts at the same thing? Quantify and identify root cause.
- Cross-tool inefficiency: did the user manually paste Slack/Jira/Confluence content that MCP could have fetched? Each paste is wasted effort.

**Decision Quality**
- Signs of indecision recurring across multiple prompts on the same topic?
- Scope creep? Started on X, ended up doing Y, Z.
- Going in circles? Same question rephrased, or reverted changes.

**Cross-Tool Friction**
- Did tool switching create overhead? (e.g., copying URLs between GitHub and Jira, manually syncing status)
- Were there manual coordination steps that should be automated? (e.g., updating a Google Doc after every PR, posting in Slack after deploys)
- Missing integrations that would have saved time?

**Automation & Process**
- What manual work could be automated?
- Missing skills, tools, or scripts? Be specific.
- Work that could be delegated to CI/CD, cron, or a background process?

**Compared to Recent Days**
- Query the last 7 days: `SELECT date, COUNT(*) FROM activities WHERE date >= date('YYYY-MM-DD', '-7 days') GROUP BY date`
- Is today above or below trend? Is the project mix shifting?
- Are the same friction points recurring?

Format as a numbered list of specific, actionable observations. Each item:
1. **The observation** — what you noticed, with data
2. **Why it matters** — the cost of not addressing it
3. **What to do about it** — a concrete next step

Aim for 3-6 items. Quality over quantity. Skip only if the day was under 5 prompts.
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

### Phase 6: Write to Obsidian vault

If the brain-vault repo exists at `~/Projects/brain-vault/`, save the generated markdown to `Activity/`.

**File naming depends on device:**
- Detect device type by checking `hostname`:
  - If hostname contains `.linkedin.biz` or matches the work laptop pattern → **work** device
  - Otherwise → **personal** device
- **Work device** file names (default, no suffix):
  - `Activity/recap-YYYY-MM-DD.md`
- **Personal device** file names (suffixed):
  - `Activity/recap-YYYY-MM-DD-personal.md`

**Frontmatter** — always include:
```yaml
---
type: activity
date: YYYY-MM-DD
period: daily
subtype: recap
device: work|personal
tags:
  - activity
  - daily-recap
---
```

**Do NOT overwrite** — if the target file already exists, skip this step silently. The vault file is a snapshot; regeneration updates the DB summary (versioned), not the vault file.

**Wikilinks** — wrap all project names in `[[wikilinks]]` (e.g., `[[brain-vault]]`, `[[neo-workflow]]`) so Obsidian graph view and backlinks connect activity logs to project notes.

### Phase 7: Capture Knowledge & Concepts

Scan the day's activity for **non-obvious technical knowledge** that would be valuable to recall later. Look for:

- Problems solved with non-obvious solutions (workarounds, debugging insights, architecture decisions)
- Integration patterns (how tool A connects to tool B)
- Configuration details that took time to figure out
- "TIL" moments — things the user learned and might forget

For each knowledge item found, check if a relevant note already exists in:
- `Projects/<project>.md` — if the knowledge is project-specific, append it to the project note's `## Notes` section
- `Concepts/<slug>.md` — if it's a reusable concept across projects (e.g., "n8n workflow patterns", "Fly.io deployment", "Gmail API authentication")

**Creating a new Concept note** (only for cross-project knowledge):
```yaml
---
type: concept
status: active
tags:
  - concept
  - <relevant-tech>
first_seen: YYYY-MM-DD
---

# <Concept Title>

## What
1-2 sentence definition.

## How
Step-by-step or key details worth remembering.

## Learned from
- [[project-name]] on YYYY-MM-DD — <context>

## Related
- [[other-concept]]
- [[related-project]]
```

**Do NOT create low-value concepts.** Only create them for knowledge that:
- Took more than 5 minutes to figure out
- Would save future-you time if you could look it up
- Applies to more than one project

### Phase 8: Update Career Artifacts

The recap has cross-tool context (PRs, Jira, meetings) that makes it best positioned to maintain resume-ready material.

**Append to `~/Projects/brain-vault/Career/accomplishments.md`** (create if missing):
```yaml
---
type: career
---

# Accomplishments Log

Searchable record of shipped work, organized for resume/portfolio use.
```

Each entry:
```markdown
### YYYY-MM-DD — <title>
- **Impact:** What changed and why it matters (1-2 sentences, resume-ready language)
- **Tech:** Technologies, tools, frameworks used
- **Skills demonstrated:** e.g., system design, debugging, automation, cross-team coordination
- **Artifacts:** PR links, doc links, dashboard links
- **Project:** [[project-name]]
```

Only add entries for **concrete shipped output** — PRs merged, features deployed, incidents resolved, workflows created. Skip exploratory/WIP/planning work.

**Tag with skill categories** so the user can later query things like:
- "What have I built with n8n?" → filter by Tech containing n8n
- "Show me all my infrastructure work" → filter by Skills containing deployment/infrastructure
- "What content creation skills do I have?" → filter by Skills containing automation, video, content pipeline
- "Draft a resume for a DevOps role" → filter by Skills containing CI/CD, deployment, monitoring, infrastructure

### Phase 9: Update brag doc

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
