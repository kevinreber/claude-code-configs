# Guardrail: Security First

## Purpose
Ensure security is considered in all code changes.

## Input Validation

### Always Validate
- User input from forms
- URL parameters and query strings
- Request bodies
- File uploads
- Headers (especially custom headers)

### Validation Rules
```typescript
// Use allowlists, not blocklists
const ALLOWED_ROLES = ['user', 'admin', 'moderator'];
if (!ALLOWED_ROLES.includes(role)) { throw new Error('Invalid role'); }

// Validate types and ranges
if (typeof age !== 'number' || age < 0 || age > 150) {
  throw new Error('Invalid age');
}

// Sanitize strings
const sanitized = DOMPurify.sanitize(userInput);
```

## Output Encoding

### Context-Appropriate Encoding
- HTML context: HTML entity encoding
- JavaScript context: JavaScript encoding
- URL context: URL encoding
- SQL context: Parameterized queries

### Never Trust User Data in Output
```javascript
// Bad
element.innerHTML = userInput;

// Good
element.textContent = userInput;
// or
element.innerHTML = DOMPurify.sanitize(userInput);
```

## Authentication & Authorization

### Every Endpoint Must
1. Verify authentication (who is the user?)
2. Verify authorization (can they do this action?)
3. Validate the request

### Common Mistakes to Avoid
- Trusting client-side validation alone
- Using predictable IDs for authorization
- Missing auth checks on API endpoints
- Exposing sensitive data in error messages

## Secure Defaults

### Use Secure Libraries
- bcrypt/argon2 for password hashing (never MD5/SHA1)
- crypto.randomUUID() for tokens (never Math.random())
- Parameterized queries for SQL (never string concatenation)

### Security Headers
```
Content-Security-Policy: default-src 'self'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Strict-Transport-Security: max-age=31536000
```

## Logging

### Never Log
- Passwords or tokens
- Full credit card numbers
- Personal identification numbers
- Session IDs
- API keys

### Always Log
- Authentication attempts (success/failure)
- Authorization failures
- Input validation failures
- Security-relevant actions

## Actions

1. Review code changes for security implications
2. Suggest security improvements proactively
3. Warn about common vulnerability patterns
4. Recommend security testing for sensitive changes
