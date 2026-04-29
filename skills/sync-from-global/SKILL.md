---
name: sync-from-global
description: Sync ~/.claude/ global configs into this repo, sanitizing work-specific content (LinkedIn plugins, Captain MCP, work email, internal URLs). Use when the user wants to refresh this repo from their global Claude configs, pull in newly added skills/commands, or update sanitization rules. Two-pass flow with diff review before commit.
---

# Sync from global

This skill syncs the user's global Claude config (`~/.claude/`) into this repo, stripping LinkedIn-specific content so the result is portable across personal devices. The repo's `install.sh` goes the other direction (repo → global); this skill is the reverse.

## How it works

Two-pass flow driven by `sync/sync.py`, preceded by a git preflight:

0. **Preflight — sync with origin**: `git fetch` + `git pull --ff-only` so we don't stage onto stale state. Aborts if the working tree is dirty or remote has diverged.
1. **Pass 1 — stage**: walks `~/.claude/`, applies skip rules and redaction patterns from `sync/sync-config.json`, writes sanitized output to `.sync-staging/` (gitignored), prints a summary diff.
2. **User review**: user inspects the diff, optionally tunes `sync-config.json`, optionally re-runs pass 1.
3. **Pass 2 — apply**: copies `.sync-staging/` → final repo paths. User then reviews `git diff` and commits.

## When to invoke

**Event-driven** (primary trigger):
- "sync my global configs"
- "pull in my new global skills"
- "update the repo from ~/.claude/"
- "refresh this repo with my latest cloud configs"
- After installing a new plugin globally, getting a plugin auto-update with new skills, or when the user mentions they've been editing skills directly in `~/.claude/`

**Periodic safety net**: every few weeks, even without an explicit prompt, it's reasonable to suggest running this if the user is in the repo and hasn't synced recently. Pass 1 is cheap — it stages and shows a diff; if nothing meaningful changed, the run is a no-op. Don't suggest more often than ~weekly; daily is overkill.

If pass 1 consistently produces no meaningful diffs, that's good — it means the user is editing the repo first and letting `install.sh` push out, rather than editing `~/.claude/` directly. Acknowledge this rather than pushing them to run it more.

## Steps

### Step 0 — sync repo with origin first

Before staging anything, make sure the local repo is up-to-date with `origin`. This avoids overwriting recent changes pushed from another device (e.g., L2 added a new skill, then L1 runs sync without pulling first → L1's pass 2 lands on stale state and creates conflicts on push).

The repo path is available at `~/.claude/configs-repo` (a symlink set up by `install.sh`). All git operations and script invocations should use this path so they work regardless of CWD.

```bash
cd ~/.claude/configs-repo
git fetch origin
git status -sb
```

Then:
1. **If working tree is dirty** (uncommitted changes shown in `git status`): **stop** and ask the user. Either commit/stash first, or confirm it's safe to proceed (the user may have intentional in-progress work).
2. **If repo is behind origin**: `git pull --ff-only` to fast-forward. If this fails (non-fast-forward, divergent history), **stop** and report — the user needs to resolve manually before syncing.
3. **If repo is up to date and clean**: proceed to Step 1.

Do **not** proceed past Step 0 if either check fails. The sanitization is wasted effort if the apply step lands on stale or dirty state.

### Step 1 — run pass 1

```bash
python3 ~/.claude/configs-repo/sync/sync.py
```

This will:
- Stage to `.sync-staging/`
- Print a summary with sections: New / Modified / Redacted / Manual review / Repo-only / Skipped

### Step 2 — present the summary to the user

After pass 1 completes, do **all** of the following:

1. Show the user the **counts** from each section (new, modified, redacted, manual review, repo-only).
2. **Always** run `diff -u <repo-file> .sync-staging/<file>` for **every file** in the "Manual review recommended" list and show the diffs inline. These files have heavy LinkedIn refs (Captain MCP, JIRA, Confluence) that automated redaction can't fully clean — the staged version may actually be **worse** than the repo's existing hand-cleaned version. If so, recommend the user either:
   - **Delete** the file from `.sync-staging/` (keeps repo version untouched on apply), or
   - **Tune** `sync-config.json` rules and re-run pass 1, or
   - **Manually edit** the staging file before apply
3. For non-review modifications, spot-check 1-2 of the most interesting diffs.
4. **Stop and ask the user**: "Review the staging dir. Should I apply, or do you want to tune `sync-config.json` / edit staging first?"

Do **not** proceed to pass 2 without explicit user approval.

### Step 3 — handle user feedback

If the user asks to **tune the rules**: edit `sync/sync-config.json`, then re-run pass 1. Common adjustments:
- Add a glob to `skip_paths` (skip a whole file/dir)
- Add a regex to `drop_line_patterns` (strip lines mentioning a specific tool/term)
- Add a `redaction_rules` entry (replace a string with something generic)
- Add a glob to `manual_review_globs` (flag a file for human review)
- Add a path to `repo_only_paths` (protect personal-only files from being overwritten by sync)
- Add/remove a plugin from `enabled_plugins_allowlist`

If the user asks to **inspect a specific file**: read both the source and staging version side-by-side.

### Step 4 — apply

When the user approves:

```bash
python3 ~/.claude/configs-repo/sync/sync.py --apply
```

Then:
1. Run `git status` to show what changed in the repo.
2. Suggest the user run `git diff` for the final review.
3. **Do not auto-commit.** The user reviews and commits manually (or via `/commit`).

## Important constraints

- **Never** auto-apply without showing the pass 1 summary and getting approval. The whole point of two-pass is that work secrets could leak via a bad/missing redaction rule.
- **Never** commit on the user's behalf. Sanitization mistakes are git history forever.
- **Never** delete `.sync-staging/` automatically — keep it around so the user can re-inspect after applying.
- If pass 1 reports `Redacted` files but the user expected `Unchanged`, that means a redaction rule fired — show them which lines got dropped/replaced before applying.

## Files in this system

- `sync/sync.py` — the script (Python stdlib only, runs anywhere)
- `sync/sync-config.json` — declarative skip + redaction rules; edit to tune behavior
- `.sync-staging/` — gitignored, intermediate output of pass 1
- `skills/sync-from-global/SKILL.md` — this file
