# Database Skill

Specialized skill for database schema design, query optimization, and data modeling.

## Activation

Use this skill when the user needs help with database design, SQL queries, query optimization, or data modeling.

## Capabilities

### Schema Design

**Normalization**
- 1NF: Atomic values, no repeating groups
- 2NF: No partial dependencies
- 3NF: No transitive dependencies
- When to denormalize for performance

**Naming Conventions**
- Tables: plural, snake_case (`user_accounts`)
- Columns: singular, snake_case (`created_at`)
- Primary keys: `id` or `table_id`
- Foreign keys: `referenced_table_id`

**Common Patterns**
- Soft deletes: `deleted_at` timestamp
- Audit fields: `created_at`, `updated_at`, `created_by`
- Polymorphic associations
- Many-to-many junction tables
- Self-referential relationships

### Query Optimization

**Analysis Steps**
1. EXPLAIN/EXPLAIN ANALYZE the query
2. Check for full table scans
3. Verify index usage
4. Look for N+1 patterns
5. Check join efficiency

**Index Strategy**
- Index columns used in WHERE, JOIN, ORDER BY
- Consider composite indexes for multi-column queries
- Partial indexes for filtered queries
- Covering indexes for read-heavy queries

**Common Optimizations**
- Avoid SELECT * - specify columns
- Use EXISTS instead of COUNT for existence checks
- Batch inserts/updates
- Use appropriate data types
- Limit result sets

### Database-Specific Knowledge

**PostgreSQL**
- JSONB for semi-structured data
- Array types
- CTEs and window functions
- Materialized views
- pg_stat_statements for query analysis

**MySQL**
- InnoDB vs MyISAM
- Query cache (deprecated in 8.0)
- Index hints
- Partitioning strategies

**SQLite**
- Single-file database
- WAL mode for concurrency
- Limitations on ALTER TABLE

### Migration Best Practices

- Always have rollback plan
- Test migrations on production-like data
- Avoid locking long-running migrations
- Use batched updates for large tables
- Separate deploy from migrate for zero-downtime

### Data Modeling

I can help with:
- ER diagram design
- Cardinality analysis
- Identifying entities and relationships
- Handling hierarchical data
- Time-series data patterns
- Multi-tenant architectures
