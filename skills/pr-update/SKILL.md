---
name: pr-update
description: Update an existing PR's title and description to reflect the latest commits while keeping it concise and reviewer-friendly.
---

# PR Update

Update the title and description of an existing pull request to accurately reflect all commits currently on the branch.

## Writing style

Follow `pr-create`'s concise PR-writing rules. Lead with what changed and why,
group checks, omit process narration, and include optional diagrams or tables
only when they materially reduce reviewer effort.

## Instructions

1. **Get current branch info:**
   ```bash
   git branch --show-current
   git log origin/main..HEAD --oneline
   ```
   - If no commits ahead of main, nothing to do — inform user

2. **Check for an open PR on this branch:**
   ```bash
   gh pr view --json number,title,body,url 2>/dev/null
   ```
   - If no PR exists, suggest running `/pr-create` instead and stop

3. **Read all commits and full diff:**
   ```bash
   git log origin/main..HEAD --format="%H %s%n%b" --no-merges
   git diff origin/main...HEAD --stat
   git diff origin/main...HEAD
   ```
   - Read the full diff carefully to understand the scope of changes

4. **Detect PR type — check BOTH the existing body AND the diff:**
   - **Existing body signals**: Does the current PR body contain `## Feature Diagram`, `## Design Trade-offs`, `## Known Limitations`, or Mermaid blocks? If yes, it's already a feature PR — preserve the extended format.
   - **Diff signals**: Classify as a feature PR if any are true:
     - Has `feat:` or `feat(...):` commits
     - Adds new user-facing functionality, new API surface, or new subsystems
     - Changes more than ~200 lines across multiple files
     - Introduces new abstractions, patterns, or dependencies
   - If either check indicates a feature PR, use the **Feature PR Format**

5. **Analyze what changed:**
   - What is the primary purpose of this PR? (1 sentence)
   - What are the key changes? (bullet list)
   - Are there any breaking changes, migrations, or notable considerations?

6. **Context discovery — add only material reviewer context:**
   - Use a table when several concrete values changed.
   - Use a diagram only for non-obvious component interactions.
   - Document only changed API or interface behavior.
   - Use a file tree only when structural changes are central.
   - For UI changes, preserve or add before-and-after visual evidence.

7. **Generate updated PR title:**
   - Follow Conventional Commits style: `<type>(<scope>): <subject>`
   - Max ~72 chars, imperative mood
   - Should reflect the primary purpose across ALL commits, not just the latest

8. **Generate updated PR description:**
   - For **non-feature PRs** (bug fix, chore, refactor, docs):
     ```
     ## Summary
     - <1-3 short bullets describing what changed and why>

     ## Testing Done
     - <1-4 grouped checks with concise results>
     ```
   - For **feature PRs**, use the Feature PR Format below

9. **Preserve custom content:**
   - Compare the existing PR body with the generated one section-by-section
   - Preserve any custom sections the user added that aren't in the template (e.g., linked issues, reviewer notes, deployment instructions)
   - For sections that exist in both, merge intelligently: keep user-written prose and update factual content (bullet points, tables, diagrams) to reflect the current diff
   - Never silently drop content — if removing a section, mention it in the diff shown to the user

10. **Show proposed title + description to user and ask for approval.**
    - Present current title vs proposed title
    - Present proposed description (highlight what changed from current)
    - Ask: "Update PR with these changes? (y/n/edit)"

11. **Apply the update:**
    ```bash
    gh pr edit --title "<new title>" --body "$(cat <<'EOF'
    <description>
    EOF
    )"
    ```

12. **Confirm:**
    ```bash
    gh pr view --json title,url
    ```
    - Show the PR URL so user can verify

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

For feature PRs, begin with concise Summary and Testing Done sections. Add
optional sections only when they materially help reviewers:

```
## Summary
- Bullet points describing what this feature does and why it was added

## Feature Diagram (optional)
<Include only for non-obvious component interactions.>

## Design Trade-offs (optional)
| Decision | Chosen Approach | Alternative(s) | Why this approach |
|----------|----------------|----------------|-------------------|
| <material decision> | <choice> | <alternative> | <brief reason> |

## How to Test (optional)
- <manual reviewer steps not already covered by Testing Done>

## Known Limitations (optional)
- <real limitation or out-of-scope item>

## Testing Done
- [ ] <test step with expected result>
- [ ] <edge case verified>
```

## Important Notes

- Always analyze ALL commits in the branch vs origin/main, not just the latest push
- If the user has manually customized the PR description, preserve any sections not in the standard template (e.g., linked issues, custom notes)
- Never update the PR without user confirmation
- If `gh` is not authenticated, tell the user to run `gh auth login`
- Optional feature sections should appear only when they add reviewer value
- Trade-offs table should capture real decisions made during implementation, not hypotheticals
- Context discovery tables should reflect actual values from the diff, not placeholders — a reviewer should learn something concrete by reading them
- When updating a feature PR with new commits, update existing sections to reflect the new state rather than appending — the PR description should read as a coherent document, not a changelog
