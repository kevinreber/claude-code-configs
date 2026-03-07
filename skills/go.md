# Go Skill

Idiomatic Go patterns, tooling, and best practices for writing clear, performant, and maintainable Go code.

## Activation

Use this skill when working on Go projects — writing new code, reviewing existing code, debugging, or setting up tooling.

---

## Tooling

| Tool | Purpose | Command |
|------|---------|---------|
| `go fmt` | Format code | `go fmt ./...` |
| `go vet` | Static analysis | `go vet ./...` |
| `golangci-lint` | Comprehensive linter | `golangci-lint run` |
| `go test` | Run tests | `go test ./...` |
| `go build` | Build | `go build ./...` |
| `go mod tidy` | Clean up dependencies | `go mod tidy` |
| `go get` | Add dependency | `go get github.com/pkg/errors` |

**Standard checks before committing:**
```bash
go fmt ./... && go vet ./... && go test ./...
```

---

## Error Handling

Go errors are values — handle them explicitly, every time.

```go
// Always check errors
result, err := doSomething()
if err != nil {
    return fmt.Errorf("doSomething failed: %w", err) // wrap with %w for unwrapping
}

// Sentinel errors — for expected, checkable errors
var ErrNotFound = errors.New("not found")

func findUser(id int) (*User, error) {
    if id == 0 {
        return nil, ErrNotFound
    }
    // ...
}

// Check sentinel errors with errors.Is
if errors.Is(err, ErrNotFound) {
    // handle not found
}

// Custom error types — for errors that carry extra data
type ValidationError struct {
    Field   string
    Message string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation failed on %s: %s", e.Field, e.Message)
}

// Unwrap with errors.As
var valErr *ValidationError
if errors.As(err, &valErr) {
    fmt.Println(valErr.Field)
}
```

**Rules:**
- Never ignore errors with `_` unless there's a clear reason (add a comment)
- Wrap errors with `%w` (not `%s`) so they can be unwrapped
- Error messages are lowercase, no punctuation at the end

---

## Interfaces

Keep interfaces small — the best Go interfaces have 1-3 methods.

```go
// Define interfaces where they're used (consumer side), not where implemented
// BAD: big interface in the producer package
type BigService interface { /* 20 methods */ }

// GOOD: small interface at the call site
type UserReader interface {
    GetUser(ctx context.Context, id int) (*User, error)
}

func NewHandler(users UserReader) *Handler { ... }

// io.Reader, io.Writer are the gold standard
type Reader interface {
    Read(p []byte) (n int, err error)
}
```

---

## Concurrency

```go
// Goroutines are cheap — use them for concurrent work
go func() {
    result := doWork()
    ch <- result
}()

// Channels for communication between goroutines
ch := make(chan int, 10) // buffered channel
done := make(chan struct{}) // signal channel

// sync.WaitGroup for waiting on multiple goroutines
var wg sync.WaitGroup
for _, item := range items {
    wg.Add(1)
    go func(item Item) {
        defer wg.Done()
        process(item)
    }(item) // pass item as argument to avoid closure capture bug
}
wg.Wait()

// sync.Mutex for shared state
type SafeCounter struct {
    mu    sync.Mutex
    count int
}

func (c *SafeCounter) Inc() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.count++
}

// context for cancellation and deadlines
func fetchData(ctx context.Context, url string) ([]byte, error) {
    req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
    if err != nil {
        return nil, err
    }
    // ...
}
```

**Rules:**
- Pass `context.Context` as the first parameter to any function that does I/O or can be cancelled
- Never store contexts in structs — pass them through function calls
- Use `defer` for cleanup (unlock, close, etc.)

---

## Structs and Methods

```go
// Constructor functions — return pointer for mutable structs
type Server struct {
    host string
    port int
    db   *sql.DB
}

func NewServer(host string, port int, db *sql.DB) *Server {
    return &Server{host: host, port: port, db: db}
}

// Methods on pointer receiver for mutation
func (s *Server) Start() error { ... }

// Methods on value receiver for read-only and small structs
func (u User) String() string {
    return fmt.Sprintf("%s <%s>", u.Name, u.Email)
}

// Functional options pattern for optional config
type Option func(*Server)

func WithTimeout(d time.Duration) Option {
    return func(s *Server) { s.timeout = d }
}

func NewServer(host string, opts ...Option) *Server {
    s := &Server{host: host, timeout: 30 * time.Second}
    for _, opt := range opts {
        opt(s)
    }
    return s
}
```

---

## Packages

```
myapp/
├── cmd/
│   └── myapp/
│       └── main.go      # entry point only — wire up dependencies
├── internal/            # private packages (not importable externally)
│   ├── server/
│   ├── storage/
│   └── domain/
├── pkg/                 # public packages (importable by others)
└── go.mod
```

- `cmd/` — entry points, minimal code
- `internal/` — business logic, unexported to outside the module
- Keep `main.go` thin — just parse flags, wire dependencies, call `run()`

---

## Testing

```go
// Table-driven tests — Go's idiomatic pattern
func TestAdd(t *testing.T) {
    tests := []struct {
        name     string
        a, b     int
        expected int
    }{
        {"positive", 2, 3, 5},
        {"negative", -1, -2, -3},
        {"zero", 0, 0, 0},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := Add(tt.a, tt.b)
            if got != tt.expected {
                t.Errorf("Add(%d, %d) = %d, want %d", tt.a, tt.b, got, tt.expected)
            }
        })
    }
}

// Test helpers
func assertNoError(t *testing.T, err error) {
    t.Helper() // marks this as a helper — error line points to caller
    if err != nil {
        t.Fatalf("unexpected error: %v", err)
    }
}

// Subtests and parallel
func TestIntegration(t *testing.T) {
    t.Parallel() // run in parallel with other tests

    t.Run("creates user", func(t *testing.T) {
        t.Parallel()
        // ...
    })
}

// Use testify for assertions in larger projects
// import "github.com/stretchr/testify/assert"
assert.Equal(t, expected, actual)
assert.NoError(t, err)
assert.ErrorIs(t, err, ErrNotFound)
```

---

## Common Patterns

### defer for cleanup

```go
f, err := os.Open(filename)
if err != nil {
    return err
}
defer f.Close() // always runs when function returns

rows, err := db.QueryContext(ctx, query)
if err != nil {
    return err
}
defer rows.Close()
```

### Zero values

```go
// Go's zero values mean you often don't need constructors
var buf bytes.Buffer  // ready to use, no init needed
var wg sync.WaitGroup // ready to use
var mu sync.Mutex     // ready to use

// Design structs so zero value is useful
type Config struct {
    Timeout time.Duration // zero = no timeout (valid behaviour)
    MaxRetries int        // zero = no retries (valid behaviour)
}
```

### Slice and map gotchas

```go
// nil slice is valid and usable
var s []int
s = append(s, 1) // works fine

// but nil map panics on write
var m map[string]int
m["key"] = 1 // PANIC

// always initialize maps
m := make(map[string]int)
// or
m := map[string]int{}

// copy a slice to avoid aliasing
original := []int{1, 2, 3}
clone := make([]int, len(original))
copy(clone, original)
```
