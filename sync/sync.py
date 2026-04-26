#!/usr/bin/env python3
"""Sync ~/.claude/ → this repo, sanitizing work-specific content.

Two-pass flow:
  Pass 1: python3 sync/sync.py
          → stages sanitized files to .sync-staging/ and prints diff summary
  Pass 2: python3 sync/sync.py --apply
          → copies staging → final repo paths

Rules live in sync/sync-config.json. Edit and re-run pass 1 to refine.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "sync" / "sync-config.json"
STAGING_DIR = REPO_ROOT / ".sync-staging"
HISTORY_LOG = REPO_ROOT / "sync" / "sync-history.log"


def log_event(event: str, detail: str = "") -> None:
    """Append a timestamped one-liner to sync-history.log (no hostname — avoid info leak)."""
    line = f"{datetime.now().isoformat(timespec='seconds')}\t{event}\t{detail}\n"
    with HISTORY_LOG.open("a") as f:
        f.write(line)


def load_config() -> dict:
    with CONFIG_PATH.open() as f:
        return json.load(f)


def expand(p: str) -> Path:
    return Path(p).expanduser().resolve()


def matches_any(rel_path: str, patterns: list[str]) -> bool:
    """True if rel_path or any of its ancestors match any glob/literal pattern."""
    parts = Path(rel_path).parts
    candidates = [rel_path] + ["/".join(parts[:i]) for i in range(1, len(parts) + 1)]
    for cand in candidates:
        for pat in patterns:
            if cand == pat or fnmatch.fnmatch(cand, pat):
                return True
    return False


def is_text_file(path: Path) -> bool:
    """Cheap text-file check: read up to 4KB, look for null bytes."""
    try:
        with path.open("rb") as f:
            chunk = f.read(4096)
        return b"\x00" not in chunk
    except OSError:
        return False


def apply_redactions(text: str, cfg: dict) -> str:
    # Strip multi-line blocks first
    for block in cfg.get("strip_blocks", []):
        start, end = re.escape(block["start"]), re.escape(block["end"])
        text = re.sub(rf"{start}.*?{end}\n?", "", text, flags=re.DOTALL)

    # Drop whole lines matching any pattern
    drop_patterns = cfg.get("drop_line_patterns", [])
    if drop_patterns:
        compiled = [re.compile(p) for p in drop_patterns]
        kept = [
            line for line in text.splitlines(keepends=True)
            if not any(c.search(line) for c in compiled)
        ]
        text = "".join(kept)

    # Apply replacements
    for rule in cfg.get("redaction_rules", []):
        pat, repl = rule["pattern"], rule["replacement"]
        if rule.get("regex"):
            text = re.sub(pat, repl, text)
        else:
            text = text.replace(pat, repl)

    return text


def sanitize_settings_json(text: str, cfg: dict) -> str:
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        print(f"  WARN: settings.json failed to parse, copying with text redactions only")
        return apply_redactions(text, cfg)

    settings_cfg = cfg.get("settings_json", {})

    # Filter enabledPlugins
    allowlist = set(settings_cfg.get("enabled_plugins_allowlist", []))
    if "enabledPlugins" in data:
        data["enabledPlugins"] = {
            k: v for k, v in data["enabledPlugins"].items() if k in allowlist
        }

    # Filter permissions.allow
    drop_pats = settings_cfg.get("drop_permission_patterns", [])
    if "permissions" in data and "allow" in data["permissions"]:
        data["permissions"]["allow"] = [
            entry for entry in data["permissions"]["allow"]
            if not any(p in entry for p in drop_pats)
        ]

    # Drop user-specific statusLine path → make generic
    if "statusLine" in data and "command" in data["statusLine"]:
        data["statusLine"]["command"] = data["statusLine"]["command"].replace(
            "/Users/kreber/", "~/"
        )

    # Filter hooks: drop entries whose command matches any deny pattern
    hook_drop_pats = settings_cfg.get("hook_command_drop_patterns", [])
    if hook_drop_pats and "hooks" in data:
        compiled = [re.compile(p, re.IGNORECASE) for p in hook_drop_pats]

        def _is_safe(hook_entry: dict) -> bool:
            cmd = hook_entry.get("command", "")
            return not any(c.search(cmd) for c in compiled)

        for event_name, event_groups in list(data["hooks"].items()):
            cleaned_groups = []
            for group in event_groups:
                inner = group.get("hooks", [])
                safe_inner = [h for h in inner if _is_safe(h)]
                if safe_inner:
                    cleaned_groups.append({**group, "hooks": safe_inner})
            if cleaned_groups:
                data["hooks"][event_name] = cleaned_groups
            else:
                del data["hooks"][event_name]

    return json.dumps(data, indent=2) + "\n"


def sanitize_marketplaces_json(text: str, cfg: dict) -> str:
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return apply_redactions(text, cfg)

    allowlist = set(cfg.get("known_marketplaces_allowlist", []))
    filtered = {k: v for k, v in data.items() if k in allowlist}
    # Strip user-specific install paths
    for entry in filtered.values():
        if "installLocation" in entry:
            entry["installLocation"] = entry["installLocation"].replace(
                "/Users/kreber/", "~/"
            )
    return json.dumps(filtered, indent=2) + "\n"


def sanitize_installed_plugins_json(text: str, cfg: dict) -> str:
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return apply_redactions(text, cfg)

    allowlist = set(cfg.get("settings_json", {}).get("enabled_plugins_allowlist", []))
    if "plugins" in data:
        data["plugins"] = {k: v for k, v in data["plugins"].items() if k in allowlist}
        for entries in data["plugins"].values():
            for e in entries:
                if "installPath" in e:
                    e["installPath"] = e["installPath"].replace("/Users/kreber/", "~/")
    return json.dumps(data, indent=2) + "\n"


def map_source_to_dest(src_rel: str, cfg: dict) -> Path | None:
    """Map a source path (relative to source_root) to a repo destination path.

    Returns None if no mapping applies (file should be skipped from sync entirely).
    """
    mappings = cfg["path_mappings"]
    # Exact match first
    if src_rel in mappings:
        return REPO_ROOT / mappings[src_rel]
    # Prefix match — e.g., "commands/foo.md" → mappings["commands"] = "commands"
    for src_prefix, dest_prefix in mappings.items():
        if src_rel == src_prefix or src_rel.startswith(src_prefix + "/"):
            tail = src_rel[len(src_prefix):].lstrip("/")
            return REPO_ROOT / dest_prefix / tail if tail else REPO_ROOT / dest_prefix
    return None


def normalize_loose_skill(src_rel: str, dest: Path) -> Path:
    """Convert ~/.claude/skills/foo.md → repo/skills/foo/SKILL.md."""
    if src_rel.startswith("skills/") and src_rel.endswith(".md") and "/" not in src_rel[len("skills/"):]:
        name = Path(src_rel).stem
        return REPO_ROOT / "skills" / name / "SKILL.md"
    return dest


def stage_file(src: Path, src_rel: str, dest: Path, cfg: dict) -> tuple[str, bool]:
    """Copy src into staging at the location mirroring dest. Returns (status, redacted)."""
    staging_path = STAGING_DIR / dest.relative_to(REPO_ROOT)
    staging_path.parent.mkdir(parents=True, exist_ok=True)

    redact_globs = cfg.get("redact_globs", [])
    should_redact = is_text_file(src) and any(
        fnmatch.fnmatch(src.name, g) or fnmatch.fnmatch(src_rel, g) for g in redact_globs
    )

    if src.name == "settings.json" and src_rel == "settings.json":
        text = src.read_text()
        sanitized = sanitize_settings_json(text, cfg)
        staging_path.write_text(sanitized)
        return ("staged", True)

    if src_rel == "plugins/known_marketplaces.json":
        text = src.read_text()
        staging_path.write_text(sanitize_marketplaces_json(text, cfg))
        return ("staged", True)

    if src_rel == "plugins/installed_plugins.json":
        text = src.read_text()
        staging_path.write_text(sanitize_installed_plugins_json(text, cfg))
        return ("staged", True)

    if should_redact:
        text = src.read_text()
        sanitized = apply_redactions(text, cfg)
        staging_path.write_text(sanitized)
        redacted = sanitized != text
        return ("staged", redacted)

    shutil.copy2(src, staging_path)
    return ("staged", False)


def file_hash(path: Path) -> str:
    if not path.exists():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pass_one(cfg: dict) -> dict:
    """Walk source, stage everything, return summary."""
    source_root = expand(cfg["source_root"])
    skip_paths = cfg.get("skip_paths", [])
    skip_globs = cfg.get("skip_globs", [])
    review_globs = cfg.get("manual_review_globs", [])

    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)
    STAGING_DIR.mkdir()

    summary = {
        "staged": [],
        "skipped": [],
        "redacted": [],
        "manual_review": [],
        "new_in_source": [],
        "repo_only": [],
        "unchanged": [],
        "modified": [],
    }

    for dirpath, dirnames, filenames in os.walk(source_root):
        rel_dir = os.path.relpath(dirpath, source_root)
        # Prune skipped dirs in-place so we don't descend into them
        dirnames[:] = [
            d for d in dirnames
            if not (
                matches_any(d if rel_dir == "." else f"{rel_dir}/{d}", skip_paths)
                or matches_any(d if rel_dir == "." else f"{rel_dir}/{d}", skip_globs)
            )
        ]
        for filename in filenames:
            src = Path(dirpath) / filename
            src_rel = str(src.relative_to(source_root))

            if matches_any(src_rel, skip_paths) or matches_any(src_rel, skip_globs):
                summary["skipped"].append(src_rel)
                continue

            dest = map_source_to_dest(src_rel, cfg)
            if dest is None:
                summary["skipped"].append(f"{src_rel} (no mapping)")
                continue

            if cfg.get("normalize_loose_skills"):
                dest = normalize_loose_skill(src_rel, dest)

            try:
                status, redacted = stage_file(src, src_rel, dest, cfg)
            except Exception as e:
                summary["skipped"].append(f"{src_rel} (error: {e})")
                continue

            rel_dest = str(dest.relative_to(REPO_ROOT))
            summary["staged"].append(rel_dest)

            if redacted:
                summary["redacted"].append(rel_dest)

            if any(fnmatch.fnmatch(rel_dest, g) for g in review_globs):
                summary["manual_review"].append(rel_dest)

            # Compare against current repo state
            staging_path = STAGING_DIR / dest.relative_to(REPO_ROOT)
            existing = REPO_ROOT / dest.relative_to(REPO_ROOT)
            if not existing.exists():
                summary["new_in_source"].append(rel_dest)
            elif file_hash(staging_path) == file_hash(existing):
                summary["unchanged"].append(rel_dest)
            else:
                summary["modified"].append(rel_dest)

    # Detect files in repo but not in staging (these are NOT deleted; just informational)
    tracked_dirs = ["commands", "skills"]
    for d in tracked_dirs:
        repo_dir = REPO_ROOT / d
        if not repo_dir.exists():
            continue
        for existing in repo_dir.rglob("*"):
            if not existing.is_file():
                continue
            rel = str(existing.relative_to(REPO_ROOT))
            staging_equiv = STAGING_DIR / rel
            if not staging_equiv.exists() and rel not in summary["staged"]:
                summary["repo_only"].append(rel)

    return summary


def print_summary(summary: dict) -> None:
    def section(title: str, items: list[str], cap: int = 50) -> None:
        if not items:
            return
        print(f"\n{title} ({len(items)})")
        print("-" * len(title))
        for item in sorted(items)[:cap]:
            print(f"  {item}")
        if len(items) > cap:
            print(f"  … and {len(items) - cap} more")

    print("\n" + "=" * 60)
    print("SYNC PASS 1 SUMMARY")
    print("=" * 60)

    section("New (not in repo yet)", summary["new_in_source"])
    section("Modified (will overwrite on apply)", summary["modified"])
    section("Unchanged", summary["unchanged"], cap=10)
    section("Redacted (sanitization rules fired)", summary["redacted"])
    section("Manual review recommended", summary["manual_review"])
    section("Repo-only (in repo but not in ~/.claude — NOT touched on apply)", summary["repo_only"])
    section("Skipped (not synced from source)", summary["skipped"], cap=20)

    print("\n" + "=" * 60)
    print(f"Staged {len(summary['staged'])} files to {STAGING_DIR.relative_to(REPO_ROOT)}/")
    print("Review with:")
    print(f"  diff -ru {REPO_ROOT.name}/ .sync-staging/  # all changes")
    print(f"  ls .sync-staging/                          # staged tree")
    print("\nThen run:  python3 sync/sync.py --apply")
    print("=" * 60)


def pass_two() -> None:
    """Copy .sync-staging/ → repo paths."""
    if not STAGING_DIR.exists():
        print("ERROR: no staging dir found. Run pass 1 first: python3 sync/sync.py")
        sys.exit(1)

    count = 0
    for staged in STAGING_DIR.rglob("*"):
        if not staged.is_file():
            continue
        rel = staged.relative_to(STAGING_DIR)
        dest = REPO_ROOT / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(staged, dest)
        count += 1

    print(f"Applied {count} files to repo.")
    print("Review with: git status && git diff")
    print(f"Clean up staging when ready: rm -rf {STAGING_DIR.relative_to(REPO_ROOT)}/")
    log_event("apply", f"copied={count}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Pass 2: copy staging → repo paths (default is pass 1: stage only)",
    )
    args = parser.parse_args()

    if args.apply:
        pass_two()
        return

    cfg = load_config()
    summary = pass_one(cfg)
    print_summary(summary)
    log_event(
        "pass1",
        f"staged={len(summary['staged'])} new={len(summary['new_in_source'])} "
        f"modified={len(summary['modified'])} redacted={len(summary['redacted'])} "
        f"manual_review={len(summary['manual_review'])} skipped={len(summary['skipped'])}",
    )


if __name__ == "__main__":
    main()
