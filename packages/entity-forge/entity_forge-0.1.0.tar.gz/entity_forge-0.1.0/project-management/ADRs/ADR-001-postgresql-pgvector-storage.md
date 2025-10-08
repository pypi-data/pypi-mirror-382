# ADR-001: PostgreSQL 17 with pgvector for Storage

**Status:** Accepted

**Date:** 2025-10-07

**Deciders:** Architecture Team

**Context:**
The Entity Intelligence Service requires storage for:
1. Relational entity data (canonical names, attributes, metadata)
2. Dense vector embeddings for semantic search
3. Full-text search capabilities
4. ACID transactions for entity operations (CRUD, MERGE, UPSERT)

Options considered:
- **Option A**: PostgreSQL 17 + pgvector extension (single database)
- **Option B**: PostgreSQL 17 + separate vector database (Qdrant/Weaviate)
- **Option C**: PostgreSQL 18 + pgvector (latest release)

## Decision

Use **PostgreSQL 17 with pgvector extension** as the primary and only storage layer for MVP.

## Rationale

**Pros of PostgreSQL 17 + pgvector:**
- **Single-store simplicity**: One database to manage, no complex synchronization
- **ACID guarantees**: Transactional entity operations (critical for MERGE/UPSERT)
- **Proven stability**: Postgres 17 is current stable release (Sep 2024)
- **pgvector maturity**: HNSW index support, sufficient for millions of vectors
- **FTS + pg_trgm built-in**: No additional tools for lexical/fuzzy search
- **Operational simplicity**: One Docker container, one connection pool
- **Cost efficiency**: No additional infrastructure

**Why not Postgres 18:**
- Beta/preview release at time of decision
- Postgres 17 features sufficient for MVP
- AIO subsystem gains (2-3× faster) are nice-to-have, not critical
- Stability prioritized over cutting-edge performance

**Why not separate vector DB:**
- Adds operational complexity (two databases to manage)
- Synchronization challenges (entity updates must propagate)
- Network latency between services
- YAGNI - prove need before adding complexity

## Consequences

### Positive:
- Simplified architecture and operations
- Single source of truth for all entity data
- Transactional consistency guaranteed
- Lower operational overhead
- Faster MVP development

### Negative:
- pgvector may be slower than specialized vector DBs at scale (>10M vectors)
- Limited to pgvector's capabilities (no advanced vector features)
- Single point of failure (can mitigate with Postgres HA later)

### Neutral:
- Can migrate to specialized vector DB if proven insufficient
- Postgres replication/sharding available if needed

## Escape Hatch

If pgvector proves insufficient (accuracy < 85% or latency > 500ms at scale):
1. Keep Postgres for relational data + FTS
2. Add Qdrant for vector search only
3. Sync entity embeddings asynchronously
4. Use Postgres as canonical source of truth

Migration path is well-documented and reversible.

## Alternatives Considered

### Qdrant (specialized vector DB)
- **Pros**: Faster vector search, advanced features (sparse vectors, filters)
- **Cons**: Additional infrastructure, sync complexity, overkill for MVP
- **Decision**: Defer until proven need

### Weaviate
- **Pros**: Vector + hybrid search, schema management
- **Cons**: Heavy infrastructure, GraphQL API (mismatch), complex setup
- **Decision**: Too complex for MVP

### Postgres 18
- **Pros**: AIO subsystem (2-3× faster), parallel COPY, skip scans
- **Cons**: Beta stability, Postgres 17 sufficient for MVP
- **Decision**: Revisit post-MVP if performance critical

## Implementation Notes

```sql
-- Required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- HNSW index for vector search (ANN)
CREATE INDEX idx_entity_embedding_hnsw ON entity
  USING hnsw (embedding_text vector_cosine_ops);

-- GIN index for full-text search
CREATE INDEX idx_entity_fts ON entity USING GIN (fts_document);

-- Trigram index for fuzzy matching
CREATE INDEX idx_entity_trgm_name ON entity USING GIN (canonical_name gin_trgm_ops);
```

## References

- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [PostgreSQL 17 Release Notes](https://www.postgresql.org/docs/17/release-17.html)
- Research: `chatgpt_canonical-entity-id-service.md` (recommends Postgres 18, we chose 17 for stability)
- BEACON Principle: Reversibility - can migrate to specialized DB if needed

## Review Date

After Bullet #6 (vector search + reranking): Assess if pgvector performance acceptable (>90% accuracy, <500ms p95).
