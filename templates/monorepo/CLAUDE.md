# Project: [Monorepo Name]

## Overview

[Brief description of what this monorepo contains]

## Repository Structure

```
.
├── apps/                     # Applications
│   ├── web/                  # Web frontend
│   ├── api/                  # Backend API
│   ├── mobile/               # Mobile app
│   └── admin/                # Admin dashboard
├── packages/                 # Shared packages
│   ├── ui/                   # Shared UI components
│   ├── config/               # Shared configurations
│   ├── utils/                # Shared utilities
│   ├── types/                # Shared TypeScript types
│   └── database/             # Database client and models
├── tools/                    # Build and development tools
├── docs/                     # Documentation
├── turbo.json                # Turborepo configuration
├── pnpm-workspace.yaml       # pnpm workspace config
└── package.json              # Root package.json
```

## Tech Stack

- **Monorepo Tool**: Turborepo / Nx / Lerna
- **Package Manager**: pnpm (recommended for monorepos)
- **Languages**: TypeScript
- **CI/CD**: GitHub Actions

## Workspace Packages

| Package | Description | Port |
|---------|-------------|------|
| `apps/web` | Customer-facing web app | 3000 |
| `apps/api` | REST/GraphQL API | 4000 |
| `apps/admin` | Admin dashboard | 3001 |
| `packages/ui` | Shared React components | - |
| `packages/utils` | Shared utility functions | - |
| `packages/types` | Shared TypeScript types | - |

## Development Commands

```bash
# Install all dependencies
pnpm install

# Run all apps in development
pnpm dev

# Run specific app
pnpm dev --filter=web
pnpm dev --filter=api

# Build all packages
pnpm build

# Build specific package
pnpm build --filter=@repo/ui

# Run tests across all packages
pnpm test

# Run tests for specific package
pnpm test --filter=api

# Lint all packages
pnpm lint

# Type check all packages
pnpm typecheck

# Add dependency to specific package
pnpm add lodash --filter=api

# Add shared dependency to workspace
pnpm add -D typescript -w
```

## Package Dependencies

### Internal Dependencies
```json
// apps/web/package.json
{
  "dependencies": {
    "@repo/ui": "workspace:*",
    "@repo/utils": "workspace:*",
    "@repo/types": "workspace:*"
  }
}
```

### Adding New Package
1. Create directory in `packages/` or `apps/`
2. Add `package.json` with correct name (`@repo/package-name`)
3. Configure `tsconfig.json` to extend root config
4. Add to `turbo.json` pipeline if needed

## Turborepo Configuration

```json
// turbo.json
{
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "test": {
      "dependsOn": ["build"]
    }
  }
}
```

## Coding Conventions

### Package Naming
- Apps: Plain names (`web`, `api`)
- Packages: Scoped (`@repo/ui`, `@repo/utils`)

### Import Conventions
```typescript
// Use package names for cross-package imports
import { Button } from '@repo/ui';
import { formatDate } from '@repo/utils';
import type { User } from '@repo/types';
```

### Shared Configuration
- TypeScript config extends from root
- ESLint config extends from `@repo/config`
- Tailwind config extends from shared preset

## Environment Variables

Each app has its own `.env` file:
- `apps/web/.env` - Frontend environment
- `apps/api/.env` - Backend environment

Root `.env` for shared variables across apps.

## CI/CD Considerations

- Use Turborepo remote caching for faster CI
- Only build/test affected packages on PRs
- Deploy apps independently

## Sensitive Areas

- `packages/database/` - Database schema and migrations
- `apps/api/src/auth/` - Authentication logic
- Root `package.json` - Workspace configuration

## Common Issues

1. **Dependency conflicts**: Use `pnpm why` to debug
2. **Build order**: Check `dependsOn` in turbo.json
3. **Type errors across packages**: Ensure `composite: true` in tsconfig
4. **Hot reload not working**: Check package.json `exports` field
