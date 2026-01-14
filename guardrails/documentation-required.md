# Guardrail: Documentation Required

## Purpose
Ensure public APIs and complex code are properly documented.

## What Requires Documentation

### Public APIs
- Exported functions and classes
- REST/GraphQL endpoints
- Public library interfaces
- CLI commands and options

### Complex Logic
- Non-obvious algorithms
- Business rules with edge cases
- Workarounds and hacks (explain why)
- Performance-critical code

### Configuration
- Environment variables
- Feature flags
- Build options

## Documentation Standards

### Function/Method Documentation
```typescript
/**
 * Calculates the total price including tax and discounts.
 *
 * @param items - Array of cart items with quantity and unit price
 * @param taxRate - Tax rate as decimal (e.g., 0.08 for 8%)
 * @param discountCode - Optional discount code to apply
 * @returns Total price in cents
 * @throws {InvalidDiscountError} If discount code is invalid
 *
 * @example
 * const total = calculateTotal(
 *   [{ quantity: 2, unitPrice: 1000 }],
 *   0.08,
 *   'SAVE10'
 * );
 */
function calculateTotal(
  items: CartItem[],
  taxRate: number,
  discountCode?: string
): number
```

### API Endpoint Documentation
```markdown
## POST /api/users

Create a new user account.

### Request
- **Headers**: `Content-Type: application/json`
- **Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "securePassword123",
    "name": "John Doe"
  }
  ```

### Response
- **201 Created**: User created successfully
- **400 Bad Request**: Validation error
- **409 Conflict**: Email already exists
```

### Inline Comments
```typescript
// Use inline comments for non-obvious code
const timeout = 30000; // 30 seconds - matches upstream API timeout

// Explain workarounds
// HACK: Safari doesn't support X, so we fall back to Y
// TODO: Remove when Safari 18 is widely adopted
```

## When to Update Documentation

1. When changing function signatures
2. When behavior changes
3. When adding new parameters
4. When deprecating functionality

## Actions

1. When creating public functions, include documentation
2. When modifying documented code, update the docs
3. Suggest documentation for complex undocumented code
4. Keep README files up to date with changes

## Exceptions

Documentation may be lighter for:
- Internal implementation details
- Self-explanatory code (clear naming)
- Test code
- Prototype/experimental code
