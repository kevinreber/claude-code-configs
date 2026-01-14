# Project: [Project Name]

## Overview

[Brief description of what this project does]

## Tech Stack

- **Language**: Go 1.21+
- **Framework**: Standard library / Chi / Gin / Fiber
- **Database**: PostgreSQL with pgx / GORM
- **Testing**: Go testing with testify
- **API**: REST / gRPC

## Project Structure

```
.
├── cmd/
│   └── server/           # Application entrypoints
│       └── main.go
├── internal/             # Private application code
│   ├── config/           # Configuration
│   ├── handler/          # HTTP handlers
│   ├── service/          # Business logic
│   ├── repository/       # Data access
│   ├── model/            # Domain models
│   └── middleware/       # HTTP middleware
├── pkg/                  # Public libraries
├── api/                  # API definitions (OpenAPI, proto)
├── migrations/           # Database migrations
├── scripts/              # Build and utility scripts
├── go.mod
└── go.sum
```

## Development Commands

```bash
# Download dependencies
go mod download

# Run the application
go run cmd/server/main.go

# Run tests
go test ./...

# Run tests with coverage
go test -cover ./...

# Run tests with race detector
go test -race ./...

# Build binary
go build -o bin/server cmd/server/main.go

# Format code
go fmt ./...

# Vet code
go vet ./...

# Run linter
golangci-lint run

# Generate code (if using go generate)
go generate ./...

# Run database migrations
migrate -path migrations -database "$DATABASE_URL" up
```

## Coding Conventions

### File Naming
- Use snake_case for files: `user_handler.go`
- Use snake_case for test files: `user_handler_test.go`
- One main type per file when possible

### Code Style
- Follow Effective Go guidelines
- Use gofmt for formatting
- Keep functions short and focused
- Prefer returning errors over panicking
- Use meaningful variable names

### Error Handling
```go
// Always handle errors explicitly
result, err := doSomething()
if err != nil {
    return fmt.Errorf("doSomething failed: %w", err)
}

// Use custom error types for business errors
type NotFoundError struct {
    Resource string
    ID       string
}

func (e *NotFoundError) Error() string {
    return fmt.Sprintf("%s with ID %s not found", e.Resource, e.ID)
}
```

### Interfaces
```go
// Define interfaces in the consuming package
// Keep interfaces small

type UserRepository interface {
    GetByID(ctx context.Context, id string) (*User, error)
    Create(ctx context.Context, user *User) error
}
```

### Context
- Pass context as first parameter
- Use context for cancellation and request-scoped values
- Don't store context in structs

## Important Patterns

### Dependency Injection
```go
type UserHandler struct {
    userService UserService
    logger      *slog.Logger
}

func NewUserHandler(us UserService, l *slog.Logger) *UserHandler {
    return &UserHandler{
        userService: us,
        logger:      l,
    }
}
```

### Configuration
```go
type Config struct {
    Port        int    `env:"PORT" envDefault:"8080"`
    DatabaseURL string `env:"DATABASE_URL,required"`
    LogLevel    string `env:"LOG_LEVEL" envDefault:"info"`
}
```

### Graceful Shutdown
```go
ctx, cancel := signal.NotifyContext(context.Background(), os.Interrupt)
defer cancel()

// Start server...

<-ctx.Done()
// Cleanup...
```

## Environment Variables

Required variables:
- `DATABASE_URL` - PostgreSQL connection string
- `PORT` - Server port (default: 8080)
- `LOG_LEVEL` - Logging level (debug/info/warn/error)

## Sensitive Areas

- `internal/config/` - Contains secrets handling
- `internal/middleware/auth.go` - Authentication logic
- `migrations/` - Database schema changes

## Performance Considerations

- Use connection pooling for database
- Profile with `pprof` when needed
- Use sync.Pool for frequently allocated objects
- Avoid unnecessary allocations in hot paths

## Common Issues

1. **Nil pointer dereference**: Always check for nil
2. **Goroutine leaks**: Use context for cancellation
3. **Race conditions**: Use `-race` flag in tests
