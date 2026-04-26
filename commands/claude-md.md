# /claude-md
Create or update this repo's Claude project memory at .claude/CLAUDE.md so an AI assistant can work effectively.

## Goals
- Analyze the repository structure and tech stack.
- Document development workflows (setup, run, test, lint, build, deploy).
- Capture key conventions (naming, code style, architecture rules, patterns).
- Add a “For AI assistants” section with safe, deterministic workflow guidance.
- Keep it accurate to the current repo state.

## Where to write (IMPORTANT)
- Always use `.claude/CLAUDE.md` as the canonical project memory.
- If `.claude/CLAUDE.md` exists, update it.
- If it does not exist, create the `.claude/` directory and write it there.
- Do NOT write to `./CLAUDE.md`.

This convention makes all Claude-related configuration discoverable in one place:
.claude/
  ├─ CLAUDE.md        ← project memory
  ├─ commands/        ← repo-specific slash commands
  └─ skills/          ← repo-specific skills (optional)

## Required repo scan (do this before writing)
1. Identify language/tooling by checking:
   - package.json / pnpm-lock.yaml / yarn.lock
   - pyproject.toml / requirements*.txt
   - go.mod, Cargo.toml, Gemfile, pom.xml, etc.
2. Determine app type:
   - web app, API, CLI, monorepo, library, etc.
3. Map structure:
   - top-level folders and what they contain
   - major services/packages
4. Find "how to run":
   - scripts in package.json
   - Makefile targets
   - README.md / docs/ dev instructions
5. Find tests + lint:
   - test frameworks, commands, CI config (.github/workflows, etc.)
6. Find conventions:
   - formatting tools (prettier, black, gofmt)
   - type checking (tsc, mypy)
   - architecture patterns (controllers/services, routes, workflows, etc.)
7. Note sharp edges:
   - env vars, secrets handling, migrations, docker-compose, local deps, etc.

## Output format for .claude/CLAUDE.md
Write a clean, skimmable document with these sections:

1. Project Summary
2. Repository Map (tree-level overview)
3. Local Development Workflow
4. Testing / Linting / Typechecking
5. Common Tasks (copy-paste commands)
6. Architecture & Data Flow
7. Key Conventions
8. For AI Assistants
9. Troubleshooting
10. Change Log

## AI assistant rules (must include)
- Prefer deterministic tools (linters, formatters, tests) over guessing.
- Never edit generated files unless explicitly instructed.
- Minimize diff size; keep changes focused.
- Inspect source-of-truth files (package.json, Makefile, CI configs).
- Never invent scripts, commands, endpoints, or config.
- Follow existing patterns and naming conventions.

## Optional arguments
If user passes $ARGUMENTS, treat them as scope hints:
- "frontend only"
- "api only"
- "monorepo overview"
- "focus on testing conventions"

Now perform the repo scan and create or update `.claude/CLAUDE.md`.
