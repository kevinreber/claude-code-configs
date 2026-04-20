# GSD (Get-Shit-Done) Methodology

A spec-driven, context-efficient approach to feature development. Trade upfront specification effort for consistency, parallelization, and quality.

## Core Philosophy

### Principles
- **Simplicity over enterprise complexity**: No sprint ceremonies, story points, or RACI matrices
- **Specification as the source of truth**: Front-load decisions to get consistent results
- **Context isolation**: Fresh context per task prevents quality degradation
- **Atomic commits**: Every task = one commit for granular tracking and revertability
- **Human checkpoints at critical decisions**: Automated where safe, confirmed where critical

### Anti-Patterns (Never Do)
- Enterprise ceremony: story points, sprint planning, RACI matrices
- Temporal language in docs: "We changed...", "Previously..."
- Generic XML tags: `<section>`, `<item>`, `<content>`
- Vague tasks without specific files, concrete actions, measurable verification
- Sycophantic filler: "Great!", "Awesome!", "Let me just..."
- Accumulated context garbage: Keep main context at 30-40% utilization

## Four-Phase Workflow

### Phase 1: Discuss
**Purpose**: Capture decisions BEFORE planning begins

- Identify gray areas specific to the feature type (UI, API, data, infrastructure)
- Use deep questioning to surface vague concepts and hidden constraints
- Get human input to resolve ambiguities upfront
- Document decisions in STATE.md

**Key Questions**:
- What are the explicit requirements?
- What are the implicit assumptions?
- What edge cases need handling?
- What are the acceptance criteria?

### Phase 2: Plan
**Purpose**: Create atomic, verifiable task plans

- Research the codebase: stack, architecture, patterns, potential pitfalls
- Create tasks with XML structure for precision
- Each task must have: specific files, concrete actions, measurable verification
- Iterate until plan passes requirements check

**Task Types**:
- `auto`: Fully automated execution
- `checkpoint:human-verify`: Requires human approval before proceeding
- `checkpoint:decision`: Presents options for human choice

**Task Structure**:
```xml
<task type="auto">
  <name>Clear task name</name>
  <files>src/path/to/specific/file.ts</files>
  <action>Specific implementation guidance with concrete steps</action>
  <verify>Testable verification: run command, check output, validate behavior</verify>
  <done>Measurable success criteria</done>
</task>
```

### Phase 3: Execute
**Purpose**: Implement with isolated context and atomic commits

- Execute each task with fresh context (prevents quality degradation)
- Run parallel execution waves when tasks are independent
- Create atomic git commit after each task completion
- Use conventional commit format with phase identifier:
  ```
  feat(01-03): add user authentication flow
  ```

**Execution Principles**:
- One task at a time (or parallel if independent)
- Verify before marking complete
- Commit immediately after verification passes
- Document blockers in STATE.md if stuck

### Phase 4: Verify
**Purpose**: Validate deliverables against acceptance criteria

- Run user acceptance testing
- Execute automated diagnostics (tests, linting, type checks)
- Debug any failures with dedicated focus
- Update documentation to reflect final state

## Documentation Structure

Maintain these files in `.planning/` or project root:

| File | Purpose | Update Frequency |
|------|---------|------------------|
| `PROJECT.md` | Vision and project context | Rarely |
| `REQUIREMENTS.md` | Scoped v1/v2/out-of-scope features | Per feature |
| `ROADMAP.md` | Phase structure and progress | Per phase |
| `STATE.md` | Decisions, blockers, current position | Continuously |
| `PLAN.md` | XML-formatted atomic tasks | Per planning phase |
| `SUMMARY.md` | Committed after phases complete | Per phase |

## Quick Mode

For bug fixes and small features, use streamlined workflow:
- Combine discuss/plan/execute into single flow
- Aggressive compression: 1-3 tasks max
- Still maintain atomic commits
- Skip formal documentation for trivial changes

## Context Management

### Why Context Matters
Context rot = quality degradation as context fills with accumulated work.

### Prevention Strategies
- Spawn subagents for heavy lifting (each gets fresh 200k tokens)
- Keep main context for user interaction and coordination
- Limit planning docs to prevent bloat
- Commit and clear completed work from active memory

## Commit Standards

### Format
```
<type>(<phase-task>): <imperative description>

<body explaining why, not what>

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code restructuring
- `test`: Test additions/changes
- `docs`: Documentation
- `chore`: Maintenance tasks

### TDD Commits (when applicable)
- `test(red)`: Failing test first
- `feat`: Implementation to pass
- `refactor`: Clean up while green

## Language and Tone

### Do
- Imperative voice: "Execute tasks" not "Execution is performed"
- Brevity with substance: "JWT auth with refresh rotation"
- Specific technical language

### Don't
- Filler words: "Let me", "Just", "Simply"
- Sycophancy: "Great question!", "Awesome!"
- Vague descriptions: "Phase complete" without details

## Integration with Existing Workflows

GSD methodology enhances but doesn't replace:
- Use with existing git-workflow skill for merge strategies
- Combine with testing skill for verification phase
- Apply code-review skill during verify phase
- Security-audit skill for security-related tasks
