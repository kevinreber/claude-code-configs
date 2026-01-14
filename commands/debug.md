# Systematic Debugging Assistant

Help diagnose and fix bugs systematically.

## Instructions

Debug issue: $ARGUMENTS

### Debugging Framework

#### 1. Reproduce
- Understand the exact steps to reproduce
- Identify expected vs actual behavior
- Note environment details (OS, versions, config)

#### 2. Isolate
- Find the smallest reproducible case
- Identify which component is failing
- Check recent changes that might be related

#### 3. Investigate
- Read error messages and stack traces carefully
- Add logging/debugging output strategically
- Check inputs and outputs at each step
- Verify assumptions about state

#### 4. Hypothesize
- Form theories about root cause
- List possible causes ranked by likelihood
- Design tests to confirm/refute each theory

#### 5. Fix
- Make minimal change to fix the issue
- Ensure fix doesn't introduce new problems
- Add tests to prevent regression

#### 6. Verify
- Confirm the fix works
- Test related functionality
- Check edge cases

### Common Bug Categories
- Off-by-one errors
- Null/undefined references
- Race conditions
- State management issues
- Type mismatches
- Async/await problems
- Incorrect assumptions
- Environment differences
- Dependency conflicts

## Output Format

```markdown
## Bug Analysis: [Brief Description]

### Reproduction Steps
1. [Step]
2. [Step]
3. [Observe: expected vs actual]

### Investigation Log
- Checked [X]: [Finding]
- Hypothesis: [Theory]
- Evidence: [What supports/refutes]

### Root Cause
[Explanation of why the bug occurs]

### Proposed Fix
[Code changes with explanation]

### Prevention
[How to prevent similar bugs]
```

Guide through this process interactively.
