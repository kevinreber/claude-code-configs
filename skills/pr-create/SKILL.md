---
name: pr-create
description: Create a pull request with proper formatting. Use when the user asks to create a PR, make a pull request, open a PR, or wants to submit their changes for review.
---

# PR Create

Create a pull request with proper formatting following project guidelines.

## Instructions

1. Run `git status` to check current branch and any uncommitted changes
2. If there are uncommitted changes:
   - Analyze the staged/unstaged changes using `git diff --cached` and `git diff`
   - Generate a smart commit message following Conventional Commits format (see /commit-changes skill)
   - Stage files if needed: `git add -A` or specific files
   - Show the generated commit message to the user
   - If approved, commit with the message using HEREDOC format
   - Add `Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>` to commit message
3. Run `git log origin/main..HEAD --oneline` to see commits that will be included in the PR
4. Run `git diff origin/main...HEAD` to understand all changes in the branch
5. Analyze all commits and changes to draft a comprehensive PR description
6. **Determine PR type** — classify as a **feature PR** if any of these are true:
   - Has `feat:` or `feat(...):`commits
   - Adds new user-facing functionality, new API surface, or new subsystems
   - Changes more than ~200 lines across multiple files
   - Introduces new abstractions, patterns, or dependencies
7. **Context discovery — scan the diff for rich context opportunities:**
   - **Classification/routing decisions**: If the diff adds, removes, or moves items between categories, registries, or config groups, generate a classification table showing each item, its category, and the rationale.
   - **Multi-component interactions**: If the diff touches multiple modules/packages that interact (caller/callee, parent/child, producer/consumer), generate a Mermaid diagram showing how they relate at runtime.
   - **Configuration/mapping changes**: If the diff modifies mappings, enums, feature flags, or permission lists, generate a table showing before→after states or the full current mapping.
   - **API/interface changes**: If the diff adds or modifies tool definitions, endpoints, or public interfaces, document the new interface with parameters and usage examples.
   - **Structural changes**: If the diff adds new directories, moves files, or reorganizes module structure, include a file tree showing the new layout. For file moves/renames, show a before→after tree to make the reorganization clear.
   - These context tables, diagrams, and file trees should appear in the appropriate feature PR sections (Summary for tables, Feature Diagram for diagrams, etc.)
   - For non-feature PRs, still add a brief context table or file tree in the Summary if the diff contains classification/mapping or structural changes — reviewers always benefit from seeing the concrete values.
8. Check if the current branch is pushed to remote:
   - If not pushed or behind remote, run `git push -u origin <branch-name>`
9. Create the PR using `gh pr create` with proper format:
   - Title should be clear and descriptive
   - For **non-feature PRs** (bug fix, chore, refactor, docs), use the standard body:
     ```
     ## Summary
     - Bullet points describing the changes

     ## Testing Done
     - [ ] Checkbox items for testing steps
     ```
   - For **feature PRs**, use the extended body (see Feature PR Format below)
10. Use a HEREDOC for the PR body to ensure correct formatting
11. Return the PR URL to the user
12. Remind them to request reviewers if needed
13. **Generate follow-up actions checklist:**
    Scan the diff and commits to identify follow-up items. Only include items that are actually relevant — skip any that don't apply.

    Check for:
    - **Documentation**: Did you add/change a public API, config option, CLI command, or user-facing behavior without updating docs (README, docstrings, wiki, Confluence)?
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

For feature PRs, the description must help reviewers understand the change deeply and be able to test it themselves:

```
## Summary
- Bullet points describing what this feature does and why it was added

## Feature Diagram
<ASCII or Mermaid diagram showing the architecture, data flow, or component relationships.
Use Mermaid (```mermaid ... ```) for component/flow diagrams when the feature has multiple
interacting parts. Keep it to what helps a reviewer understand the design.>

## Design Trade-offs
| Decision | Chosen Approach | Alternative(s) | Why this approach |
|----------|----------------|----------------|-------------------|
| <topic>  | <what was done> | <other options> | <reasoning + when you'd choose differently> |

## How to Test
Concrete inputs/scenarios anyone can run to verify the feature works:
- [ ] <step or input> → expected output
- [ ] <edge case> → expected behavior
- [ ] <error/failure scenario> → expected handling

## Known Limitations
- <limitation or out-of-scope item> — <context or future work if applicable>

## Testing Done
- [ ] <test step with expected result>
- [ ] <edge case verified>
```

## Important Notes

- Always analyze ALL commits in the branch, not just the latest one
- The Summary should accurately reflect the purpose and scope of changes
- For feature PRs: the diagram, trade-offs, test steps, and limitations are **required** — don't skip them even if brief
- Trade-offs table should capture real decisions made during implementation, not hypotheticals
- Test steps should use real example values (not `<your value>`) so anyone can copy-paste and run them
- Default base branch is `main` (check git config if unsure)
- If there are uncommitted changes, commit them first with a smart message
- Use Conventional Commits format for commit messages (feat, fix, docs, etc.)
- Always add Co-Authored-By footer to commits
- Use HEREDOC format for multi-line commit messages and PR bodies
