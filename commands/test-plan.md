# Test Plan Generator

Generate a comprehensive test plan for the specified code or feature.

## Instructions

Analyze: $ARGUMENTS

Create a test plan covering:

### Testing principles
- Prioritize behavior and public contracts over implementation details
- Include happy paths, edge cases, and meaningful failure paths
- Prefer the smallest test level that provides confidence
- Use realistic dependency behavior; do not let mocks hide integration risks
- Keep tests isolated, deterministic, and readable
- Add tests only for behavior introduced or fixed by the change

### Unit Tests
- Individual function/method tests
- Edge cases and boundary conditions
- Error scenarios
- Mock requirements

### Integration Tests
- Component interactions
- API endpoint tests
- Database operations
- External service integrations

### Edge Cases
- Empty inputs
- Maximum values
- Invalid data types
- Concurrent access
- Network failures

## Output Format

```markdown
## Test Plan: [Feature/Component Name]

### Unit Tests
| Test Case | Input | Expected Output | Priority |
|-----------|-------|-----------------|----------|
| ...       | ...   | ...             | High/Med/Low |

### Integration Tests
| Scenario | Components | Setup Required | Priority |
|----------|------------|----------------|----------|
| ...      | ...        | ...            | High/Med/Low |

### Edge Cases
- [ ] [Description]

### Test Data Requirements
- [Data needed for tests]

### Mocking Strategy
- [What needs to be mocked and why]

### Validation Commands
- [Smallest commands that cover the change]
```

If targeting an existing test file, suggest additional tests to improve coverage.
