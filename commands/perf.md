# Performance Analysis

Analyze code for performance issues and optimization opportunities.

## Instructions

Analyze: $ARGUMENTS

### Performance Categories

#### 1. Time Complexity
- Identify algorithm complexity (O notation)
- Find nested loops that could be optimized
- Spot unnecessary iterations
- Suggest more efficient algorithms

#### 2. Space Complexity
- Memory allocation patterns
- Potential memory leaks
- Unnecessary data copies
- Large object retention

#### 3. I/O Performance
- Database query efficiency (N+1 problems)
- File system operations
- Network request patterns
- Caching opportunities

#### 4. Concurrency
- Blocking operations
- Parallelization opportunities
- Resource contention
- Deadlock potential

#### 5. Language-Specific
**JavaScript/TypeScript:**
- Bundle size impact
- Render performance (React, etc.)
- Event loop blocking
- Memory leaks (closures, listeners)

**Python:**
- GIL considerations
- Generator vs list comprehension
- Import time
- Numpy/vectorization opportunities

**General:**
- Hot path identification
- Lazy loading opportunities
- Memoization candidates

### Analysis Process

1. Read the code
2. Identify the hot path (most executed code)
3. Analyze complexity
4. Check for common anti-patterns
5. Suggest optimizations with trade-offs

## Output Format

```markdown
## Performance Analysis: [file/component]

### Summary
[Overall assessment and biggest concerns]

### Complexity Analysis
- Time: O(n²) due to [reason]
- Space: O(n) for [data structure]

### Issues Found

#### Critical
| Location | Issue | Impact | Fix |
|----------|-------|--------|-----|
| file:line | N+1 query | High latency | Eager load |

#### Moderate
...

### Optimization Suggestions
1. **[Optimization]**
   - Current: [code/pattern]
   - Suggested: [improvement]
   - Trade-off: [consideration]
   - Expected improvement: [estimate]

### Benchmarking Recommendations
- [What to measure and how]
```

Prioritize suggestions by impact and implementation effort.
