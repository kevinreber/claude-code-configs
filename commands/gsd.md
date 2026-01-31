# GSD: Get-Shit-Done Workflow

Spec-driven feature development with the Discuss → Plan → Execute → Verify cycle.

## Usage

```
/gsd <phase> [feature-description]
```

**Phases**:
- `discuss` or `d` - Capture decisions before planning
- `plan` or `p` - Create atomic task plan
- `execute` or `e` - Implement with atomic commits
- `verify` or `v` - Validate against acceptance criteria
- `quick` or `q` - Streamlined flow for small changes
- `status` or `s` - Show current phase and progress

---

## Phase: Discuss

**Trigger**: `/gsd discuss $ARGUMENTS`

### Objective
Surface ambiguities and capture decisions BEFORE any code is written.

### Process

1. **Understand the Request**
   - What is being asked?
   - What are the explicit requirements?
   - What problem does this solve?

2. **Identify Gray Areas**
   Ask about:
   - UI/UX: Layout, responsiveness, accessibility, error states, loading states
   - API: Endpoints, payloads, authentication, rate limiting, versioning
   - Data: Schema, migrations, validation, relationships
   - Infrastructure: Scaling, caching, monitoring, deployment

3. **Surface Hidden Constraints**
   - Existing code patterns to follow?
   - Dependencies or integrations affected?
   - Performance requirements?
   - Security considerations?
   - Backward compatibility needs?

4. **Define Acceptance Criteria**
   Work with user to establish:
   - What does "done" look like?
   - How will we verify success?
   - What edge cases must be handled?

5. **Document Decisions**
   Record in STATE.md or conversation:
   - Decisions made
   - Tradeoffs accepted
   - Out-of-scope items

### Output
Clear understanding with documented decisions, ready for planning.

---

## Phase: Plan

**Trigger**: `/gsd plan $ARGUMENTS`

### Objective
Create atomic, verifiable tasks with specific files and measurable outcomes.

### Process

1. **Research Codebase**
   Investigate before planning:
   - Technology stack and patterns in use
   - Relevant existing code and architecture
   - Similar implementations to reference
   - Potential pitfalls or edge cases

2. **Create Task List**
   For each task, define:
   ```xml
   <task type="auto|checkpoint:human-verify|checkpoint:decision">
     <name>Clear, specific task name</name>
     <files>Exact file paths to create/modify</files>
     <action>
       Concrete implementation steps:
       1. Specific change to make
       2. Pattern to follow
       3. Integration points
     </action>
     <verify>
       Testable verification:
       - Command to run
       - Expected output
       - Behavior to validate
     </verify>
     <done>Measurable success criteria</done>
   </task>
   ```

3. **Order Tasks**
   - Dependencies first
   - Foundation before features
   - Tests alongside or after implementation
   - Group parallelizable tasks

4. **Validate Plan**
   Self-check:
   - Does each task have specific files? (No "various files")
   - Is each action concrete? (No "implement feature")
   - Is verification testable? (No "works correctly")
   - Do tasks map to acceptance criteria?

### Task Types
- `auto`: Execute without confirmation
- `checkpoint:human-verify`: Pause for user review before continuing
- `checkpoint:decision`: Present options, wait for user choice

### Output
Numbered task list with XML structure, ready for execution.

---

## Phase: Execute

**Trigger**: `/gsd execute $ARGUMENTS`

### Objective
Implement each task with atomic commits and verified outcomes.

### Process

1. **For Each Task**:

   a. **Announce**: State which task is being executed

   b. **Implement**: Follow the action steps precisely

   c. **Verify**: Run the verification steps

   d. **Commit**: Create atomic commit on success
   ```
   <type>(<phase-task>): <description>

   <body>

   Co-Authored-By: Claude <noreply@anthropic.com>
   ```

   e. **Report**: Confirm completion or document blocker

2. **Handle Checkpoints**
   - `checkpoint:human-verify`: Pause, show work, wait for approval
   - `checkpoint:decision`: Present options, wait for selection

3. **Handle Blockers**
   If stuck:
   - Document the blocker clearly
   - Suggest potential solutions
   - Ask for guidance if needed
   - Do NOT proceed past blockers without resolution

4. **Parallel Execution**
   When tasks are independent:
   - Identify parallelizable groups
   - Execute simultaneously if possible
   - Maintain atomic commits per task

### Commit Format
```
feat(01-03): add user authentication endpoint

Implement JWT-based auth with refresh token rotation.
Includes rate limiting and account lockout after failed attempts.

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Output
Completed implementation with atomic commits for each task.

---

## Phase: Verify

**Trigger**: `/gsd verify $ARGUMENTS`

### Objective
Validate the complete implementation against acceptance criteria.

### Process

1. **Run Automated Checks**
   - Test suite: `npm test`, `pytest`, etc.
   - Type checking: `tsc --noEmit`, `mypy`, etc.
   - Linting: `eslint`, `ruff`, etc.
   - Build: `npm run build`, etc.

2. **Manual Verification**
   Walk through acceptance criteria:
   - [ ] Criterion 1: Verified by [method]
   - [ ] Criterion 2: Verified by [method]
   - [ ] Edge case handling confirmed

3. **Debug Failures**
   If issues found:
   - Identify root cause
   - Create targeted fix
   - Re-run verification
   - Commit fix with clear message

4. **Documentation Check**
   - README updated if needed?
   - API documentation current?
   - Inline comments for complex logic?

5. **Final Summary**
   Report:
   - Tasks completed
   - Commits created
   - Tests passing
   - Known limitations or follow-ups

### Output
Verification report with all checks passing or documented issues.

---

## Quick Mode

**Trigger**: `/gsd quick $ARGUMENTS`

Streamlined workflow for bug fixes and small features (< 3 tasks).

### Process
1. **Quick Discuss**: 2-3 clarifying questions max
2. **Quick Plan**: 1-3 atomic tasks, no formal XML
3. **Quick Execute**: Implement with atomic commits
4. **Quick Verify**: Run tests, confirm fix

### When to Use
- Bug fixes with clear reproduction
- Small feature additions
- Configuration changes
- Documentation updates

### When NOT to Use
- New features with unclear scope
- Refactoring multiple files
- Changes affecting multiple systems
- Security-sensitive changes

---

## Status Check

**Trigger**: `/gsd status`

### Output
```
## GSD Status

**Current Phase**: [discuss|plan|execute|verify|none]
**Feature**: [description]

### Progress
- [x] Discuss: [summary of decisions]
- [x] Plan: [X tasks defined]
- [ ] Execute: [Y/X tasks complete]
- [ ] Verify: [pending]

### Current Task
[Task N]: [description]
Status: [in-progress|blocked|complete]

### Blockers
[None | List of blockers]
```

---

## Best Practices

### Do
- Front-load decisions in discuss phase
- Be specific in task definitions
- Commit after each verified task
- Document blockers immediately
- Use checkpoints for risky changes

### Don't
- Skip discuss phase for complex features
- Create vague tasks ("implement feature")
- Batch multiple changes in one commit
- Proceed past blockers without resolution
- Assume requirements are complete

### Integration
- Pairs with `/review` for code review phase
- Use `/test-plan` to enhance verify phase
- Apply `/security` for security-sensitive features
- Reference `/commit` standards for messages
