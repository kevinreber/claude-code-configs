---
name: pr-review
description: Perform an issue-focused review of a pull request, post concise natural-language inline comments, and leave a short summary with the overall verdict.
---

# PR Review

Perform a deep review internally, then post concise, actionable feedback.

## Feedback policy

- Do not generate praise findings or "what is working well" sections.
- Prefer one issue per inline comment: problem, impact, and concrete fix.
- Write like a teammate, not an audit tool. Use plain words, active voice, and natural sentences.
- Start with the concrete behavior or failure. Avoid generic openings such as
  "This change introduces," "It is important to note," or "There is a
  potential risk."
- Do not use `Problem:`, `Impact:`, `Recommendation:`, or similar report-style
  labels inside posted comments.
- Avoid canned praise and politeness such as "Looks good overall," "Great
  work," or "Thanks for the changes."
- Use project terminology from the diff instead of vague phrases such as "the
  system," "the logic," or "the implementation."
- Keep inline comments under roughly 100 words and summaries under roughly 200
  words unless a complex issue requires more.
- Do not expose internal review mechanics or reviewer personas.
- For non-trivial PRs, use three independent read-only passes when available,
  merge the union of findings, and verify each against the diff.

## Phase 1: Setup & Specialization

1. **Identify the PR to review:**
   - If a PR number or URL was provided, use it
   - Otherwise run: `gh pr list --limit 10` and ask the user which PR to review

2. **Fetch PR metadata:**
   ```bash
   gh pr view <number> --json number,title,body,author,baseRefName,headRefName,url,additions,deletions,changedFiles
   ```

3. **Fetch the full diff:**
   ```bash
   gh pr diff <number>
   ```

4. **Detect languages and frameworks:**
   - Scan file extensions and import/require/use statements in the diff
   - Identify frameworks, libraries, and patterns in use (e.g. React hooks, Express middleware, Go interfaces, Django ORM, etc.)

5. **Adopt specialist mindset:**
   Based on detected stack, internalize the relevant expert knowledge:
   - **Go**: idiomatic error handling, goroutine safety, interface design, avoid naked returns
   - **TypeScript/JS**: type safety, async/await pitfalls, React hook rules, bundle size awareness
   - **Python**: Pythonic idioms, type hints, exception handling, generator/comprehension use
   - **Java/Kotlin**: null safety, resource management, SOLID principles, thread safety
   - **SQL**: query performance, index usage, N+1 problems, injection safety
   - **Rust**: ownership/borrowing correctness, unsafe usage, error propagation
   - **Shell/Bash**: quoting, error handling (`set -e`/`set -u`), portability
   - **YAML/Config**: schema correctness, secret exposure, env var usage
   - *(Apply equivalent expertise for any other detected language)*

   Use the specialization internally rather than announcing a persona.

---

## Phase 2: Description Quality Check (Feature PRs)

**Before reviewing code**, determine if this is a feature PR:
- Has `feat:` commits, adds new user-facing functionality, new API surface, or new subsystems
- Or changes 200+ lines across multiple files introducing new behavior

If it **is** a feature PR, check whether these sections are needed and present:

| Section | What to look for |
|---------|-----------------|
| **Feature Diagram** | Architecture, data flow, or component diagram (ASCII or Mermaid) |
| **Design Trade-offs** | Table or list of key decisions with alternatives and reasoning |
| **How to Test** | Concrete example inputs/steps with expected outputs anyone can run |
| **Known Limitations** | Explicit callouts of what's out of scope or has known gaps |

Separately, whenever UI or frontend files changed, check for screenshots or a
short recording regardless of PR size. For missing material context, include
only the applicable items in a short top-level list:

```
### PR description
- **How to Test:** Add concrete reviewer steps and expected results.
- **Screenshots:** Add before-and-after evidence for the UI change.
```

Skip feature-only sections for non-feature PRs, but still apply the screenshots
check to UI changes.

---

## Phase 3: Code Analysis

Read every changed file carefully. For each change, evaluate:

### Correctness & Bugs
- Logic errors, off-by-one errors, null/nil dereferences
- Race conditions, deadlocks, improper resource cleanup
- Incorrect error handling (swallowed errors, wrong propagation)
- Edge cases not handled

### Security
- Injection vulnerabilities (SQL, command, XSS, SSRF)
- Secrets or credentials in code
- Improper authentication/authorization checks
- Insecure deserialization, path traversal

### Mutation and blast radius

For every changed endpoint, command, or workflow step, classify it as
read-only or mutating. For mutating operations, check authorization,
confirmation, idempotency, rollback, dry-run or staging support, and test
coverage proportional to the blast radius.

### Performance
- N+1 queries, missing indexes, unbounded loops
- Memory leaks, unnecessary allocations
- Blocking calls in async contexts
- Missing caching opportunities

### Design & Architecture
- Violation of SOLID/DRY/YAGNI principles
- Poor separation of concerns
- Hard-to-test code (tight coupling, no dependency injection)
- Missing or incorrect abstractions

### Code Quality & Maintainability
- Unclear naming (variables, functions, types)
- Functions doing too many things
- Missing or misleading comments/docs
- Unnecessary complexity

### Style & Conventions
- Inconsistency with surrounding codebase style
- Formatting, naming convention deviations
- Trivial suggestions (nits)

---

## Phase 4: Build Comment List

Compile all findings into a structured list before posting. Each finding needs:
- `file`: the file path
- `line`: the line number in the diff (the **right side / new file** line number)
- `severity`: one of CRITICAL / MAJOR / MINOR / NIT
- `comment`: the feedback text

Format each inline comment body as:
```
[SEVERITY] <plain-language statement of the issue>

<Why it matters and what should change, written as natural prose.>
```

Example:

```
[MAJOR] Invalid requests are retried

A 400 response will be sent three more times even though another attempt cannot succeed. Treat 4xx responses as non-retryable and keep retries for transient failures.
```

Read the comment aloud before posting. If it sounds like a report template,
rewrite it.

---

## Phase 5: Post Inline Comments

For each finding, post an inline review comment using the GitHub API:

```bash
# Get the PR's head commit SHA first
COMMIT_SHA=$(gh pr view <number> --json headRefOid --jq '.headRefOid')

# Post each inline comment
gh api repos/:owner/:repo/pulls/<number>/comments \
  --method POST \
  --field commit_id="$COMMIT_SHA" \
  --field path="<file>" \
  --field line=<line_number> \
  --field side="RIGHT" \
  --field body="<comment_body>"
```

- Get `:owner/:repo` from: `gh repo view --json nameWithOwner --jq '.nameWithOwner'`
- Post comments one at a time; confirm each posts successfully (HTTP 201)
- If a line number is ambiguous (e.g. in a deletion), use the closest added line or the file-level comment fallback:
  ```bash
  gh pr comment <number> --body "<file>: <comment>"
  ```
- Do not batch — post each comment individually so failures are isolated

---

## Phase 6: Summary Comment

After all inline comments are posted, post one final top-level PR comment:

```bash
gh pr comment <number> --body "$(cat <<'EOF'
## Review summary

**Verdict:** <one of: ✅ Approve | 🔄 Request Changes | 💬 Comment>

<One short paragraph in plain language. Say what needs attention and why. Include counts only when they help the reader.>

### Needs a fix before merge
- `file.go:42` — <critical or major issue>

### Data-changing behavior
- `<operation>` — <read-only or mutating, plus any material concern>

### PR description
- <only applicable missing reviewer information>
EOF
)"
```

Omit empty sections. If there are no findings, post only the heading, verdict,
and `No issues found.` Do not repeat every minor inline finding in the summary.
Do not use phrases such as "Overall, this PR..." or "The implementation appears
to..." State the conclusion directly.

---

## Severity Guide

| Label | When to use |
|-------|-------------|
| `[CRITICAL]` | Bugs, security vulnerabilities, data loss risk, crashes — **block merge** |
| `[MAJOR]` | Significant performance issues, design flaws, missing error handling — **strongly recommend fix** |
| `[MINOR]` | Code quality, maintainability, non-blocking improvements — **fix if time allows** |
| `[NIT]` | Style, naming, tiny preferences — **optional, no pressure** |

---

## Important Notes

- **Read the ENTIRE diff** before posting any comments — context from later files may reframe earlier findings
- **Be precise with line numbers** — wrong line numbers break inline comments; double-check against the diff
- **Be constructive** — every CRITICAL/MAJOR/MINOR comment must include a concrete suggestion, not just criticism
- **Calibrate to the PR size** — a 5-line fix doesn't need 20 nits; a 500-line feature deserves thorough coverage
- **Keep posted output concise** — detailed reasoning stays internal unless
  needed to understand or fix an issue
- **Sound human** — remove canned transitions, generic praise, repeated
  context, and report-style labels before posting
- **Respect existing patterns** — if the codebase uses a certain convention consistently, flag deviations as NITs not MAJORs
- **Never post the summary before all inline comments** — inline comments first, summary last
- If `gh` is not authenticated, tell the user to run `gh auth login`
- If the PR is from a fork, note that inline comments on fork PRs may require the `--repo` flag
