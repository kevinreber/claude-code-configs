# Rust Skill

Idiomatic Rust patterns, tooling, and best practices for writing safe, performant code.

## Activation

Use this skill when working on Rust projects — writing new code, reviewing existing code, debugging, or refactoring.

---

## Tooling

| Tool | Purpose | Command |
|------|---------|---------|
| `cargo fmt` | Format code | `cargo fmt` |
| `cargo clippy` | Lint (treat warnings as errors) | `cargo clippy -- -D warnings` |
| `cargo check` | Type-check without building | `cargo check` |
| `cargo test` | Run tests | `cargo test` |
| `cargo build --release` | Optimized build | `cargo build --release` |
| `cargo add <crate>` | Add dependency | `cargo add serde --features derive` |

---

## Error Handling

### Application code → `anyhow`

```rust
use anyhow::{Context, Result};

fn read_config(path: &Path) -> Result<Config> {
    let content = std::fs::read_to_string(path)
        .with_context(|| format!("Failed to read config from {}", path.display()))?;
    let config: Config = toml::from_str(&content)
        .context("Failed to parse config file")?;
    Ok(config)
}
```

### Library/public API → `thiserror`

```rust
use thiserror::Error;

#[derive(Debug, Error)]
pub enum StorageError {
    #[error("Record not found: {id}")]
    NotFound { id: u64 },
    #[error("Database error: {0}")]
    Database(#[from] rusqlite::Error),
}
```

### Rules
- Never use `.unwrap()` or `.expect()` in production paths (only in tests or with a comment explaining why it's safe)
- Use `?` for error propagation
- Add context to errors with `.with_context(|| ...)` — include the relevant value (path, id, etc.)

---

## Ownership & Borrowing

```rust
// Prefer borrowing over cloning when possible
fn process(data: &[u8]) -> usize { data.len() }

// Clone only when you need to own the value
fn store(value: String) { /* takes ownership */ }
let s = String::from("hello");
store(s.clone()); // clone if you need to use s again
store(s);         // move if you don't

// Use Arc for shared ownership across threads
use std::sync::Arc;
let shared = Arc::new(expensive_data);
let clone = Arc::clone(&shared);
```

---

## Async (Tokio)

```rust
use tokio::task;

// Use spawn_blocking for CPU-intensive or blocking I/O (e.g., rusqlite)
let result = task::spawn_blocking(move || {
    db.query_blocking()
}).await??;

// Avoid blocking calls in async fn — they block the runtime thread
// BAD:
async fn bad() {
    std::thread::sleep(Duration::from_secs(1)); // blocks runtime!
}

// GOOD:
async fn good() {
    tokio::time::sleep(Duration::from_secs(1)).await;
}
```

**Axum state must be `Clone + Send + Sync + 'static`:**
```rust
#[derive(Clone)]
struct AppState {
    db: Arc<Mutex<Connection>>,
    config: Arc<Config>,
}
```

---

## Common Patterns

### Builder pattern
```rust
#[derive(Default)]
struct QueryBuilder {
    limit: Option<usize>,
    offset: Option<usize>,
    filter: Option<String>,
}

impl QueryBuilder {
    fn limit(mut self, n: usize) -> Self { self.limit = Some(n); self }
    fn offset(mut self, n: usize) -> Self { self.offset = Some(n); self }
    fn filter(mut self, f: impl Into<String>) -> Self { self.filter = Some(f.into()); self }
    fn build(self) -> Query { /* ... */ }
}

let q = QueryBuilder::default().limit(10).offset(20).build();
```

### Newtype for type safety
```rust
struct UserId(u64);
struct PostId(u64);
// Now you can't accidentally pass a PostId where UserId is expected
```

### Option/Result combinators
```rust
// Use map, and_then, unwrap_or, unwrap_or_else instead of match when concise
let name = user.name.as_deref().unwrap_or("Anonymous");
let upper = maybe_string.map(|s| s.to_uppercase());
let result = find_user(id).and_then(|u| validate(u));
```

---

## Clippy Rules to Know

```bash
# Most useful clippy lints (already included in -- -D warnings):
# clippy::unwrap_used       - catches .unwrap()
# clippy::expect_used       - catches .expect()
# clippy::clone_on_ref_ptr  - unnecessary Arc clones
# clippy::inefficient_to_string - use .to_owned() not .to_string() on &str
# clippy::map_unwrap_or     - use .unwrap_or() instead of .map().unwrap_or()
```

---

## Testing

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::TempDir;

    #[test]
    fn test_basic() {
        assert_eq!(add(2, 3), 5);
    }

    #[tokio::test]
    async fn test_async() {
        let result = fetch_data().await.unwrap();
        assert!(!result.is_empty());
    }

    #[test]
    fn test_with_temp_db() {
        let dir = TempDir::new().unwrap();
        let db_path = dir.path().join("test.db");
        // TempDir auto-cleans on drop
    }
}
```

---

## Performance Tips

- Prefer `&str` over `String` for function parameters when you don't need ownership
- Use `Vec::with_capacity(n)` when you know the size upfront
- Avoid `clone()` in hot paths — restructure to borrow instead
- Use `Cow<str>` when a function sometimes needs to allocate and sometimes doesn't
- Profile before optimizing — `cargo flamegraph` or `criterion` for benchmarks
