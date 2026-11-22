---
name: worktree-gc
description: Inventory Git worktrees and safely remove explicitly selected clean, inactive worktrees. Use for worktree cleanup or a read-only worktree inventory.
---

# Worktree GC

Default to a read-only inventory of the current repository. Inspect other
repositories only when the user explicitly supplies their paths.

Use `git worktree list --porcelain`, check each candidate's status including
untracked files, and identify the main and current worktrees, locked
worktrees, branches, and known active sessions. Check merge status only
against a known local base; otherwise report it as unknown.

Report exact paths and reasons a worktree is or is not a candidate. Never
remove the main or current worktree, a locked, dirty, untracked, active, or
unverifiable worktree. Do not prune worktree records or delete branches.

Removal requires the user to explicitly identify every exact worktree path.
Recheck all safety conditions immediately before using
`git worktree remove <path>` without `--force`; stop on any failure.
