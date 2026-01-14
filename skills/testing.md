# Testing Skill

Specialized skill for test writing, test strategy, and coverage analysis.

## Activation

Use this skill when the user wants help writing tests, improving test coverage, or designing a testing strategy.

## Testing Philosophy

### Testing Pyramid
```
         /\
        /  \     E2E Tests (few, slow, expensive)
       /----\
      /      \   Integration Tests (some)
     /--------\
    /          \ Unit Tests (many, fast, cheap)
   --------------
```

### Good Test Characteristics (F.I.R.S.T.)
- **Fast**: Run quickly
- **Independent**: No test depends on another
- **Repeatable**: Same result every time
- **Self-validating**: Pass or fail, no interpretation
- **Timely**: Written with or before production code

## Test Types

### Unit Tests
- Test single units in isolation
- Mock external dependencies
- Fast execution
- High coverage target (80%+)

### Integration Tests
- Test component interactions
- Use real dependencies where practical
- Test database operations
- API endpoint testing

### End-to-End Tests
- Test complete user workflows
- Browser automation for web apps
- Slower, more brittle
- Focus on critical paths

## Test Structure

### Arrange-Act-Assert (AAA)
```javascript
describe('Calculator', () => {
  it('adds two numbers correctly', () => {
    // Arrange
    const calc = new Calculator();

    // Act
    const result = calc.add(2, 3);

    // Assert
    expect(result).toBe(5);
  });
});
```

### Given-When-Then (BDD)
```javascript
describe('Shopping Cart', () => {
  describe('given an empty cart', () => {
    describe('when adding an item', () => {
      it('then the cart contains one item', () => {
        // ...
      });
    });
  });
});
```

## What I Help With

### Writing Tests
- Generate test cases from code
- Identify edge cases to test
- Create test fixtures and factories
- Mock setup and configuration

### Test Coverage
- Identify untested code paths
- Suggest missing test cases
- Find dead code
- Coverage report analysis

### Test Quality
- Review existing tests
- Identify flaky tests
- Improve test readability
- Reduce test duplication

### Testing Patterns
- Factory pattern for test data
- Builder pattern for complex objects
- Object Mother for common setups
- Test containers for integration tests

## Framework Support

I can help with:
- Jest / Vitest (JavaScript/TypeScript)
- pytest (Python)
- RSpec (Ruby)
- JUnit (Java)
- Go testing
- And more...
