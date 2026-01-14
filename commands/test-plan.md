# Test Plan Generator

Generate a comprehensive test plan for the specified code or feature.

## Instructions

Analyze: $ARGUMENTS

Create a test plan covering:

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
```

If targeting an existing test file, suggest additional tests to improve coverage.
