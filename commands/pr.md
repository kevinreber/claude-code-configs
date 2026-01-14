# Pull Request Description Generator

Generate comprehensive PR descriptions from branch changes.

## Instructions

Analyze changes between current branch and main/master: $ARGUMENTS

If argument provided, use it as the base branch for comparison.

### Analysis Steps

1. Get branch diff: `git log main..HEAD --oneline`
2. Get file changes: `git diff main...HEAD --stat`
3. Read modified files for context
4. Identify the purpose and impact

### PR Template

```markdown
## Summary
[2-3 sentences describing what this PR does]

## Changes
- [Bullet points of key changes]

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update
- [ ] Refactoring (no functional changes)
- [ ] Performance improvement
- [ ] Test coverage

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

### Test Instructions
[How to test these changes]

## Screenshots
[If applicable]

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings introduced
- [ ] Dependent changes merged

## Related Issues
Closes #[issue number]

## Additional Notes
[Any other context reviewers should know]
```

## Output

Generate the filled-in PR template based on actual changes.
Ask if the user wants to create the PR with `gh pr create`.
