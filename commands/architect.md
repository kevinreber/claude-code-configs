# Architecture Assistant

Help design and evaluate software architecture decisions.

## Instructions

Analyze or design: $ARGUMENTS

### Architecture Analysis

When analyzing existing architecture:
1. Map the system components
2. Identify dependencies and coupling
3. Evaluate against quality attributes
4. Find architectural smells

### Architecture Design

When designing new architecture:
1. Clarify requirements and constraints
2. Identify key quality attributes
3. Propose architecture options
4. Evaluate trade-offs
5. Recommend approach

### Quality Attributes to Consider

- **Scalability**: Handle growth in load/data/users
- **Reliability**: Fault tolerance, recovery
- **Performance**: Latency, throughput
- **Security**: Authentication, authorization, data protection
- **Maintainability**: Ease of change, modularity
- **Testability**: Isolation, mockability
- **Deployability**: CI/CD, rollback capability
- **Observability**: Logging, monitoring, tracing

### Common Patterns

- Microservices vs Monolith
- Event-driven architecture
- CQRS and Event Sourcing
- Hexagonal/Clean Architecture
- Domain-Driven Design
- API Gateway pattern
- Circuit Breaker
- Saga pattern
- Strangler Fig (migration)

### Architectural Smells

- God classes/services
- Circular dependencies
- Shared databases between services
- Synchronous chains
- Missing abstraction layers
- Over-engineering

## Output Format

```markdown
## Architecture Analysis/Proposal: [System Name]

### Context
[Problem statement and constraints]

### Current State (if analyzing)
[Component diagram description]
[Key dependencies]
[Quality attribute assessment]

### Proposed Architecture (if designing)
[High-level design]
[Component responsibilities]
[Integration patterns]

### Trade-offs
| Decision | Pros | Cons |
|----------|------|------|
| [Choice] | [Benefits] | [Drawbacks] |

### Recommendations
1. [Priority recommendation]
2. [Secondary recommendation]

### Migration Path (if applicable)
[Steps to move from current to proposed]

### Open Questions
- [Questions needing stakeholder input]
```
