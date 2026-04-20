# Bash Skill

Safe, portable, and maintainable shell scripting best practices.

## Activation

Use this skill when writing or reviewing shell scripts (`.sh` files), bash functions, Makefiles, or CI/CD configurations.

---

## Script Header

Every script should start with:

```bash
#!/usr/bin/env bash
set -euo pipefail

# -e: exit on error
# -u: treat unset variables as errors
# -o pipefail: pipe fails if any command in the pipe fails
```

Use `/usr/bin/env bash` (not `/bin/bash`) for portability — `bash` may be at a different path on some systems (e.g., macOS via Homebrew).

---

## Variables

```bash
# Always quote variables to handle spaces and special chars
FILE="$1"
echo "Processing: $FILE"
cp "$FILE" "$DEST_DIR/"

# Use ${VAR:-default} for defaults
NAME="${1:-World}"
echo "Hello, $NAME"

# Use ${VAR:?error message} to require a variable
DB_URL="${DATABASE_URL:?DATABASE_URL must be set}"

# Uppercase for exported/global, lowercase for local
GLOBAL_CONFIG="/etc/myapp/config"
local_temp_file=$(mktemp)

# Use $() not backticks for command substitution
DATE=$(date +%Y-%m-%d)
FILES=$(find . -name "*.ts")
```

---

## Functions

```bash
# Use functions for reusable logic
log_info() {
  echo "[INFO] $*"
}

log_error() {
  echo "[ERROR] $*" >&2  # errors to stderr
}

die() {
  log_error "$*"
  exit 1
}

# Check if a command exists
require() {
  command -v "$1" >/dev/null 2>&1 || die "$1 is required but not installed"
}

require git
require jq
```

---

## Control Flow

```bash
# Check file/dir existence
if [ -f "$FILE" ]; then echo "file exists"; fi
if [ -d "$DIR" ]; then echo "dir exists"; fi
if [ ! -e "$PATH" ]; then echo "doesn't exist"; fi

# Check command success
if ! git status >/dev/null 2>&1; then
  die "Not a git repository"
fi

# Use [[ ]] for string comparisons (bash-specific but safer)
if [[ "$OS" == "Darwin" ]]; then
  echo "macOS"
elif [[ "$OS" == "Linux" ]]; then
  echo "Linux"
fi

# Regex matching with [[
if [[ "$VERSION" =~ ^[0-9]+\.[0-9]+$ ]]; then
  echo "Valid version: $VERSION"
fi
```

---

## Safety Patterns

### Idempotent operations

```bash
# Check before creating/installing
if ! command -v brew >/dev/null 2>&1; then
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Create dir only if it doesn't exist
mkdir -p "$DEST_DIR"

# Copy only if source is newer
cp -u "$SRC" "$DEST"
```

### Cleanup with traps

```bash
TEMP_DIR=$(mktemp -d)

cleanup() {
  rm -rf "$TEMP_DIR"
  echo "Cleaned up temp dir"
}

trap cleanup EXIT  # runs on exit, including errors
trap 'cleanup; exit 1' INT TERM  # runs on Ctrl+C

# Now use TEMP_DIR safely
cp files/* "$TEMP_DIR/"
process "$TEMP_DIR"
```

### Safe file operations

```bash
# Never rm -rf a variable without checking it's set and non-empty
if [ -n "$BUILD_DIR" ] && [ "$BUILD_DIR" != "/" ]; then
  rm -rf "$BUILD_DIR"
fi

# Backup before overwriting
cp "$CONFIG" "${CONFIG}.bak"

# Atomic write (write to temp, then move)
echo "new content" > "${CONFIG}.tmp"
mv "${CONFIG}.tmp" "$CONFIG"
```

---

## Input Handling

```bash
# Validate argument count
if [ $# -lt 2 ]; then
  echo "Usage: $0 <source> <destination>" >&2
  exit 1
fi

SOURCE="$1"
DEST="$2"

# Parse flags
VERBOSE=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    -v|--verbose) VERBOSE=true; shift ;;
    -n|--dry-run) DRY_RUN=true; shift ;;
    -h|--help) usage; exit 0 ;;
    --) shift; break ;;
    -*) die "Unknown flag: $1" ;;
    *) break ;;
  esac
done
```

---

## Common Patterns

### Detect OS

```bash
OS="$(uname -s)"
case "$OS" in
  Darwin) echo "macOS" ;;
  Linux)  echo "Linux" ;;
  *)      die "Unsupported OS: $OS" ;;
esac
```

### Run from script's directory

```bash
# Makes the script work regardless of where it's called from
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
```

### Check if running as root

```bash
if [ "$(id -u)" -ne 0 ]; then
  die "This script must be run as root"
fi
```

### Confirmation prompt

```bash
confirm() {
  read -rp "$1 [y/N] " response
  [[ "$response" =~ ^[Yy]$ ]]
}

if confirm "Delete $FILE?"; then
  rm "$FILE"
fi
```

---

## Common Mistakes

```bash
# BAD: unquoted variable with spaces breaks
cp $FILE $DEST     # breaks if $FILE has spaces
ls $DIRECTORY/*    # breaks if $DIRECTORY is empty

# GOOD:
cp "$FILE" "$DEST"
ls "$DIRECTORY"/

# BAD: ignoring errors
git pull
run_tests   # runs even if git pull failed

# GOOD: set -e or check explicitly
git pull || die "git pull failed"

# BAD: using test (single bracket) for == with strings
if [ "$a" == "$b" ]  # works but == isn't POSIX in [
if [ "$a" = "$b" ]   # POSIX correct
if [[ "$a" == "$b" ]] # correct and supports patterns

# BAD: parsing output of ls
for f in $(ls *.txt); do  # breaks with spaces in filenames

# GOOD: use glob directly
for f in *.txt; do
```
