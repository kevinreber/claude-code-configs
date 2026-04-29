---
name: genericize
description: Transform a work-specific or company-specific skill/config into a generic, portable version. Replaces proprietary tools, internal URLs, and company references with generic equivalents while preserving the useful patterns and structure. Use when porting a work skill to the public config repo.
---

# Genericize Skill

Transform a work-specific Claude Code skill, command, or config file into a generic, portable version suitable for the public `claude-code-configs` repo.

Unlike the sync's line-dropping approach (which can mangle files), this skill **understands intent** and replaces company-specific elements with useful generic equivalents.

## When to invoke

- "genericize this skill"
- "make this portable"
- "turn this work skill into something I can use anywhere"
- "I have a work skill that does X, can we make a generic version?"
- When the user pastes or references a work-specific skill they want to add to this repo
- After `/sync-from-global` flags files in manual review — if the redacted version is too mangled, genericize the original instead

## Input

The user provides one of:
1. A file path to a work-specific skill (e.g., `~/.claude/skills/company-deploy.md`)
2. Pasted content of a work-specific skill
3. A description of what a work skill does (for building from scratch)

## Steps

### Step 1 — Analyze the source

Read the input and identify:
- **Core pattern**: What does this skill actually do, abstractly? (e.g., "deploys a service" not "deploys a LinkedIn service via Mint")
- **Company-specific elements**: Internal tools, URLs, team names, proprietary CLIs, internal APIs
- **Generic equivalents**: What standard/open-source tools serve the same purpose?
- **Reusable structure**: The workflow, checklist, decision tree, or prompt pattern that's valuable regardless of company

### Step 2 — Build a mapping table

Present the user with a mapping of what will be replaced:

| Work-specific | Generic replacement | Notes |
|---|---|---|
| `mint deploy` | Standard deploy CLI (e.g., `kubectl`, `docker`, provider CLI) | Preserves deploy workflow |
| `go/internal-dashboard` | `<your-monitoring-dashboard>` | Placeholder for user to fill |
| `JIRA-PROJECT-123` | Issue tracker reference | Generic pattern |
| LinkedIn-specific API patterns | REST/GraphQL best practices | Generalized |

Ask the user to confirm or adjust the mappings before proceeding.

### Step 3 — Transform

Create the generic version following these principles:

1. **Replace, don't remove.** A line like "Check the Mint build status" becomes "Check the build/deploy status" — not a blank line or a dropped section.
2. **Preserve structure.** Keep the same sections, checklists, and flow. The skill's value is often in its *structure* (what to check, in what order) not the specific tools.
3. **Use placeholder patterns** for things that vary per user/company:
   - `<your-deploy-tool>` — for proprietary CLIs
   - `<your-monitoring-url>` — for internal dashboards
   - `<your-ci-system>` — for CI/CD references
   - `<your-issue-tracker>` — for project management tools
4. **Add a "Customize" section** at the bottom listing all placeholders the user should fill in for their environment.
5. **Generalize domain knowledge.** If the work skill encodes expertise about "how LinkedIn handles X," extract the general principle: "how large-scale services handle X."
6. **Keep the frontmatter format** consistent with this repo's conventions:
   ```yaml
   ---
   name: kebab-case-name
   description: One-line description of what the skill does generically.
   ---
   ```

### Step 4 — Review with user

Show the full generic version. Ask:
- "Does this capture the useful patterns from the original?"
- "Anything company-specific I missed?"
- "Should any placeholders be filled in with defaults for your personal setup?"

### Step 5 — Write to repo

Save to `skills/<name>/SKILL.md` in the repo. If the skill should be protected from future sync overwrites (because it was hand-crafted, not synced), suggest adding it to `repo_only_paths` in `sync/sync-config.json`.

## Important constraints

- **Never include** the original work-specific content in the output file or in git history. The generic version should stand on its own.
- **Never guess** at internal tool names if the user hasn't provided them — ask.
- **Bias toward useful defaults** over empty placeholders. If the generic equivalent is obvious (e.g., `git` instead of a proprietary VCS wrapper), just use it directly.
- **Preserve the "why"** — if the original skill has comments explaining *why* a step matters (e.g., "check this because deploys can silently fail"), keep that wisdom even if the specific tool changes.

## Customize section template

Add this at the end of every genericized skill:

```markdown
## Customize for your environment

Replace these placeholders with your actual tools and URLs:

| Placeholder | Description | Example |
|---|---|---|
| `<your-deploy-tool>` | Your deployment CLI or platform | `kubectl`, `fly`, `vercel` |
| ... | ... | ... |
```
