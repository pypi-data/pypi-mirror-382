# ADR-007: Memgraph for Graph Boosting (Optional Stage 7)

**Status:** Accepted

**Date:** 2025-10-07

**Deciders:** Architecture Team

**Context:**
The Entity Intelligence Service includes graph boosting as Stage 7 of the resolution pipeline to leverage relationship context for entity matching. Use case:
- "John Smith at IBM" vs "John Smith at Microsoft" (relationship disambiguates)
- Company subsidiaries (parent-child relationships boost confidence)
- Co-occurrences in documents (entities mentioned together likely related)

Graph databases add operational complexity and are not required for basic entity resolution. Research shows graph boosting provides 5-10% accuracy lift in complex domains (legal, scientific).

Options considered:
- **Option A**: Memgraph (in-memory, fast Cypher queries, optional sidecar)
- **Option B**: Neo4j (mature, enterprise-grade, heavier)
- **Option C**: PostgreSQL + AGE extension (Postgres-native graphs)
- **Option D**: No graph database (defer indefinitely)

## Decision

Use **Memgraph as an optional sidecar service** for Stage 7 graph boosting, deployed only when needed.

**Deployment Strategy:**
- MVP (Bullets 1-6): No graph database (disable Stage 7)
- Bullet #8: Add Memgraph sidecar for relationship-based boosting
- Production: Optional - deploy if accuracy gains justify operational cost

## Rationale

**Why Memgraph:**
- **In-Memory Performance**: Faster than disk-based Neo4j for small-medium graphs (<10M entities)
- **Cypher Support**: Standard graph query language
- **Lightweight**: <500MB RAM for typical entity graphs
- **Easy Docker Deployment**: Single container sidecar
- **Relationship Queries**: Efficient pattern matching (MATCH paths)
- **Optional**: Service works without it (graceful degradation)

**Why not Neo4j:**
- Heavier deployment (requires more RAM, disk)
- Overkill for MVP (enterprise features not needed)
- Memgraph simpler for self-hosted

**Why not PostgreSQL + AGE:**
- AGE extension adds complexity to single-store Postgres
- Cypher queries less mature than native Memgraph
- Mixing concerns (relational + graph in one DB)

**Why not defer indefinitely:**
- Research shows 5-10% accuracy lift in complex domains
- Relationship context valuable for ambiguous entities
- Bullet #8 is appropriate time to evaluate

## Consequences

### Positive:
- **Optional Complexity**: Only deploy if accuracy requires it
- **Fast Queries**: In-memory Cypher queries <100ms
- **Clear Separation**: Graph concerns isolated from core resolution
- **Easy Removal**: Can disable Stage 7 without affecting Stages 1-6
- **Relationship Modeling**: Natural representation of entity connections

### Negative:
- **Operational Overhead**: Additional container to manage
- **Memory Requirements**: ~500MB-1GB RAM for graph storage
- **Data Sync**: Must keep entity relationships in sync with PostgreSQL
- **Learning Curve**: Team must learn Cypher query language

### Neutral:
- **Accuracy Validation**: Measure lift vs cost in Bullet #8
- **May Not Deploy**: If Stages 1-6 achieve >90% accuracy, graph optional

## Implementation Strategy

### Docker Compose Sidecar
```yaml
# docker-compose.yml
services:
  entity-service:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/entities
      - MEMGRAPH_URL=bolt://memgraph:7687  # Optional
      - GRAPH_ENABLED=true  # Set to false to disable Stage 7

  postgres:
    image: postgres:17
    volumes:
      - pgdata:/var/lib/postgresql/data

  memgraph:
    image: memgraph/memgraph:latest
    ports:
      - "7687:7687"  # Bolt protocol
      - "7444:7444"  # Memgraph Lab UI
    volumes:
      - mgdata:/var/lib/memgraph
    command: ["--log-level=WARNING"]

volumes:
  pgdata:
  mgdata:
```

### Graph Schema
```cypher
// Nodes: Entities (mirrors PostgreSQL entity table)
CREATE (:Entity {
  entity_id: "uuid-here",
  kind: "company",
  canonical_name: "IBM"
});

// Relationships: Entity connections
CREATE (e1:Entity)-[:MENTIONED_WITH {
  document_id: "doc-123",
  co_occurrence_count: 5
}]->(e2:Entity);

CREATE (e1:Entity)-[:SUBSIDIARY_OF]->(e2:Entity);
CREATE (e1:Entity)-[:WORKS_AT]->(e2:Entity);
CREATE (e1:Entity)-[:LOCATED_IN]->(e2:Entity);
```

### Sync Strategy
```python
async def create_entity_with_graph(
    pool: asyncpg.Pool,
    memgraph: Memgraph | None,
    entity: EntityCreate
) -> Entity:
    """Create entity in both PostgreSQL and Memgraph"""

    # Primary storage: PostgreSQL
    async with pool.acquire() as conn:
        entity_id = await conn.fetchval(
            "INSERT INTO entity (...) VALUES (...) RETURNING entity_id",
            ...
        )

    # Optional graph storage: Memgraph
    if memgraph and config.graph_enabled:
        await memgraph.execute(
            """
            CREATE (e:Entity {
              entity_id: $entity_id,
              kind: $kind,
              canonical_name: $canonical_name
            })
            """,
            entity_id=str(entity_id),
            kind=entity.kind,
            canonical_name=entity.canonical_name
        )

    return entity
```

### Stage 7: Graph Boosting
```python
async def graph_boosting_stage(
    query_entity: Entity,
    candidates: list[Match],
    memgraph: Memgraph
) -> list[Match]:
    """Boost candidate scores based on relationship context"""

    if not config.graph_enabled or not memgraph:
        return candidates  # Skip stage if graph disabled

    # Query: Find entities connected to query_entity
    connected_entities = await memgraph.query(
        """
        MATCH (q:Entity {entity_id: $query_id})-[r]-(connected:Entity)
        RETURN connected.entity_id, type(r), count(r) as strength
        """,
        query_id=str(query_entity.entity_id)
    )

    # Boost candidates that share connections with query_entity
    for candidate in candidates:
        boost = 0.0
        for conn in connected_entities:
            if candidate.entity_id == conn["entity_id"]:
                # Relationship exists: boost confidence
                boost += 0.1 * conn["strength"]  # Scale by relationship strength

        candidate.confidence = min(1.0, candidate.confidence + boost)
        candidate.boost_details["graph"] = boost

    # Re-sort candidates by boosted confidence
    return sorted(candidates, key=lambda m: m.confidence, reverse=True)
```

### Example: Person Disambiguation
```python
# Query: "John Smith" (ambiguous - many people named John Smith)
# Context: Mentioned in document with "IBM"

# Without graph: Multiple candidates with similar confidence
candidates = [
    Match(entity_id="john-smith-1", confidence=0.7),  # John Smith at IBM
    Match(entity_id="john-smith-2", confidence=0.68), # John Smith at Microsoft
    Match(entity_id="john-smith-3", confidence=0.65), # John Smith at Google
]

# With graph boosting:
# Query Cypher: Find John Smith entities connected to IBM
# Result: john-smith-1 has WORKS_AT relationship with IBM
# Boost: john-smith-1 confidence → 0.7 + 0.15 = 0.85

candidates_boosted = [
    Match(entity_id="john-smith-1", confidence=0.85),  # BOOSTED (connected to IBM)
    Match(entity_id="john-smith-2", confidence=0.68),
    Match(entity_id="john-smith-3", confidence=0.65),
]
```

## Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| Query latency | <100ms | Cypher pattern matching |
| Memory | <1GB | For 1M entities + relationships |
| Accuracy lift | +5-10% | Vs non-graph baseline |
| Sync latency | <10ms | Entity create/update propagation |

## Configuration

```yaml
# config/prod.yaml
graph:
  enabled: true  # Set to false to disable Stage 7
  url: "bolt://memgraph:7687"
  username: ""
  password: ""
  connection_timeout: 5.0

resolution:
  stages:
    graph_boosting:
      enabled: true  # Tied to graph.enabled
      confidence_threshold: 0.65
      boost_factor: 0.1  # How much to boost per relationship
      max_boost: 0.2     # Cap boost at 20%
```

## Evaluation Criteria (Bullet #8)

Before deploying Memgraph in production, measure:
1. **Accuracy Lift**: Run test dataset with/without graph boosting
   - Target: +5% F1 improvement to justify operational cost
2. **Latency Impact**: Measure p95 latency with Stage 7 enabled
   - Target: <100ms added latency (stay within 500ms total)
3. **Operational Complexity**: Docker Compose deployment ease
   - Target: Single `docker-compose up` command
4. **Memory Cost**: Measure RAM usage for 10K-100K entities
   - Target: <1GB additional RAM

**Decision Gate:** If accuracy lift <3% OR latency >100ms, disable Stage 7 and remove Memgraph.

## Escape Hatch

**If Memgraph proves unnecessary:**
- Set `graph.enabled = false` in config
- Remove Memgraph container from docker-compose
- Stage 7 skipped automatically (graceful degradation)
- Keep code for future re-evaluation

**If Memgraph insufficient:**
- Upgrade to Neo4j for advanced graph features (APOC, graph algorithms)
- Consider graph embeddings (node2vec) for similarity
- Hybrid: Memgraph for simple queries, PostgreSQL for complex analytics

**If sync complexity too high:**
- Use event-driven sync (Postgres triggers → Kafka → Memgraph)
- Accept eventual consistency (graph lags by seconds)
- Or remove graph entirely if not worth maintenance cost

## Alternatives Considered

### Neo4j
- **Pros**: Mature, enterprise features, APOC library, graph algorithms
- **Cons**: Heavier (requires 2GB+ RAM), complex deployment, overkill for MVP
- **Decision**: Memgraph simpler for self-hosted, can upgrade later

### PostgreSQL + AGE Extension
- **Pros**: Single database, no sync complexity
- **Cons**: AGE less mature, Cypher support limited, mixing relational + graph concerns
- **Decision**: Keep Postgres pure relational, Memgraph for graphs

### No Graph Database
- **Pros**: Simplest architecture, no operational overhead
- **Cons**: Misses relationship-based accuracy lift
- **Decision**: Defer to Bullet #8, evaluate if needed

### Graph Embeddings Only (No Graph DB)
- **Pros**: Store embeddings in Postgres pgvector, no separate DB
- **Cons**: Loses explicit relationship semantics, harder to query
- **Decision**: Explicit graphs more interpretable and queryable

## References

- [Memgraph Documentation](https://memgraph.com/docs)
- [Cypher Query Language](https://neo4j.com/docs/cypher-manual/current/)
- Research: `claude_legal-prd.md` (Stage 7: Graph boosting for legal entities)
- Research: `chatgpt_canonical-entity-id-service.md` (Optional graph layer)
- BEACON Principle: YAGNI - build only if accuracy requires it

## Review Date

After Bullet #8 (graph boosting implemented): Measure accuracy lift and operational cost.
- If accuracy lift ≥ 5% AND latency <100ms: Keep Memgraph
- If accuracy lift < 5% OR latency >100ms: Disable Memgraph, remove from docker-compose
- Document decision in retrospective (did graph boosting earn its keep?)
