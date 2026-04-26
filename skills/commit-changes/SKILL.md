---
name: commit-changes
description: Generate a smart commit message from staged or unstaged changes and create a commit. Use when the user wants to commit their work with a meaningful message.
---

# Commit Changes

Analyze current changes and generate a meaningful commit message following Conventional Commits specification.

## Instructions

1. **Check for changes:**
   - Run `git status` to see what files have changed
   - If there are unstaged changes, ask user if they want to stage all or specific files

2. **Stage files if needed:**
   - If user wants to stage all: `git add -A`
   - If specific files: `git add <files>`

3. **Analyze staged changes:**
   - Run `git diff --cached --stat` to see what's staged
   - Run `git diff --cached` to see detailed changes
   - Analyze the changes to understand what was done

4. **Show diff preview to user:**
   - Run `git diff --cached` to get the full staged diff
   - Present the diff to the user so they can review exactly what will be committed
   - Ask if they want to proceed or make any changes before continuing

5. **Generate commit message following Conventional Commits:**

   **Format:**
   ```
   <type>(<scope>): <subject>

   <body>

   <footer>
   ```

   **Types:**
   - `feat`: New feature
   - `fix`: Bug fix
   - `docs`: Documentation only
   - `style`: Formatting, missing semicolons, etc.
   - `refactor`: Code change that neither fixes a bug nor adds a feature
   - `perf`: Performance improvement
   - `test`: Adding or updating tests
   - `chore`: Maintenance tasks, dependency updates
   - `ci`: CI/CD changes
   - `build`: Build system changes

   **Guidelines:**
   - Subject line: max 50 characters, imperative mood (e.g., "add", "fix", "update")
   - Body: wrap at 72 characters, explain what and why (not how)
   - Reference issues when applicable (e.g., "Closes #123", "Fixes #456")
   - Add `Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>` in footer

6. **Present the commit message:**
   ```
   Suggested commit message:

   feat(auth): add OAuth2 login support

   Implement Google and GitHub OAuth2 providers for user authentication.
   This replaces the legacy session-based auth system.

   - Add OAuth2 configuration endpoints
   - Implement token refresh logic
   - Update user model with provider fields

   Closes #123

   Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
   ```

7. **Ask for approval:**
   - Show the generated message to the user
   - Ask if they want to commit with this message or modify it

8. **Create the commit:**
   - Use HEREDOC format for proper multi-line message:
   ```bash
   git commit -m "$(cat <<'EOF'
   <commit message here>
   EOF
   )"
   ```

9. **Confirm success:**
   - Run `git log -1 --oneline` to show the commit was created
   - Display the commit hash and message

## Important Notes

- Always analyze the actual changes, don't guess
- Subject should be clear and concise (max 50 chars)
- Use imperative mood: "add feature" not "added feature"
- Body should explain WHY, not just WHAT
- Break down complex changes into bullet points
- Always add the Co-Authored-By footer
- Use HEREDOC for multi-line commit messages
- If changes span multiple concerns, suggest splitting into multiple commits
- Reference issue numbers when relevant (e.g., JIRA tickets, GitHub issues)
