# CLAUDE.md Templates

Project-specific instruction files that tell Claude how to work with your codebase.

## What is CLAUDE.md?

`CLAUDE.md` is a special file that Claude Code reads at the start of each session. It provides:

- Project context and architecture overview
- Coding standards and conventions
- Important commands and workflows
- Warnings about sensitive areas
- Links to documentation

## How to Use

1. Choose a template that matches your project type
2. Copy it to your project root as `CLAUDE.md`
3. Customize the sections to match your project
4. Commit it to your repository

```bash
cp templates/typescript-node/CLAUDE.md /path/to/your/project/CLAUDE.md
```

## Template Structure

Each template includes:

- **Project Overview**: What the project does
- **Tech Stack**: Languages, frameworks, key libraries
- **Architecture**: How the code is organized
- **Development Workflow**: How to build, test, run
- **Conventions**: Coding standards and patterns
- **Important Paths**: Key files and directories
- **Gotchas**: Things to be careful about

## Composing Templates

You can combine templates for complex projects:

```bash
# Start with base template
cat templates/typescript-node/CLAUDE.md > CLAUDE.md

# Add guardrails
cat guardrails/no-secrets.md >> CLAUDE.md

# Add project-specific section
cat << 'EOF' >> CLAUDE.md

## Project-Specific Notes

[Your custom instructions here]
EOF
```

## Best Practices

1. **Keep it focused** - Include only what Claude needs to know
2. **Update regularly** - Keep it in sync with your codebase
3. **Be specific** - Concrete examples are better than abstract rules
4. **Include examples** - Show preferred patterns with code
5. **Document gotchas** - Warn about non-obvious behaviors
