---
name: pr-smart-commit
description: Analyze all changes and split them into small, focused, reviewable commits grouped by logical concern. Use when the user wants to commit with best practices, create atomic commits, split changes into multiple commits, or make their PR easier to review.
---

# Smart Commit - Small, Focused Commits

Analyze all current changes and organize them into the smallest possible logical commits without breaking functionality. This makes code reviews faster and easier.

## Core Philosophy

- **One commit = one logical change**: Each commit should answer "what does this do?" in a single sentence
- **Reviewers read commits one at a time**: Each commit should leave the codebase in a working state
- **Small beats large**: A PR with 5 small commits is easier to review than 1 giant commit

## Instructions

1. **Gather all changes:**
   ```bash
   git status
   git diff --stat          # unstaged changes
   git diff --cached --stat # staged changes
   ```
   - Collect both staged and unstaged changes into one view

2. **Read the full diff:**
   ```bash
   git diff HEAD
   ```
   - Read every changed file carefully
   - Note: what files changed, what logic changed, what was added vs modified vs deleted

3. **Group changes into logical buckets:**

   Analyze the diff and propose a commit plan. Group by:
   - **Feature / functionality**: New behavior added together
   - **Bug fix**: Fix to a specific problem
   - **Refactor**: Code restructuring with no behavior change
   - **Tests**: Test additions/updates (can be with feature or separate)
   - **Config/build**: Package.json, CI configs, environment files
   - **Docs**: README, comments, documentation files
   - **Style/formatting**: Whitespace, linting, formatting (always separate — never mix with logic)

   Rules for grouping:
   - Changes to the same file can be in different commits if they serve different purposes
   - Test files for a feature should usually go in the same commit as the feature
   - Formatting/whitespace fixes must be in their own commit
   - Dependency additions go with the feature that requires them

4. **Present the commit plan to the user:**

   Show a structured plan like:
   ```
   Proposed commit plan (3 commits):

   Commit 1: feat(auth): add JWT token validation middleware
     - src/middleware/auth.js (new file)
     - src/routes/index.js (lines 12-18: add middleware to protected routes)

   Commit 2: test(auth): add unit tests for JWT middleware
     - tests/middleware/auth.test.js (new file)

   Commit 3: chore(deps): add jsonwebtoken dependency
     - package.json
     - package-lock.json

   Does this look right? Should any groups be merged or split differently?
   ```

   Wait for user approval before proceeding. They may want to:
   - Merge some commits together
   - Split a commit further
   - Reorder the commits
   - Exclude some changes for a later commit

5. **Execute each commit in order:**

   For each commit in the approved plan:

   a. Stage only the relevant files/hunks:
      - For full files: `git add <file>`
      - For partial files (specific hunks): use `git add -p <file>` logic — read the file and stage only the relevant sections by constructing a precise patch

   b. Verify staged content:
      ```bash
      git diff --cached --stat
      git diff --cached
      ```
      Confirm the staged diff matches exactly what was planned for this commit.

   c. Generate a commit message following Conventional Commits:
      ```
      <type>(<scope>): <subject>   ← max 50 chars, imperative mood

      <body>                        ← wrap at 72 chars, explain WHY

      Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
      ```

   d. Show the message and ask for approval.

   e. Commit:
      ```bash
      git commit -m "$(cat <<'EOF'
      <message>
      EOF
      )"
      ```

   f. Confirm: `git log -1 --oneline`

6. **Handle partial file staging (hunk-level splitting):**

   When a file has changes that belong to different commits:
   - Read the file's diff carefully
   - Use `git add -p` interactively OR create a temporary patch file approach:
     ```bash
     git diff <file> > /tmp/full.patch
     # Then stage only specific hunks
     git apply --cached /tmp/partial.patch
     ```
   - Always verify with `git diff --cached` that only the intended changes are staged

7. **Final summary + push:**
   - Run `git log --oneline -<n>` where n = number of commits created
   - Show the full commit list so the user can review
   - Ask: "Push these commits now? (y/n)"
   - If yes, run `git push` (or `git push -u origin <branch>` if no upstream set)
   - After pushing, check if an open PR exists: `gh pr view --json number,url 2>/dev/null`
     - If a PR exists: automatically run the `pr-update` skill to refresh the PR title and description
     - If no PR exists: ask if they want to create one with `/pr-create`

## Commit Message Types

| Type | When to use |
|------|-------------|
| `feat` | New feature or behavior |
| `fix` | Bug fix |
| `refactor` | Code restructure, no behavior change |
| `test` | Adding/updating tests |
| `docs` | Documentation only |
| `style` | Formatting, whitespace (no logic change) |
| `chore` | Dependencies, build config, tooling |
| `perf` | Performance improvement |
| `ci` | CI/CD configuration |

## Red Flags - Always Split These

- A commit that touches both business logic AND tests AND config → split into 3
- A commit with "and" in the subject line → split it
- A commit touching more than ~5-7 files → likely needs splitting
- A commit mixing a bug fix with new features → always split

## Important Notes

- **Never commit broken code**: Each commit must leave tests passing (or at minimum, not introduce new failures)
- **Don't mix formatting with logic**: Auto-formatter changes hide real diffs — always separate them
- **Unstaged changes are fine to leave**: If some changes don't belong in this session's commits, leave them unstaged
- **Ask before skipping anything**: If a change doesn't fit any planned commit, ask the user rather than silently leaving it out
