# Entity Intelligence Service - Development Roadmap

## Current Status

**Active Bullet:** #2 - Fuzzy Matching with RapidFuzz
**Phase:** BUILD (Foundation)
**Started:** 2025-10-07
**Bullet #1 Completed:** 2025-10-07 (~1.5 hours)
**Target MVP Completion:** 2025-10-15 (Bullet #6 complete)

## Project Overview

Building a unified entity intelligence service that extracts, resolves, and manages canonical entity IDs across arbitrary domains. Uses BEACON Framework with tracer bullet methodology - each bullet delivers working, shippable software.

**Key Documents:**
- [Problem Statement](../Background/00-problem-statement.md)
- [Architecture](../Background/01-final-architecture-document.md)
- [ADRs](../ADRs/) (8 architectural decisions documented)

## Tracer Bullet Progress

### Foundation Phase (Bullets 1-3) - Basic Pipeline

#### ✅ Planning Complete
- [x] Problem statement documented
- [x] Architecture designed
- [x] ADRs created (001-008)
- [x] Technology stack selected

#### ✅ Bullet #1: Hardcoded Exact Match (COMPLETED - 1.5 hours)
**Goal:** Prove end-to-end plumbing works
**Status:** ✅ Complete (2025-10-07)
**Deliverable:** `/match` endpoint returns hardcoded exact matches

**Success Criteria:**
- [x] FastAPI service runs on port 8000
- [x] POST `/match` accepts entity text
- [x] Returns hardcoded matches (in-memory dictionary)
- [x] Includes confidence score (1.0 for exact, 0.0 for no match)
- [x] Unit tests pass (11/11 passing)
- [x] Can demo: "IBM" → canonical ID

**Session Doc:** [2025-10-07-bullet-01-exact-match.md](../Work/sessions/2025-10-07-bullet-01-exact-match.md)

**Implementation Notes:**
- Use FastAPI with Pydantic models
- In-memory dictionary: `{"IBM": "uuid-123", "Microsoft": "uuid-456"}`
- No database yet (defer to Bullet #3)
- Simple JSON responses

**Acceptance Test:**
```bash
curl -X POST http://localhost:8000/match \
  -H "Content-Type: application/json" \
  -d '{"text": "IBM", "kind": "company"}'

# Expected: {"canonical_id": "uuid-123", "canonical_name": "IBM", "confidence": 1.0}
```

---

#### ⏳ Bullet #2: Fuzzy Matching with RapidFuzz (3-4 hours)
**Goal:** Add typo/abbreviation handling
**Status:** Blocked by Bullet #1
**Deliverable:** `/match` handles fuzzy matches (e.g., "I.B.M." → "IBM")

**Success Criteria:**
- [ ] RapidFuzz integrated (Levenshtein distance)
- [ ] Fuzzy matches work (threshold: 0.8)
- [ ] Confidence scores reflect match quality (0.8-1.0 range)
- [ ] Bullet #1 tests still pass (exact match preserved)
- [ ] New fuzzy tests pass
- [ ] Can demo: "Microsft" → Microsoft (typo fixed)

**Implementation Notes:**
- Install `rapidfuzz` library
- Fallback logic: Exact → Fuzzy (if no exact match)
- Confidence = RapidFuzz score
- Keep in-memory dictionary (expand with test data)

**Acceptance Test:**
```bash
curl -X POST http://localhost:8000/match \
  -d '{"text": "I.B.M.", "kind": "company"}'

# Expected: {"canonical_id": "uuid-123", "canonical_name": "IBM", "confidence": 0.85}
```

---

#### ⏳ Bullet #3: PostgreSQL Persistence (4 hours)
**Goal:** Survive restart, real storage
**Status:** Blocked by Bullet #2
**Deliverable:** Entities stored in Postgres, CRUD endpoints work

**Success Criteria:**
- [ ] PostgreSQL 17 + pgvector Docker container running
- [ ] Database schema created (entity table)
- [ ] POST `/entities` creates entity (returns UUID)
- [ ] GET `/entities/{id}` retrieves entity
- [ ] PUT `/entities/{id}` updates entity
- [ ] DELETE `/entities/{id}` removes entity
- [ ] Bullets #1-2 tests pass with real database
- [ ] Can demo: Create entity, restart service, entity persists

**Implementation Notes:**
- Use `asyncpg` for database driver
- Create schema from ADR-001 (entity table with UUID primary key)
- Enable pgvector extension (for future bullets)
- Environment variable for DATABASE_URL
- Connection pooling (5-20 connections)

**Database Schema:**
```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TABLE entity (
  entity_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  kind              TEXT NOT NULL,
  canonical_name    TEXT NOT NULL,
  aliases           TEXT[] DEFAULT '{}',
  attributes        JSONB NOT NULL DEFAULT '{}',
  created_at        TIMESTAMPTZ DEFAULT now(),
  updated_at        TIMESTAMPTZ DEFAULT now(),
  confidence        FLOAT DEFAULT 1.0,
  source            TEXT,
  embedding_text    VECTOR(768),  -- For Bullet #4
  fts_document      tsvector GENERATED ALWAYS AS (
    setweight(to_tsvector('english', coalesce(canonical_name, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(array_to_string(aliases, ' '), '')), 'B')
  ) STORED
);
```

**Acceptance Test:**
```bash
# Create entity
curl -X POST http://localhost:8000/entities \
  -d '{"kind": "company", "canonical_name": "IBM", "aliases": ["International Business Machines"]}'

# Returns: {"entity_id": "uuid-123", ...}

# Restart service (docker-compose restart)

# Retrieve entity
curl http://localhost:8000/entities/uuid-123
# Entity still exists
```

---

### Core Logic Phase (Bullets 4-6) - Advanced Matching

#### ⏳ Bullet #4: Vector Search with EmbeddingGemma (4-5 hours)
**Goal:** Semantic matching ("IBM Corp" matches "International Business Machines")
**Status:** Blocked by Bullet #3
**Deliverable:** Vector similarity stage in resolution pipeline

**Success Criteria:**
- [ ] EmbeddingGemma-308M loaded on startup
- [ ] Entities generate embeddings on creation (768-dim vectors)
- [ ] Embeddings stored in PostgreSQL (pgvector VECTOR(768))
- [ ] HNSW index created for fast vector search
- [ ] `/match` uses vector similarity if fuzzy fails (confidence < 0.8)
- [ ] Semantic matches work (e.g., "Big Blue" → IBM)
- [ ] Latency < 100ms (embedding + vector search)
- [ ] Can demo: "Big Blue" → IBM (semantic match)

**Implementation Notes:**
- Load `sentence-transformers` model: `google/embedding-gemma-308m`
- Generate embeddings on entity creation (async)
- pgvector HNSW index: `CREATE INDEX ... USING hnsw (embedding_text vector_cosine_ops)`
- Vector search query: `SELECT ... ORDER BY embedding_text <=> $query_vector LIMIT 10`
- Pipeline: Exact → Fuzzy → Vector (first match wins)

**Acceptance Test:**
```bash
curl -X POST http://localhost:8000/match \
  -d '{"text": "Big Blue", "kind": "company"}'

# Expected: {"canonical_id": "uuid-123", "canonical_name": "IBM", "confidence": 0.75, "method": "vector"}
```

---

#### ⏳ Bullet #5: Hybrid Fusion (Dense + Sparse + FTS) (3-4 hours)
**Goal:** Combine multiple matching strategies with RRF fusion
**Status:** Blocked by Bullet #4
**Deliverable:** Multi-stage pipeline with Reciprocal Rank Fusion

**Success Criteria:**
- [ ] Full-Text Search (FTS) stage added using PostgreSQL `tsvector`
- [ ] GIN index on `fts_document` for fast FTS
- [ ] RRF fusion combines results from Exact, FTS, Fuzzy, Vector stages
- [ ] Pipeline runs stages in parallel (async.gather)
- [ ] Top 10 results from each stage fused with RRF formula
- [ ] Confidence scores reflect fused ranking
- [ ] Latency < 200ms (parallel stages + fusion)
- [ ] Can demo: "IBM machines" → IBM (FTS + vector fusion)

**Implementation Notes:**
- FTS query: `SELECT ... WHERE fts_document @@ plainto_tsquery('english', $query)`
- RRF formula: `score = sum(1/(60 + rank_i))` across all stages
- Parallel execution: `await asyncio.gather(exact_stage(), fts_stage(), fuzzy_stage(), vector_stage())`
- Sort by fused score descending
- Return top K candidates (K=10)

**Acceptance Test:**
```bash
curl -X POST http://localhost:8000/match \
  -d '{"text": "IBM machines", "kind": "company"}'

# Expected: {"canonical_id": "uuid-123", "canonical_name": "IBM", "confidence": 0.88, "method": "rrf_fusion"}
```

---

#### ⏳ Bullet #6: Cross-Encoder Reranking (3-4 hours)
**Goal:** Boost precision with semantic reranking
**Status:** Blocked by Bullet #5
**Deliverable:** Reranker improves top candidate quality

**Success Criteria:**
- [ ] `cross-encoder/ms-marco-MiniLM-L-12-v2` loaded on startup
- [ ] Top 10 RRF candidates passed to reranker
- [ ] Reranker scores: `(query, candidate)` pairs → similarity scores
- [ ] Candidates re-sorted by reranker scores
- [ ] Confidence updated to reranker score
- [ ] Accuracy improves 10-15% vs Bullet #5 baseline
- [ ] Latency < 250ms (fusion + reranking)
- [ ] Can demo: "IBM Corp" vs "IBM India" disambiguation

**Implementation Notes:**
- Load `sentence-transformers.CrossEncoder` model
- Rerank top K=10 candidates only (efficiency)
- Score pairs: `[(query_text, candidate_name), ...]`
- Replace RRF scores with reranker scores
- Keep audit trail (RRF score vs reranker score)

**Acceptance Test:**
```bash
curl -X POST http://localhost:8000/match \
  -d '{"text": "IBM", "kind": "company"}'

# Expected: Top result is "IBM" not "IBM India" (reranker disambiguated)
```

**Milestone: MVP Core Complete** 🎯
- All basic matching stages working (exact, fuzzy, vector, FTS, fusion, reranking)
- Accuracy target: >85% on test dataset
- Latency target: <500ms p95
- Ready for production pilot

---

### Advanced Features Phase (Bullets 7-9) - Production Hardening

#### ⏳ Bullet #7: Probabilistic Linking with Splink (5 hours)
**Goal:** Multi-field matching with Fellegi-Sunter model
**Status:** Blocked by Bullet #6
**Deliverable:** Stage 6 (probabilistic) in resolution pipeline

**Success Criteria:**
- [ ] Splink library integrated
- [ ] Multi-field matching: name + attributes (e.g., location, industry)
- [ ] Fellegi-Sunter model trained on synthetic/test data
- [ ] Stage 6 runs only if confidence < 0.7 (expensive)
- [ ] Accuracy improves 5% on complex entities
- [ ] Latency < 200ms for probabilistic stage
- [ ] Can demo: "IBM, Armonk, NY" matches correctly using location context

**Implementation Notes:**
- Install `splink` library
- Define match rules: exact name (weight=0.5), fuzzy name (weight=0.3), location (weight=0.2)
- Train Fellegi-Sunter model on labeled pairs (100-500 examples)
- Run stage conditionally: `if top_confidence < 0.7`
- Update confidence with probabilistic score

**Acceptance Test:**
```bash
curl -X POST http://localhost:8000/match \
  -d '{"text": "IBM", "kind": "company", "attributes": {"location": "Armonk, NY"}}'

# Expected: Matches "IBM" (Armonk) not "IBM India" (Bangalore)
```

---

#### ⏳ Bullet #8: Graph Boosting with Memgraph (Optional, 5-6 hours)
**Goal:** Relationship-based disambiguation
**Status:** Blocked by Bullet #7
**Deliverable:** Stage 7 (graph) in resolution pipeline (optional)

**Success Criteria:**
- [ ] Memgraph Docker container running (sidecar)
- [ ] Entities synced to Memgraph on creation
- [ ] Relationships created (MENTIONED_WITH, WORKS_AT, SUBSIDIARY_OF)
- [ ] Stage 7 queries relationships to boost confidence
- [ ] Accuracy improves 5-10% on ambiguous entities
- [ ] Latency < 100ms for graph queries
- [ ] Can disable via config (`graph.enabled = false`)
- [ ] Can demo: "John Smith at IBM" → correct John Smith (graph disambiguates)

**Implementation Notes:**
- Add Memgraph to docker-compose.yml
- Sync entities: Create Cypher node on entity creation
- Stage 7 query: `MATCH (q:Entity)-[r]-(c:Entity) WHERE q.entity_id = $query_id`
- Boost candidates with shared relationships
- Measure accuracy lift vs Bullet #7 baseline

**Decision Gate:** If accuracy lift < 3%, remove Memgraph and disable Stage 7.

**Acceptance Test:**
```bash
curl -X POST http://localhost:8000/match \
  -d '{"text": "John Smith", "context": "mentioned_with: IBM"}'

# Expected: Matches John Smith (IBM employee) not other John Smiths
```

---

#### ⏳ Bullet #9: LLM Adjudication (Optional, 4-5 hours)
**Goal:** Use LLMs for uncertain matches and domain identification
**Status:** Blocked by Bullet #8
**Deliverable:** LLM integration with OpenAI-compatible API

**Success Criteria:**
- [ ] OpenAI-compatible client configured (LM Studio for dev)
- [ ] LLM called for low-confidence matches (0.6-0.8 range)
- [ ] Domain identification works (e.g., "Apple" → company vs fruit)
- [ ] Few-shot entity extraction enhancement
- [ ] Accuracy improves 5-10% on edge cases
- [ ] Latency < 500ms for LLM calls (only when needed)
- [ ] Fallback if LLM unavailable (timeout after 5s)
- [ ] Config allows LM Studio (dev) or production LLM
- [ ] Can demo: "Apple mentioned in tech article" → Apple Inc (not fruit)

**Implementation Notes:**
- Install `openai` Python library
- Config: `llm.api_base = "http://localhost:1234/v1"` (LM Studio)
- Call LLM when: `0.6 <= top_confidence <= 0.8`
- Prompt: "Are 'IBM Corp' and 'International Business Machines' the same entity?"
- Parse JSON response, update confidence
- Measure accuracy lift vs Bullet #8 baseline

**Decision Gate:** If accuracy lift < 5%, disable LLM integration.

**Acceptance Test:**
```bash
curl -X POST http://localhost:8000/match \
  -d '{"text": "Apple", "context": "tech industry"}'

# Expected: {"canonical_id": "uuid-apple-inc", "canonical_name": "Apple Inc.", "confidence": 0.85, "method": "llm_adjudication"}
```

---

### Production Deployment Phase (Bullet 10) - Finalization

#### ⏳ Bullet #10: FastMCP Wrapper + Production Hardening (4 hours)
**Goal:** LLM integration via MCP, deployment ready
**Status:** Blocked by Bullet #9
**Deliverable:** FastMCP wrapper, production configs, deployment docs

**Success Criteria:**
- [ ] FastMCP server wraps FastAPI service
- [ ] MCP tools: `extract_and_match`, `create_entity`, `get_entity`, `merge_entities`
- [ ] Claude/GPT-4 can use service as tools
- [ ] Docker image optimized (<2GB)
- [ ] Production config (DATABASE_URL, LLM config)
- [ ] Deployment docs (docker-compose.yml)
- [ ] Monitoring: `/health`, `/metrics` endpoints
- [ ] Logging configured (structured JSON logs)
- [ ] Can demo: Claude extracts entities via MCP

**Implementation Notes:**
- Install `fastmcp` library
- Create `app/mcp.py` with tool definitions
- Dual deployment: FastAPI (port 8000) + FastMCP (port 3000)
- Docker multi-stage build (optimize image size)
- Add `/health` endpoint (returns 200 if healthy)
- Add `/metrics` endpoint (Prometheus format)
- Structured logging: JSON format with request IDs

**Acceptance Test:**
```bash
# Test HTTP API
curl http://localhost:8000/health
# Expected: {"status": "healthy"}

# Test MCP (via Claude Desktop)
# User: "Extract companies from: IBM and Microsoft announced..."
# Claude calls extract_and_match tool
# Returns: [{"text": "IBM", "canonical_id": "..."}, {"text": "Microsoft", ...}]
```

**Milestone: Production Ready** 🚀
- All 10 tracer bullets complete
- MVP deployed and accessible
- LLM integration via FastMCP
- Monitoring and logging in place

---

## Current Focus

**Next Step:** Start Bullet #1 (Hardcoded Exact Match)
- Create feature branch: `feature/bullet-01-exact-match`
- Set up FastAPI project with `uv`
- Implement `/match` endpoint with hardcoded dictionary
- Write unit tests
- Demo working endpoint

---

## Tracer Bullet Summary Table

| # | Bullet | Hours | Outcome | Dependencies |
|---|--------|-------|---------|--------------|
| 1 | Hardcoded Exact Match | 2-3h | `/match` endpoint works | None |
| 2 | Fuzzy Matching | 3-4h | Typo/abbreviation handling | #1 |
| 3 | Postgres Persistence | 4h | CRUD endpoints, survives restart | #2 |
| 4 | Vector Search | 4-5h | Semantic matching | #3 |
| 5 | Hybrid Fusion | 3-4h | Multi-stage pipeline with RRF | #4 |
| 6 | Cross-Encoder Reranking | 3-4h | Precision boost | #5 |
| 7 | Probabilistic Linking | 5h | Multi-field matching | #6 |
| 8 | Graph Boosting (Optional) | 5-6h | Relationship-based disambiguation | #7 |
| 9 | LLM Adjudication (Optional) | 4-5h | Edge case handling | #8 |
| 10 | FastMCP + Production | 4h | LLM integration, deployment ready | #9 |
| **Total** | **Foundation + Core + Advanced + Prod** | **40-48h** | **Working entity intelligence service** | |

---

## Success Metrics

### Technical Metrics (Measured at Each Bullet)
- **Accuracy:** Entity matching correctness on test dataset
  - Bullet #1: Baseline (exact match only)
  - Bullet #6: Target >85% accuracy
  - Bullet #10: Target >90% accuracy

- **Latency:** p95 response time
  - Bullet #1: <10ms (hardcoded)
  - Bullet #6: <250ms (fusion + reranking)
  - Bullet #10: <500ms (full pipeline)

- **Test Coverage:** Percentage of code covered by tests
  - Target: >80% by Bullet #10

### Product Metrics (Post-MVP)
- Multi-domain validation (test on 2+ domains: companies, products)
- LLM integration success rate (MCP tools work reliably)
- Production pilot feedback (user satisfaction)

---

## Blockers & Decisions

**Current Blockers:** None - ready to start Bullet #1

**Pending Decisions:**
- [ ] Which test dataset to use for accuracy measurement? (Need labeled entity pairs)
- [ ] Deploy Memgraph in production? (Depends on Bullet #8 accuracy lift)
- [ ] Deploy LLM in production? (Depends on Bullet #9 accuracy lift)

---

## Notes

- **Philosophy:** Ship working software daily, each bullet adds value
- **Testing:** Write acceptance test first, implement to pass
- **Quality:** Would I sign this? Check before marking bullet complete
- **Scope:** Build ONLY what's in the bullet, resist feature creep
- **Documentation:** Update this roadmap after each bullet completion

---

## Timeline Estimate

**Foundation (Bullets 1-3):** 9-11 hours → Target: Days 1-2
**Core Logic (Bullets 4-6):** 10-13 hours → Target: Days 3-4
**Advanced (Bullets 7-9):** 14-16 hours → Target: Days 5-6
**Production (Bullet 10):** 4 hours → Target: Day 7

**Total:** 40-48 hours of focused development
**Calendar Time:** 7-10 days (accounting for testing, debugging, reviews)

---

*Last Updated: 2025-10-07*
*Next Review: After Bullet #3 (Foundation complete)*
*Status: Ready to begin Bullet #1*
