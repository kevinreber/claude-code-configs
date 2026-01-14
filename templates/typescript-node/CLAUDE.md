# Project: [Project Name]

## Overview

[Brief description of what this project does]

## Tech Stack

- **Runtime**: Node.js 20+
- **Language**: TypeScript 5.x
- **Package Manager**: npm / pnpm / yarn
- **Framework**: [Express / Fastify / NestJS / etc.]
- **Database**: [PostgreSQL / MongoDB / etc.]
- **Testing**: Jest / Vitest

## Project Structure

```
src/
├── index.ts          # Application entry point
├── config/           # Configuration and environment
├── controllers/      # Request handlers
├── services/         # Business logic
├── models/           # Data models / entities
├── middleware/       # Express/Fastify middleware
├── utils/            # Utility functions
├── types/            # TypeScript type definitions
└── __tests__/        # Test files
```

## Development Commands

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Run tests
npm test

# Run tests in watch mode
npm run test:watch

# Type check
npm run typecheck

# Lint
npm run lint

# Build for production
npm run build

# Start production server
npm start
```

## Coding Conventions

### File Naming
- Use kebab-case for files: `user-service.ts`
- Use PascalCase for classes: `UserService`
- Use camelCase for functions and variables
- Suffix test files with `.test.ts` or `.spec.ts`

### Code Style
- Use explicit return types for public functions
- Prefer `const` over `let`
- Use async/await over raw promises
- Prefer named exports over default exports
- Max line length: 100 characters

### Error Handling
- Use custom error classes extending `Error`
- Always include error codes for API errors
- Log errors with context (request ID, user ID)
- Never expose internal errors to clients

### Testing
- Co-locate tests with source files or use `__tests__` directory
- Name test files `*.test.ts`
- Use descriptive test names
- Mock external dependencies

## Important Patterns

### Dependency Injection
```typescript
// Services receive dependencies through constructor
class UserService {
  constructor(
    private readonly userRepository: UserRepository,
    private readonly emailService: EmailService
  ) {}
}
```

### Error Responses
```typescript
// Use consistent error format
throw new AppError('USER_NOT_FOUND', 'User not found', 404);
```

## Environment Variables

Required environment variables (see `.env.example`):
- `DATABASE_URL` - Database connection string
- `JWT_SECRET` - Secret for JWT signing
- `NODE_ENV` - Environment (development/production)

## Sensitive Areas

- `src/config/` - Contains security-sensitive configuration
- `src/middleware/auth.ts` - Authentication logic
- Database migrations - Review carefully before running

## Common Issues

1. **Port already in use**: Kill process on port 3000 or change PORT env var
2. **TypeScript errors after install**: Run `npm run typecheck` to verify
3. **Database connection fails**: Check DATABASE_URL and ensure DB is running
