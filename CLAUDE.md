# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**claude-code-configs** is a portable library of reusable Claude Code configurations for consistent AI-assisted development across devices and projects. It provides slash commands, skills, hooks, guardrails, MCP server configs, CLAUDE.md templates, and a statusline script — all installable via a single script.

This is a **configuration and documentation repo**, not a software project. There is no build step. The "output" is Claude Code configured the way you want it.

## Repository Structure

```
claude-code-configs/
├── install.sh              # Main installer — copies configs to ~/.claude/
├── README.md               # User-facing documentation
├── commands/               # Slash commands (.md files → ~/.claude/commands/)
│   ├── gsd.md              # /gsd — Get-Shit-Done workflow
│   ├── commit.md           # /commit — smart commit messages
│   ├── explain.md          # /explain — deep code explanation
│   ├── debug.md            # /debug — systematic debugging
│   ├── docs.md             # /docs — documentation generator
│   └── architect.md        # /architect — system design assistance
├── skills/                 # Skill files (.md → ~/.claude/skills/)
│   ├── git-workflow.md     # Git branching and operations
│   ├── gsd-methodology.md  # GSD workflow methodology
│   ├── code-review.md      # Code review checklist
│   ├── testing.md          # Test writing and coverage
│   ├── security-audit.md   # Security vulnerability scanning
│   ├── api-design.md       # REST/GraphQL API design
│   └── database.md         # Schema design and query optimization
├── hooks/                  # Hook configurations and examples
│   ├── README.md
│   └── examples/           # Example hook patterns
├── templates/              # CLAUDE.md templates by project type
│   ├── README.md
│   ├── typescript-node/    # Node.js/TypeScript projects
│   ├── python-fastapi/     # Python FastAPI projects
│   ├── react-frontend/     # React/Next.js frontends
│   ├── rust-cli/           # Rust CLI applications
│   ├── go-service/         # Go microservices
│   └── monorepo/           # Monorepo configurations
├── guardrails/             # Safety constraints for settings.json
│   ├── no-secrets.md
│   ├── scope-limits.md
│   ├── confirmation-required.md
│   └── ...
├── activity-db/            # SQLite/Turso activity storage CLI
│   ├── README.md           # Setup guide (Turso, tokens, multi-device)
│   ├── main.py             # CLI source
│   └── pyproject.toml      # Python dependencies
├── mcp-servers/            # MCP server JSON configs
│   ├── github.json
│   ├── filesystem.json
│   ├── sqlite.json
│   └── ...
└── statusline/             # Custom Claude Code statusline script
    └── README.md
```

## Installation

```bash
# Install everything
./install.sh --all

# Install specific components
./install.sh --commands     # Slash commands only
./install.sh --skills       # Skills only
./install.sh --hooks        # Hooks only
./install.sh --guardrails   # Guardrails only
./install.sh --activity-db  # activity-db CLI (for v2 daily skills)

# Install with symlinks (for active development)
./install.sh --symlink
```

Files are copied to `~/.claude/`:
- `commands/` → `~/.claude/commands/`
- `skills/` → `~/.claude/skills/`
- `activity-db/` → `~/.claude/bin/activity-db/`

## Working with This Repo

### Adding a New Slash Command

1. Create `commands/<name>.md`
2. Use the pattern: markdown with a `## Trigger` section describing when to activate
3. See existing commands for examples

### Adding a New Skill

1. Create `skills/<name>.md`
2. Skills are markdown files with instructions for specialized tasks
3. Name in `kebab-case`

### Adding a Hook Example

1. Create a file in `hooks/examples/`
2. Document the hook's trigger, command, and purpose
3. Include a `settings.json` snippet showing how to use it

### Adding a CLAUDE.md Template

1. Create a directory in `templates/<project-type>/`
2. Add `CLAUDE.md` — the template file
3. Add `README.md` explaining when to use this template

### Updating MCP Server Configs

MCP server configs in `mcp-servers/` are JSON files for `~/.claude/claude_desktop_config.json`. Each file documents the server configuration for a specific tool or service.

## File Naming Conventions

- Slash commands and skills: `kebab-case.md`
- MCP servers: `kebab-case.json`
- Templates: in `templates/<project-type>/CLAUDE.md`
- All markdown header: `# Title` matching the file's purpose

## Syncing Across Devices

```bash
# Clone on new device
git clone git@github.com-kevinreber:kevinreber/claude-code-configs.git ~/claude-configs
cd ~/claude-configs && ./install.sh --all
```

Or with symlinks so edits are instantly reflected:
```bash
./install.sh --symlink
```

## Automated Hooks

Claude Code hooks (`.claude/settings.json`) automatically:
- Check markdown formatting after editing `.md` files
