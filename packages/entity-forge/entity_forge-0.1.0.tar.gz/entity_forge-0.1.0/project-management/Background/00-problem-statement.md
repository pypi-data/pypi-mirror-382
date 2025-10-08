# Problem Statement

## Core Problem

Platform engineers and data teams need a **unified entity intelligence service** that:
1. **Extracts entities** from arbitrary inputs (strings, emails, documents) via Named Entity Recognition
2. **Resolves entities** to canonical IDs through multi-stage matching (exact → fuzzy → vector → graph) OR creates new canonical entities when no match exists
3. **Manages entities** across arbitrary domains via CRUD, MERGE, UPSERT operations
4. **Provides canonical GUIDs** as the source of truth for master data management

Existing solutions are fragmented:
- **Enterprise MDM** ($100K+, not self-hosted, complex)
- **NER-only** (spaCy, GLiNER - no resolution or storage)
- **Resolution-only** (dedupe.io, splink - no NER, no entity management)
- **Custom integrations** (5+ tools, high operational overhead)

**Scope:** Full pipeline from text → extracted entities → canonical IDs (matched OR newly created) → optional knowledge graph

## Target User

**Who:** Platform engineers, data engineers, and application developers building systems that handle entity data (companies, products, people, etc.)

**Context:** When users enter entity data in free-text form (e.g., "IBM" vs "International Business Machines" vs "I.B.M. Corporation"), systems need to recognize these as the same canonical entity to prevent duplicates, enable proper analytics segmentation, and maintain data integrity.

**Current Pain:**
- **Enterprise MDM solutions** (Informatica, SAP MDG, IBM InfoSphere) cost $100K+, require extensive implementation, and aren't self-hosted
- **Open-source libraries** (dedupe.io, splink) provide basic fuzzy matching but lack modern ML techniques (vector search, graph algorithms, LLM integration) and require extensive training data
- **Custom solutions** require stitching together 5+ tools (Elasticsearch for fuzzy matching, separate vector DB, separate graph DB, custom NER models) with no unified API
- **No zero/few-shot solutions** - all require extensive training per domain

## Success Criteria

- [ ] **Accuracy**: >90% correct entity matches on test dataset (starting with companies domain)
- [ ] **Latency**: <500ms p95 for match requests (accuracy prioritized over speed initially)
- [ ] **Multi-domain**: Successfully identifies/resolves entities in at least 2 different domains (e.g., companies + products)
- [ ] **Multi-stage Pipeline**: 7-stage gracefully degrading pipeline (exact → rules → FTS → fuzzy → vector → probabilistic → graph)
- [ ] **LLM Integration**: Service accessible via FastMCP, allowing LLMs to query for entity IDs and create/manage entities
- [ ] **Operational Simplicity**: Deployable via docker-compose, runs self-hosted, no external dependencies (optional Memgraph/vLLM sidecars)

## Non-Goals (What We're NOT Solving)

1. NOT an ETL pipeline - Won't bulk extract/transform/load data from source systems (though accepts individual inputs via API)
2. NOT a data warehouse - Won't store large historical datasets or perform analytics
3. NOT a business intelligence tool - No dashboards, reports, or visualization UI
4. NOT a workflow engine - No approval processes or data stewardship workflows (though can create/merge entities)
5. NOT a data quality platform - Won't validate comprehensive data quality rules beyond entity matching
6. NOT a schema registry - Won't manage upstream/downstream schema evolution
7. NOT multi-datacenter replication - Single deployment to start (can evolve later)
8. NOT real-time streaming - Accepts REST API calls, not Kafka/streaming ingestion
9. NOT enterprise security - Basic auth/API keys initially, not SSO/SAML/enterprise IAM
10. NOT a semantic search engine - Won't index documents for retrieval (though can extract entities from them)

## Why This Matters

Entity resolution is a critical cornerstone of master data management. Without canonical entity IDs:
- Analytics are fragmented across duplicate entities
- Business rules fail (e.g., license enforcement on company X when recorded as 3 different companies)
- Data quality degrades over time
- Integration between systems breaks down

A self-hosted, extensible, zero/few-shot service that combines modern ML (vector search, graph algorithms, LLM integration) with traditional entity resolution techniques provides a **10x simpler** solution than existing alternatives.

## Existing Solutions Analysis

| Solution | Pros | Cons | Why 10x Worse |
|----------|------|------|---------------|
| **Enterprise MDM** (Informatica, SAP, IBM) | Battle-tested, comprehensive | $100K+ licensing, complex implementation, not self-hosted | Cost and complexity prohibitive |
| **dedupe.io** | Python-friendly, probabilistic matching | No vector search, no graph, no LLM integration, requires training | Missing modern ML capabilities |
| **splink** | Good statistical matching | Focused on linkage only, no entity management, no vectors | Not a complete service |
| **Senzing** | Entity-focused | Primarily commercial, limited open-source | Not truly self-hostable |
| **Custom (ES + vectors + graph)** | Flexible | Requires stitching 5+ tools, no unified API, high operational overhead | Operational complexity |

## User Persona: Sarah the Platform Engineer

Sarah is building a B2B SaaS platform. Her users enter company names in free text across multiple forms:
- Signup form: "IBM"
- Invoice import: "International Business Machines Corp."
- CRM integration: "I.B.M. Corporation"

**Problem:** Without entity resolution, Sarah's system treats these as 3 different companies, breaking:
- License seat counting
- Usage analytics
- Account consolidation
- Duplicate prevention

**Current Solution:** Manual deduplication OR pay $150K for Informatica MDM + 6 months implementation

**Our Solution:** Deploy Docker container, POST to `/entities/match`, get canonical `entity_id` back. Zero training required for basic matching, improves over time with usage.

---

_Created: 2025-10-07_
_Last Updated: 2025-10-07 (DESIGN phase: Research synthesis integrated)_
_Status: Living Document - Update as requirements evolve_
