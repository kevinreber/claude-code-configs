# Smart Commit Message Generator

Generate meaningful commit messages from staged changes.

## Instructions

Analyze the current git diff (staged changes) and generate a commit message.

### Commit Message Format

Follow Conventional Commits specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, missing semicolons, etc.
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `perf`: Performance improvement
- `test`: Adding or updating tests
- `chore`: Maintenance tasks, dependency updates
- `ci`: CI/CD changes
- `build`: Build system changes

### Guidelines
- Subject line: max 50 characters, imperative mood
- Body: wrap at 72 characters, explain what and why
- Reference issues when applicable

## Process

1. Run `git diff --cached` to see staged changes
2. Analyze the changes
3. Determine the appropriate type and scope
4. Generate the message

## Output Format

```
Suggested commit message:

feat(auth): add OAuth2 login support

Implement Google and GitHub OAuth2 providers for user authentication.
This replaces the legacy session-based auth system.

- Add OAuth2 configuration endpoints
- Implement token refresh logic
- Update user model with provider fields

Closes #123
```

Then ask if the user wants to commit with this message.
