# Guardrails

Safety constraints and boundaries to add to your Claude Code configuration.

## What Are Guardrails?

Guardrails are instructions that:
- Prevent common mistakes
- Enforce coding standards
- Protect sensitive areas
- Require confirmation for dangerous operations

## How to Use

Append guardrails to your `CLAUDE.md` file:

```bash
cat guardrails/no-secrets.md >> CLAUDE.md
```

Or include multiple:

```bash
cat guardrails/no-secrets.md guardrails/style-enforcement.md >> CLAUDE.md
```

## Available Guardrails

| Guardrail | Purpose |
|-----------|---------|
| `no-secrets.md` | Prevent committing secrets and credentials |
| `style-enforcement.md` | Enforce project coding standards |
| `scope-limits.md` | Restrict access to certain files/directories |
| `confirmation-required.md` | Require confirmation for destructive operations |
| `testing-required.md` | Ensure tests are written for new code |
| `documentation-required.md` | Ensure documentation for public APIs |
| `security-first.md` | Security-focused development practices |

## Customization

Each guardrail is a markdown file with instructions. Customize by:

1. Copying the guardrail file
2. Editing the rules to match your needs
3. Adding project-specific exceptions

## Combining Guardrails

Create a combined guardrails file for your project:

```bash
# Create combined guardrails
cat << 'EOF' > .claude/guardrails.md
# Project Guardrails

EOF

cat guardrails/no-secrets.md >> .claude/guardrails.md
cat guardrails/security-first.md >> .claude/guardrails.md
```

Then reference in CLAUDE.md:

```markdown
See also: .claude/guardrails.md for security constraints.
```
