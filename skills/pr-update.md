---
name: pr-update
description: Update an existing PR's title and description to reflect the latest commits on the branch. Use when the user has pushed new commits to an existing PR and wants the PR metadata to stay accurate.
---

# PR Update

Update the title and description of an existing pull request to accurately reflect all commits currently on the branch.

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
   ```
   - Read the full diff carefully to understand the scope of changes

4. **Analyze what changed:**
   - What is the primary purpose of this PR? (1 sentence)
   - What are the key changes? (bullet list)
   - Are there any breaking changes, migrations, or notable considerations?

5. **Generate updated PR title:**
   - Follow Conventional Commits style: `<type>(<scope>): <subject>`
   - Max ~72 chars, imperative mood
   - Should reflect the primary purpose across ALL commits, not just the latest

6. **Generate updated PR description:**
   ```
   ## Summary
   - <bullet 1>
   - <bullet 2>
   - ...

   ## Testing Done
   - [ ] <test step 1>
   - [ ] <test step 2>

   🤖 Generated with [Claude Code](https://claude.com/claude-code)
   ```

7. **Show proposed title + description to user and ask for approval.**
   - Present current title vs proposed title
   - Present proposed description
   - Ask: "Update PR with these changes? (y/n/edit)"

8. **Apply the update:**
   ```bash
   gh pr edit --title "<new title>" --body "$(cat <<'EOF'
   <description>
   EOF
   )"
   ```

9. **Confirm:**
   ```bash
   gh pr view --json title,url
   ```
   - Show the PR URL so user can verify

## Important Notes

- Always analyze ALL commits in the branch vs origin/main, not just the latest push
- If the user has manually customized the PR description, preserve any sections not in the standard template (e.g., linked issues, custom notes) — only update Summary and Testing Done
- Never update the PR without user confirmation
- If `gh` is not authenticated, tell the user to run `gh auth login`
