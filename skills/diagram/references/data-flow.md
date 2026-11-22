# Data-flow diagrams

Use Graphviz to show where data originates, how it changes, where it waits,
and where it is stored or consumed.

## Conventions

| Element | Shape | Fill |
|---|---|---|
| Source or sink | ellipse | `#FEE2E2` |
| Transformation | rounded box | `#DBEAFE` |
| Data store | cylinder | `#DCFCE7` |
| Queue or stream | parallelogram | `#FFEDD5` |
| Offline dataset | cylinder | `#FEF3C7` |

## Guidance

- Label edges with actual data, not vague verbs such as "send."
- Show validation or rejection paths, durable boundaries, and batch versus
  streaming movement.
- Do not mix control-flow decisions into a data-flow diagram unless they
  change the data path.
- Add volume, freshness, or ownership only when supported and relevant.

Look for request payloads, serializers, schema validation, database
operations, file I/O, queue producers or consumers, and mapping functions.
