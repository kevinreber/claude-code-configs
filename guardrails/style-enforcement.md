# Guardrail: Style Enforcement

## Purpose
Maintain consistent code style across the project.

## Rules

### Before Writing Code
1. Check for existing style configuration files:
   - `.prettierrc` / `prettier.config.js`
   - `.eslintrc` / `eslint.config.js`
   - `pyproject.toml` (for Python)
   - `.editorconfig`
   - `rustfmt.toml`

2. Check for style examples in existing code

3. Follow the established patterns, even if different from personal preference

### General Style Rules

**Consistency over preference**: Match the existing codebase style, even if it differs from common conventions.

**Indentation**: Use whatever the project uses (spaces vs tabs, 2 vs 4 spaces)

**Naming**: Follow existing naming conventions:
- If the codebase uses `camelCase`, use `camelCase`
- If the codebase uses `snake_case`, use `snake_case`

**Imports**: Match existing import organization:
- Order (stdlib, external, internal)
- Grouping
- Absolute vs relative imports

**Comments**: Follow existing comment style:
- JSDoc vs plain comments
- When to comment vs when not to

### Language-Specific

**JavaScript/TypeScript**:
- Check if project uses semicolons
- Check quote style (single vs double)
- Check trailing commas preference

**Python**:
- Follow PEP 8 unless project deviates
- Check docstring style (Google, NumPy, reST)

**Go**:
- Always use gofmt style
- Follow Effective Go guidelines

### Actions

1. Run formatter before suggesting code: `npm run format`, `black .`, etc.
2. Check linter output: `npm run lint`, `ruff check .`, etc.
3. If style conflicts exist, ask which style to follow
4. Don't "fix" style in unrelated code during a focused change
