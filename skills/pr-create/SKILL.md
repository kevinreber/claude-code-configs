---
name: pr-create
description: Create a pull request with concise, reviewer-friendly formatting. Use when the user asks to create, open, or submit a pull request.
---

# PR Create

Create a pull request with proper formatting following project guidelines.

## Writing style

- Lead with what changed and why. Prefer one to three short summary bullets.
- Write in the same plain language you would use when handing the change to a
  teammate. Prefer concrete verbs and project terms over generic phrases such
  as "enhances," "streamlines," "robust," or "comprehensive."
- Skip stock introductions such as "This PR introduces..." when the first
  bullet can state the change directly.
- Keep non-feature PR bodies under roughly 250 words and feature PRs under
  roughly 500 words unless material risk requires more.
- Include only information that helps a human understand, test, or safely
  review the change.
- Group related checks. Do not list every test, file, commit, validation pass,
  or implementation detail.
- Omit empty and not-applicable sections.
- For non-trivial PRs, perform three fresh passes over context discovery and
  follow-up items, merge unique results, and verify them against the diff.

### Testing Done

- Prefer one to three bullets. A simple change often needs only one.
- Group checks by reviewer value, not by the order they ran. Combine linters
  or targeted suites when the result is the same.
- State the observed result. Do not infer coverage from test names or explain
  every assertion.
- Mention failures, skipped checks, or unverified behavior only when they
  affect review or release confidence.
- Use `Not run: <reason>` for a material check that was not run. Do not list
  every check that could theoretically apply.

Too much:

> Ran the auth unit tests, then re-ran them after the null guard, then ran the formatter, linter, type checker, and a local code review. All validation steps completed successfully.

Better:

> - Auth tests: 182 passed, 3 skipped.
> - Formatting, lint, and type checks: passed.

## Instructions

1. Run `git status` to check current branch and any uncommitted changes
2. If there are uncommitted changes:
   - Analyze the staged/unstaged changes using `git diff --cached` and `git diff`
   - Generate a smart commit message following Conventional Commits format (see /commit-changes skill)
   - Stage files if needed: `git add -A` or specific files
   - Show the generated commit message to the user
   - If approved, commit with the message using HEREDOC format
   - Add `Co-Authored-By: Claude <noreply@anthropic.com>` to the commit message
3. Run `git log origin/main..HEAD --oneline` to see commits that will be included in the PR
4. Run `git diff origin/main...HEAD` to understand all changes in the branch
5. Analyze all commits and changes to draft a concise, complete PR description
6. **Determine PR type** — classify as a **feature PR** if any of these are true:
   - Has `feat:` or `feat(...):`commits
   - Adds new user-facing functionality, new API surface, or new subsystems
   - Changes more than ~200 lines across multiple files
   - Introduces new abstractions, patterns, or dependencies
7. **Context discovery — add only context that materially reduces reviewer effort:**
   - Use a small table when several concrete values changed and prose is harder
     to scan.
   - Use a diagram only for non-obvious interactions across components.
   - Document only changed API or interface behavior, with at most one useful
     example.
   - Use a short file tree only when structural changes are central.
   - For UI changes, include before-and-after screenshots or a short recording.
8. Check if the current branch is pushed to remote:
   - If not pushed or behind remote, run `git push -u origin <branch-name>`
9. Create the PR using `gh pr create` with proper format:
   - Title should be clear and descriptive
   - For **non-feature PRs** (bug fix, chore, refactor, docs), use the standard body:
     ```
     ## Summary
     - <1-3 short bullets describing what changed and why>

     ## Testing Done
     - <1-3 grouped checks with concise results>
     ```
   - For **feature PRs**, use the extended body (see Feature PR Format below)
10. Use a HEREDOC for the PR body to ensure correct formatting
11. Return the PR URL to the user
12. Remind them to request reviewers if needed
13. **Generate follow-up actions checklist:**
    Scan the diff and commits to identify follow-up items. Only include items that are actually relevant — skip any that don't apply.

    Check for:
    - **Documentation**: Did you add/change a public API, config option, CLI command, or user-facing behavior without updating docs?
    - **Tests**: Are there new code paths, edge cases, or error handling without corresponding tests?
    - **Migration/schema**: Did you add a DB migration, schema change, or data format change that needs coordination (rollback plan, backfill, backward compatibility)?
    - **Configuration**: Did you add new env vars, feature flags, or config entries that need to be set in staging/production?
    - **Dependencies**: Did you add or upgrade a dependency that may need security review or license check?
    - **Monitoring**: Did you add a new service, endpoint, or error path that should have alerts, dashboards, or logging?
    - **Cleanup**: Are there TODOs, temporary workarounds, or deprecated code paths introduced that should be tracked?
    - **Downstream impact**: Could these changes break or require updates in other services, consumers, or shared libraries?

    Present as a comment after the PR URL:
    ```
    ## Follow-up Actions
    - [ ] <action item with brief context>
    - [ ] <action item with brief context>
    ```

    If no follow-up actions are needed, say so explicitly: "No follow-up actions needed."

## Feature PR Format

For feature PRs, begin with the same concise Summary and Testing Done sections.
Add optional sections only when they materially help reviewers:

```
## Summary
- Bullet points describing what this feature does and why it was added

## Screenshots
<!-- REQUIRED for any UI change: show the final UI inline (rendered, not just a link).
See the "embedding screenshots" note in Important Notes for how to make images render in a
PR body, including on private repos. Use a Before | After table when a comparison helps. -->
| Before | After |
|--------|-------|
| <img> | <img> |

## Feature Diagram
<ASCII or Mermaid diagram showing the architecture, data flow, or component relationships.
Use Mermaid (```mermaid ... ```) for component/flow diagrams when the feature has multiple
interacting parts. Keep it to what helps a reviewer understand the design.>

## Design Trade-offs (optional)
| Decision | Chosen Approach | Alternative(s) | Why this approach |
|----------|----------------|----------------|-------------------|
| <material decision> | <choice> | <alternative> | <brief reason> |

## How to Test (optional)
- <manual reviewer steps not already covered by Testing Done>

## Known Limitations (optional)
- <real limitation or out-of-scope item>

## Testing Done
- <1-3 grouped checks with concise results>
```

## Important Notes

- Always analyze ALL commits in the branch, not just the latest one
- The Summary should accurately reflect the purpose and scope of changes
- Optional feature sections should appear only when they add reviewer value
- Trade-offs should capture real decisions, not hypotheticals
- Test steps should use real example values (not `<your value>`) so anyone can copy-paste and run them
- Before posting, remove filler, repeated context, and any sentence that sounds
  like a generated status report rather than a useful handoff
- Default base branch is `main` (check git config if unsure)
- If there are uncommitted changes, commit them first with a smart message
- Use Conventional Commits format for commit messages (feat, fix, docs, etc.)
- Always add Co-Authored-By footer to commits
- Do not poll CI after creating the PR unless the user requested a full
  lifecycle or CI status
- Use HEREDOC format for multi-line commit messages and PR bodies
- **UI changes: show the final UI inline in the PR body**, not just a linked file.
  Capture with Playwright or a headless browser and save to a real file path (a browser
  MCP extension often cannot persist a capture where you can attach it). To make an image
  RENDER inline: on a public repo any raw image URL works, but on a **private repo** `gh`
  cannot upload to GitHub user-attachments and `raw.githubusercontent.com` needs a token —
  so commit the PNG into the repo and reference it with a commit-SHA-pinned blob URL,
  `![alt](https://github.com/<owner>/<repo>/blob/<FULL_SHA>/<path>.png?raw=true)`, which
  renders for authenticated viewers and keeps working after the branch is deleted on merge.
