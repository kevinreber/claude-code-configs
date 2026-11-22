---
name: pr-shepherd
description: Shepherd a specified pull request through requested review, validation, feedback, and CI steps without merging it.
allowed-tools:
  - Bash
  - Glob
  - Grep
  - Read
  - Edit
  - Write
---

# PR Shepherd

Identify the repository, PR, branch, and requested scope before acting. Reuse
the `pr-pipeline` skill for an explicitly requested full lifecycle and
`pr-comments-fix` for approved review or CI fixes.

- A status or review request is read-only unless the user authorizes edits,
  pushes, or GitHub comments.
- Never push to someone else's branch without explicit permission. Check the
  worktree and remote head before editing or pushing, preserve unrelated work,
  and stop if another worker is changing the same files or branch.
- Do not poll CI after plain `pr-create` unless requested. CI checking is in
  scope for an explicitly requested pipeline or babysitting run.
- Investigate actual review threads and failed-check output, not only status
  summaries. Bound repeated passes and report blocked or external failures.
- Never merge or close a pull request.
- Report the PR URL, checks actually run, confirmed pushes or replies, and
  remaining gaps. Never claim a side effect or check succeeded without
  evidence.
