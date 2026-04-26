---
name: explain
description: Provide a deep, educational explanation of code. Use when the user wants to understand how code works, why it's designed a certain way, or learn about patterns and concepts used.
---

# Code Explainer

Provide a deep, educational explanation of code at multiple levels of detail.

## Instructions

When the user runs `/explain <target>`, explain the specified code target.

**Target can be:**
- A file path (e.g., `/explain src/utils/auth.ts`)
- A function name (e.g., `/explain validateUser`)
- A specific line or range (e.g., `/explain auth.ts:42-56`)
- A concept in context (e.g., `/explain the authentication flow`)

### Process

1. **Identify the target:**
   - If file path provided, read the file
   - If function name provided, search for it using Grep or Glob
   - If line range provided, read that specific section
   - If concept provided, find relevant code files

2. **Gather context using agent (for complex targets):**
   - **Use Explore agent** when target is complex or has many dependencies:
     ```
     Task: Explore the codebase to gather context for explaining [target].

     Instructions for agent:
     - Find the target code (function/file/concept)
     - Identify all related files (imports, usages, callers, callees)
     - Read dependencies and related code
     - Trace data flow through the system
     - Find examples of usage
     - Return: Summary of target code, dependencies, related files, and usage examples
     ```
   - Agent will explore thoroughly without consuming main context
   - Use subagent_type="Explore" with thoroughness level based on complexity
   - For simple single-file explanations, skip agent and read directly

3. **Analyze the code:**
   - Review target code and agent findings (if used)
   - Understand what it does
   - Identify patterns and techniques used
   - Trace data flow and dependencies
   - Consider the broader system context

3. **Provide explanation at multiple depth levels:**

   **Overview**: What does this code do at a high level?

   **Flow**: Step-by-step execution walkthrough

   **Concepts**: Programming concepts and patterns used

   **Why**: Rationale behind design decisions

   **Context**: How it fits in the broader system

4. **Cover these aspects:**
   - **Purpose**: What problem does this solve?
   - **Inputs/Outputs**: What goes in, what comes out?
   - **Dependencies**: What does it rely on?
   - **Side Effects**: What external state does it modify?
   - **Patterns**: Design patterns or idioms used
   - **Trade-offs**: Why this approach vs alternatives?
   - **Gotchas**: Non-obvious behaviors or edge cases

5. **Format the explanation:**

```markdown
## [File/Function Name]

### Purpose
[1-2 sentence summary of what this code does and why it exists]

### How It Works
[Step-by-step explanation with code references. Include line numbers when relevant.]

1. [First step with explanation]
2. [Second step with explanation]
3. [etc.]

### Key Concepts
- **[Concept/Pattern Name]**: [Brief explanation of the pattern/technique used]
- **[Another Concept]**: [Why it's used here]

### Data Flow
```
[Input] -> [Processing Steps] -> [Output]
```
[Explain how data flows through the code]

### Dependencies
- **[dependency name]**: [Why it's needed and how it's used]
- **[another dependency]**: [Purpose in this code]

### Example Usage
```[language]
[Code example showing typical usage of this function/module]
```

### Related Code
- [other files/functions that interact with this]
- [where this is called from]
- [what this calls]

### Gotchas & Edge Cases
- [Non-obvious behavior #1]
- [Edge case #2]
- [Common pitfall #3]
```

6. **Adjust depth based on complexity:**
   - Simple utility function: Brief explanation with example
   - Complex algorithm: Detailed step-by-step walkthrough
   - System component: Include architecture context and interactions

## Important Notes

- **Use Explore agent** for complex code with many dependencies to avoid context overload
- Simple targets (single functions, small files) can be explained directly without agent
- Agent handles exploration; main context does the actual explanation
- Always read the code before explaining it
- Use code references with line numbers (e.g., `auth.ts:42`)
- Explain WHY, not just WHAT the code does
- Use analogies when helpful for complex concepts
- Include visual representations (ASCII diagrams) for data flow when useful
- Point out best practices and anti-patterns
- Mention language-specific idioms and features
- Consider the audience's likely knowledge level
- If code has issues or could be improved, mention it
- Link to related documentation or resources when relevant
