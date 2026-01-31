# Git Workflow Skill

Specialized skill for Git operations, branching strategies, and version control best practices.

## Activation

Use this skill when the user needs help with Git operations, resolving conflicts, or establishing Git workflows.

## Branching Strategies

### Git Flow
```
main ─────●─────────────●───────────●─────
          │             │           ↑
develop ──●──●──●──●────●──●────────●─────
              │  ↑      │  ↑
feature ──────●──●      │  │
                        │  │
hotfix ─────────────────●──●
```

- `main`: Production-ready code
- `develop`: Integration branch
- `feature/*`: New features
- `release/*`: Release preparation
- `hotfix/*`: Emergency fixes

### GitHub Flow
```
main ────●────●────●────●────
         │    ↑    │    ↑
feature ─●────●    ●────●
```

- Simple: main + feature branches
- Deploy from main after merge
- Good for continuous deployment

### Trunk-Based Development
```
main ──●──●──●──●──●──●──●──●──
       ↑  ↑  ↑  ↑  ↑  ↑  ↑  ↑
       Small, frequent commits
```

- All developers commit to main
- Short-lived feature branches (<1 day)
- Feature flags for incomplete features

## Common Operations

### Commit Best Practices
```bash
# Good commit message
git commit -m "feat(auth): add OAuth2 login support

Implement Google and GitHub OAuth providers.
Closes #123"

# Conventional commit types
# feat, fix, docs, style, refactor, perf, test, chore
```

### Interactive Rebase
```bash
# Clean up commits before merge
git rebase -i HEAD~3

# Commands: pick, reword, edit, squash, fixup, drop
```

### Conflict Resolution
1. Identify conflicting files: `git status`
2. Open file, find conflict markers
3. Choose correct code between `<<<` and `>>>`
4. Remove conflict markers
5. Stage resolved file: `git add <file>`
6. Continue: `git rebase --continue` or `git merge --continue`

## PR Sync Workflow

Keep your PR branches in sync with the main branch to prevent merge conflicts and CI failures.

### Before Pushing to a PR
```bash
# 1. Fetch latest from origin
git fetch origin main

# 2. Check if you're behind
git rev-list --count HEAD..origin/main

# 3. If behind, merge main into your branch
git merge origin/main

# 4. Resolve any conflicts, then push
git push
```

### Automated PR Sync (Recommended)
Use the `pr-sync` hook to automatically check for sync issues after every push.
The hook will alert you when your branch is behind main/master and needs to be synced.

## Advanced Conflict Resolution

### Understanding Conflict Markers
```
<<<<<<< HEAD (Current Change)
Your local changes on the current branch
=======
Incoming changes from the branch being merged
>>>>>>> branch-name (Incoming Change)
```

### Conflict Resolution Strategies

#### 1. Semantic Merge (Preferred)
Don't just pick one side - understand the **intent** of both changes:

```javascript
// <<<<<<< HEAD
function calculateTotal(items) {
  return items.reduce((sum, item) => sum + item.price, 0);
}
// =======
function calculateTotal(items, taxRate) {
  const subtotal = items.reduce((sum, item) => sum + item.price, 0);
  return subtotal;
}
// >>>>>>> main

// CORRECT resolution - merge the INTENT of both changes:
function calculateTotal(items, taxRate = 0) {
  const subtotal = items.reduce((sum, item) => sum + item.price, 0);
  return subtotal * (1 + taxRate);
}
```

#### 2. Import/Dependency Conflicts
When both branches add imports, include ALL needed imports:

```python
# Keep imports from BOTH sides, remove duplicates
from module_a import func_a  # from HEAD
from module_b import func_b  # from main
from module_c import func_c  # from both (dedupe)
```

#### 3. Configuration File Conflicts (package.json, etc.)
- Merge dependencies from both sides
- Use the higher version number when same package differs
- Regenerate lock files after resolution: `npm install` / `yarn`

#### 4. Database Migration Conflicts
- Never merge migration files - one must come first
- Renumber the later migration
- Test the full migration sequence

### Post-Conflict Checklist
After resolving conflicts, ALWAYS:

1. **Verify syntax**: Ensure no stray conflict markers remain
   ```bash
   grep -r "<<<<<<" . --include="*.{js,ts,py,go,rs,java}"
   ```

2. **Run tests**: Conflicts can introduce subtle bugs
   ```bash
   npm test  # or pytest, go test, cargo test, etc.
   ```

3. **Run linters**: Check for introduced errors
   ```bash
   npm run lint  # or ruff, golangci-lint, etc.
   ```

4. **Build the project**: Ensure it compiles
   ```bash
   npm run build  # or go build, cargo build, etc.
   ```

5. **Manual review**: Check the conflict areas make logical sense

### Common Conflict Scenarios

| Scenario | Resolution Strategy |
|----------|---------------------|
| Both branches edit same function | Merge the logic; may need refactoring |
| Both branches add to same list/array | Include items from both sides |
| Deleted vs modified file | Determine if deletion or modification is correct |
| Renamed vs modified file | Apply modifications to renamed file |
| Both branches add same feature differently | Choose better implementation or combine |

## Pre-Commit Quality Checks

Before committing, ensure all checks pass to prevent CI failures:

### Automated Checks (Recommended)
Use the `pre-commit-checks` hook to automatically run:
- Linters (ESLint, Ruff, golangci-lint, etc.)
- Type checkers (TypeScript, mypy, etc.)
- Unit tests
- Build verification

### Manual Pre-Commit Checklist
```bash
# 1. Run linter
npm run lint        # JS/TS
ruff check .        # Python
go vet ./...        # Go
cargo clippy        # Rust

# 2. Run type checker
npm run typecheck   # TypeScript
mypy .              # Python

# 3. Run tests
npm test            # JS/TS
pytest              # Python
go test ./...       # Go
cargo test          # Rust

# 4. Verify build
npm run build       # JS/TS
go build ./...      # Go
cargo build         # Rust
```

### Why Pre-Commit Checks Matter
- Catch errors before they reach CI
- Faster feedback loop (local vs waiting for CI)
- Prevent broken builds on shared branches
- Maintain code quality standards

### Recovering from Mistakes
```bash
# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1

# Recover deleted branch
git reflog
git checkout -b branch-name <sha>

# Undo a pushed commit (creates new commit)
git revert <sha>
```

### Stashing
```bash
# Save work in progress
git stash push -m "WIP: feature description"

# List stashes
git stash list

# Apply and remove
git stash pop

# Apply but keep stash
git stash apply stash@{0}
```

## What I Help With

- Choosing appropriate branching strategy
- Writing good commit messages
- Resolving merge conflicts (semantic resolution)
- Keeping PR branches in sync with main
- Running pre-commit quality checks
- Preventing CI failures before they happen
- Cleaning up Git history
- Setting up Git hooks
- Recovering from Git mistakes
- Configuring .gitignore
- Managing large files (Git LFS)
