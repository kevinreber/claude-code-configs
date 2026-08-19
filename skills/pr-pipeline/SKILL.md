---
name: pr-pipeline
description: Orchestrate the full pull-request workflow end to end — pick the right mode (review an existing PR, ship new work, or respond to review comments), chain the pr-* and validate skills in the right order, converge over repeated passes, and always leave a visible trail on GitHub. Use when the user says "run the pipeline", "/pr-pipeline", "review this PR properly", "take this change all the way to a PR", or wants the standard post-change review workflow instead of invoking each skill by hand.
---

# PR Pipeline

The orchestrator for pull-request work. Individual skills (`validate`, `pr-review`, `pr-create`, …) each do one job well; this skill decides **which** of them to run, **in what order**, and **when to stop**.

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

The user may pass natural language alongside the invocation — `/pr-pipeline "review only, skip the validate passes"`, `/pr-pipeline "focus on correctness and rollout risk, skip the nits"`, `/pr-pipeline "do a review without pipeline"`. Honor it: it overrides the mode table and the phase selection. A modifier asking for less work means run less, not run the same work and summarize it differently.

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

This is the core of the pipeline. Run both skills — they catch different classes of problem, and the overlap between them is the signal that a finding is real.

1. **Invoke the `validate` skill** on the diff. Its six independent lenses (correctness, integration, adversarial, observability, test quality, operational readiness) plus the synthesis pass produce the deep findings.
2. **Invoke the `pr-review` skill** on the PR. It produces the line-anchored, severity-labeled comments that actually land on GitHub.

### Converging over repeated passes

A single pass under-reports. Repeat Phase 2 until findings stop changing, to a **maximum of three rounds**:

- **Round 1** establishes the baseline finding set.
- **Round 2** re-runs against the same diff. Genuinely new findings mean round 1 was incomplete; keep going.
- **Round 3** is the ceiling. Stop here even if new findings appear, and say so in the report rather than looping.

Stop early the moment a round produces no new findings. Deduplicate across rounds by `file:line` plus the substance of the claim — the same defect described two ways is one finding.

### Filtering before you post

Findings survive to Phase 5 only if you can state a concrete failure: specific inputs or state producing a wrong result, a crash, a security hole, or an operational failure. A finding you cannot make fail is a question, not a defect — either ask it as a question or drop it.

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

Close every run with this, in the conversation:

```
## PR Pipeline — <mode>

**PR:** <url or "not yet opened">
**Rounds run:** <n> (<converged | hit the 3-round ceiling>)

### Blockers
<findings that should stop a merge, with file:line and the concrete failure>

### Non-blocking
<worth fixing, will not break production>

### Checked and clean
<what you verified that turned out fine — this is what makes "no blockers" mean something>

### Posted to GitHub
<inline comment count, summary comment URL, review state — or an explicit "nothing posted, because …">

### Skipped
<any phase you did not run, and why>
```

## Important Notes

- **The pipeline composes skills; it does not reimplement them.** When a phase says invoke `validate` or `pr-review`, invoke that skill and follow it. Duplicating their logic here means the two drift apart.
- **Do not auto-commit on a PR you do not own.** Not even a formatting fix. Suggest it in a comment.
- **Three rounds is a ceiling, not a target.** Most PRs converge in one or two. Burning three rounds on a small diff produces manufactured findings.
- **Report honestly.** If the tests failed, show the output. If you skipped a phase, name it in the Skipped section. If findings were capped or filtered out, say how many and why.
- **Never post a review comment you have not verified against the actual diff.** A confidently wrong inline comment costs the author more time than no review at all.
