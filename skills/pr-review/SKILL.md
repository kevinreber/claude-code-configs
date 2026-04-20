---
name: pr-review
description: Perform a thorough code review on a PR. Detects the language/framework, posts inline comments with severity labels (CRITICAL/MAJOR/MINOR/NIT/PRAISE) on specific lines, and leaves a single summary comment with overall verdict. Use when the user wants to review a PR, give feedback on a pull request, or do a code review.
---

# PR Review

Perform a deep, expert-level code review. Specialize in the languages and frameworks present in the PR, post granular inline comments with severity labels, and conclude with a comprehensive summary.

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

   State your specialization at the start: e.g. _"Reviewing as a Go + PostgreSQL specialist."_

---

## Phase 2: Description Quality Check (Feature PRs)

**Before reviewing code**, determine if this is a feature PR:
- Has `feat:` commits, adds new user-facing functionality, new API surface, or new subsystems
- Or changes 200+ lines across multiple files introducing new behavior

If it **is** a feature PR, check the PR description for these required sections:

| Section | What to look for |
|---------|-----------------|
| **Feature Diagram** | Architecture, data flow, or component diagram (ASCII or Mermaid) |
| **Design Trade-offs** | Table or list of key decisions with alternatives and reasoning |
| **How to Test** | Concrete example inputs/steps with expected outputs anyone can run |
| **Known Limitations** | Explicit callouts of what's out of scope or has known gaps |

For any missing section, include a top-level comment (not inline) at the end of your summary:

```
### Description Gaps
The following sections are missing from the PR description and would help reviewers:
- [ ] **Feature Diagram** — add an architecture or data flow diagram
- [ ] **Design Trade-offs** — document key decisions and why alternatives were rejected
- [ ] **How to Test** — add concrete example inputs with expected outputs
- [ ] **Known Limitations** — note what's out of scope or has known issues
```

Skip this check entirely for non-feature PRs (bug fixes, chores, docs, refactors).

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

### Praise
- Identify genuinely good patterns, clever solutions, or improvements worth calling out explicitly

---

## Phase 4: Build Comment List

Compile all findings into a structured list before posting. Each finding needs:
- `file`: the file path
- `line`: the line number in the diff (the **right side / new file** line number)
- `severity`: one of CRITICAL / MAJOR / MINOR / NIT / PRAISE
- `comment`: the feedback text

Format each inline comment body as:
```
[SEVERITY] <concise description of the issue>

<explanation of why this matters and/or what the impact is>

**Suggestion:**
<concrete fix or alternative approach, with code example if helpful>
```

For PRAISE:
```
[PRAISE] <what's good here>

<why this is a good pattern or particularly well done>
```

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
## Code Review Summary

**Reviewed by:** Claude Code (as <detected language/framework> specialist)
**Verdict:** <one of: ✅ Approve | 🔄 Request Changes | 💬 Comment>

---

### Overview
<2-4 sentence high-level assessment of the PR: what it does, overall quality, major themes>

---

### Findings by Severity

| Severity | Count |
|----------|-------|
| 🔴 CRITICAL | <n> |
| 🟠 MAJOR | <n> |
| 🟡 MINOR | <n> |
| 🔵 NIT | <n> |
| ✅ PRAISE | <n> |

---

### Critical Issues
<List each CRITICAL finding with file reference — must be resolved before merge>
- `file.go:42` — <short description>

### Major Issues
<List each MAJOR finding with file reference>
- `file.go:87` — <short description>

### Themes & Patterns
<Cross-cutting observations, e.g. "Error handling is consistently missing across the new service layer" or "Strong use of dependency injection throughout">

### What's Working Well
<Highlight PRAISE items and any broader positive patterns>

---

> 🤖 Review generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

---

## Severity Guide

| Label | When to use |
|-------|-------------|
| `[CRITICAL]` | Bugs, security vulnerabilities, data loss risk, crashes — **block merge** |
| `[MAJOR]` | Significant performance issues, design flaws, missing error handling — **strongly recommend fix** |
| `[MINOR]` | Code quality, maintainability, non-blocking improvements — **fix if time allows** |
| `[NIT]` | Style, naming, tiny preferences — **optional, no pressure** |
| `[PRAISE]` | Genuinely good code worth calling out — **no action needed** |

---

## Important Notes

- **Read the ENTIRE diff** before posting any comments — context from later files may reframe earlier findings
- **Be precise with line numbers** — wrong line numbers break inline comments; double-check against the diff
- **Be constructive** — every CRITICAL/MAJOR/MINOR comment must include a concrete suggestion, not just criticism
- **Calibrate to the PR size** — a 5-line fix doesn't need 20 nits; a 500-line feature deserves thorough coverage
- **Respect existing patterns** — if the codebase uses a certain convention consistently, flag deviations as NITs not MAJORs
- **Never post the summary before all inline comments** — inline comments first, summary last
- If `gh` is not authenticated, tell the user to run `gh auth login`
- If the PR is from a fork, note that inline comments on fork PRs may require the `--repo` flag
