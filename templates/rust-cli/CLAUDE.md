# Project: [Project Name]

## Overview

[Brief description of what this CLI tool does]

## Tech Stack

- **Language**: Rust (latest stable)
- **CLI Framework**: clap v4
- **Error Handling**: anyhow / thiserror
- **Async Runtime**: tokio (if needed)
- **Serialization**: serde + serde_json

## Project Structure

```
.
├── src/
│   ├── main.rs           # Entry point, CLI parsing
│   ├── lib.rs            # Library root (if hybrid crate)
│   ├── cli.rs            # CLI argument definitions
│   ├── commands/         # Command implementations
│   │   ├── mod.rs
│   │   └── init.rs
│   ├── config.rs         # Configuration handling
│   ├── error.rs          # Error types
│   └── utils/            # Utility functions
├── tests/                # Integration tests
├── Cargo.toml
└── Cargo.lock
```

## Development Commands

```bash
# Build in debug mode
cargo build

# Build in release mode
cargo build --release

# Run the CLI
cargo run -- <args>

# Run tests
cargo test

# Run tests with output
cargo test -- --nocapture

# Run specific test
cargo test test_name

# Check without building
cargo check

# Format code
cargo fmt

# Lint with clippy
cargo clippy -- -D warnings

# Generate docs
cargo doc --open

# Install locally
cargo install --path .
```

## Coding Conventions

### File Naming
- Use snake_case for files and directories
- Modules match file names

### Code Style
- Follow Rust API Guidelines
- Use `rustfmt` for formatting
- No warnings allowed (treat as errors)
- Write documentation comments for public API

### Error Handling
```rust
// Use thiserror for library errors
#[derive(Debug, thiserror::Error)]
pub enum AppError {
    #[error("Configuration error: {0}")]
    Config(#[from] ConfigError),

    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),

    #[error("Not found: {0}")]
    NotFound(String),
}

// Use anyhow for application errors
use anyhow::{Context, Result};

fn load_config() -> Result<Config> {
    let content = std::fs::read_to_string("config.toml")
        .context("Failed to read config file")?;
    // ...
}
```

### CLI Structure (clap)
```rust
use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(name = "myapp", about = "Description")]
struct Cli {
    #[command(subcommand)]
    command: Commands,

    #[arg(short, long, global = true)]
    verbose: bool,
}

#[derive(Subcommand)]
enum Commands {
    /// Initialize a new project
    Init {
        #[arg(short, long)]
        name: String,
    },
    /// Run the application
    Run,
}
```

## Important Patterns

### Builder Pattern
```rust
pub struct Config {
    pub timeout: Duration,
    pub retries: u32,
}

impl Config {
    pub fn builder() -> ConfigBuilder {
        ConfigBuilder::default()
    }
}
```

### Logging
```rust
use tracing::{info, debug, warn, error};

// Initialize subscriber in main
tracing_subscriber::fmt::init();

// Use structured logging
info!(user = %user_id, "Processing request");
```

### Testing
```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_feature() {
        // Arrange
        let input = "test";

        // Act
        let result = process(input);

        // Assert
        assert_eq!(result, expected);
    }
}
```

## Environment Variables

- `RUST_LOG` - Logging level (trace/debug/info/warn/error)
- `NO_COLOR` - Disable colored output
- Application-specific vars documented in README

## Sensitive Areas

- Config file handling (may contain secrets)
- Network requests (validate URLs, handle timeouts)
- File system operations (path traversal prevention)

## Performance Considerations

- Profile with `cargo flamegraph`
- Use `&str` instead of `String` when possible
- Avoid unnecessary allocations
- Use `rayon` for CPU-bound parallelism

## Common Issues

1. **Borrow checker**: Use references correctly, consider `Rc`/`Arc` for shared ownership
2. **Async complexity**: Keep async boundaries clear
3. **Binary size**: Use `strip` and LTO for smaller binaries
