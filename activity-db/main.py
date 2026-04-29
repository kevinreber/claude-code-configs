#!/usr/bin/env python3
"""activity-db: CLI for managing daily activity logs in SQLite with Turso sync."""

import argparse
import datetime
import json
import os
import re
import sys
from pathlib import Path

import platform
import socket

import libsql_experimental as libsql

# Paths
CLAUDE_DIR = Path.home() / ".claude"
ENV_FILE = CLAUDE_DIR / "turso.env"
DB_FILE = CLAUDE_DIR / "activity.db"
DAILY_LOGS_DIR = CLAUDE_DIR / "daily-logs"


def get_device_id():
    """Return a stable identifier for this machine.

    Uses the hostname, which is already used in the sessions table
    (e.g. 'kreber-mn1802.linkedin.biz' for work, 'kevinrebers-MacBook-Pro.local' for personal).
    """
    return socket.gethostname()


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
            device_id TEXT NOT NULL DEFAULT '',
            created_at TEXT DEFAULT (datetime('now')),
            UNIQUE(date, category, source, title, device_id)
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
            device_id TEXT NOT NULL DEFAULT '',
            created_at TEXT DEFAULT (datetime('now')),
            UNIQUE(date, period, type, version, device_id)
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

    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            date TEXT NOT NULL,
            project TEXT NOT NULL,
            project_path TEXT NOT NULL,
            prompt_count INTEGER NOT NULL DEFAULT 0,
            duration_minutes INTEGER NOT NULL DEFAULT 0,
            is_personal INTEGER NOT NULL DEFAULT 0,
            device_id TEXT NOT NULL DEFAULT '',
            first_prompt_at TEXT NOT NULL,
            last_prompt_at TEXT NOT NULL,
            metadata TEXT,
            enriched_at TEXT,
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
    conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_date ON sessions(date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_session_id ON sessions(session_id)")

    conn.commit()
    conn.sync()
    print("Database initialized at", DB_FILE)
    print("Tables: activities, summaries, goals, sessions")


def cmd_write(args):
    """Insert an activity row."""
    conn = get_connection()
    device_id = args.device_id or get_device_id()

    try:
        conn.execute(
            """INSERT OR IGNORE INTO activities (date, category, source, title, detail, url, metadata, tag, device_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (args.date, args.category, args.source, args.title,
             args.detail, args.url, args.metadata, args.tag or "work", device_id),
        )
        conn.commit()
        conn.sync()
        print(f"Wrote activity: [{args.source}] {args.category} — {args.title} (device: {device_id})")
    except Exception as e:
        print(f"Error writing activity: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_summary(args):
    """Insert a new versioned summary. Existing summaries for the same (date, period, type, device_id)
    are preserved — a new version is appended instead of overwriting."""
    conn = get_connection()
    device_id = args.device_id or get_device_id()

    # Compute next version for this (date, period, type, device_id).
    cur = conn.execute(
        """SELECT COALESCE(MAX(version), 0) + 1 FROM summaries
           WHERE date = ? AND period = ? AND type = ? AND device_id = ?""",
        (args.date, args.period, args.type, device_id),
    )
    next_version = cur.fetchone()[0]

    conn.execute(
        """INSERT INTO summaries (date, period, type, content, metadata, version, device_id)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (args.date, args.period, args.type, args.content, args.metadata, next_version, device_id),
    )
    conn.commit()
    conn.sync()
    if next_version == 1:
        print(f"Saved {args.period} {args.type} summary for {args.date} (v1, device: {device_id})")
    else:
        print(f"Saved {args.period} {args.type} summary for {args.date} (v{next_version}, {next_version - 1} prior version(s) preserved, device: {device_id})")


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


def _ingest_orphan_transcript(conn, transcript_path, session_id):
    """Create a sessions row for a transcript that has no DB entry yet.

    Derives date, project, first/last prompt times from the transcript itself.
    Returns the new sessions.id, or None if the transcript can't be read.
    """
    from datetime import datetime
    first_ts = None
    last_ts = None
    project_path = ""
    prompt_count = 0
    try:
        with open(transcript_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                ts = obj.get("timestamp")
                if isinstance(ts, str):
                    if first_ts is None:
                        first_ts = ts
                    last_ts = ts
                if obj.get("type") == "user":
                    prompt_count += 1
                # cwd hints at project path
                if not project_path:
                    pp = obj.get("cwd") or (obj.get("message", {}) if isinstance(obj.get("message"), dict) else {}).get("cwd")
                    if isinstance(pp, str):
                        project_path = pp
    except Exception:
        return None
    if not first_ts:
        return None

    # Derive date (local) from first timestamp
    try:
        ts_norm = first_ts[:-1] + "+00:00" if first_ts.endswith("Z") else first_ts
        date = datetime.fromisoformat(ts_norm).astimezone().strftime("%Y-%m-%d")
    except Exception:
        date = first_ts[:10]

    project = project_path.rstrip("/").split("/")[-1] if project_path else "<unknown>"
    cur = conn.execute(
        """INSERT INTO sessions (session_id, date, project, project_path, prompt_count,
                                 duration_minutes, is_personal, device_id,
                                 first_prompt_at, last_prompt_at, metadata)
           VALUES (?, ?, ?, ?, ?, 0, 0, '', ?, ?, ?)""",
        (
            session_id,
            date,
            project,
            project_path,
            prompt_count,
            first_ts,
            last_ts or first_ts,
            json.dumps({"source": "enrich-from-transcripts/orphan-ingest"}),
        ),
    )
    return cur.lastrowid


def cmd_enrich_from_transcripts(args):
    """Parse per-session transcripts and write structured events into the activities table.

    Sources: ~/.claude/projects/<proj-hash>/<session-id>.jsonl
    Targets: activities table (new rows with category in tool_use|file_edit|command|mcp_call|plan|paste)

    Tracks processed sessions via sessions.enriched_at to avoid double-processing.
    Also ingests orphan transcripts (disk file exists but no sessions row) by creating
    sessions rows from transcript metadata, unless --no-orphans is set.
    """
    import glob
    from pathlib import Path

    # Late import so bare imports of main.py don't force this dependency to exist
    from transcript_parser import parse_transcript

    conn = get_connection()

    # Build an index of transcript files: session_id → path
    projects_root = CLAUDE_DIR / "projects"
    transcript_index = {}
    for p in glob.glob(str(projects_root / "*" / "*.jsonl")):
        p = Path(p)
        transcript_index[p.stem] = p
    print(f"Found {len(transcript_index)} transcript files on disk")

    # Optionally ingest orphan transcripts as new sessions rows
    orphans_ingested = 0
    if not args.no_orphans and not args.session:
        db_sessions = set(
            r[0] for r in conn.execute("SELECT session_id FROM sessions").fetchall()
        )
        orphan_ids = [sid for sid in transcript_index if sid not in db_sessions]
        if orphan_ids:
            print(f"Ingesting {len(orphan_ids)} orphan transcripts as sessions...")
            for sid in orphan_ids:
                new_id = _ingest_orphan_transcript(conn, transcript_index[sid], sid)
                if new_id:
                    orphans_ingested += 1
            conn.commit()
            print(f"  Ingested {orphans_ingested} new session rows")

    # Gather target sessions from the sessions table
    where = ["1=1"]
    params = []
    if args.session:
        where.append("session_id = ?")
        params.append(args.session)
    if args.date:
        where.append("date = ?")
        params.append(args.date)
    if args.since:
        where.append("date >= ?")
        params.append(args.since)
    if not args.force:
        where.append("enriched_at IS NULL")

    sql = f"SELECT id, session_id, date FROM sessions WHERE {' AND '.join(where)} ORDER BY date ASC, id ASC"
    target_sessions = conn.execute(sql, tuple(params)).fetchall()
    print(f"Sessions to enrich: {len(target_sessions)}")

    if not target_sessions:
        return

    device_id = get_device_id()
    total_events = 0
    sessions_processed = 0
    sessions_skipped_missing = 0

    for row in target_sessions:
        session_pk, session_id, session_date = row[0], row[1], row[2]
        transcript = transcript_index.get(session_id)
        if transcript is None:
            sessions_skipped_missing += 1
            continue

        # Buffer all events for this session, then batch-insert
        rows_to_insert = []
        for ev in parse_transcript(transcript, session_id=session_id):
            metadata_json = json.dumps(ev["metadata"]) if ev["metadata"] is not None else None
            rows_to_insert.append((
                ev["date"],
                ev["category"],
                ev["source"],
                ev["title"],
                ev["detail"],
                ev["url"],
                metadata_json,
                ev["tag"],
                device_id,
            ))

        events_for_session = 0
        if rows_to_insert:
            try:
                conn.executemany(
                    """INSERT OR IGNORE INTO activities
                       (date, category, source, title, detail, url, metadata, tag, device_id)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    rows_to_insert,
                )
                events_for_session = len(rows_to_insert)
            except Exception as e:
                print(f"  error batch-writing session {session_id}: {e}", file=sys.stderr)

        # Mark session as enriched
        conn.execute(
            "UPDATE sessions SET enriched_at = datetime('now') WHERE id = ?",
            (session_pk,),
        )
        conn.commit()
        total_events += events_for_session
        sessions_processed += 1

        if sessions_processed % 5 == 0:
            print(f"  processed {sessions_processed}/{len(target_sessions)} sessions, {total_events} events so far", flush=True)

    conn.sync()
    print(f"\nEnrichment complete:")
    print(f"  Orphan transcripts ingested: {orphans_ingested}")
    print(f"  Sessions processed: {sessions_processed}")
    print(f"  Sessions skipped (transcript file missing): {sessions_skipped_missing}")
    print(f"  Total events written: {total_events}")


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

    device_id = get_device_id()
    print(f"Found {len(log_files)} daily log files to backfill... (device: {device_id})")
    total_activities = 0
    total_summaries = 0

    for log_file in log_files:
        date = log_file.stem
        content = log_file.read_text()

        # Store the full log as a summary
        try:
            conn.execute(
                """INSERT OR IGNORE INTO summaries (date, period, type, content, device_id)
                   VALUES (?, 'daily', 'review', ?, ?)""",
                (date, content, device_id),
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
                       (date, category, source, title, detail, metadata, tag, device_id)
                       VALUES (?, 'project_activity', 'claude', ?, ?, ?, ?, ?)""",
                    (date, project_name, detail, metadata, tag, device_id),
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
                               (date, category, source, title, detail, tag, device_id)
                               VALUES (?, 'skill_usage', 'claude', ?, ?, ?, ?)""",
                            (date, skill, project_name, tag, device_id),
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
                       (date, category, source, title, url, tag, device_id)
                       VALUES (?, ?, 'extracted', ?, ?, 'work', ?)""",
                    (date, cat, url.split("/")[-1][:100], url, device_id),
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
                       (date, category, source, title, tag, device_id)
                       VALUES (?, 'jira', 'extracted', ?, 'work', ?)""",
                    (date, ticket, device_id),
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
                           (date, category, source, title, tag, device_id)
                           VALUES (?, 'accomplishment', 'claude', ?, 'work', ?)""",
                        (date, item[:200], device_id),
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
    write_p.add_argument("--device-id", dest="device_id", default=None,
                         help="Override device identifier (default: hostname)")

    # summary
    summary_p = subparsers.add_parser("summary", help="Insert/update a summary")
    summary_p.add_argument("--date", required=True)
    summary_p.add_argument("--period", required=True, choices=["daily", "weekly", "monthly", "project"])
    summary_p.add_argument("--type", required=True, choices=["review", "recap", "standup", "brag"])
    summary_p.add_argument("--content", required=True)
    summary_p.add_argument("--metadata", default=None)
    summary_p.add_argument("--device-id", dest="device_id", default=None,
                           help="Override device identifier (default: hostname)")

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

    # enrich-from-transcripts
    enrich_p = subparsers.add_parser(
        "enrich-from-transcripts",
        help="Parse per-session transcripts and write events to activities"
    )
    enrich_p.add_argument("--session", default=None, help="Enrich only the given session_id")
    enrich_p.add_argument("--date", default=None, help="Enrich only sessions from this date")
    enrich_p.add_argument("--since", default=None, help="Enrich sessions on or after this date")
    enrich_p.add_argument("--force", action="store_true",
                          help="Re-enrich even if already done (default: skip already-enriched sessions)")
    enrich_p.add_argument("--no-orphans", action="store_true",
                          help="Skip creating sessions rows for transcripts that have no DB entry yet")

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
        "enrich-from-transcripts": cmd_enrich_from_transcripts,
        "export-md": cmd_export_md,
    }

    commands[args.command](args)


if __name__ == "__main__":
    main()
