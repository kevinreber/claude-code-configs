---
name: pr-comments-fix
description: Address pull-request comments and failing CI checks, post concise replies, verify results, and repeat until nothing actionable remains or progress is blocked.
---

# PR Comments Fix

Fetch all review feedback and CI state, analyze it, propose scoped fixes, and
verify every approved action.

## Writing style

- Keep discovery and verification internal; do not turn them into a transcript.
- Write replies the way a teammate would: answer the point directly, use the
  reviewer's terminology, and say what changed or why the suggestion does not
  fit.
- Avoid canned phrases such as "Thank you for the feedback," "Addressed,"
  "Implemented as suggested," or "This has been resolved."
- Do not use `Analysis:`, `Resolution:`, `Rationale:`, or similar report-style
  labels in posted replies.
- Mention a commit hash only when it helps the reviewer find the change. A
  useful reply explains the change; `Fixed in abc123` by itself usually does
  not.

## Instructions

1. **Identify the current PR:**
   - Run `gh pr view --json number,title,url,headRefName` to get current PR info
   - If not on a PR branch, ask user which PR to work on
   - If user provides PR number, use that: `gh pr view <number>`

2. **Fetch all comments, threads, and checks:**
   - Fetch issue comments: `gh api /repos/{owner}/{repo}/issues/{pr_number}/comments`
   - Fetch inline comments: `gh api /repos/{owner}/{repo}/pulls/{pr_number}/comments`
   - Fetch review summaries: `gh pr view {pr_number} --json reviews`
   - Fetch resolved-thread state with GraphQL:
     ```bash
     gh api graphql -f query='
       query($owner:String!, $repo:String!, $pr:Int!) {
         repository(owner:$owner, name:$repo) {
           pullRequest(number:$pr) {
             reviewThreads(first:100) {
               nodes {
                 id
                 isResolved
                 comments(first:50) {
                   nodes { id body path line author { login } }
                 }
               }
             }
           }
         }
       }' -f owner="<owner>" -f repo="<repo>" -F pr=<number>
     ```
   - Fetch CI state: `gh pr checks <number> --json name,state,bucket,link`
   - For failing GitHub Actions checks, fetch actual failure output with
     `gh run view <run-id> --log-failed`
   - Reconcile REST and GraphQL comments by ID. Missing data is an access
     limitation, not a clean result.

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

   **CI failures**:
   - Tests, lint, type-check, build, coverage, or policy failures
   - Flaky or external failures that reproduce independently of the PR
   - Never bypass a check merely to make it green

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

5. **Propose responses and fixes:**

   Group items that share a root cause and present a compact table:

   ```markdown
   | Item | Action | Reason |
   |---|---|---|
   | `auth.ts:42` — @reviewer | Accept: add null guard | Prevents a confirmed crash |
   | `README.md:10` — @reviewer | Decline | Existing name matches project convention |
   | `unit-tests` | Fix auth header | Failure is caused by the new middleware |
   ```

   Show a code diff only when the fix is not obvious from the table.

6. **Wait for user approval:**
   - Show proposed actions for all comments and failing checks
   - Ask which comments and check fixes to address
   - User can approve all, approve specific ones, or modify approach
   - **Do NOT make changes until approved**

7. **Apply approved fixes:**
   - Make code changes for approved comments and check failures
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

8. **Post replies for approved actions:**
   - For ACCEPTED changes: Say what changed in one sentence, optionally
     followed by the commit hash. Example: `Updated the retry path so 4xx
     responses fail immediately; the change is in abc123.`
   - For DECLINED changes: Explain the concrete reason in one or two sentences
     without sounding defensive.
   - For QUESTIONS: Answer the question directly without first summarizing the
     thread.
   - Reply in-thread for inline comments instead of posting disconnected
     top-level comments

9. **Verify and repeat:**
   - Re-fetch issue comments, inline comments, GraphQL threads, and CI checks.
   - Confirm every intended reply is present.
   - Confirm approved fixes were pushed and checks pass.
   - If new actionable comments arrived or checks remain red because of this
     PR, repeat the cycle. Stop after three iterations or when blocked.

10. **Provide a concise summary:**

    ```markdown
    ## PR Feedback

    Addressed 3 comments, confirmed all 3 replies, and required checks are passing.

    - Fixed the null-handling issue and updated the affected test.
    - Answered the caching question in-thread.

    **Still open:** One external integration check remains unavailable.
    ```

    Omit Still open when nothing remains. Keep the summary focused on outcomes,
    not the sequence of work.

## Important Notes

- **CRITICAL**: Never make code changes without user approval
- Discover comments and checks exhaustively instead of relying on one API
- Verify every reply, push, and check result before reporting success
- Treat failing checks as first-class feedback
- Loop until clean or blocked, up to three iterations
- Always read the code context for each comment
- Evaluate feedback objectively - not all suggestions should be implemented
- Consider project conventions and existing patterns
- Be respectful when declining suggestions - explain reasoning
- Group related fixes into single commits
- Use conventional commit messages
- Always add Co-Authored-By footer to commits
- Bot comments are usually informational - acknowledge but don't always act
- Questions should be answered, not just dismissed
- Prioritize confirmed security and correctness issues, but preserve the
  approval gate before changing code
- Style preferences should align with project conventions
- If unsure about a comment, ask the user for guidance
- Update PR description if significant changes were made
