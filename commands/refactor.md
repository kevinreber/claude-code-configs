# Refactoring Assistant

Analyze code and suggest refactoring improvements.

## Instructions

Analyze: $ARGUMENTS

Identify refactoring opportunities:

### Code Smells to Detect
- Long methods (>20 lines)
- Large classes (>300 lines)
- Long parameter lists (>4 params)
- Duplicate code
- Feature envy
- Data clumps
- Primitive obsession
- Switch statements that should be polymorphism
- Parallel inheritance hierarchies
- Lazy classes
- Speculative generality
- Temporary fields
- Message chains
- Middle man
- Inappropriate intimacy

### Suggest Refactorings
- Extract Method/Function
- Extract Class
- Move Method
- Replace Conditional with Polymorphism
- Introduce Parameter Object
- Replace Magic Numbers with Constants
- Decompose Conditional
- Consolidate Duplicate Conditional Fragments
- Remove Dead Code
- Rename for Clarity

## Output Format

```markdown
## Refactoring Suggestions for [file]

### High Priority
1. **[Smell]** at line X
   - Problem: [description]
   - Solution: [specific refactoring]
   - Example: [code snippet]

### Medium Priority
...

### Low Priority
...

### Estimated Impact
- Readability: [improvement description]
- Maintainability: [improvement description]
- Testability: [improvement description]
```

Ask before implementing any changes.
