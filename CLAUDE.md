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
├── agents/                 # Reusable custom agents
├── commands/               # Slash commands (.md files → ~/.claude/commands/)
│   ├── gsd.md              # /gsd — Get-Shit-Done workflow
│   ├── commit.md           # /commit — smart commit messages
│   ├── explain.md          # /explain — deep code explanation
│   ├── debug.md            # /debug — systematic debugging
│   ├── docs.md             # /docs — documentation generator
│   └── architect.md        # /architect — system design assistance
├── skills/                 # Skill files (.md → ~/.claude/skills/)
│   ├── validate/           # Multi-lens change validation
│   ├── pr-simplicity-review/ # Focused removable-complexity review
│   ├── pr-pipeline/        # Pull-request lifecycle orchestration
│   ├── diagram/            # Diagram source, references, and render helpers
│   ├── perf-sweep/         # Evidence-backed performance scan
│   └── docs-drift/         # Documentation drift audit
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
├── settings/               # Global settings and personal instructions
└── statusline/             # Custom Claude Code statusline script
```

## Installation

```bash
# Install everything
./install.sh --all

# Install specific components
./install.sh --commands     # Slash commands only
./install.sh --agents       # Custom agents only
./install.sh --skills       # Skills only
./install.sh --hooks        # Hooks only
./install.sh --guardrails   # Guardrails only
./install.sh --activity-db  # activity-db CLI (for v2 daily skills)

# Install with symlinks (for active development)
./install.sh --symlink
```

Files are copied to `~/.claude/`:
- `commands/` → `~/.claude/commands/`
- `agents/` → `~/.claude/agents/`
- `skills/` → `~/.claude/skills/`
- `activity-db/` → `~/.claude/bin/activity-db/`

## Working with This Repo

### Adding a New Slash Command

1. Create `commands/<name>.md`
2. Use the pattern: markdown with a `## Trigger` section describing when to activate
3. See existing commands for examples

### Adding a New Skill

1. Create `skills/<name>/SKILL.md`
2. Add YAML frontmatter with `name` and a precise trigger description
3. Put references and helper scripts under the same skill directory

### Adding a Hook Example

1. Create a file in `hooks/examples/`
2. Document the hook's trigger, command, and purpose
3. Include a `settings.json` snippet showing how to use it

### Adding a CLAUDE.md Template

1. Create a directory in `templates/<project-type>/`
2. Add `CLAUDE.md` — the template file
3. Add `README.md` explaining when to use this template

### Updating MCP Server Configs

MCP server configs are templates that point to locally installed, reviewed
executables. Never replace them with auto-download commands. Install only
approved servers and keep permissions and credentials least-privilege.

## File Naming Conventions

- Slash commands: `kebab-case.md`
- Skills: `skills/kebab-case/SKILL.md`
- MCP servers: `kebab-case.json`
- Templates: in `templates/<project-type>/CLAUDE.md`
- All markdown header: `# Title` matching the file's purpose

## Multi-Device Workflow

This repo serves as the **sanitized, portable hub** for Claude Code configs across multiple devices. The owner maintains configs on both a work laptop and personal devices, with different concerns on each.

### Device Topology

| Device | Role | Has work-specific skills? | Sync direction |
|---|---|---|---|
| **Work laptop** | Primary authoring device | Yes (private plugins, MCP servers, and internal CLIs) | `~/.claude/` → repo via `/sync-from-global` |
| **Personal devices** | Consumers + personal-only additions | No | repo → `~/.claude/` via `install.sh` |
| **This repo** | Sanitized intersection | Never — work secrets are stripped | Hub for both directions |

### Sync Directions

```
Work ~/.claude/  ──▶  /sync-from-global  ──▶  This repo  ──▶  install.sh  ──▶  Personal ~/.claude/
     (source of truth       (sanitizes)         (hub)         (deploys)        (consumer)
      for most skills)
```

- **Work → Repo** (`/sync-from-global`): Sanitizes private plugins, internal URLs, work email, and internal integrations via shared rules plus the gitignored local overlay. Two-pass with human review before apply. Never auto-commits.
- **Repo → Personal** (`install.sh`): Copies or symlinks repo configs into `~/.claude/`. No sanitization needed — repo is already clean.
- **Personal-only configs**: Some skills/commands exist only in this repo and were never on the work laptop. These are protected by `repo_only_paths` in `sync-config.json` so sync never overwrites them.

### Key Constraints

- **Work skills are private.** They never enter this public repo. The sync strips them via `skip_paths` and `drop_line_patterns`.
- **Sync is additive on apply.** Pass 2 copies staging → repo but never deletes repo files. Files in repo but not in `~/.claude/` appear as "Repo-only" in the summary and are left untouched.
- **`repo_only_paths`** in `sync-config.json` lists paths that are personal-only and must not be overwritten by sync, even if a work version exists. This prevents losing personal configs when syncing from a work laptop that doesn't have or need them.
- **Genericize, don't just strip.** When a work skill has useful patterns, use `/genericize` to transform it into a portable version (replacing company-specific tools with generic equivalents) rather than just dropping lines.

### Setting Up a New Device

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
