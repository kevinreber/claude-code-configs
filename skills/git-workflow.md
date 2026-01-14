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
- Resolving merge conflicts
- Cleaning up Git history
- Setting up Git hooks
- Recovering from Git mistakes
- Configuring .gitignore
- Managing large files (Git LFS)
