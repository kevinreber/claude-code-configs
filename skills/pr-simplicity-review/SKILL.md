---
name: pr-simplicity-review
description: Review a PR, branch diff, or uncommitted changes for unnecessary complexity, redundant code or tests, speculative abstractions, and scope creep. Use before a PR review or when the user asks whether changes are as small, simple, readable, and maintainable as possible.
---

# PR Simplicity Review

Run one focused maintainability pass over the changed surface. Find material
complexity that can be removed without weakening correctness, safety, type
checking, error handling, or meaningful test coverage.

This skill works on a GitHub PR, a branch diff, or local uncommitted changes.
It complements correctness validation and `pr-review`; it does not replace them.

## Phase 1: Resolve the Changed Surface

1. If the user supplied a PR number or URL, fetch its metadata and full diff:
   ```bash
   gh pr view <ref> --json number,url,author,baseRefName,headRefName,title
   gh pr diff <ref>
   ```
2. If there is no PR, review the current branch and working tree against the
   repository's default branch. Include staged, unstaged, and untracked files.
3. Read the complete diff before forming findings. Then read enough surrounding
   code to understand the existing design and search for helpers or patterns the
   change could reuse.
4. For a PR, compare its author with `gh api user --jq .login`.
   - Another author's PR is always report-only.
   - The user's own change is report-only unless the user or a parent workflow
     explicitly authorized applying simplifications.

## Phase 2: Review for Removable Complexity

Check only complexity introduced by the changed surface:

- **Redundant scope:** unrelated cleanup, duplicate branches, repeated
  validation, unused compatibility paths, or multiple implementations of one
  behavior.
- **Missed reuse:** new helpers, endpoints, resources, configuration, or
  dependencies where an existing path already meets the requirement.
- **Premature abstraction:** wrappers, factories, generic frameworks,
  extension points, or future-proofing that serves no current use case.
- **Unnecessary indirection:** nested functions, callback layers, pass-through
  methods, fragmented control flow, or data transformations that make the
  behavior harder to follow without buying real reuse or isolation.
- **Low-value tests:** duplicate coverage, assertions tied only to
  implementation details, tests for constants/framework behavior/trivial
  accessors, or setup cost disproportionate to the behavior protected.
- **Maintenance-only baggage:** comments that restate the code, configuration
  that is never used, dependencies added for trivial behavior, or new public
  surface that can remain private.

## Finding Bar

Report a finding only when all of these are true:

1. The exact unnecessary code, test, configuration, or scope is identifiable.
2. A concrete simpler alternative exists.
3. The alternative preserves required behavior and safety.
4. The change meaningfully reduces review or maintenance burden.

Do not report subjective style preferences, fewer-lines-only rewrites, or
changes that remove useful clarity. Do not remove defensive handling for
realistic failures, type safety, observability, authorization, rollback
support, or tests that protect meaningful behavior.

Consolidate related findings and keep at most the three highest-value items.
If nothing clears the bar, return `No material simplifications found.`

## Phase 3: Return or Apply

For each finding, provide:

- `location`: file and changed line
- `remove/simplify`: the unnecessary part
- `replacement`: the concrete simpler shape
- `why safe`: why behavior and safeguards remain intact
- `maintenance value`: what ongoing cost disappears

In apply mode:

1. Make only high-confidence, behavior-preserving simplifications.
2. Re-read the resulting diff to ensure scope did not grow.
3. Run the smallest relevant tests, lint, or build checks after simplifying.
4. Do not commit or push unless the user or parent workflow authorized it.

This skill does not post GitHub comments directly. In a review workflow,
return findings to `pr-review`, which verifies, deduplicates, assigns severity,
and owns all GitHub-facing comments.

## `pr-pipeline` Contract

`pr-pipeline` invokes this skill once after validation and immediately before
`pr-review` in every analysis round:

- On the user's PR, the pipeline may apply confirmed simplifications, validate
  them, and push the updated diff before `pr-review`.
- On another author's PR, remain report-only and pass material candidates to
  `pr-review`.
- Do not ensemble or internally loop this skill. The outer pipeline rounds
  rerun it after changes so newly introduced complexity is reviewed again.
