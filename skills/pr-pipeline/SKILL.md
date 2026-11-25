---
name: pr-pipeline
description: Orchestrate the full pull-request workflow end to end — pick the right mode, validate and simplify the diff, review it, respond to feedback, converge over repeated passes, and leave a visible trail on GitHub. Use when the user says "run the pipeline", "/pr-pipeline", "review this PR properly", "take this change all the way to a PR", or wants the standard post-change review workflow instead of invoking each skill by hand.
---

# PR Pipeline

The orchestrator for pull-request work. Individual skills (`validate`,
`pr-simplicity-review`, `pr-review`, `pr-create`, …) each do one job well; this
skill decides **which** of them to run, **in what order**, and **when to stop**.

Two rules govern everything below:

1. **Never silently change someone else's pull request.** On a PR you do not own, the pipeline is advisory: it reads, analyzes, and comments. It does not commit, push, or force-push.
2. **Review effort that stays in the terminal did not happen.** Every review pass ends with something visible on GitHub — inline comments, a summary comment, or a formal review. A local-only analysis is an incomplete run.

## Phase 0: Detect Mode

Gather state first, then pick a mode. Do not ask the user which mode to use if the state answers it.

```bash
git status --short --branch
git log --oneline @{u}..HEAD 2>/dev/null | head
gh pr status --json number,title,url,author,isDraft,reviewDecision 2>/dev/null
```

If the user named a PR number or URL, fetch it directly and skip the inference:

```bash
gh pr view <ref> --json number,title,author,url,state,isDraft,baseRefName,headRefName,additions,deletions,changedFiles
```

Choose the mode:

| State | Mode | What runs |
|---|---|---|
| A PR reference was given, or an open PR exists and its author is not you | **review** | Phase 1 → Phase 2 → Phase 5 |
| An open PR exists, you authored it, and it has unaddressed review comments | **respond** | Phase 4 → Phase 2 → Phase 5 |
| An open PR exists, you authored it, no outstanding comments | **review** (self-review) | Phase 1 → Phase 2 → Phase 5 |
| Uncommitted or unpushed work, no PR yet | **ship** | Phase 1 → Phase 3 → Phase 2 → Phase 5 |

Determine PR ownership by comparing the PR author to `gh api user --jq .login`. Do not assume from the branch name.

State the chosen mode in one line before proceeding, so the user can redirect you if the inference was wrong.

### Freeform modifiers

The user may pass natural language alongside the invocation —
`/pr-pipeline "review only, skip the validate passes"`,
`/pr-pipeline "skip simplicity"`, `/pr-pipeline "focus on correctness and
rollout risk, skip the nits"`, or `/pr-pipeline "do a review without
pipeline"`. Honor it: it overrides the mode table and phase selection. A
modifier asking for less work means run less, not run the same work and
summarize it differently.

## Phase 1: Pre-flight

Before analyzing anything, make sure you are analyzing the right thing.

1. **Confirm the diff base.** For a PR, review `gh pr diff <number>` — not `git diff HEAD`, which misses commits and includes local noise.
2. **Check for drift from the base branch.** Run `scripts/pr-sync-check.sh` if the repo has it, otherwise:
   ```bash
   git fetch origin <base> --quiet
   git log --oneline HEAD..origin/<base> | wc -l
   ```
   If the branch is behind by enough that the diff is misleading (conflicting files, or the base has moved under the changed files), invoke the **`pr-sync-branch`** skill before continuing. Skip this on a PR you do not own — flag the staleness in the review instead.
3. **Read the PR description.** A description that does not match the diff is itself a finding, and it is the most common one.

## Phase 2: Analysis Passes

This is the core of the pipeline. Run these skills in order:

1. **Invoke the `validate` skill** on the diff. Its six independent lenses
   (correctness, integration, adversarial, observability, test quality,
   operational readiness) plus the synthesis pass produce the deep findings.
2. **Invoke `pr-simplicity-review` once** against the same current diff. It
   checks for removable complexity, redundant code or tests, missed reuse,
   speculative abstractions, and scope creep.
3. **Invoke the `pr-review` skill** on the resulting PR diff. It verifies and
   deduplicates the earlier candidates, then produces the line-anchored,
   severity-labeled comments that land on GitHub.

On the user's PR, `pr-simplicity-review` may apply high-confidence,
behavior-preserving simplifications. Run the smallest relevant validation,
commit, and push before `pr-review` so it reviews the updated diff. On another
author's PR, `validate` and `pr-simplicity-review` are report-only; pass their
material candidates into `pr-review` without changing the branch.

### Converging over repeated passes

A single pass can under-report. Repeat Phase 2 against the current diff until
findings stop changing, to a **maximum of three rounds**. Run
`pr-simplicity-review` once per round; do not ensemble it separately.

- **Round 1** establishes the baseline finding set.
- **Round 2** re-runs against the same diff. Genuinely new findings mean round 1 was incomplete; keep going.
- **Round 3** is the ceiling. Stop here even if new findings appear, and say so in the report rather than looping.

Stop early the moment a round produces no new findings or material
simplifications. Deduplicate across rounds by `file:line` plus the substance of
the claim — the same issue described two ways is one finding.

### Filtering before you post

Correctness findings survive to Phase 5 only if you can state a concrete
failure: specific inputs or state producing a wrong result, a crash, a security
hole, or an operational failure. A finding you cannot make fail is a question,
not a defect — either ask it as a question or drop it.

Simplicity findings use `pr-simplicity-review`'s stricter maintainability bar
instead: an exact unnecessary element, a concrete behavior-preserving
alternative, and meaningful maintenance value. Treat these as non-blocking
unless the complexity also creates a correctness or operational risk.

Weight the output toward correctness and rollout blockers. Style nits are worth posting only when the surrounding code makes the convention unambiguous.

## Phase 3: Ship (ship mode only)

1. Invoke the **`pr-smart-commit`** skill to split the work into focused, reviewable commits. If the change is genuinely one concern, one commit is the correct answer — do not manufacture a split.
2. Push the branch.
3. Invoke the **`pr-create`** skill to open the PR with a properly formatted description.
4. Return to Phase 2 and self-review the PR you just opened. Reviewing your own PR after it exists — rather than before — keeps the diff equal to your actual changes and produces a visible review artifact.

## Phase 4: Respond (respond mode only)

1. Fetch the outstanding threads:
   ```bash
   gh api repos/{owner}/{repo}/pulls/<number>/comments --paginate
   gh api repos/{owner}/{repo}/pulls/<number>/reviews --paginate
   ```
2. Invoke the **`pr-comments-fix`** skill to work through them.
3. Return to Phase 2 to confirm the fixes are correct and did not introduce new problems — review feedback applied without re-validation is how regressions ship.
4. If the description no longer matches the changed diff, invoke the **`pr-update`** skill.

## Phase 5: Land the Trail on GitHub

Non-negotiable. Pick the form that fits, but post something.

- **Findings to report:** let `pr-review` post the inline comments, then post one summary comment with the verdict.
- **Someone else's PR, clean:** post a short summary comment stating what you checked and that you found no blockers, then approve if you intend to. "It looked fine" with nothing on the PR leaves teammates and future readers no record that a review happened.
- **Your own PR:** post the self-review as a comment. It tells reviewers where you already looked.
- **The user explicitly asked for a local-only read:** honor that, and say plainly in your final message that nothing was posted.

Verify the post landed:

```bash
gh pr view <number> --json comments --jq '.comments[-1].url'
```

## Final Report

Close every run with a short teammate-style handoff:

```
**PR:** <url or "not yet opened">
**Result:** <ready for review/merge, needs changes, or review posted>
- <material blocker or outcome>
- <current check status>
**Still open:** <only items that need a human decision>
```

- Omit Still open when nothing remains.
- Mention the round count only when the three-round ceiling was reached or a
  later round materially changed the result.
- Mention skipped work only when it leaves something unverified.
- Do not add a "checked and clean" inventory, narrate every phase, or paste the
  internal analysis into the handoff.
- Use direct sentences, concrete outcomes, and no generic praise or
  generated-sounding status language.

## Important Notes

- **The pipeline composes skills; it does not reimplement them.** When a phase
  says invoke `validate`, `pr-simplicity-review`, or `pr-review`, invoke that
  skill and follow it. Duplicating their logic here means the skills drift.
- **Do not auto-commit on a PR you do not own.** Not even a formatting fix. Suggest it in a comment.
- **Never merge, close, or force-push a pull request.**
- **Three rounds is a ceiling, not a target.** Most PRs converge in one or two. Burning three rounds on a small diff produces manufactured findings.
- **Do not multiply review passes.** `validate` and `pr-review` already perform
  independent analysis. `pr-simplicity-review` is deliberately one bounded pass
  per outer round.
- **Report honestly.** If the tests failed, show the output. If skipped work leaves something unverified, say so. If findings were capped or filtered out, say how many and why.
- **Never post a review comment you have not verified against the actual diff.** A confidently wrong inline comment costs the author more time than no review at all.
- **Keep GitHub-facing text human.** Comments, replies, summaries, and PR-body
  updates inherit the natural-language rules from the underlying skills.
