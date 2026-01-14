# Code Review

Review the specified code with a focus on quality, security, and maintainability.

## Instructions

Analyze the provided code file(s) or changes: $ARGUMENTS

Perform a thorough review covering:

### 1. Security
- Input validation and sanitization
- Authentication/authorization issues
- Injection vulnerabilities (SQL, XSS, command injection)
- Sensitive data exposure
- Insecure dependencies

### 2. Code Quality
- Readability and clarity
- Naming conventions
- Function/method length and complexity
- DRY violations
- Dead code

### 3. Logic & Correctness
- Edge cases not handled
- Off-by-one errors
- Null/undefined handling
- Race conditions
- Error handling completeness

### 4. Performance
- Unnecessary computations
- N+1 queries
- Memory leaks
- Inefficient algorithms

### 5. Maintainability
- Test coverage gaps
- Documentation needs
- Breaking changes
- API contract violations

## Output Format

Provide findings as:
```
## Summary
[One paragraph overview]

## Critical Issues
- [Issue with file:line reference]

## Recommendations
- [Suggested improvements]

## Positive Notes
- [What's done well]
```

If no file specified, review the most recent changes (git diff).
