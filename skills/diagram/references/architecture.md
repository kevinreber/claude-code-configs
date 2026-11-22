# Architecture diagrams

Use Graphviz for service relationships, system boundaries, APIs, queues, and
storage.

## Conventions

| Element | Shape | Fill |
|---|---|---|
| Human or caller | ellipse | `#FEE2E2` |
| Service | rounded box | `#DBEAFE` |
| Worker or batch job | rounded box | `#EDE9FE` |
| Database or cache | cylinder | `#DCFCE7` |
| Queue or event bus | parallelogram | `#FFEDD5` |
| External system | component | `#E5E7EB` |

Use clusters only for meaningful trust, ownership, network, or deployment
boundaries. Avoid decorative containers.

## Template

```dot
digraph architecture {
    graph [rankdir=LR, bgcolor="white", pad="0.3", nodesep="0.45",
           ranksep="0.7", splines=polyline, fontname="Arial"];
    node [shape=box, style="rounded,filled", fillcolor="#DBEAFE",
          color="#CBD5E1", fontcolor="#1E293B", fontname="Arial"];
    edge [color="#334155", fontcolor="#475569", fontname="Arial",
          fontsize=9, arrowsize=0.7];

    user [label="User", shape=ellipse, fillcolor="#FEE2E2"];
    api [label="API\n(HTTPS)"];
    worker [label="Worker\n(async)", fillcolor="#EDE9FE"];
    queue [label="Event Queue", shape=parallelogram, fillcolor="#FFEDD5"];
    db [label="Primary DB", shape=cylinder, style=filled, fillcolor="#DCFCE7"];
    vendor [label="External API", shape=component, style=filled, fillcolor="#E5E7EB"];

    user -> api [label="request"];
    api -> db [label="read/write"];
    api -> queue [label="publish"];
    queue -> worker [label="consume"];
    worker -> vendor [label="REST", style=dashed];
}
```

## Review checklist

- Dependency direction is accurate.
- Runtime relationships are not confused with build-time dependencies.
- Optional or inferred relationships are visually distinguished.
- Storage and queues are not rendered as generic services.
