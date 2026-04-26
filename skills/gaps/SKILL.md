---
name: gaps
description: Proactive gap analysis on existing code. Finds what's missing — tests, error handling, observability, security, documentation, architectural holes — at micro (file), meso (module/feature), or macro (codebase) scope. Unlike /validate which checks recent changes, /gaps audits what already exists. Use when you want to know what's missing, undertested, unobserved, or architecturally incomplete.
---

# Gaps — Proactive Gap Analysis

Find what's missing in existing code. Unlike `/validate` which checks recent changes, this audits what already exists and identifies what *should* be there but isn't.

## How Scope is Determined

| What you provide | Scope | Focus |
|-----------------|-------|-------|
| A specific file or function | **Micro** | Missing cases, error handling, edge inputs |
| A directory or feature area | **Meso** | Test coverage, observability, API completeness |
| Nothing (whole codebase) | **Macro** | Architecture, cross-cutting concerns, systemic holes |

If scope is unclear, ask: _"What area do you want me to focus on — a specific file, a feature, or the whole codebase?"_

---

## Phase 0: Orientation

1. **Determine scope** from user input or ask
2. **Read the target area:**
   - Micro: read the specific file(s) in full
   - Meso: read directory structure, key files, entry points
   - Macro: read project structure, CLAUDE.md, main entry points, core abstractions
3. **Understand the intent:** What is this code supposed to do? If unclear, infer from naming, structure, and any docs
4. **State your understanding** before diving in: _"This looks like a [description]. I'll be analyzing it for gaps at [scope] level."_

---

## Gap Analysis Dimensions

Run all relevant dimensions for the scope. Skip dimensions that clearly don't apply (e.g. "API coverage" for a CLI tool with no API).

### 1. Error Handling Gaps
- What can go wrong that isn't handled?
- Are there `catch`/`rescue`/`recover` blocks that swallow errors silently?
- Are there operations that can fail (network, IO, parsing) with no fallback?
- Are error messages specific enough to diagnose problems?
- Are errors propagated to callers or lost?

### 2. Test Coverage Gaps
*(extends `/validate` Pass 5 — applied to existing code, not just recent changes)*
- What behaviors have no test?
- What error paths are untested?
- What edge cases are unexercised?
- Are integration points tested, or only unit behavior?
- Are the tests that exist actually asserting meaningful outcomes?
- What would break silently if tests passed but production differed?

### 3. Observability Gaps
*(extends `/validate` Pass 4 — applied to existing code)*
- What operations have no logging?
- What failure modes would be invisible in production?
- Are there code paths that could degrade silently for hours before being noticed?
- Are there metrics or traces that should exist but don't?
- If this area started misbehaving, would you know in under 5 minutes?

### 4. Security Gaps
- Are there input validation gaps at trust boundaries?
- Is any user-controlled data used in queries, commands, or file paths without sanitization?
- Are there authorization checks missing for sensitive operations?
- Is sensitive data logged, exposed in errors, or returned to clients?
- Are there dependency vulnerabilities in this area?

### 5. Edge Case & Boundary Gaps
- What input values or states aren't accounted for?
- What happens at the boundaries of collections (empty, one element, max size)?
- Are there assumed preconditions that aren't validated?
- What happens with concurrent access to shared state?

### 6. Documentation & Discoverability Gaps
- Are public APIs documented well enough for a new engineer to use correctly?
- Are non-obvious design decisions explained?
- Are there footguns with no warning?
- Is there behavior that only makes sense with tribal knowledge?
- Invoke `/discover` to check if documentation exists externally (Confluence, wiki) that isn't referenced from the code — undiscoverable docs are almost as bad as no docs

### 7. Architectural Gaps *(macro/meso scope)*
*(use `/brain` design mode thinking for this dimension)*
- Are there missing abstractions that should exist? (repeated patterns without a home)
- Are there abstractions that exist but aren't used consistently?
- Are concerns separated appropriately, or is business logic mixed with infrastructure?
- Are there cross-cutting concerns (auth, logging, rate limiting) applied inconsistently?
- Are there circular dependencies or tight coupling that limits flexibility?
- Is there a missing layer? (e.g. no validation layer, no retry layer, no caching layer)

### 8. API & Interface Completeness Gaps *(meso/macro scope)*
- Are there CRUD operations that are partially implemented? (e.g. can create but not delete)
- Are there related operations that are missing from an interface?
- Are there inconsistencies in how similar operations are exposed?
- Are there missing pagination, filtering, or sorting capabilities?

### 9. Operational Readiness Gaps *(meso/macro scope)*
*(extends `/validate` Pass 6 — applied to existing code)*
- Is there a graceful shutdown path?
- Is there a health check endpoint?
- Are there configuration gaps (hardcoded values that should be config)?
- Is there a way to degrade gracefully under load?

---

## Phase 1: Deep Dive Reasoning

For each dimension, don't just scan — **reason about what should exist**:

1. What is this code *trying* to do?
2. What would a thorough implementation of that look like?
3. What's the delta between what's there and what that looks like?

Use `/brain` design mode thinking for architectural dimensions — think about what a well-designed version of this area would look like, then identify what's missing.

---

## Phase 2: Gap Report

Produce a structured report:

```
## Gap Analysis Report

**Scope:** <micro/meso/macro — what was analyzed>
**Area:** <file, module, or "full codebase">

---

### Critical Gaps (fix before shipping)
Issues likely to cause production failures, data loss, or security incidents.

- [ERROR HANDLING] `auth/login.go:47` — network timeout has no retry or fallback; will drop requests silently
- [SECURITY] `api/upload.go:23` — file path not sanitized before use in `os.Open`; path traversal possible

### Major Gaps (high value, address soon)
Significant holes that increase risk or toil.

- [OBSERVABILITY] Payment processing has no metrics — failures would be invisible until customer complaints
- [TESTS] Happy path tested but all error branches in `processOrder()` are uncovered

### Minor Gaps (useful, not urgent)
Real gaps but low immediate risk.

- [DOCS] `UserService` public methods have no documentation; intent of `forceRefresh` param is unclear
- [EDGE CASES] `parseDate()` has no handling for malformed input — throws uncaught exception

### Architectural Observations
Cross-cutting patterns worth knowing about.

- [ARCHITECTURE] Auth checks are applied in 3 different ways across the codebase — inconsistent and hard to audit
- [ARCHITECTURE] No retry layer exists anywhere; each caller implements (or skips) retries independently

---

### Biggest Bang for Effort
Top 3 gaps where fixing would give the most risk reduction for the least work:

1. <gap> — why it's high leverage
2. <gap> — why it's high leverage
3. <gap> — why it's high leverage

### Open Questions
Things that would change this analysis if answered differently:
- <question>
```

---

## Important Notes

- **This is analysis only** — no code changes. To act on findings, use `/validate`, start a task, or tell Claude explicitly to fix something
- **Be specific about locations** — every gap should reference a file and line number where possible, not just a vague concern
- **Distinguish absence from unknown** — "no tests exist for X" is different from "I couldn't find tests for X"
- **Cross-reference with `/validate` findings** — if you've recently run `/validate`, note whether any gaps align with those findings
- **Macro scope is expensive** — for large codebases, ask the user to narrow scope or focus on the highest-risk areas first
- If the user asks to fix a gap found during this session, acknowledge you're exiting gap analysis mode before making changes
