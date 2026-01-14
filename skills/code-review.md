# Code Review Skill

A comprehensive code review skill that provides structured, thorough reviews.

## Activation

Use this skill when the user asks for a code review or wants feedback on their code.

## Capabilities

When reviewing code, I will:

### 1. Understand Context First
- Read the entire file(s) being reviewed
- Check related files for context
- Understand the project structure and conventions

### 2. Apply Review Checklist

**Correctness**
- Does the code do what it's supposed to do?
- Are edge cases handled?
- Is error handling appropriate?

**Security**
- Input validation present?
- No injection vulnerabilities?
- Sensitive data protected?

**Performance**
- Efficient algorithms used?
- No unnecessary operations?
- Appropriate data structures?

**Maintainability**
- Clear and readable?
- Well-organized?
- Appropriate abstraction level?

**Testing**
- Testable design?
- Tests included?
- Edge cases covered?

### 3. Provide Actionable Feedback

I structure feedback as:
- **Must Fix**: Critical issues that need addressing
- **Should Consider**: Important improvements
- **Nitpicks**: Minor style/preference suggestions
- **Praise**: Things done well (encourages good patterns)

### 4. Explain the "Why"

For each suggestion, I explain:
- Why it's a problem
- What could go wrong
- How to fix it
- Example of better approach

## Review Style

- Constructive, not critical
- Focus on the code, not the person
- Acknowledge constraints and trade-offs
- Ask questions when intent is unclear
- Prioritize feedback by importance
