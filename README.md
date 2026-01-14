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
- `code-review` - Thorough code review with checklist
- `security-audit` - Security vulnerability scanning
- `api-design` - REST/GraphQL API design assistance
- `database` - Schema design and query optimization
- `testing` - Test writing and coverage analysis

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

## Syncing Across Devices

### Using Git
```bash
# On new device
git clone <this-repo> ~/claude-configs
cd ~/claude-configs && ./install.sh --all
```

### Using Symlinks (recommended for active development)
```bash
./install.sh --symlink
```

## License

MIT - Use freely across personal and professional projects.
