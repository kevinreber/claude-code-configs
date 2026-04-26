# Claude Code Configurations Library

A portable collection of reusable Claude Code configurations for consistent AI-assisted development across devices and projects.

## Structure

```
.
├── commands/           # Slash commands (.md files)
├── skills/             # Skills for specialized tasks
├── hooks/              # Hook configurations (pre/post tool execution)
├── templates/          # CLAUDE.md templates for different project types
├── guardrails/         # Safety and constraint configurations
├── mcp-servers/        # MCP server configurations
├── statusline/         # Custom statusline script and settings
└── install.sh          # Installation script
```

## Quick Start

### Install Everything
```bash
./install.sh --all
```

### Install Specific Components
```bash
./install.sh --commands      # Just slash commands
./install.sh --skills        # Just skills
./install.sh --hooks         # Just hooks
./install.sh --guardrails    # Just guardrails
```

### Manual Installation
Copy desired configurations to your `~/.claude/` directory:
```bash
cp -r commands/* ~/.claude/commands/
cp -r skills/* ~/.claude/skills/
```

## Components

### Slash Commands (`/commands`)
Custom commands invoked with `/command-name` in Claude Code:
- `/review` - Code review with security focus
- `/test-plan` - Generate comprehensive test plans
- `/refactor` - Suggest refactoring improvements
- `/explain` - Deep code explanation
- `/commit` - Smart commit message generation
- `/pr` - Pull request description generator
- `/debug` - Systematic debugging assistant
- `/docs` - Documentation generator
- `/perf` - Performance analysis

### Skills
Specialized capabilities for domain-specific tasks:

**Language skills** (global reference guides for idiomatic code):
- `rust` - Error handling, async/Tokio, clippy, ownership patterns
- `typescript` - Strict mode, type utilities, async patterns, tooling
- `python` - Type hints, uv/ruff, async, pytest, dataclasses, FastAPI
- `react` - Hooks patterns, component design, state management, performance
- `go` - Error handling, interfaces, concurrency, context, table-driven tests
- `bash` - Safe scripting, quoting, traps, idempotency, portability

**Workflow skills**:
- `code-review` - Thorough code review with checklist
- `security-audit` - Security vulnerability scanning
- `api-design` - REST/GraphQL API design assistance
- `database` - Schema design and query optimization
- `testing` - Test writing and coverage analysis
- `git-workflow` - Branching strategies and git operations
- `gsd-methodology` - Get-Shit-Done workflow methodology

### Hooks
Event-driven automations:
- `pre-commit-lint` - Run linters before commits
- `post-edit-format` - Auto-format after edits
- `notification` - Desktop notifications on completion

### Templates
Project-specific CLAUDE.md files:
- `typescript-node` - Node.js/TypeScript projects
- `python-fastapi` - Python FastAPI projects
- `react-frontend` - React/Next.js frontends
- `rust-cli` - Rust CLI applications
- `go-service` - Go microservices
- `monorepo` - Monorepo configurations

### Guardrails
Safety constraints and boundaries:
- `no-secrets` - Prevent committing sensitive data
- `style-enforcement` - Enforce coding standards
- `scope-limits` - Restrict file/directory access
- `confirmation-required` - Require confirmation for destructive ops

### MCP Servers
Model Context Protocol server configurations:
- `github` - GitHub integration
- `filesystem` - Extended file operations
- `database` - Database connections
- `custom` - Template for custom servers

### Statusline
Custom statusline script that displays session info in the Claude Code terminal:
```
👤 kreber[a1b2c3d4] | 🤖 Claude Sonnet 4.6 | 📊 [====                ] 21% | 42k/200k | 🪙 $0.13 | 🌿 main | ✏️  +12 -3 | 📁 my-project
```
See [`statusline/README.md`](statusline/README.md) for installation and customization details.

## Usage Examples

### Using a Slash Command
```
/review src/auth/login.ts
```

### Combining Components
Create a project-specific setup by combining templates:
```bash
# For a TypeScript API project
cat templates/typescript-node/CLAUDE.md > ./CLAUDE.md
cat guardrails/no-secrets.md >> ./CLAUDE.md
```

## Customization

Each component is designed to be:
1. **Standalone** - Works independently
2. **Composable** - Combine multiple configs
3. **Customizable** - Edit to fit your needs

## Contributing

Add your own configurations:
1. Create the config file in the appropriate directory
2. Follow the naming convention: `kebab-case.md`
3. Include a header comment explaining the purpose

## Multi-device workflow

This repo is designed to be the **shared, sanitized superset** of Claude Code configs across multiple devices (e.g., a work laptop and a personal laptop). Two scripts handle the bidirectional flow:

```
       ┌────────────────────────┐
       │  ~/.claude/  (device)  │
       └──────┬──────────▲──────┘
              │          │
   /sync-from-global   ./install.sh
   (sanitize → repo)   (repo → ~/.claude/)
              │          │
              ▼          │
       ┌────────────────────────┐
       │   claude-code-configs  │
       │   (shared via git)     │
       └────────────────────────┘
```

### Sync direction 1: device → repo (`/sync-from-global`)

Pulls your global `~/.claude/` configs into the repo, stripping work-specific content (LinkedIn plugins, Captain MCP, work email, internal URLs). Two-pass with diff review — see [`skills/sync-from-global/SKILL.md`](skills/sync-from-global/SKILL.md).

**Important: this is additive, never destructive.**
- Pass 2 only **copies** staged files into the repo. It does not delete.
- Files that exist in the repo but not in this device's `~/.claude/` are listed under "Repo-only" in the pass 1 summary and are **left untouched** on apply.
- This means each device contributes its slice of generic skills to the union; nothing gets removed when another device syncs.

### Sync direction 2: repo → device (`install.sh`)

Pushes the repo's configs into a device's `~/.claude/`:

```bash
# On a new device
git clone <this-repo> ~/claude-code-configs
cd ~/claude-code-configs && ./install.sh --all

# Or use symlinks so `git pull` instantly updates ~/.claude/ — recommended
./install.sh --symlink --all
```

### Recommended workflow for keeping devices in sync

1. **Pick a primary "writer" device** — the one where new configs evolve fastest. For most people this is the work laptop.
2. **On the writer device**: when you've added/refined skills globally, run `/sync-from-global` → review the diff → commit → push.
3. **On reader devices**: install with `./install.sh --symlink --all`. After that, `git pull` is enough — your `~/.claude/` updates instantly via symlinks.
4. **For per-device customizations**: use `*.local.md` and `*.local.json` filenames — these are gitignored, so they stay on the device that needs them.
5. **Conflict prevention**: avoid editing `~/.claude/<file>` directly on a "reader" device. Edit the repo file instead, push, then pull on the writer.

### Cadence

`/sync-from-global` should run when there's drift to capture, not on a fixed schedule:

- **Event-based (primary)**: after you install a new plugin globally, get a plugin update that adds new skills, or notice you've been editing skills directly in `~/.claude/` instead of in the repo.
- **Periodic safety net (every few weeks)**: even if you don't think anything's drifted, it's worth a pass to catch things you forgot about — plugin auto-updates, skills you tweaked in passing. Pass 1 is cheap (it stages and shows a diff; if nothing meaningful changed, you skip pass 2). Treat it like `git fetch` for your global state.
- **Don't over-run it**: weekly is fine, daily is overkill. The two-pass review takes ~5 minutes once you know the workflow; running it constantly produces more noise than signal.

If `/sync-from-global` consistently produces no meaningful changes, that's a signal you're doing the right thing — editing the repo first and letting `install.sh` push out, instead of editing `~/.claude/` directly.

### What about putting `~/.claude/` itself under git (Obsidian-vault style)?

**Not recommended.** Unlike an Obsidian vault (mostly stable text content), `~/.claude/` is a runtime data directory: `activity.db`, `history.jsonl`, `sessions/`, `paste-cache/`, `statsig/`, `projects/` all change constantly and would create endless merge conflicts. Plus, work-device `~/.claude/` contains internal plugins and settings that shouldn't go to a personal/public remote. The two-script flow above keeps the sanitized, sharable parts in git and the runtime/work-specific parts on each device where they belong.

## License

MIT - Use freely across personal and professional projects.
