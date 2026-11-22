---
name: find-skills
description: Search for an installable agent skill only when the user explicitly asks about skills, plugins, or extending Claude. Do not trigger for ordinary how-to questions.
---

# Find Skills

This skill helps you discover and install skills from the open agent skills ecosystem.

## When to Use This Skill

Use this skill only when the user:

- Says "find a skill for X" or "is there a skill for X"
- Explicitly asks to search a skill registry or marketplace
- Asks how to extend Claude with a reusable skill

Do not trigger for ordinary "how do I do X?" requests. Answer those directly.

## How to Help Users Find Skills

### Step 1: Understand What They Need

When a user asks for help with something, identify:

1. The domain (e.g., React, testing, design, deployment)
2. The specific task (e.g., writing tests, creating animations, reviewing PRs)
3. Whether this is a common enough task that a skill likely exists

### Step 2: Search without installing

Search an approved registry using built-in web tools. Do not invoke a package
runner merely to search; it may download and execute code.

### Step 3: Verify before recommending

**Do not recommend a skill based solely on search results.** Always verify:

1. The source is approved or explicitly trusted by the user.
2. The repository, publisher, and requested version are identifiable.
3. The skill instructions and any bundled hooks or scripts have been reviewed.
4. The package does not require unexpected network, credential, filesystem, or
   execution permissions.

Install count and stars are weak signals; they do not establish safety.

### Step 4: Present options

When you find relevant skills, present them to the user with:

1. The skill name and what it does
2. The install count and source
3. The reviewed source and version
4. The approved installation instructions, if any

Example response:

```
I found a skill that might help! The "react-best-practices" skill provides
React and Next.js performance optimization guidelines from Vercel Engineering.
(185K installs)

Source: <reviewed repository and version>
Install: <approved instructions, or "manual review required">
```

### Step 5: Install only after approval

Never install an unreviewed third-party skill. After reviewing the exact source
and receiving explicit user approval, follow the approved source's documented
installation process. Do not use flags that bypass review or confirmation.

## Common Skill Categories

When searching, consider these common categories:

| Category        | Example Queries                          |
| --------------- | ---------------------------------------- |
| Web Development | react, nextjs, typescript, css, tailwind |
| Testing         | testing, jest, playwright, e2e           |
| DevOps          | deploy, docker, kubernetes, ci-cd        |
| Documentation   | docs, readme, changelog, api-docs        |
| Code Quality    | review, lint, refactor, best-practices   |
| Design          | ui, ux, design-system, accessibility     |
| Productivity    | workflow, automation, git                |

## Tips for Effective Searches

1. **Use specific keywords**: "react testing" is better than just "testing"
2. **Try alternative terms**: If "deploy" doesn't work, try "deployment" or "ci-cd"
3. **Check popular sources**: Many skills come from `vercel-labs/agent-skills` or `ComposioHQ/awesome-claude-skills`

## When No Skills Are Found

If no relevant skills exist:

1. Acknowledge that no existing skill was found
2. Offer to help with the task directly using your general capabilities
3. Suggest creating a local skill manually or with an already approved tool

Example:

```
I searched for skills related to "xyz" but didn't find any matches.
I can still help you with this task directly! Would you like me to proceed?

If this is something you do often, you could create a local skill under
`~/.claude/skills/<name>/SKILL.md`.
```
