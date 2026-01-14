# API Design Skill

Specialized skill for designing RESTful and GraphQL APIs.

## Activation

Use this skill when the user wants to design an API, review API design, or needs help with API architecture decisions.

## Design Principles

### REST API Design

**Resource Naming**
- Use nouns, not verbs: `/users` not `/getUsers`
- Plural for collections: `/users`, `/orders`
- Hierarchical relationships: `/users/{id}/orders`
- Consistent naming convention (kebab-case recommended)

**HTTP Methods**
- GET: Retrieve (idempotent, cacheable)
- POST: Create (not idempotent)
- PUT: Full update (idempotent)
- PATCH: Partial update
- DELETE: Remove (idempotent)

**Status Codes**
- 200 OK: Success with body
- 201 Created: Resource created
- 204 No Content: Success, no body
- 400 Bad Request: Client error
- 401 Unauthorized: Authentication required
- 403 Forbidden: No permission
- 404 Not Found: Resource doesn't exist
- 409 Conflict: State conflict
- 422 Unprocessable Entity: Validation failed
- 500 Internal Server Error: Server fault

**Pagination**
```
GET /users?page=2&limit=20
GET /users?cursor=abc123&limit=20
```

**Filtering & Sorting**
```
GET /users?status=active&sort=-created_at
GET /orders?created_after=2024-01-01
```

**Versioning**
- URL path: `/v1/users`
- Header: `Accept: application/vnd.api+json;version=1`
- Query param: `/users?version=1`

### GraphQL Design

**Schema Design**
- Start with domain modeling
- Use descriptive type names
- Leverage interfaces for shared fields
- Use enums for fixed values

**Query Design**
- Avoid deeply nested queries
- Implement pagination (Relay cursor-based)
- Use input types for complex arguments

**Performance**
- Implement DataLoader for N+1 prevention
- Set query complexity limits
- Use persisted queries in production

### Error Handling

**Standard Error Format**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input provided",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ],
    "request_id": "abc-123"
  }
}
```

### Documentation

I help generate:
- OpenAPI/Swagger specifications
- GraphQL schema documentation
- Example request/response pairs
- Authentication guides
