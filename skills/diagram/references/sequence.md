# Sequence diagrams

Use Mermaid to show an ordered request, event, or workflow across components.

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant API
    participant Worker
    participant DB

    User->>API: Submit request
    API->>DB: Read current state
    DB-->>API: State
    alt valid request
        API-)Worker: Publish work
        API-->>User: 202 Accepted
        Worker->>DB: Persist result
    else invalid request
        API-->>User: 400 Bad Request
    end
```

- Keep participants to eight or fewer.
- Use `->>` for calls, `-->>` for responses, and `-)` for async messages.
- Use `alt`, `opt`, `loop`, and `par` only when they improve the story.
- Confirm response and error paths rather than showing only the happy path.
