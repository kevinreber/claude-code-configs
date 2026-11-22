---
name: diagram
description: Create, edit, render, or improve engineering diagrams, including architecture, sequence, flowchart, data-flow, and state-machine diagrams from code or a design description.
---

# Diagram

Create clear engineering diagrams with editable source and rendered output.
Use Graphviz for relationship-heavy diagrams and Mermaid for temporal or
compact process diagrams.

## Safety

- Use only tools already installed on the machine.
- Never download packages through `npx`, `curl`, or another network command as
  part of rendering.
- If a renderer is missing, run `scripts/check-tools.sh`, report its setup
  guidance, and wait for explicit approval before installing anything.
- Keep the workflow generic and independent of private services.

## Workflow

1. Determine whether the request creates a new diagram or edits existing
   `.dot` or `.mmd` source.
2. Select the diagram type:

   | Diagram | Default engine | Best for |
   |---|---|---|
   | Architecture | Graphviz | Components, boundaries, dependencies |
   | Sequence | Mermaid | Ordered requests, responses, async messages |
   | Flowchart | Mermaid under 15 nodes; otherwise Graphviz | Decisions and process steps |
   | Data flow | Graphviz | Sources, transformations, stores, sinks |
   | State machine | Mermaid | Lifecycle states and transitions |

3. For code-driven diagrams, inspect only relevant entry points, interfaces,
   calls, and configuration. Distinguish confirmed behavior from inference.
4. Read the matching file under `references/`.
5. Save editable source to `docs/diagrams/<descriptive-name>.dot` or `.mmd`
   unless the user gives another path.
6. Use the installed skill scripts:

   ```bash
   SKILL_DIR="${CLAUDE_PLUGIN_ROOT:+$CLAUDE_PLUGIN_ROOT/skills/diagram}"
   SKILL_DIR="${SKILL_DIR:-$HOME/.claude/skills/diagram}"
   "$SKILL_DIR/scripts/check-tools.sh" graphviz
   "$SKILL_DIR/scripts/render.sh" <source> png --open
   ```

7. Inspect the render. Fix clipped text, crossings, inconsistent spacing,
   invalid syntax, and unreadable labels before reporting completion.

## Design system

- Prefer a white background, dark slate text (`#1E293B`), subtle borders
  (`#CBD5E1`), and restrained pastel fills.
- Use semantic color consistently:

  | Meaning | Fill |
  |---|---|
  | Primary service or process | `#DBEAFE` |
  | Data store or successful outcome | `#DCFCE7` |
  | Batch job or decision | `#EDE9FE` |
  | Queue or asynchronous boundary | `#FFEDD5` |
  | Note or offline dataset | `#FEF3C7` |
  | Error, risk, or human actor | `#FEE2E2` |
  | External or out-of-scope system | `#E5E7EB` |

- Do not rely on color alone. Pair colors with labels and distinct shapes.
- Prefer one primary reading direction.
- Keep the main diagram to roughly 5-12 nodes; split dense systems.
- Label edges when the protocol, event, command, or data matters.
- Use dashed edges for optional, asynchronous, inferred, or out-of-scope
  relationships and state which meaning applies.

## Editing rules

- Preserve the existing engine, palette, and layout unless asked to redesign.
- Make the smallest source change that communicates the new behavior.
- Re-render after every edit; source-only validation is insufficient.
- Never overwrite a user-authored diagram without reading and integrating it.
