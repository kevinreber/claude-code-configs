# sync

Pulls configs from `~/.claude/` into this repo, sanitizing private or
device-specific content along the way. The reverse direction (repo →
`~/.claude/`) is handled by the top-level `install.sh`.

## Why this exists

`~/.claude/` typically mixes portable configuration with private plugins,
internal URLs, user identifiers, and device-only paths. This repo is meant to
be the **sanitized, sharable union** of generic configs across multiple devices.
The script automates that sanitization with a diff-review checkpoint.

## Files

| File | Purpose |
|---|---|
| `sync.py` | Two-pass sync script. Pass 1 stages to `.sync-staging/` with a diff summary; pass 2 (`--apply`) copies staging → repo. |
| `sync-config.json` | Portable shared rules: skip lists, redaction patterns, manual-review globs, and plugin allowlists. |
| `sync-config.local.json` | Optional gitignored private overlay for company-, user-, or device-specific rules. Lists and dictionaries are merged into the shared config. |
| `sync-history.log` | Append-only audit trail. One line per pass-1 / apply, with timestamp + counts. |

## Quick reference

```bash
# Pass 1: stage everything (or invoke /sync-from-global skill instead — recommended)
python3 sync/sync.py

# Inspect staging
ls .sync-staging/
diff -u skills/foo/SKILL.md .sync-staging/skills/foo/SKILL.md

# Tune rules and re-run if needed
$EDITOR sync/sync-config.json
python3 sync/sync.py

# When happy: pass 2
python3 sync/sync.py --apply

# Then review and commit
git status && git diff
```

The `/sync-from-global` skill (in `skills/sync-from-global/SKILL.md`) wraps this workflow and adds a git-pull preflight + diff review for files flagged for manual review. Prefer invoking the skill over running the script directly — that's where the safety guidance lives.

## Configuration cheat sheet

`sync-config.json` has the following knobs:

- **`source_root`** — where to read from (`~/.claude` by default).
- **`path_mappings`** — source path → repo destination. Exact match or longest-prefix wins.
- **`skip_paths`** — literal paths under source root that are skipped entirely. The walker doesn't descend into skipped dirs.
- **`skip_globs`** — glob patterns for skipping (e.g., `**/.venv/**`, `**/*.env`).
- **`redact_globs`** — file types where text redaction is applied (`**/*.md`, `**/*.json`, etc.). Files not matching are copied verbatim.
- **`redaction_rules`** — string/regex find-and-replace within file content. Use for in-prose substitutions like `Kevin Reber` → `<your-name>`.
- **`drop_line_patterns`** — regexes that, if any matches a line, drop the entire line. Aggressive; keep private tool names in `sync-config.local.json`.
- **`strip_blocks`** — multi-line markers; content between them (and the markers) gets removed. E.g., `<!-- CLAUDE_ONLY_START --> ... <!-- CLAUDE_ONLY_END -->`.
- **`settings_json`** — special handling for `~/.claude/settings.json`:
  - `enabled_plugins_allowlist` — which plugins survive in the synced settings
  - `drop_permission_patterns` — `permissions.allow` entries containing any of these substrings get dropped
  - `hook_command_drop_patterns` — hooks whose `command` field matches any pattern get dropped
- **`known_marketplaces_allowlist`** — which plugin marketplaces survive in `known_marketplaces.json`.
- **`repo_only_paths`** — paths (relative to repo root, supports globs) that are personal-only and must NOT be overwritten by `--apply`. These files were created directly in the repo, not synced from work. Pass 1 flags them; pass 2 skips them.
- **`manual_review_globs`** — files flagged for manual review in pass 1's summary (because automated redaction can't fully clean them).
- **`normalize_loose_skills`** — if true, loose `~/.claude/skills/foo.md` files get reshaped to repo's `skills/foo/SKILL.md` directory layout.

## Important behaviors

- **Pass 2 is purely additive.** It only copies staging → repo. It never deletes from the repo. Files in repo but not in source are listed as "Repo-only" in the pass-1 summary and are left untouched on apply.
- **`.sync-staging/` is gitignored.** It's intermediate output and survives between pass 1 and pass 2.
- **Manual-review files** (`daily-recap*`, `daily-review*`, `update-docs-wiki`, `discover`, `find-skills`) get flagged because the automated redaction can't fully clean them — drop-line patterns can't catch references mid-prose without mangling examples. The recommended workflow is to **delete these from staging** before pass 2 if the repo's hand-cleaned version is better than the staged one.
- **No hostname or user identifier** is logged to `sync-history.log` — just timestamp and counts. The log is committed to the repo as a cross-device audit trail.

## Adding new redaction rules

When pass 1 surfaces private content, edit `sync-config.local.json`:

1. **Whole-line private tool reference**: add it to `drop_line_patterns`.
2. **In-prose word/name**: decide between:
   - `drop_line_patterns` — drops the whole line, can leave malformed example blocks
   - `redaction_rules` — replaces with a placeholder, preserves line structure
3. **Whole-file private artifact**: add it to `skip_paths`.
4. **File where automation can't be trusted**: add to `manual_review_globs`. Pass 1 will flag it for human review.

Then re-run pass 1 to verify, before pass 2.
