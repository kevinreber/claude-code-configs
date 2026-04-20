---
name: pr-comments-fix
description: Address PR comments intelligently by analyzing feedback, proposing fixes, and providing a summary of actions taken. Use when the user wants to respond to PR review comments.
---

# PR Comments Fix

Fetch PR comments, analyze reviewer feedback, propose fixes, and provide a comprehensive summary of actions taken.

## Instructions

1. **Identify the current PR:**
   - Run `gh pr view --json number,title,url,headRefName` to get current PR info
   - If not on a PR branch, ask user which PR to work on
   - If user provides PR number, use that: `gh pr view <number>`

2. **Fetch all PR comments:**
   - Fetch issue comments: `gh api /repos/{owner}/{repo}/issues/{pr_number}/comments`
   - Fetch review comments: `gh api /repos/{owner}/{repo}/pulls/{pr_number}/comments`
   - Fetch review summaries: `gh pr view {pr_number} --json reviews`

3. **Parse and categorize comments:**

   **Bot Comments** (informational, usually low priority):
   - CI/CD bots (github-actions, CircleCI, etc.)
   - Coverage bots
   - Linting/formatting bots
   - Security scanning bots

   **Human Comments** (require analysis):
   - Questions needing answers
   - Suggestions for improvement
   - Required changes
   - Design feedback
   - Nitpicks (style, naming, formatting)

4. **Analyze each human comment:**

   For each comment:
   - **Read the context:** Fetch the relevant code/file mentioned in the comment
   - **Understand the request:** What is the reviewer asking for?
   - **Categorize the feedback:**
     - `QUESTION`: Needs answer/clarification
     - `REQUIRED`: Must be addressed (security, bugs, breaking issues)
     - `SUGGESTION`: Optional improvement (best practices, clarity, performance)
     - `NITPICK`: Style/formatting preference
     - `DESIGN`: Architectural or design feedback

   - **Evaluate the merit:**
     - Is this feedback valid?
     - Does it improve code quality, security, or maintainability?
     - Are there trade-offs to consider?
     - Does it align with project conventions?

5. **Propose response for each comment:**

   Present to user in this format:

   ```
   Comment #1 - @reviewer (file.ts:42)
   Type: SUGGESTION
   Comment: "Consider using a Map instead of an object for better performance"

   Analysis:
   - Current code uses plain object for lookup
   - Map would provide O(1) lookup vs O(n) for large datasets
   - No significant downside for this use case

   Proposed Action: ACCEPT
   Proposed Fix:
   [Show code diff of the change]

   Reasoning: Valid performance optimization with no breaking changes

   ---

   Comment #2 - @reviewer (README.md:10)
   Type: NITPICK
   Comment: "Can we rename this variable for clarity?"

   Analysis:
   - Current name is consistent with project conventions
   - Suggested name is more descriptive but breaks pattern

   Proposed Action: DECLINE
   Reasoning: Conflicts with existing project naming conventions
   Alternative: Add comment explaining the naming

   ---
   ```

6. **Wait for user approval:**
   - Show proposed actions for ALL comments
   - Ask: "Which comments would you like me to address?"
   - User can approve all, approve specific ones, or modify approach
   - **Do NOT make changes until approved**

7. **Apply approved fixes:**
   - Make code changes for approved comments
   - Stage changes: `git add <files>`
   - Create commit with message:
     ```
     Address PR feedback

     - [Comment #1]: Use Map instead of object for performance
     - [Comment #2]: Update error handling per reviewer suggestion
     - [Comment #3]: Add JSDoc comments for clarity

     Co-Authored-By: Claude <noreply@anthropic.com>
     ```
   - Push changes: `git push`

8. **Optionally reply to comments:**
   - Ask user if they want to post replies to PR comments
   - For ACCEPTED changes: Reply with "Fixed in [commit hash]"
   - For DECLINED changes: Reply with polite explanation
   - For QUESTIONS: Reply with answer
   - Use: `gh pr comment {pr_number} --body "..."`

9. **Provide comprehensive summary:**

   ```markdown
   ## PR Comments Summary

   **PR #123**: [Title]

   ### Addressed Comments (3)

   **Comment #1** (@reviewer - auth.ts:42)
   - Type: SUGGESTION
   - Request: Use Map instead of object
   - Action: Implemented change
   - Commit: abc123d

   **Comment #2** (@reviewer - utils.ts:15)
   - Type: REQUIRED
   - Request: Fix null pointer exception
   - Action: Added null check
   - Commit: abc123d

   **Comment #3** (@reviewer - README.md:5)
   - Type: QUESTION
   - Request: How does caching work?
   - Action: Replied with explanation

   ### Ignored Comments (2)

   **Comment #4** (@reviewer - styles.css:10)
   - Type: NITPICK
   - Request: Different color scheme
   - Reason: Follows existing design system

   **Comment #5** (github-actions bot)
   - Type: BOT
   - Content: Coverage report
   - Reason: Informational only, no action needed

   ### Bot Comments (1)

   **github-actions**: CI check results
   - Informational warnings
   - No critical issues

   ### Stats
   - Total Comments: 6
   - Addressed: 3
   - Ignored: 2
   - Bot/Info: 1
   - Commits Created: 1
   - Files Changed: 3
   ```

## Important Notes

- **CRITICAL**: Never make changes without user approval
- Always read the code context for each comment
- Evaluate feedback objectively - not all suggestions should be implemented
- Consider project conventions and existing patterns
- Be respectful when declining suggestions - explain reasoning
- Group related fixes into single commits
- Use conventional commit messages
- Always add Co-Authored-By footer to commits
- Bot comments are usually informational - acknowledge but don't always act
- Questions should be answered, not just dismissed
- Security and bug fixes should always be implemented
- Style preferences should align with project conventions
- If unsure about a comment, ask the user for guidance
- Update PR description if significant changes were made
