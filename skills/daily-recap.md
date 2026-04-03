---
name: daily-recap
description: "Full workday recap across all tools — Jira, GitHub, Slack, and Claude Code activity. Pulls activity from multiple sources into a unified timeline. For Claude-only activity tracking, use /daily-review instead."
user_invocable: true
---

# Daily Recap

Generate a comprehensive workday recap by pulling activity from all available sources — not just Claude Code, but GitHub, Jira, Slack, and more. Produces a unified view of everything you did in a day.

## User Identity Resolution

Before starting, resolve the current user's identity dynamically:
- **Full name:** Run `git config user.name`
- **Username:** Run `whoami`
- **Email:** Run `git config user.email`

Use these values everywhere the skill references the user's name or email. Never hardcode a specific user's identity.

## Prerequisites

This skill works best with external tool integrations but degrades gracefully:
- **GitHub CLI (`gh`)** — for PR and commit activity (install via `brew install gh` or [cli.github.com](https://cli.github.com))
- **Jira MCP server** — for ticket activity (optional, see MCP Setup below)
- **Slack MCP server** — for message/thread activity (optional, see MCP Setup below)
- **Google Docs MCP server** — for document activity and sync (optional, see MCP Setup below)
- **Claude Code history** (`~/.claude/history.jsonl`) — always available as the baseline

If a source fails (auth, timeout, not configured), skip it and note the gap. Never let a single source failure block the entire recap.

## MCP Setup (Optional)

To get the full cross-tool experience, configure MCP servers for the tools you use. Add them to your `~/.claude/mcp_servers.json` or Claude Desktop config.

**Recommended MCP servers:**
- **Jira:** Any MCP server that provides `search_jira_issues` and `get_jira_issue` tools
- **Slack:** Any MCP server that provides `search_slack` or `search_messages` tools
- **Google Docs:** Any MCP server that provides `create_document`, `read_document`, and `write_document` tools
- **Confluence:** Any MCP server that provides `search_confluence` tools

Without MCP servers, the recap will use GitHub CLI + Claude Code history, which still provides significant value.

## Subcommands

| Command | Description |
|---|---|
| `/daily-recap` | Full recap for today |
| `/daily-recap YYYY-MM-DD` | Full recap for a specific date |
| `/daily-recap YYYY-MM-DD YYYY-MM-DD` | Recap for a date range |
| `/daily-recap sources` | Show which sources are available and authenticated |
| `/daily-recap insights` | Cross-tool optimization insights from recent recaps |

**Filters** (can be combined with any subcommand):

| Flag | Description |
|---|---|
| `--work` | Only include work projects (applies to Claude Code source and git commits) |
| `--personal` | Only include personal projects (applies to Claude Code source and git commits) |

---

## How It Works

### Phase 1: Gather from all sources (parallel)

Fan out data collection across all sources **in parallel** using the Agent tool or sequential tool calls. For the target date(s), collect:

#### Source 1: Claude Code (local — always available)
Read `~/.claude/history.jsonl` and filter for the target date. Extract:
- Prompts with timestamps, projects, session IDs
- Skills used
- URLs and references mentioned in prompts
- Tag each project as `personal` or `work` (personal if path contains `/personal/`, work otherwise)

If a daily log already exists at `~/.claude/daily-logs/YYYY-MM-DD.md`, read it instead of regenerating.

#### Source 2: GitHub (via `gh` CLI)
Use the `gh` CLI via Bash tool to pull your activity:
```bash
# PRs you created or updated
gh pr list --author @me --state all --json number,title,state,url,createdAt,updatedAt,repository

# PRs you reviewed
gh api search/issues --method GET -f q="is:pr reviewed-by:@me updated:YYYY-MM-DD"

# Your commits across repos (check each active project)
# For each project in Claude history, run:
cd <project-path> && git log --author="<full_name>" --since="YYYY-MM-DD" --until="YYYY-MM-DD+1" --oneline
```

Capture:
- PRs created with title, status, URL
- PRs reviewed with title, URL
- Commits pushed with repo, message, hash

#### Source 3: Jira (via MCP — optional)
If a Jira MCP server is available, search for tickets you interacted with:
```
JQL: (assignee = currentUser() OR reporter = currentUser()) AND updated >= "YYYY-MM-DD" AND updated < "YYYY-MM-DD+1" ORDER BY updated DESC
```

For each ticket returned, capture:
- Issue key, summary, status, priority
- Whether you created it, updated it, commented on it, or transitioned it
- Link to the ticket

If the Jira MCP is not configured or the query fails, note it in the output and continue.

#### Source 4: Slack (via MCP — optional)
If a Slack MCP server is available, search for threads you participated in:
```
query: "<username>"
limit: 15
```

Focus on:
- Threads where you asked questions or provided answers
- Announcements you posted
- Review discussions

Capture:
- Channel name, thread topic/summary
- Whether you initiated or responded

If Slack MCP is not configured, skip and continue.

#### Source 5: Google Docs (via MCP — optional)
Check if any Google Doc URLs appeared in Claude Code prompts that day. For each one, use the Google Docs MCP to get the title and verify it was worked on.

Capture:
- Document title, URL
- Whether created or edited

If Google Docs MCP is not configured, just list the URLs found in prompts without fetching titles.

---

### Phase 2: Build unified timeline

Merge all source data into a single chronological timeline. Each entry has:
- **Time** (HH:MM or approximate)
- **Source** (Claude, GitHub, Jira, Slack, Docs)
- **Action** (created, updated, reviewed, commented, committed, searched, etc.)
- **Details** (ticket key, PR title, page name, etc.)
- **URL** (link to the artifact)

Sort by time. Group nearby activities into logical work blocks.

---

### Phase 3: Generate the recap

Write to `~/.claude/daily-logs/recap-YYYY-MM-DD.md`:

```markdown
# Daily Recap — YYYY-MM-DD (DayName)

**Sources queried:** GitHub ✓ | Jira ✓ | Slack ✗ | Google Docs ✗ | Claude Code ✓
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
| 10:01 | Claude | Drafted migration script |
| 10:15 | GitHub | Opened PR #456 on my-api |

### Afternoon (12:00 - 17:00)
...

### Evening (after 17:00)
...

---

## By Source

### GitHub
| PR/Commit | Repo | Action | Status |
|---|---|---|---|
| [#456](url) | my-api | Created | Open |
| [#123](url) | shared-lib | Reviewed comments | Merged |

**Commits:**
- `my-api` — 3 commits: "feat: add auth middleware", "fix: token validation", "test: add auth tests"
- `my-frontend` — 1 commit: "fix: update API client"

### Jira
| Ticket | Summary | Action | Status |
|---|---|---|---|
| [PROJ-123](url) | Auth middleware refactor | Updated, commented | In Progress |
| [PROJ-456](url) | API versioning | Created | Open |

### Slack
| Channel | Topic | Role |
|---|---|---|
| #engineering | API changes announcement | Initiated thread |
| #code-review | PR review feedback | Responded |

### Google Docs
| Document | Action |
|---|---|
| [Architecture RFC](url) | Created and iterated |

### Claude Code
(Link to daily log if it exists)
See detailed breakdown: [YYYY-MM-DD.md](./YYYY-MM-DD.md)

---

## Impact & Accomplishments

Write **specific, cross-tool impact statements** that connect activities across sources:
- "Shipped PR #456 (GitHub) for auth refactor, linked to PROJ-123 (Jira), announced in #engineering (Slack)"
- "Created test fixtures for shared-lib (GitHub commits), tested locally (Claude), pushed updates (GitHub)"

These cross-tool connections are the unique value of the recap vs. the daily review.

---

## Cross-Tool Insights

Analyze the day's activity for optimization opportunities that span tools:

### Workflow Efficiency
- **Jira <-> GitHub gap:** "Updated 3 Jira tickets but only linked 1 to a PR. Auto-linking could save time."
- **Manual context switching:** "You copy-pasted external content into Claude 3 times. Could streamline with integrations."
- **PR descriptions:** "Your PR descriptions reference Jira tickets by key but don't deep-link."

### Automation Candidates
- **Status sync:** "You transitioned 2 tickets to In Progress after opening PRs. Could automate: PR opened -> ticket moves to In Progress."
- **Standup generation:** "You have Jira updates + GitHub commits + Slack announcements — a standup could auto-generate from these."
- **Review routing:** "You reviewed 3 PRs today. If these are recurring (same repos), consider a review queue."

### Time Allocation
- **By source:** "45% Claude, 25% GitHub, 15% Jira, 10% Slack, 5% Docs"
- **By project:** "60% my-api, 20% shared-lib, 15% my-frontend, 5% other"
- **Deep work vs. coordination:** "3 hours deep coding (Claude+GitHub), 1.5 hours coordination (Slack+Jira), 0.5 hours docs"
```

---

### Phase 4: Immutability check

Same rules as `/daily-review`:
- Check if `recap-YYYY-MM-DD.md` exists before writing
- If it exists, ask before overwriting
- Daily logs (`YYYY-MM-DD.md`) are never touched by this skill

### Phase 5: Update brag doc

After generating the recap, append cross-tool accomplishments to `~/.claude/daily-logs/BRAG-DOC.md`. These are higher-signal than Claude-only accomplishments because they capture the full picture.

---

## Subcommand: Sources

`/daily-recap sources` — Check which sources are available:

1. Test GitHub: `gh auth status`
2. Test Jira: Check if a Jira MCP tool is available, run a simple query
3. Test Slack: Check if a Slack MCP tool is available, run a simple query
4. Test Google Docs: Check if a Google Docs MCP tool is available
5. Claude Code: always available (local file)

Output:
```
Source Status:
  Claude Code  ✓ always available
  GitHub       ✓ authenticated (gh cli)
  Jira         ✓ MCP server configured
  Slack        ✗ no MCP server found
  Google Docs  ✗ no MCP server found
```

---

## Subcommand: Insights

`/daily-recap insights` — Analyze recent recaps (last 7 days) for cross-tool patterns:

Read all `recap-*.md` files from the last 7 days and look for:

1. **Repeated cross-tool workflows** — "Every day you: update Jira -> code in Claude -> push PR -> post in Slack. This 4-step sequence could be a single workflow."
2. **Tool underutilization** — "You referenced 5 wiki pages this week but never updated them with code changes."
3. **Context fragmentation** — "You pasted external messages into Claude 12 times this week. Average 2x/day."
4. **Jira hygiene** — "3 tickets you worked on still show status 'Open' despite having merged PRs."
5. **Communication patterns** — "You announced changes in 2 different channels. Could consolidate."

Output to screen (not file) as actionable recommendations.

---

## Error Handling

- If no external tools are available (no MCP, no `gh`), fall back to Claude-only mode and suggest the user run `/daily-review` instead
- If individual sources fail (auth expired, timeout), skip that source and mark it with ✗ in the output
- Never let a single source failure block the entire recap
- Report which sources succeeded and which failed at the top of the recap

## Google Docs Sync

Daily recaps can be synced to a private Google Doc for cloud backup and access.

### Prerequisites

Requires a Google Docs MCP server (see MCP Setup section above).

### Configuration

Uses the same config file as `/daily-review`: `~/.claude/daily-logs/gdoc-config.json`, under the `daily_recap` key.

### Sync flags

| Flag | Description |
|---|---|
| `--sync` | After generating the recap locally, also append it to the Google Doc |
| `--sync-all` | Bulk-push ALL existing local recap files to the Google Doc (one-time backfill, skips dates already in doc) |
| `--sync-only` | Don't generate a new recap, just sync an existing local recap to Google Doc |
| `--force-sync` | Used with `--sync` to bypass the dedup check and sync even if the date already exists in the doc |

Examples:
- `/daily-recap --sync` — generate today's recap and sync to Google Doc
- `/daily-recap 2026-03-30 --sync` — generate for a date and sync
- `/daily-recap --sync-all` — push all existing recaps to the doc

### How sync works

1. **Check config:** Read `~/.claude/daily-logs/gdoc-config.json` for the `daily_recap.document_id`
2. **Auto-create if missing:** If no doc ID exists, create one via Google Docs MCP with title `[username] - Daily Recap Log`. Save the ID back to config.
3. **Read the local recap:** Read the markdown content from `~/.claude/daily-logs/recap-YYYY-MM-DD.md`
4. **Dedup check:** Before writing, read the Google Doc and check if an entry for this date already exists. Search for the header pattern `Daily Recap — YYYY-MM-DD` in the doc content.
   - **If the date already exists:** Skip the sync and tell the user: `"Skipped sync — recap for YYYY-MM-DD already exists in the Google Doc. Use --force-sync to overwrite."`
   - **If `--force-sync` is used and the date exists:** Proceed with the sync — insert the new content at the top.
   - **If the date does not exist:** Proceed normally with step 5.
5. **Append to Google Doc:** Write the full markdown content of the recap with a horizontal rule separator between entries.
6. **Newest first:** Insert new entries at the TOP of the doc (after the header) so the most recent day is always first.
7. **Confirm to user:** After a successful sync, print a confirmation message with the doc title and URL.

### Privacy

- Google Docs should be created as **private by default** — only the creator has access
- No sharing or link-sharing is enabled unless the user does it manually

---

## File Locations

| File | Purpose | Mutable? |
|---|---|---|
| `~/.claude/daily-logs/recap-YYYY-MM-DD.md` | Full workday recaps | Immutable (ask before overwriting) |
| `~/.claude/daily-logs/YYYY-MM-DD.md` | Claude-only daily logs (read by recap, never written) | Owned by /daily-review |
| `~/.claude/daily-logs/gdoc-config.json` | Google Doc IDs for sync | Mutable (auto-managed) |
| `~/.claude/daily-logs/BRAG-DOC.md` | Consolidated brag doc (appended to) | Append-only |

## Important Notes

- **Parallel collection:** Fan out tool calls in parallel wherever possible to minimize wait time
- **Graceful degradation:** Always produce output even if some sources fail
- **Real data only:** Never fabricate activity — only report what the tools actually return
- **Privacy aware:** Slack search results may include other people's messages. Only include threads where the user participated.
- **Rate limiting:** Don't spam MCP tools. One call per source per date is usually sufficient.
- **Cross-referencing:** The unique value of this skill is connecting dots across tools. Always look for activities that span multiple sources and call them out.
- **Relationship to /daily-review:** This skill reads from but never writes to daily log files. It produces its own `recap-*` files. The two skills are complementary.
- **Google Docs sync:** When `--sync` is used, always write locally first, then sync. Local files are the source of truth. Google Doc is the backup/access layer.
