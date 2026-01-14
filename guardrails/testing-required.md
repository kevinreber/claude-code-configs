# Guardrail: Testing Required

## Purpose
Ensure adequate test coverage for new and modified code.

## Rules

### New Code Must Have Tests
When creating new:
- Functions/methods with logic
- API endpoints
- Components with behavior
- Utilities and helpers
- Business logic

### Tests Should Cover
1. **Happy path** - Normal expected usage
2. **Edge cases** - Boundary conditions
3. **Error cases** - Invalid inputs, failures
4. **Integration points** - How components interact

### Test Quality Standards

**Good tests are:**
- Independent (no test depends on another)
- Repeatable (same result every run)
- Fast (unit tests < 100ms)
- Clear (test name describes the scenario)

**Test structure:**
```javascript
describe('UserService', () => {
  describe('createUser', () => {
    it('creates a user with valid input', () => { ... });
    it('throws ValidationError for invalid email', () => { ... });
    it('throws DuplicateError if user exists', () => { ... });
  });
});
```

### When Modifying Existing Code

1. **Run existing tests first** to understand current behavior
2. **Update tests** if behavior changes intentionally
3. **Add tests** for new behavior
4. **Don't delete tests** unless the feature is removed

### Minimum Coverage

Before considering a feature complete:
- All public methods/functions have at least one test
- Critical paths have multiple tests
- Error handling is tested

### Actions

1. After writing code, suggest: "Should I write tests for this?"
2. If tests exist, run them: `npm test`, `pytest`, etc.
3. If tests fail after changes, fix them or discuss if behavior change is intentional
4. Suggest test improvements when reviewing code

### Exceptions

Tests may not be needed for:
- Configuration files
- Type definitions only
- Simple re-exports
- Prototype/experimental code (but flag for later)
