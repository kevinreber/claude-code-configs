# Resume — Recover Context Fast

Re-orient after `/clear`, a fresh session, or a context switch. Replaces the "let me re-explain everything" pattern with a single command that pulls just-enough state.

## Usage

```
/resume                  # auto-detect: full briefing for current project
/resume short            # one-paragraph summary, no details
/resume vault            # force vault mode (today's activity + active projects)
/resume project          # force project mode (git state + CLAUDE.md + PRs)
```

## Instructions

Goal: produce a tight "where you left off" briefing in **under 10 seconds of reading**. No wall of text. Skim-friendly headings.

### Step 1: Detect mode

- If `pwd` ends in `brain-vault` → **vault mode**
- Else if a `CLAUDE.md` exists in cwd or any parent → **project mode**
- Else → **minimal mode** (just `git status` + recent commits)

### Step 2: Vault mode — pull today's signal

Run these in parallel:

1. **Today's activity log** — `Activity/<YYYY-MM-DD>.md` (work) or `Activity/<YYYY-MM-DD>-personal.md` (personal, hostname does not end in `.linkedin.biz`). If today's file doesn't exist, fall back to the most recent file in `Activity/`.
2. **Active projects** — `Glob` for `Projects/*.md`, then `Grep` frontmatter for `status: active`. Cap at 5.
3. **Open PRs** — `gh pr list --author @me --state open --json number,title,repository,updatedAt --limit 10` (skip silently if `gh` not authed).
4. **Top of backlog** — first 10 lines of `Backlog/ideas.md`.
5. **Recent decisions** — `ls -t Decisions/*.md | head -3` then read titles only.

### Step 3: Project mode — pull just-enough state

Run in parallel:

1. **Project CLAUDE.md** — read it (always)
2. **Branch + status** — `git status -sb` + `git log --oneline -10`
3. **Uncommitted work** — if dirty, list changed files (no diffs)
4. **Open PRs for this repo** — `gh pr list --author @me --state open --json number,title,updatedAt`
5. **Most recently edited files** — `git diff --name-only HEAD~5 HEAD | head -10`

### Step 4: Output

**Format the briefing exactly like this:**

```markdown
## Resume — <project name> · <date>

**Mode**: vault | project | minimal

### Where you left off
<2-3 sentence narrative — what was being worked on most recently, inferred from the signals above. Concrete: "You were debugging the daily-recap-v2 ingest script — the SQL query in main.py:142 was failing on rows with null updated_at.">

### Active threads
- **<thread name>** — <one-line status>
- **<thread name>** — <one-line status>

### Open loops
- [ ] <thing that's pending>
- [ ] <thing waiting on someone>

### Suggested next action
<One concrete sentence: "Run `npm test` to confirm the fix from yesterday's last commit holds." Or: "Open PRs/<repo>/<num>.md to address the review comments left on Tuesday.">
```

**Length budget:** 15-25 lines total. If you're going longer, you're including too much.

### Step 5: Self-check before responding

- [ ] Did I read the actual files, not just list them?
- [ ] Is the "where you left off" narrative grounded in evidence (file names, commit messages, PR titles)? Or did I make it up?
- [ ] Are all `Active threads` real (each one cites a Project note, PR, or recent commit)?
- [ ] Is the `Suggested next action` concrete enough that the user can act on it without asking me to clarify?

If any answer is "no", redo that section.

## Failure modes — do not do these

- ❌ Don't dump raw `git log` or `gh pr list` output. Synthesize.
- ❌ Don't list every file in Activity/ or Projects/. Most recent + active only.
- ❌ Don't write a "Today I will..." section — that's planning, not resuming. The user asked where they left off, not what to do next (the *suggested* action is one line, not a roadmap).
- ❌ Don't ask clarifying questions. The whole point is to skip the back-and-forth. If signals are weak, say so in the briefing.

## Short mode

`/resume short` returns a single paragraph (3-4 sentences) summarizing state. No headings. No lists. Use when the user is mid-flow and just needs a reminder.

## Integration

- Pairs with `/daily-review-v2` (which writes the activity log this command reads).
- Pairs with `/vault-ingest-prs` (which populates `PRs/` notes referenced in vault mode).
- If invoked immediately after `/clear`, the prior conversation is gone — this is the recovery path.
