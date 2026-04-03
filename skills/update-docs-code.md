---
name: update-docs-code
description: Update all documentation inside the repository based on recent changes. Use when the user wants to refresh docs, update README, sync documentation with code changes, or maintain documentation.
---

# Update Docs Code

Analyze recent changes in the repository and update all documentation to reflect those changes.

## Instructions

1. **Identify recent changes:**
   - Run `git log --oneline -10` to see recent commits
   - Run `git diff origin/main...HEAD --stat` to see changed files (try `origin/master` if `origin/main` fails)
   - If on main/master, compare with recent commits: `git diff HEAD~5..HEAD --stat`
   - Read key changed files to understand the scope of changes

2. **Use agent to find and analyze documentation:**
   - **Launch Explore agent** to discover all documentation:
     ```
     Task: Find all documentation files in the repository and analyze their current state.

     Instructions for agent:
     - Search for README.md files (exclude node_modules, .git, vendor dirs)
     - Find all markdown files in docs/ directories
     - Look for CLAUDE.md, CONTRIBUTING.md, CHANGELOG.md, API.md
     - Find API documentation (OpenAPI/Swagger, JSDoc, godoc, etc.)
     - Read each documentation file
     - Return: List of all docs with their paths, content summaries, and last updated dates
     - Note: Focus on docs that might need updates based on recent code changes
     ```
   - Agent will comprehensively discover docs without consuming main context
   - Use subagent_type="Explore" for thorough search

3. **Analyze what needs updating:**
   - Review agent findings and documentation inventory
   - Compare with actual code to identify outdated information:
     - API endpoints that changed
     - Configuration options that were added/removed
     - New features that aren't documented
     - Changed setup/installation steps
     - Updated dependencies or requirements
     - Architecture changes
     - Deprecated features

4. **Update documentation systematically:**
   - Start with README.md (most important)
   - Update CLAUDE.md if it exists (project context for Claude)
   - Update API documentation
   - Update setup/installation guides
   - Update architecture documentation
   - Add documentation for new features
   - Remove documentation for deleted features

5. **Verify updates:**
   - Ensure all links work
   - Check that code examples are current and correct
   - Verify commands and instructions are accurate
   - Make sure formatting is consistent

6. **Summarize changes:**
   - List all documentation files that were updated
   - Highlight major changes made
   - Suggest any additional documentation that might be needed

## Important Notes

- **Use Explore agent** to comprehensively discover all documentation files
- Agent handles finding and reading docs; main context does analysis and updates
- This prevents missing documentation files that might be in unexpected locations
- Always read the documentation file before updating it
- Keep the existing documentation style and tone
- Don't remove information unless it's truly obsolete
- Add examples where helpful
- Update version numbers if applicable
- Check for broken links or outdated references
- If unsure about a change, ask the user before updating
- Consider the audience (developers, users, operators)
- Update table of contents if the documentation has one
