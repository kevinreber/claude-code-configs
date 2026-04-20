---
name: pr-sync-branch
description: Pull the latest changes from master/main into the current branch and resolve any merge conflicts. Use when the user wants to sync their branch with upstream, update from main, rebase on master, or fix merge conflicts.
---

# Sync Branch with Main

Fetch the latest changes from origin master/main and integrate them into the current branch, resolving any conflicts intelligently.

## Instructions

1. **Check current state:**
   - Run `git status` to ensure there are no uncommitted changes that would block the operation
   - If there are uncommitted changes, ask the user: stage & stash them first, or abort?
   - If stashing: run `git stash push -m "pr-sync-branch: auto-stash before sync"`

2. **Identify the main branch:**
   - Run `git remote show origin | grep 'HEAD branch'` to detect whether the default is `main` or `master`
   - Fall back to checking `git branch -r | grep -E 'origin/(main|master)'`

3. **Fetch latest from origin:**
   ```bash
   git fetch origin
   ```

4. **Check current branch:**
   - Run `git branch --show-current` to get the current branch name
   - If already on main/master, just pull: `git pull origin <main-branch>` and stop here

5. **Attempt rebase (preferred for clean history):**
   ```bash
   git rebase origin/<main-branch>
   ```
   - If rebase succeeds with no conflicts, skip to step 8

6. **Handle conflicts if rebase reports them:**
   - Run `git diff --name-only --diff-filter=U` to list conflicted files
   - For each conflicted file:
     a. Read the file contents including conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`)
     b. Analyze both sides: `HEAD` (current branch) vs incoming (main branch)
     c. Resolve by keeping the correct logic:
        - If changes are in different parts of the file: keep both
        - If changes conflict semantically: prefer the current branch's intent but incorporate upstream changes
        - If upstream deleted something the branch modified: show user and ask
     d. Write the resolved file (no conflict markers remaining)
     e. Stage the resolved file: `git add <file>`
   - After resolving all conflicts: `git rebase --continue`
   - If more conflict rounds appear, repeat step 6

7. **If rebase cannot be cleanly continued:**
   - Abort the rebase: `git rebase --abort`
   - Fall back to merge: `git merge origin/<main-branch>`
   - Resolve conflicts using the same approach in step 6
   - Stage resolved files and run `git merge --continue` or `git commit`

8. **Pop stash if applicable:**
   - If changes were stashed in step 1: `git stash pop`
   - If stash pop has conflicts, resolve them the same way as step 6

9. **Verify and summarize:**
   - Run `git log --oneline origin/<main-branch>..HEAD` to show commits ahead of main
   - Run `git status` to confirm clean working tree
   - Report: how many commits were rebased, how many conflicts were resolved, and the final branch state

## Conflict Resolution Principles

- **Prefer additive merges**: If both sides add different things, keep both
- **Respect current branch intent**: This branch exists for a reason; don't silently drop its changes
- **Ask when uncertain**: If a conflict involves deleted code, renamed functions, or non-obvious semantic changes, present both versions to the user and ask which to keep
- **Never silently discard**: Always tell the user what was resolved and how

## Important Notes

- Always `git fetch` before rebasing — never rebase on stale data
- Rebase is preferred over merge to keep history linear, but merge is the safe fallback
- After a successful sync, remind the user to force-push their branch if it was already pushed: `git push --force-with-lease`
- Do NOT auto-push — always let the user decide when to push
