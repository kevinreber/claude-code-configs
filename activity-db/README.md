# activity-db

A lightweight CLI for storing Claude Code daily activity logs in SQLite, with optional [Turso](https://turso.tech) sync for cross-device access.

This is the storage backend for the `/daily-review-v2` and `/daily-recap-v2` skills. Without it, those skills cannot persist structured data. The v1 skills (`/daily-review`, `/daily-recap`) use plain markdown files and do **not** require this tool.

## Quick Start

```bash
# 1. Install the CLI
./install.sh          # copies to ~/.claude/bin/activity-db/

# 2. Initialize the database (local-only, no Turso needed)
cd ~/.claude/bin/activity-db && uv run python main.py init

# 3. Verify it works
cd ~/.claude/bin/activity-db && uv run python main.py stats
```

That's it for local-only usage. Turso sync is optional — see below.

## Prerequisites

### Required

| Dependency | Version | Install |
|---|---|---|
| **Python** | 3.13+ | `brew install python` or [python.org](https://www.python.org/downloads/) |
| **uv** | latest | `brew install uv` or `curl -LsSf https://astral.sh/uv/install.sh \| sh` |

### Optional (for cross-device sync)

| Dependency | Purpose | Install |
|---|---|---|
| **Turso CLI** | Create and manage Turso databases | `brew install tursodatabase/tap/turso` or `curl -sSfL https://get.tur.so/install.sh \| bash` |
| **Turso account** | Free tier is sufficient | `turso auth signup` |

## Installation

### Option A: Via install.sh (recommended)

From the repo root:
```bash
./install.sh --all        # installs everything including activity-db
# or
./install.sh --activity-db  # install just activity-db
```

### Option B: Manual

```bash
# Copy the CLI to ~/.claude/bin/activity-db/
mkdir -p ~/.claude/bin/activity-db
cp activity-db/main.py activity-db/pyproject.toml ~/.claude/bin/activity-db/

# Install Python dependencies
cd ~/.claude/bin/activity-db
uv sync

# Initialize the database
uv run python main.py init
```

This creates `~/.claude/activity.db` with the required tables.

## Turso Setup (Optional)

Turso gives you cross-device sync — your activity data is available on any machine. The free tier includes 500 databases and 9 GB storage, which is more than enough.

### Step 1: Install the Turso CLI

```bash
# macOS
brew install tursodatabase/tap/turso

# Linux / WSL
curl -sSfL https://get.tur.so/install.sh | bash
```

### Step 2: Sign up / log in

```bash
turso auth signup    # first time
# or
turso auth login     # returning user
```

This opens a browser for authentication.

### Step 3: Create a database

```bash
turso db create activity-db
```

Pick a region close to you for lower latency. The default (closest) is usually fine.

### Step 4: Get your credentials

```bash
# Database URL
turso db show activity-db --url

# Auth token (non-expiring for personal use)
turso db tokens create activity-db
```

### Step 5: Save credentials

Create `~/.claude/turso.env`:

```bash
cat > ~/.claude/turso.env << 'EOF'
TURSO_DATABASE_URL=libsql://<your-db-name>-<your-username>.turso.io
TURSO_AUTH_TOKEN=<your-auth-token>
EOF
```

Replace the placeholders with the values from Step 4.

**Important:** Keep this file private. It contains your database credentials.

```bash
chmod 600 ~/.claude/turso.env
```

### Step 6: Re-initialize with sync

```bash
cd ~/.claude/bin/activity-db && uv run python main.py init
```

This creates the tables both locally and on Turso. From now on, every write syncs automatically.

### Step 7: Verify sync

```bash
cd ~/.claude/bin/activity-db && uv run python main.py sync
```

If it prints `Synced to Turso.` without errors, you're set.

### Setting up a second device

On your new machine:

1. Install Python 3.13+ and `uv`
2. Clone this repo and run `./install.sh --activity-db`
3. Copy your `~/.claude/turso.env` from the first device (or re-generate the token with `turso db tokens create activity-db`)
4. Run `cd ~/.claude/bin/activity-db && uv run python main.py init`

The embedded replica will pull down all existing data on first connect.

## How It Works

activity-db uses [libsql](https://github.com/tursodatabase/libsql) (the Turso fork of SQLite) as an **embedded replica**:

- **Local-first:** All reads and writes go to `~/.claude/activity.db` on disk. It's fast and works offline.
- **Sync on write:** After each write, the CLI calls `conn.sync()` to push changes to Turso.
- **Sync on connect:** On startup, it pulls the latest state from Turso before reading.
- **Offline resilient:** If Turso is unreachable, the local DB still works. Changes sync next time you're online.

Without Turso credentials, it operates as a plain local SQLite database — no data is sent anywhere.

## Database Schema

### activities

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Auto-incrementing primary key |
| `date` | TEXT | ISO date (YYYY-MM-DD) |
| `category` | TEXT | Activity type (see below) |
| `source` | TEXT | Where the data came from (see below) |
| `title` | TEXT | Short description |
| `detail` | TEXT | Extended description (optional) |
| `url` | TEXT | Link to artifact (optional) |
| `metadata` | TEXT | JSON blob for extra data (optional) |
| `tag` | TEXT | `work` or `personal` (default: `work`) |
| `created_at` | TEXT | Timestamp of insertion |

**Categories:** `project_activity`, `skill_usage`, `accomplishment`, `pr`, `pr_review`, `commit`, `jira`, `jira_comment`, `gdoc`, `confluence`, `slack_thread`, `alert`, `reference`, `prompt`

**Sources:** `claude`, `github`, `jira`, `slack`, `confluence`, `gdocs`, `extracted`

### summaries

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Auto-incrementing primary key |
| `date` | TEXT | ISO date |
| `period` | TEXT | `daily`, `weekly`, `monthly`, `project` |
| `type` | TEXT | `review`, `recap`, `standup`, `brag` |
| `content` | TEXT | Full markdown content |
| `metadata` | TEXT | JSON blob (optional) |
| `created_at` | TEXT | Timestamp |

### goals

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Auto-incrementing primary key |
| `week` | TEXT | ISO week (e.g., `2026-W14`) |
| `text` | TEXT | Goal description |
| `status` | TEXT | `open`, `in-progress`, `done` |
| `completed` | TEXT | Completion date |
| `created_at` | TEXT | Timestamp |

## CLI Reference

```bash
cd ~/.claude/bin/activity-db

# Initialize database tables
uv run python main.py init

# Write an activity
uv run python main.py write \
  --date 2026-04-04 \
  --category project_activity \
  --source claude \
  --title "my-project" \
  --detail "Implemented auth middleware" \
  --tag work

# Write a summary
uv run python main.py summary \
  --date 2026-04-04 \
  --period daily \
  --type review \
  --content "# Daily Activity Log — 2026-04-04 ..."

# Query activities
uv run python main.py query --date 2026-04-04
uv run python main.py query --start 2026-04-01 --end 2026-04-04
uv run python main.py query --category pr --source github
uv run python main.py query --sql "SELECT * FROM activities WHERE title LIKE '%auth%'"
uv run python main.py query --date 2026-04-04 --format table

# Query summaries
uv run python main.py query-summaries --date 2026-04-04 --type review

# Backfill from existing markdown daily logs
uv run python main.py backfill

# Export a day as markdown
uv run python main.py export-md --date 2026-04-04

# Database stats
uv run python main.py stats

# Force sync to Turso
uv run python main.py sync
```

## Backfilling Existing Data

If you've been using `/daily-review` (v1) and have markdown logs in `~/.claude/daily-logs/`, you can import them:

```bash
cd ~/.claude/bin/activity-db && uv run python main.py backfill
```

This parses all `YYYY-MM-DD.md` files and inserts:
- Project activities with prompt counts and time ranges
- Skills used per project
- Extracted references (PRs, Jira tickets, docs)
- Impact/accomplishment statements
- The full markdown content as a summary

Backfill uses `INSERT OR IGNORE`, so it's safe to run multiple times.

## Troubleshooting

### `ModuleNotFoundError: No module named 'libsql_experimental'`

Run `uv sync` from the activity-db directory:
```bash
cd ~/.claude/bin/activity-db && uv sync
```

### `Error: unable to open database file`

The `~/.claude/` directory might not exist:
```bash
mkdir -p ~/.claude
```

### Turso sync errors / `Error connecting to remote database`

1. Check your credentials: `cat ~/.claude/turso.env`
2. Verify the database exists: `turso db show activity-db`
3. Verify your token: `turso db tokens create activity-db` (creates a new one if needed)
4. Check connectivity: `curl -s https://<your-db>.turso.io/health`

### `requires-python >= 3.13` but you have an older Python

Install Python 3.13+:
```bash
brew install python@3.13
# or
uv python install 3.13
```

### Works locally but doesn't sync

The CLI falls back to local-only mode silently when `~/.claude/turso.env` is missing or empty. Check that the file exists and has both `TURSO_DATABASE_URL` and `TURSO_AUTH_TOKEN` set.

## Security Notes

- `~/.claude/turso.env` contains your database token — don't commit it to git
- `~/.claude/activity.db` contains your activity history — it's local to your machine
- Turso databases are private by default — only your token can access them
- The free tier is single-tenant — your data is not shared with other users
- If you're concerned about cloud storage, skip Turso entirely — local-only mode works fine
