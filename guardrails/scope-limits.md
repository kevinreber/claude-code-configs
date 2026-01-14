# Guardrail: Scope Limits

## Purpose
Restrict modifications to certain files and directories to prevent accidental changes to critical areas.

## Protected Areas

### Configuration Files (Read-Only Unless Explicitly Requested)
- `package.json` - dependency changes need careful review
- `tsconfig.json` - compiler settings affect entire project
- `*.config.js` - build and tool configurations
- `docker-compose.yml` - infrastructure definitions
- `Dockerfile` - container definitions
- CI/CD files (`.github/workflows/`, `.gitlab-ci.yml`)

### Infrastructure (Never Modify Without Explicit Request)
- Terraform files (`*.tf`)
- Kubernetes manifests (`*.yaml` in k8s directories)
- CloudFormation templates
- Ansible playbooks

### Database (Extreme Caution)
- Migration files - never edit existing migrations
- Schema files - coordinate with team
- Seed data - may affect production

### Generated Files (Never Edit Directly)
- `package-lock.json` / `yarn.lock` / `pnpm-lock.yaml`
- Generated type definitions
- Compiled output (`dist/`, `build/`, `out/`)
- API client code from OpenAPI specs

### Vendor/Dependencies
- `node_modules/`
- `vendor/`
- `venv/` / `.venv/`

## Rules

1. **Ask before modifying protected files** unless the change was explicitly requested

2. **Never modify generated files** - modify the source instead

3. **Database migrations**:
   - Never edit existing migration files
   - Always create new migrations for changes
   - Test migrations on sample data first

4. **Config changes**:
   - Explain the impact before making changes
   - Suggest testing in isolated environment first

5. **CI/CD changes**:
   - Small, incremental changes
   - Explain what each change does

## Exceptions

These rules can be bypassed when:
- User explicitly requests the change
- The file is clearly in scope for the current task
- It's a new file being created (not modifying existing)
