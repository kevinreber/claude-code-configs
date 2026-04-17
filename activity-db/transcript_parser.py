"""Parser for ~/.claude/projects/<hash>/<session-id>.jsonl transcript files.

Streams line-by-line and extracts structured events suitable for the `activities`
table: tool uses, file edits, bash commands, MCP calls, plan entries, pastes.

Does NOT inline bash output, paste content, or assistant responses — only metadata
(names, paths, timestamps, commands) to protect sensitive data.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Iterator


# Tool name buckets → (category, title_builder)
FILE_EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}


def _iso_to_local_hhmmss(iso_ts: str) -> str:
    """Convert an ISO timestamp to local HH:MM:SS. Falls back to the raw string."""
    try:
        # Python 3.11+ fromisoformat handles trailing Z
        if iso_ts.endswith("Z"):
            iso_ts = iso_ts[:-1] + "+00:00"
        dt = datetime.fromisoformat(iso_ts).astimezone()
        return dt.strftime("%H:%M:%S")
    except Exception:
        return iso_ts[-8:] if len(iso_ts) >= 8 else iso_ts


def _iso_to_local_date(iso_ts: str) -> str:
    """Convert an ISO timestamp to local YYYY-MM-DD."""
    try:
        if iso_ts.endswith("Z"):
            iso_ts = iso_ts[:-1] + "+00:00"
        dt = datetime.fromisoformat(iso_ts).astimezone()
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return iso_ts[:10]


def _mcp_server_and_tool(tool_name: str) -> tuple[str, str]:
    """Parse `mcp__<server>__<tool>` into (server, tool). Tool name may contain underscores."""
    # e.g. mcp__github__create_issue → ("github", "create_issue")
    parts = tool_name.split("__", 2)
    if len(parts) == 3:
        return parts[1], parts[2]
    return "unknown", tool_name


def _short_path(file_path: str) -> str:
    """Return the last 2 segments of a path for compact titles."""
    if not file_path:
        return ""
    parts = file_path.rstrip("/").split("/")
    return "/".join(parts[-2:]) if len(parts) >= 2 else file_path


def _event_from_tool_use(
    block: dict,
    turn_timestamp: str,
    session_id: str,
    date: str,
) -> dict | None:
    """Convert one tool_use block into an activity-ready event dict.

    Returns a dict with keys: date, category, source, title, detail, url, metadata, tag
    — matching the activities table columns and the `write` CLI command.
    Returns None if the block should be skipped.
    """
    name = block.get("name", "")
    inp = block.get("input") or {}
    hhmmss = _iso_to_local_hhmmss(turn_timestamp)

    base_metadata = {
        "tool": name,
        "session_id": session_id,
        "timestamp": turn_timestamp,
    }

    if name == "Bash":
        cmd = (inp.get("command") or "").strip()
        cmd_summary = cmd[:80] + ("…" if len(cmd) > 80 else "")
        meta = {**base_metadata, "command": cmd, "description": inp.get("description")}
        return {
            "date": date,
            "category": "command",
            "source": "claude",
            "title": f"Bash: {cmd_summary} @ {hhmmss}",
            "detail": inp.get("description"),
            "url": None,
            "metadata": meta,
            "tag": "work",
        }

    if name in FILE_EDIT_TOOLS:
        fp = inp.get("file_path") or inp.get("notebook_path") or ""
        sp = _short_path(fp)
        meta = {**base_metadata, "file_path": fp}
        return {
            "date": date,
            "category": "file_edit",
            "source": "claude",
            "title": f"{name}: {sp} @ {hhmmss}",
            "detail": None,
            "url": f"file://{fp}" if fp else None,
            "metadata": meta,
            "tag": "work",
        }

    if name.startswith("mcp__"):
        server, mcp_tool = _mcp_server_and_tool(name)
        meta = {**base_metadata, "mcp_server": server, "mcp_tool": mcp_tool, "input_keys": list(inp.keys())[:8]}
        return {
            "date": date,
            "category": "mcp_call",
            "source": "claude",
            "title": f"mcp.{server}.{mcp_tool} @ {hhmmss}",
            "detail": None,
            "url": None,
            "metadata": meta,
            "tag": "work",
        }

    if name == "EnterPlanMode":
        meta = {**base_metadata}
        return {
            "date": date,
            "category": "plan",
            "source": "claude",
            "title": f"EnterPlanMode @ {hhmmss}",
            "detail": None,
            "url": None,
            "metadata": meta,
            "tag": "work",
        }

    # Everything else (Read, Glob, Grep, ToolSearch, Agent, Skill, Task*, etc.)
    meta = {**base_metadata}
    return {
        "date": date,
        "category": "tool_use",
        "source": "claude",
        "title": f"{name} @ {hhmmss}",
        "detail": None,
        "url": None,
        "metadata": meta,
        "tag": "work",
    }


def _event_from_paste(
    line_obj: dict,
    session_id: str,
    date: str,
) -> dict | None:
    """Convert a paste attachment into an activity event. Never inlines content."""
    paste_id = line_obj.get("id") or line_obj.get("attachmentId") or "unknown"
    # Heuristic: if line has a filename referencing paste-cache, use that
    url = None
    content_meta = line_obj.get("content") or {}
    if isinstance(content_meta, dict):
        maybe_file = content_meta.get("path") or content_meta.get("file")
        if maybe_file and "paste-cache" in str(maybe_file):
            url = f"file://{maybe_file}"
    ts = line_obj.get("timestamp", "")
    hhmmss = _iso_to_local_hhmmss(ts)
    meta = {"session_id": session_id, "timestamp": ts, "paste_id": paste_id}
    return {
        "date": date,
        "category": "paste",
        "source": "claude",
        "title": f"Paste: {paste_id[:12]} @ {hhmmss}",
        "detail": None,
        "url": url,
        "metadata": meta,
        "tag": "work",
    }


def parse_transcript(
    path: Path | str,
    session_id: str | None = None,
) -> Iterator[dict]:
    """Stream events from a transcript JSONL file.

    Yields activity-ready event dicts. Caller is responsible for writing them
    to the DB (e.g., via the existing write path in main.py).
    """
    p = Path(path)
    if not p.exists():
        return

    # Derive session_id from filename if not provided
    if session_id is None:
        session_id = p.stem

    with p.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            t = obj.get("type")

            if t == "assistant":
                msg = obj.get("message", {}) or {}
                content = msg.get("content")
                ts = obj.get("timestamp", "")
                date = _iso_to_local_date(ts)
                if not isinstance(content, list):
                    continue
                for block in content:
                    if not isinstance(block, dict):
                        continue
                    if block.get("type") != "tool_use":
                        continue
                    ev = _event_from_tool_use(block, ts, session_id, date)
                    if ev:
                        yield ev

            elif t == "attachment":
                # Conservatively treat attachments as pastes (reference only)
                ts = obj.get("timestamp", "")
                date = _iso_to_local_date(ts)
                if date:
                    ev = _event_from_paste(obj, session_id, date)
                    if ev:
                        yield ev
