---
name: validate
description: Validate recent changes through correctness, integration, adversarial failure, observability, test-quality, and operational-readiness analysis, then return a concise issue-focused verdict.
---

# Validate Changes

Perform six independent validation passes on recent changes, each with a distinct lens, followed by a synthesis pass that cross-references all findings. Designed to catch what any single review pass would miss.

## Feedback policy

- Keep the final response issue-focused and factual.
- Do not generate praise sections or narrate every pass.
- Consolidate duplicate findings by root cause.
- Include detailed output only for failures, actionable issues, or material
  uncertainty.

## Independent review strategy

For non-trivial changes, perform three independent read-only analyses when
subagents are available, or three deliberate fresh passes otherwise. Keep each
pass blind to the others, merge the union of candidate findings, and verify
every candidate against the actual source before reporting it. Trivial
documentation or formatting changes need only one pass.

Run build, test, lint, and type-check commands once against the real repository
state; mechanical checks do not need independent duplication.

## Phase 0: Scope the Changes

1. **Identify what changed:**
   ```bash
   git diff HEAD
   ```
   If nothing staged/unstaged, check the last commit:
   ```bash
   git diff HEAD~1 HEAD
   ```

2. **Understand the intent:**
   - Read the task description, commit message, or ask the user: _"What was the goal of these changes?"_
   - State the intent clearly before starting — e.g. _"Goal: Add rate limiting to the login endpoint."_

3. **Inventory changed files:**
   - List all modified/added/deleted files
   - Read each changed file in full to understand surrounding context, not just the diff

---

## Pass 1: Implementation Correctness

**Lens: "Does the code do what it's supposed to do?"**

Adopt the mindset of someone who knows exactly what the requirement was and is checking whether the code fulfills it.

Check for:

### Logic & Behavior
- Does the implementation match the stated intent step by step?
- Trace through the main code path manually — does the output match expectations?
- Are all branches of conditionals handled correctly?
- Off-by-one errors, wrong comparisons, inverted logic

### Error Handling
- Are all error cases handled? (null/nil, empty input, missing keys)
- Are errors propagated correctly or silently swallowed?
- Are error messages meaningful?

### Data Integrity
- Are data transformations correct? (parsing, formatting, encoding)
- Are there precision/rounding issues?
- Are collections mutated safely?

### Completeness
- Is anything the spec required left unimplemented?
- Are there TODO/FIXME comments that represent unfinished work?

**Output:** List of findings as `[PASS 1 ISSUE]` or `[PASS 1 OK]` per concern.

---

## Pass 2: Integration & Side Effects

**Lens: "How does this interact with everything else?"**

Step back from the changed code and think about the system it lives in.

Check for:

### Callers & Consumers
- Read usages of modified functions/classes/APIs throughout the codebase
- Do existing callers still work with signature/behavior changes?
- Are return types, error types, or contract semantics preserved?

### Dependencies
- Do the changes depend on anything that might not be available in all environments?
- Are new imports/packages available in production, not just dev?
- If dependency behavior is unclear, read its authoritative documentation or
  source before assuming

### State & Shared Resources
- Do changes affect global state, shared caches, or databases in ways that could impact other operations?
- If mutating state, is it safe under concurrent access?

### Configuration & Environment
- Do changes require new environment variables, config keys, or feature flags?
- Are defaults safe if the new config is absent?

### Backwards Compatibility
- If this is an API or interface, are existing clients broken?
- Are there database migrations needed that weren't included?

### Tests
- Are existing tests still valid, or do they need updating?
- Are the new code paths covered by tests?
- Would the tests actually catch a regression here?

**Output:** List of findings as `[PASS 2 ISSUE]` or `[PASS 2 OK]` per concern.

---

## Pass 3: Adversarial / "Break It"

**Lens: "I'm trying to make this fail."**

Adopt the mindset of a QA engineer or attacker who is actively trying to find failure modes the implementer didn't anticipate.

Check for:

### Boundary Conditions
- What happens with empty input, null/nil, zero, negative numbers, max values?
- What happens with very large inputs or payloads?
- What happens with unexpected types or formats?

### Timing & Concurrency
- Is there a race condition if two requests hit this simultaneously?
- Is there a TOCTOU (time-of-check/time-of-use) issue?
- What if a timeout or cancellation happens mid-operation?

### Failure Injection
- What if a downstream service or DB call fails?
- What if the network is slow or drops?
- What if the file system is full or a file is missing?

### Security
- Can input be crafted to cause injection (SQL, command, path traversal, XSS)?
- Are there authorization checks that could be bypassed?
- Is any sensitive data leaked in logs, errors, or responses?

### Resource Exhaustion
- Can this loop infinitely or near-infinitely on bad input?
- Does this create unbounded memory growth?
- Could this open file handles or connections that are never closed?

### Operational Failures
- What happens on first deploy to an existing system (migration safety)?
- What happens on rollback — is the change reversible?

**Output:** List of findings as `[PASS 3 ISSUE]` or `[PASS 3 OK]` per concern. For each issue, describe the exact scenario that triggers it.

---

## Pass 4: Observability

**Lens: "If this breaks at 3am, can I tell why?"**

Assume the code ships and silently degrades in production. Would you know?

Check for:

### Logging
- Are new code paths logged at appropriate levels?
- Do error logs include enough context to diagnose the problem? (relevant IDs, inputs, state)
- Are there silent catch blocks that swallow exceptions without logging?
- Are success/failure outcomes logged for non-trivial operations?

### Metrics & Instrumentation
- Are new operations instrumented? (counters, histograms, timers)
- Are error rates trackable for new failure paths?
- If this change affects latency, is there a way to measure it?

### Tracing
- Are new async operations, external calls, or background jobs included in traces?
- Are span names/attributes meaningful enough to diagnose issues?

### Alerting Surface
- If this new code starts failing, would an existing alert fire?
- Is there a new failure mode that has no alert coverage?

### Debuggability
- If a bug is reported, are there enough breadcrumbs (logs, IDs, state) to reproduce it?
- Are important state transitions visible in logs?

**Output:** List of findings as `[PASS 4 ISSUE]` or `[PASS 4 OK]` per concern.

---

## Pass 5: Test Quality

**Lens: "Would these tests actually catch a regression?"**

Don't just check if tests exist — check if they're meaningful. A test that can't fail is worse than no test.

Check for:

### Coverage of Real Paths
- Do tests cover the code paths that would actually break in production?
- Are the happy path, error path, and edge cases all exercised?
- Are the most dangerous paths (concurrent access, external failures) tested?

### Assertion Quality
- Do assertions verify observable behavior, or just that the code ran?
- Are assertions specific enough to catch a regression? (not just `assert result is not None`)
- Would a broken implementation still pass these tests?

### Mock Fidelity
- Are mocks accurately representing real dependencies?
- Could a mock hide a failure that would occur with the real implementation?
- Are integration points tested with real (or realistic) dependencies anywhere?

### Test Isolation
- Could tests pass in isolation but fail when run together (shared state, ordering)?
- Are tests cleaning up after themselves?

### Brittleness
- Are tests tied to implementation details that might change without the behavior changing?
- Would a valid refactor break these tests?

**Output:** List of findings as `[PASS 5 ISSUE]` or `[PASS 5 OK]` per concern.

---

## Pass 6: Operational Readiness

**Lens: "Is this safe to deploy to production right now?"**

Think like an SRE doing a pre-deploy checklist.

Check for:

### Deploy Safety
- Will the first deployment cause a spike in errors, latency, or resource usage?
- Are there cold start effects (cache warmup, connection pool initialization)?
- Does anything need to be true in production before this code can run safely?

### Migration Safety
- If there's a schema or data migration, is it backwards-compatible during rollout?
- Can the old and new code run simultaneously (for rolling deploys)?
- Is the migration reversible if rollback is needed?

### Feature Flag / Gradual Rollout
- Should this be behind a feature flag for staged rollout?
- If it goes wrong, can it be disabled without a deploy?

### Rollback Plan
- If this causes an incident, what's the rollback path?
- Does rollback leave the system in a consistent state, or could it corrupt data?

### Runbook / On-Call Impact
- Does this change what on-call engineers need to know to respond to incidents?
- Are there new failure modes that require new runbook entries?

**Output:** List of findings as `[PASS 6 ISSUE]` or `[PASS 6 OK]` per concern.

---

## Pass 7: Synthesis & Cross-Reference

**Lens: "What does the full picture tell us that no single pass could?"**

This pass operates **only on the findings from Passes 1–6**. Do not re-examine the code. Reason about the findings as a set.

### Issue Combination
- Do any two findings from different passes **combine into something worse**?
  - e.g. a race condition (Pass 3) + no metric to detect it (Pass 4) = silent data corruption with no alert
  - e.g. a missing error handler (Pass 1) + no log on that path (Pass 4) = undiagnosable failure
- Are there pairs of issues that, together, represent a CRITICAL risk even if each is a WARN individually?

### Root Cause Patterns
- Do multiple findings across passes point to the **same underlying problem**?
  - e.g. three separate issues about missing null checks may indicate the abstraction is wrong, not just missing guards
  - e.g. observability gaps + test quality gaps may indicate the engineer wasn't thinking about failure modes at all
- If a root cause is identified, name it explicitly — it changes the remediation.

### Confidence Calibration
- Given all findings together, is the initial per-pass confidence still accurate?
- Does the volume or pattern of findings shift the overall risk level up or down?
- Are there areas where passes gave `OK` but the combination of surrounding findings suggests a blind spot?

### Remediation Priority
- Sequence all issues from all passes into a single prioritized list
- Flag which issues must be fixed before shipping vs. can be follow-up work
- If two issues have the same fix, consolidate them

**Output:** Synthesized findings, root causes identified (if any), and the consolidated issue list.

---

## Phase 2: Run Build & Tests (if applicable)

If a build or test command is available, run it mechanically:

1. **Detect test runner:**
   - Check for `Makefile`, `package.json`, `pom.xml`, `go.mod`, `Cargo.toml`, `pytest.ini`, etc.
   - Prefer: `make test`, `npm test`, `go test ./...`, `cargo test`, `pytest`, `./gradlew test`

2. **Run tests:**
   ```bash
   <detected test command>
   ```
   Report concise pass, failure, and skip counts. Include only the failure
   excerpt needed to identify the cause.

3. **If tests fail:**
   - Identify which tests failed and why
   - Determine if the failure is from the new changes or pre-existing
   - Report clearly

---

## Phase 3: Validation Verdict

After all passes and tests, produce one compact, consolidated report:

```
## Validation

**Verdict:** <High confidence | Needs attention | Do not ship>
**Scope:** <one sentence describing what was validated>

### Issues
- [SEVERITY] `file:line` — <issue, impact, and required fix>

### Checks
- <grouped test, build, lint, or type-check result>

### Limitations
- <only unresolved uncertainty or environment limitation>
```

If no issues were found, replace the Issues section with
`No actionable issues found.` Omit Limitations when empty. Prefer one to three
grouped check bullets.

---

## Important Notes

- **Do not skip passes** — each pass catches what the others miss
- **Do not publish the pass-by-pass analysis** — synthesize it
- **Pass 7 must not re-examine code** — it reasons only from prior pass findings
- **State findings as specific scenarios**, not vague concerns: "If `user` is null, line 47 will panic" not "null handling might be an issue"
- **Distinguish real issues from hypotheticals** — mark theoretical concerns as `[WARN - THEORETICAL]` vs confirmed issues `[ISSUE - CONFIRMED]`
- **Read the full file context**, not just the diff — bugs often come from misunderstanding existing behavior
- **Be honest about confidence** — if you can't determine whether something is safe without running the code, say so
- If the user says "quick validate" or "fast check", run only Passes 1, 3, and 7
- If the user says "deep validate", expand each pass with additional file reads and grep searches across the codebase
- If validation findings lead to fixes, re-run focused checks and at least one
  complete validation pass before claiming the result is clean
