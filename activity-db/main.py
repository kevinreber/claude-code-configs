#!/usr/bin/env python3
"""activity-db: CLI for managing daily activity logs in SQLite with Turso sync."""

import argparse
import datetime
import json
import os
import re
import sys
from pathlib import Path

import libsql_experimental as libsql

# Paths
CLAUDE_DIR = Path.home() / ".claude"
ENV_FILE = CLAUDE_DIR / "turso.env"
DB_FILE = CLAUDE_DIR / "activity.db"
DAILY_LOGS_DIR = CLAUDE_DIR / "daily-logs"


def load_env():
    """Load Turso credentials from env file."""
    env = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def get_connection(sync_on_connect=True):
    """Get a libsql connection with embedded replica + Turso sync."""
    env = load_env()
    url = env.get("TURSO_DATABASE_URL", "")
    token = env.get("TURSO_AUTH_TOKEN", "")

    if url and token:
        conn = libsql.connect(
            str(DB_FILE),
            sync_url=url,
            auth_token=token,
        )
        if sync_on_connect:
            conn.sync()
    else:
        # Local-only fallback
        conn = libsql.connect(str(DB_FILE))

    return conn


def cmd_init(args):
    """Create database tables."""
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            source TEXT NOT NULL,
            title TEXT NOT NULL,
            detail TEXT,
            url TEXT,
            metadata TEXT,
            tag TEXT DEFAULT 'work',
            created_at TEXT DEFAULT (datetime('now')),
            UNIQUE(date, category, source, title)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            period TEXT NOT NULL,
            type TEXT NOT NULL,
            content TEXT NOT NULL,
            metadata TEXT,
            version INTEGER NOT NULL DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now')),
            UNIQUE(date, period, type, version)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            week TEXT NOT NULL,
            text TEXT NOT NULL,
            status TEXT DEFAULT 'open',
            completed TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # Indexes for common queries
    conn.execute("CREATE INDEX IF NOT EXISTS idx_activities_date ON activities(date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_activities_source ON activities(source)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_activities_category ON activities(category)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_activities_tag ON activities(tag)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_summaries_date ON summaries(date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_summaries_type ON summaries(type)")

    conn.commit()
    conn.sync()
    print("Database initialized at", DB_FILE)
    print("Tables: activities, summaries, goals")


def cmd_write(args):
    """Insert an activity row."""
    conn = get_connection()

    try:
        conn.execute(
            """INSERT OR IGNORE INTO activities (date, category, source, title, detail, url, metadata, tag)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (args.date, args.category, args.source, args.title,
             args.detail, args.url, args.metadata, args.tag or "work"),
        )
        conn.commit()
        conn.sync()
        print(f"Wrote activity: [{args.source}] {args.category} — {args.title}")
    except Exception as e:
        print(f"Error writing activity: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_summary(args):
    """Insert a new versioned summary. Existing summaries for the same (date, period, type)
    are preserved — a new version is appended instead of overwriting."""
    conn = get_connection()

    # Compute next version for this (date, period, type).
    cur = conn.execute(
        """SELECT COALESCE(MAX(version), 0) + 1 FROM summaries
           WHERE date = ? AND period = ? AND type = ?""",
        (args.date, args.period, args.type),
    )
    next_version = cur.fetchone()[0]

    conn.execute(
        """INSERT INTO summaries (date, period, type, content, metadata, version)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (args.date, args.period, args.type, args.content, args.metadata, next_version),
    )
    conn.commit()
    conn.sync()
    if next_version == 1:
        print(f"Saved {args.period} {args.type} summary for {args.date} (v1)")
    else:
        print(f"Saved {args.period} {args.type} summary for {args.date} (v{next_version}, {next_version - 1} prior version(s) preserved)")


def cmd_query(args):
    """Query activities and return JSON."""
    conn = get_connection()

    if args.sql:
        cursor = conn.execute(args.sql)
        cols = [d[0] for d in cursor.description]
        rows = cursor.fetchall()
        results = [dict(zip(cols, row)) for row in rows]
    else:
        where_clauses = []
        params = []

        if args.date:
            where_clauses.append("date = ?")
            params.append(args.date)
        if args.start and args.end:
            where_clauses.append("date >= ? AND date <= ?")
            params.extend([args.start, args.end])
        if args.category:
            where_clauses.append("category = ?")
            params.append(args.category)
        if args.source:
            where_clauses.append("source = ?")
            params.append(args.source)
        if args.tag:
            where_clauses.append("tag = ?")
            params.append(args.tag)

        where = " AND ".join(where_clauses) if where_clauses else "1=1"
        sql = f"SELECT * FROM activities WHERE {where} ORDER BY date, category, source"

        cursor = conn.execute(sql, tuple(params))
        cols = [d[0] for d in cursor.description]
        rows = cursor.fetchall()
        results = [dict(zip(cols, row)) for row in rows]

    if args.format == "table":
        if not results:
            print("No results.")
            return
        keys = list(results[0].keys())
        widths = {k: max(len(k), max(len(str(r.get(k, ""))) for r in results)) for k in keys}
        header = " | ".join(k.ljust(widths[k]) for k in keys)
        sep = "-+-".join("-" * widths[k] for k in keys)
        print(header)
        print(sep)
        for r in results:
            print(" | ".join(str(r.get(k, "")).ljust(widths[k]) for k in keys))
    else:
        print(json.dumps(results, indent=2))

    print(f"\n({len(results)} rows)", file=sys.stderr)


def cmd_query_summaries(args):
    """Query summaries and return JSON. Defaults to the latest version per (date, period, type);
    use --all-versions to see history, or --version N to pin a specific version."""
    conn = get_connection()

    where_clauses = []
    params = []

    if args.date:
        where_clauses.append("date = ?")
        params.append(args.date)
    if args.start and args.end:
        where_clauses.append("date >= ? AND date <= ?")
        params.extend([args.start, args.end])
    if args.period:
        where_clauses.append("period = ?")
        params.append(args.period)
    if args.type:
        where_clauses.append("type = ?")
        params.append(args.type)
    if args.version is not None:
        where_clauses.append("version = ?")
        params.append(args.version)

    where = " AND ".join(where_clauses) if where_clauses else "1=1"

    if args.all_versions or args.version is not None:
        sql = f"SELECT * FROM summaries WHERE {where} ORDER BY date DESC, version DESC"
    else:
        # Default: only the latest version per (date, period, type).
        sql = f"""
            SELECT s.* FROM summaries s
            INNER JOIN (
                SELECT date, period, type, MAX(version) AS max_v
                FROM summaries WHERE {where}
                GROUP BY date, period, type
            ) m ON s.date = m.date AND s.period = m.period AND s.type = m.type AND s.version = m.max_v
            ORDER BY s.date DESC
        """
        # Params appear twice when using the subquery, duplicate them
        params = params + params if params else params

    cursor = conn.execute(sql, tuple(params))
    cols = [d[0] for d in cursor.description]
    rows = cursor.fetchall()
    results = [dict(zip(cols, row)) for row in rows]

    print(json.dumps(results, indent=2))
    print(f"\n({len(results)} rows)", file=sys.stderr)


def cmd_sync(args):
    """Force a sync to Turso."""
    conn = get_connection()
    conn.sync()
    print("Synced to Turso.")


def cmd_stats(args):
    """Show database statistics."""
    conn = get_connection()

    activity_count = conn.execute("SELECT COUNT(*) FROM activities").fetchone()[0]
    summary_count = conn.execute("SELECT COUNT(*) FROM summaries").fetchone()[0]
    goal_count = conn.execute("SELECT COUNT(*) FROM goals").fetchone()[0]

    date_range = conn.execute(
        "SELECT MIN(date), MAX(date) FROM activities"
    ).fetchone()

    sources = conn.execute(
        "SELECT source, COUNT(*) as cnt FROM activities GROUP BY source ORDER BY cnt DESC"
    ).fetchall()

    categories = conn.execute(
        "SELECT category, COUNT(*) as cnt FROM activities GROUP BY category ORDER BY cnt DESC"
    ).fetchall()

    print(f"Database: {DB_FILE}")
    print(f"Activities: {activity_count}")
    print(f"Summaries: {summary_count}")
    print(f"Goals: {goal_count}")
    if date_range[0]:
        print(f"Date range: {date_range[0]} — {date_range[1]}")
    print()
    if sources:
        print("By source:")
        for source, cnt in sources:
            print(f"  {source}: {cnt}")
    print()
    if categories:
        print("By category:")
        for cat, cnt in categories:
            print(f"  {cat}: {cnt}")


def cmd_backfill(args):
    """Parse existing .md daily logs and insert into DB."""
    conn = get_connection(sync_on_connect=False)

    if not DAILY_LOGS_DIR.exists():
        print("No daily-logs directory found.", file=sys.stderr)
        sys.exit(1)

    log_files = sorted(DAILY_LOGS_DIR.glob("????-??-??.md"))
    if not log_files:
        print("No daily log files found.", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(log_files)} daily log files to backfill...")
    total_activities = 0
    total_summaries = 0

    for log_file in log_files:
        date = log_file.stem
        content = log_file.read_text()

        # Store the full log as a summary
        try:
            conn.execute(
                """INSERT OR IGNORE INTO summaries (date, period, type, content)
                   VALUES (?, 'daily', 'review', ?)""",
                (date, content),
            )
            total_summaries += 1
        except Exception:
            pass

        # Parse header for metadata
        prompts_match = re.search(r"\*\*Total prompts:\*\*\s*(\d+)", content)
        total_prompts = int(prompts_match.group(1)) if prompts_match else 0

        active_hours_match = re.search(r"\*\*Active hours:\*\*\s*(.+)", content)
        active_hours = active_hours_match.group(1).strip() if active_hours_match else ""

        est_time_match = re.search(r"\*\*Estimated active time:\*\*\s*(.+)", content)
        est_time = est_time_match.group(1).strip() if est_time_match else ""

        # Parse projects
        project_blocks = re.findall(
            r"### (.+?)\s*\((\d+) prompts?,\s*(.+?)\)\s*\n(.*?)(?=\n### |\n---|\Z)",
            content,
            re.DOTALL,
        )

        for project_name, prompt_count, time_range, block_content in project_blocks:
            tag = "personal" if "personal" in project_name.lower() else "work"

            activities = re.findall(r"^- (.+)$", block_content, re.MULTILINE)
            key_activities = [
                a for a in activities
                if not a.startswith("**") and not a.startswith("http") and "more prompts" not in a
            ]

            metadata = json.dumps({
                "prompts": int(prompt_count),
                "time_range": time_range,
                "total_day_prompts": total_prompts,
                "active_hours": active_hours,
                "estimated_time": est_time,
            })

            detail = "\n".join(key_activities[:10]) if key_activities else None

            try:
                conn.execute(
                    """INSERT OR IGNORE INTO activities
                       (date, category, source, title, detail, metadata, tag)
                       VALUES (?, 'project_activity', 'claude', ?, ?, ?, ?)""",
                    (date, project_name, detail, metadata, tag),
                )
                total_activities += 1
            except Exception:
                pass

            # Extract skills
            skills_match = re.search(r"\*\*Skills used:\*\*\s*(.+)", block_content)
            if skills_match:
                skills = [s.strip() for s in skills_match.group(1).split(",")]
                for skill in skills:
                    try:
                        conn.execute(
                            """INSERT OR IGNORE INTO activities
                               (date, category, source, title, detail, tag)
                               VALUES (?, 'skill_usage', 'claude', ?, ?, ?)""",
                            (date, skill, project_name, tag),
                        )
                        total_activities += 1
                    except Exception:
                        pass

        # Extract references (URLs and Jira tickets)
        urls = re.findall(r"https?://[^\s\)]+", content)
        for url in set(urls):
            cat = "reference"
            if "github.com" in url and "/pull/" in url:
                cat = "pr"
            elif "atlassian.net/browse/" in url:
                cat = "jira"
            elif "docs.google.com" in url:
                cat = "gdoc"
            elif "confluence" in url or "atlassian.net/wiki" in url:
                cat = "confluence"

            try:
                conn.execute(
                    """INSERT OR IGNORE INTO activities
                       (date, category, source, title, url, tag)
                       VALUES (?, ?, 'extracted', ?, ?, 'work')""",
                    (date, cat, url.split("/")[-1][:100], url),
                )
                total_activities += 1
            except Exception:
                pass

        # Extract Jira ticket IDs (only if a URL wasn't already captured)
        jira_tickets = set(re.findall(r"\b([A-Z]+-\d{3,6})\b", content))
        for ticket in jira_tickets:
            try:
                conn.execute(
                    """INSERT OR IGNORE INTO activities
                       (date, category, source, title, tag)
                       VALUES (?, 'jira', 'extracted', ?, 'work')""",
                    (date, ticket),
                )
                total_activities += 1
            except Exception:
                pass

        # Parse impact section
        impact_section = re.search(
            r"## Impact & Accomplishments\s*\n(.*?)(?=\n## |\n---|\Z)",
            content,
            re.DOTALL,
        )
        if impact_section:
            impact_items = re.findall(r"^- (.+)$", impact_section.group(1), re.MULTILINE)
            for item in impact_items:
                try:
                    conn.execute(
                        """INSERT OR IGNORE INTO activities
                           (date, category, source, title, tag)
                           VALUES (?, 'accomplishment', 'claude', ?, 'work')""",
                        (date, item[:200]),
                    )
                    total_activities += 1
                except Exception:
                    pass

    conn.commit()
    conn.sync()
    print(f"Backfill complete: {total_activities} activities, {total_summaries} summaries from {len(log_files)} files")


def cmd_export_md(args):
    """Export a day's activities as markdown."""
    conn = get_connection()

    # Check for stored summary first
    row = conn.execute(
        "SELECT content FROM summaries WHERE date = ? AND type = 'review'",
        (args.date,),
    ).fetchone()

    if row:
        print(row[0])
        return

    # Generate from activities
    cursor = conn.execute(
        "SELECT * FROM activities WHERE date = ? ORDER BY category, source",
        (args.date,),
    )
    cols = [d[0] for d in cursor.description]
    activities = [dict(zip(cols, row)) for row in cursor.fetchall()]

    if not activities:
        print(f"No data for {args.date}", file=sys.stderr)
        sys.exit(1)

    # Group by source
    by_source = {}
    for r in activities:
        by_source.setdefault(r["source"], []).append(r)

    day_name = datetime.date.fromisoformat(args.date).strftime("%A")
    print(f"# Activity Export — {args.date} ({day_name})\n")
    print(f"**Total activities:** {len(activities)}\n")

    for source, items in sorted(by_source.items()):
        print(f"## {source.title()}")
        for item in items:
            line = f"- **[{item['category']}]** {item['title']}"
            if item.get("url"):
                line += f" — [{item['url']}]({item['url']})"
            if item.get("detail"):
                line += f"\n  {item['detail'][:150]}"
            print(line)
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Manage daily activity logs in SQLite with Turso sync"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init
    subparsers.add_parser("init", help="Create database tables")

    # write
    write_p = subparsers.add_parser("write", help="Insert an activity")
    write_p.add_argument("--date", required=True)
    write_p.add_argument("--category", required=True)
    write_p.add_argument("--source", required=True)
    write_p.add_argument("--title", required=True)
    write_p.add_argument("--detail", default=None)
    write_p.add_argument("--url", default=None)
    write_p.add_argument("--metadata", default=None)
    write_p.add_argument("--tag", default="work")

    # summary
    summary_p = subparsers.add_parser("summary", help="Insert/update a summary")
    summary_p.add_argument("--date", required=True)
    summary_p.add_argument("--period", required=True, choices=["daily", "weekly", "monthly", "project"])
    summary_p.add_argument("--type", required=True, choices=["review", "recap", "standup", "brag"])
    summary_p.add_argument("--content", required=True)
    summary_p.add_argument("--metadata", default=None)

    # query
    query_p = subparsers.add_parser("query", help="Query activities")
    query_p.add_argument("--sql", default=None, help="Raw SQL query")
    query_p.add_argument("--date", default=None)
    query_p.add_argument("--start", default=None)
    query_p.add_argument("--end", default=None)
    query_p.add_argument("--category", default=None)
    query_p.add_argument("--source", default=None)
    query_p.add_argument("--tag", default=None)
    query_p.add_argument("--format", default="json", choices=["json", "table"])

    # query-summaries
    qsum_p = subparsers.add_parser("query-summaries", help="Query summaries (defaults to latest version)")
    qsum_p.add_argument("--date", default=None)
    qsum_p.add_argument("--start", default=None)
    qsum_p.add_argument("--end", default=None)
    qsum_p.add_argument("--period", default=None)
    qsum_p.add_argument("--type", default=None)
    qsum_p.add_argument("--version", type=int, default=None, help="Return a specific version")
    qsum_p.add_argument("--all-versions", action="store_true", help="Return all versions, not just the latest")

    # sync
    subparsers.add_parser("sync", help="Force sync to Turso")

    # stats
    subparsers.add_parser("stats", help="Show database statistics")

    # backfill
    subparsers.add_parser("backfill", help="Parse existing .md logs into DB")

    # export-md
    export_p = subparsers.add_parser("export-md", help="Export a day as markdown")
    export_p.add_argument("--date", required=True)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "init": cmd_init,
        "write": cmd_write,
        "summary": cmd_summary,
        "query": cmd_query,
        "query-summaries": cmd_query_summaries,
        "sync": cmd_sync,
        "stats": cmd_stats,
        "backfill": cmd_backfill,
        "export-md": cmd_export_md,
    }

    commands[args.command](args)


if __name__ == "__main__":
    main()
