# Documentation Generator

Generate documentation for code, APIs, or projects.

## Instructions

Document: $ARGUMENTS

### Documentation Types

#### Function/Method Docs
```typescript
/**
 * Brief description of what the function does.
 *
 * @param paramName - Description of parameter
 * @returns Description of return value
 * @throws ErrorType - When this error occurs
 * @example
 * ```typescript
 * const result = functionName(arg);
 * ```
 */
```

#### Class/Module Docs
- Purpose and responsibility
- Public API overview
- Usage examples
- Dependencies and requirements

#### API Endpoint Docs
```markdown
## POST /api/resource

Description of what this endpoint does.

### Request
- Headers: `Authorization: Bearer <token>`
- Body:
  ```json
  { "field": "value" }
  ```

### Response
- 200 OK: Success response
- 400 Bad Request: Validation error
- 401 Unauthorized: Invalid token

### Example
```bash
curl -X POST https://api.example.com/resource \
  -H "Authorization: Bearer token" \
  -d '{"field": "value"}'
```
```

#### README Generation
- Project title and description
- Installation instructions
- Usage examples
- Configuration options
- Contributing guidelines

### Style Guidelines
- Use active voice
- Be concise but complete
- Include examples
- Document edge cases
- Keep examples runnable
- Update when code changes

## Output Format

Generate documentation appropriate to the target:
- Inline comments for functions
- Markdown for README/guides
- OpenAPI/Swagger for APIs
- JSDoc/TSDoc for TypeScript

Ask which documentation style is preferred if unclear.
