# Guardrail: Confirmation Required

## Purpose
Require explicit confirmation before executing potentially destructive or irreversible operations.

## Operations Requiring Confirmation

### Destructive File Operations
- Deleting files or directories
- Overwriting files with `>` redirect
- `rm`, `rm -rf`, `rmdir` commands

**Before executing**: "I'm about to delete [files]. This cannot be undone. Proceed?"

### Git Operations
- `git push --force` or `git push -f`
- `git reset --hard`
- `git clean -fd`
- `git rebase` on shared branches
- Deleting branches (`git branch -D`)

**Before executing**: "This will [describe impact]. This may affect other developers. Proceed?"

### Database Operations
- `DROP TABLE`, `DROP DATABASE`
- `DELETE FROM` without WHERE clause
- `TRUNCATE TABLE`
- Schema migrations on production databases

**Before executing**: "This will permanently delete data from [table/database]. Proceed?"

### Production/Deployment
- Deploying to production
- Modifying production configuration
- Running scripts against production data

**Before executing**: "This will affect production. Have you verified this is correct?"

### Package Management
- Removing dependencies that might be in use
- Major version upgrades
- Changing package manager lockfiles

**Before executing**: "This changes project dependencies. Run tests after to verify nothing broke."

### System Operations
- `chmod` with recursive flag
- `chown` with recursive flag
- Modifying system files
- Installing global packages

**Before executing**: "This modifies system configuration. Proceed?"

## Confirmation Format

When confirmation is needed:

```
⚠️  Confirmation Required

Action: [Describe the action]
Impact: [Describe what will happen]
Reversible: [Yes/No/Partially]

Type 'yes' to proceed or 'no' to cancel.
```

## Exceptions

Confirmation can be skipped when:
- User explicitly said "just do it" or similar
- Operating in a clearly disposable environment (temp directory, test database)
- The operation is clearly reversible (git stash, etc.)
