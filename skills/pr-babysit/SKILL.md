---
name: pr-babysit
description: Check a specified pull request for new review feedback and failing checks, with explicitly authorized fixes. Use when the user asks to babysit, monitor, or re-check a PR.
---

# PR Babysit

Accept an explicit PR reference (`owner/repo#number` or URL). A bare number is
valid only when the current repository is unambiguous. Identify its repository,
author, branch, worktree, remote head, and open or closed state.

Default to read-only. Fetch issue comments, reviews, inline comments,
review-thread state, CI checks, and actual failure logs where available.
Reconcile items by ID and distinguish new actionable feedback from
already-addressed or informational comments. Report incomplete access instead
of treating it as clean.

An explicit request to act authorizes scoped fixes only for the specified PR:
use `pr-comments-fix`, commit and push only to the user's own branch, and post
necessary replies. Never push to someone else's branch without separate
permission, force-push, merge, or close the PR. Preserve unrelated work and
stop if another worker is editing the same branch or files.

Verify the remote head, replies, and check results. If reply history cannot be
checked, do not risk posting a duplicate.
