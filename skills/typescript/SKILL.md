# TypeScript Skill

Idiomatic TypeScript patterns, strict mode best practices, and tooling for type-safe development.

## Activation

Use this skill when working on TypeScript projects — writing new code, reviewing types, debugging type errors, or configuring tooling.

---

## Tooling

| Tool | Purpose | Command |
|------|---------|---------|
| `tsc --noEmit` | Type-check without emitting | `npx tsc --noEmit` |
| `eslint` | Lint | `npx eslint .` |
| `biome` | Lint + format (modern alternative) | `npx biome check .` |
| `prettier` | Format | `npx prettier --write .` |
| `vitest` | Unit testing | `npx vitest` |
| `jest` | Unit testing (older) | `npx jest` |

**Preferred package managers by project:**
- Check `package.json` for `packageManager` field or presence of `yarn.lock` / `pnpm-lock.yaml`
- Default to `npm` if unclear

---

## Type System

### Prefer `type` for unions/intersections, `interface` for object shapes

```typescript
// interface for objects (extensible, mergeable)
interface User {
  id: string;
  name: string;
}

// type for unions, intersections, mapped types
type Status = 'active' | 'inactive' | 'pending';
type ReadonlyUser = Readonly<User>;
type PartialUser = Partial<User>;
```

### Avoid `any` — use `unknown` instead

```typescript
// BAD: any disables type checking
function parse(data: any) { return data.name; }

// GOOD: unknown forces you to narrow the type first
function parse(data: unknown): string {
  if (typeof data === 'object' && data !== null && 'name' in data) {
    return String((data as { name: unknown }).name);
  }
  throw new Error('Invalid data shape');
}
```

### Discriminated unions

```typescript
type Result<T> =
  | { success: true; data: T }
  | { success: false; error: string };

function handle(result: Result<User>) {
  if (result.success) {
    console.log(result.data.name); // TypeScript knows data exists here
  } else {
    console.error(result.error);   // and error exists here
  }
}
```

### Utility types

```typescript
Partial<T>       // all properties optional
Required<T>      // all properties required
Readonly<T>      // all properties readonly
Pick<T, K>       // pick subset of keys
Omit<T, K>       // omit subset of keys
Record<K, V>     // object with keys K and values V
NonNullable<T>   // removes null and undefined
ReturnType<F>    // return type of a function
Parameters<F>    // parameter types of a function
```

---

## Strict Mode

Always enable in `tsconfig.json`:
```json
{
  "compilerOptions": {
    "strict": true,           // enables all strict checks
    "noUncheckedIndexedAccess": true,  // arr[i] is T | undefined
    "exactOptionalPropertyTypes": true  // optional props can't be set to undefined
  }
}
```

**Key strict checks:**
- `strictNullChecks` — `null` and `undefined` are not assignable to other types
- `noImplicitAny` — no implicit `any` types
- `strictFunctionTypes` — stricter function type checking

---

## Async Patterns

```typescript
// Always type async function return values
async function fetchUser(id: string): Promise<User> {
  const res = await fetch(`/api/users/${id}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json() as Promise<User>;
}

// Use Promise.all for parallel async operations
const [user, posts] = await Promise.all([
  fetchUser(id),
  fetchPosts(id),
]);

// Error handling in async
try {
  const data = await fetchUser(id);
} catch (error) {
  // error is unknown in strict mode — narrow it
  if (error instanceof Error) {
    console.error(error.message);
  }
}
```

---

## Common Patterns

### Type narrowing

```typescript
// typeof
if (typeof value === 'string') { /* value is string */ }

// instanceof
if (error instanceof Error) { /* error is Error */ }

// in
if ('name' in obj) { /* obj has name property */ }

// Type guard function
function isUser(obj: unknown): obj is User {
  return typeof obj === 'object' && obj !== null && 'id' in obj;
}
```

### Const assertions

```typescript
const ROLES = ['admin', 'user', 'guest'] as const;
type Role = typeof ROLES[number]; // 'admin' | 'user' | 'guest'

const config = { port: 3000, env: 'production' } as const;
// All properties are now readonly with literal types
```

### Template literal types

```typescript
type EventName = `on${Capitalize<string>}`;
type Route = `/api/${string}`;
```

---

## Error Handling

```typescript
// Result pattern (no exceptions)
type Result<T, E = Error> =
  | { ok: true; value: T }
  | { ok: false; error: E };

// Or use a library like neverthrow for this pattern

// Standard try/catch — always narrow the error type
try {
  await riskyOperation();
} catch (error) {
  if (error instanceof CustomError) {
    // handle specifically
  } else if (error instanceof Error) {
    // handle generically
  } else {
    // unexpected non-Error thrown
    throw error;
  }
}
```

---

## Module Patterns

```typescript
// Prefer named exports for tree-shaking
export function doThing() {}
export type { User };

// Use barrel files (index.ts) sparingly — they can hurt bundle splitting
// Import directly from the file when possible
import { doThing } from './utils/doThing';  // better than:
import { doThing } from './utils';           // if utils/index.ts re-exports everything
```

---

## Testing

```typescript
// Vitest (preferred for modern projects)
import { describe, it, expect, vi } from 'vitest';

describe('fetchUser', () => {
  it('returns user data on success', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ id: '1', name: 'Alice' }),
    });
    vi.stubGlobal('fetch', mockFetch);

    const user = await fetchUser('1');
    expect(user.name).toBe('Alice');
  });
});
```
