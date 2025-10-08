# SEED Phase Evaluation - Entity Intelligence Service

**Date:** 2025-10-07
**Status:** ✅ APPROVED - Proceed to DESIGN
**Evaluator:** Claude (BEACON Framework Assistant)

---

## Does This Idea Deserve to Exist?

### 1. ONE Specific Problem for ONE Specific User

**Problem:** Platform engineers and data teams spend weeks integrating multiple enterprise MDM systems ($100K+) or writing brittle custom entity resolution code that breaks on edge cases and doesn't generalize across domains.

**User:** Platform engineer at mid-sized company (50-500 employees) building data pipelines or LLM applications that need canonical entity IDs for:
- Deduplicating customer records across systems
- Normalizing vendor/supplier names
- Resolving product mentions in documents
- Building knowledge graphs from unstructured text

**Pain Point:** They need:
1. Entity extraction (NER) from arbitrary text
2. Entity resolution to canonical IDs OR creation of new entities
3. Multi-domain support (companies, people, products, custom domains)
4. Self-hosted (no SaaS dependency)
5. Works in days, not months

**Current Pain:**
- Enterprise MDM: $100K+ license, 6-month implementation, IT department approval
- dedupe.io/splink: Python libraries for deduplication, but no NER, no canonical ID service, no REST API
- Custom solutions: Hardcoded rules per domain, brittle, doesn't scale
- LLM-only: Slow (500-2000ms per extraction), expensive, needs prompt engineering per domain

---

### 2. THREE Existing Solutions (and Why They're Insufficient)

#### Solution A: Enterprise MDM (Informatica, Profisee, Reltio)
**What it is:** Master Data Management platforms for large enterprises
**Strengths:**
- Production-proven at scale
- Enterprise support and SLAs
- Advanced governance and workflow

**Weaknesses (Why NOT Use):**
- **Cost:** $100K+ annually (licensing + implementation)
- **Complexity:** 6-month implementation, requires consultants
- **Procurement:** IT/legal approval, multi-year contracts
- **Overkill:** Too heavy for MVP/prototype use cases
- **Cloud-only:** Often SaaS, not self-hosted

**Evidence:** Research shows mid-sized companies abandon enterprise MDM due to cost and complexity, resort to custom solutions

---

#### Solution B: Python Libraries (dedupe.io, splink)
**What it is:** Open-source Python libraries for record linkage and deduplication
**Strengths:**
- Free and open-source
- Production-quality algorithms (Fellegi-Sunter, probabilistic matching)
- Self-hosted

**Weaknesses (Why NOT Use):**
- **No NER:** Only matches records you already have, doesn't extract from text
- **No Service:** Python library only, not a REST API service
- **Single Domain:** Requires training per domain (companies, products, people)
- **No Canonical IDs:** Outputs match probability, not a canonical GUID system
- **Code Required:** Must write glue code for every use case

**Evidence:** Research documents use splink for Stage 6 (probabilistic), but it's a component, not a complete solution

---

#### Solution C: Custom Heuristics + Manual Rules
**What it is:** Teams write custom entity resolution code per domain
**Strengths:**
- Full control
- No external dependencies
- Can optimize for specific use case

**Weaknesses (Why NOT Use):**
- **Brittle:** Breaks on edge cases (typos, abbreviations, new entities)
- **Domain-Specific:** Must rewrite for each entity type
- **Maintenance:** Requires constant tuning as data evolves
- **Low Recall:** Misses entities that don't match exact rules
- **No Learning:** Doesn't improve over time

**Evidence:** This is what users do today when enterprise MDM too expensive - it's painful

---

### 3. What We're NOT Building (Clear Boundaries)

**NOT:**
1. ❌ **NOT** an enterprise governance platform (no workflows, approvals, data stewardship UI)
2. ❌ **NOT** a replacement for Neo4j/specialized graph databases (graph is optional Stage 7)
3. ❌ **NOT** a comprehensive Knowledge Graph construction platform (focuses on entity resolution, not full KG)
4. ❌ **NOT** a data quality/profiling tool (focused on entity matching, not broader data quality)
5. ❌ **NOT** a multi-tenant SaaS (self-hosted Docker, single-tenant deployment)
6. ❌ **NOT** a training platform for custom ML models (zero/few-shot, no model training required)
7. ❌ **NOT** supporting every entity type out-of-box (arbitrary domains via zero-shot, not pre-trained)

**In Scope:**
- ✅ Extract entities from text (NER via GLiNER)
- ✅ Resolve to canonical IDs OR create new entities
- ✅ CRUD operations (create, read, update, delete, merge entities)
- ✅ Multi-domain support (companies, products, people, custom)
- ✅ Self-hosted Docker deployment
- ✅ REST API + FastMCP wrapper for LLMs
- ✅ Hybrid matching (exact, fuzzy, vector, probabilistic, optional graph)

---

### 4. 10x Simpler Than Alternatives

**Our Solution:**
- **Cost:** $0 (open-source, self-hosted)
- **Time to Value:** Days (not months)
- **Deployment:** `docker-compose up` (not 6-month implementation)
- **Multi-Domain:** Zero-shot (not per-domain training)
- **API-First:** REST + MCP (not Python library requiring glue code)

**Comparison:**

| Aspect | Enterprise MDM | dedupe.io/splink | Our Solution |
|--------|----------------|------------------|--------------|
| Cost | $100K+/year | Free | Free |
| Implementation | 6 months | Weeks (code) | Days (Docker) |
| Deployment | SaaS or complex on-prem | Python library | Docker Compose |
| NER | ✅ (sometimes) | ❌ No | ✅ GLiNER |
| Multi-Domain | ✅ Pre-configured | ❌ Train per domain | ✅ Zero-shot |
| Canonical IDs | ✅ Yes | ❌ No (just probabilities) | ✅ UUID system |
| LLM Integration | ❌ No | ❌ No | ✅ FastMCP |
| Self-Hosted | ⚠️ Complex | ✅ Library only | ✅ Docker |

**10x Factor:**
- 100x cheaper ($100K → $0)
- 30x faster (6 months → 1 week)
- 10x simpler (complex enterprise platform → Docker Compose)
- Zero-shot vs per-domain training

---

### 5. Evidence This is Real

**Research Validation:**
- 6 research documents reviewed covering entity resolution, NER, hybrid systems
- Research consensus: Multi-stage pipeline (exact → fuzzy → vector → probabilistic → graph)
- GLiNER validated for zero-shot NER (research: `claude_enhanced-ner-proposal-v2.md`)
- Hybrid retrieval (dense + sparse) validated (research: `chatgpt_canonical-entity-id-service.md`)
- Legal domain case study shows 7-stage pipeline achieves >90% accuracy (research: `claude_legal-prd.md`)

**User Request:**
- User explicitly documented this problem in `initial-problem.md`
- User has research backing the approach
- User needs self-hosted solution (not SaaS)
- User wants FastMCP integration (LLM use case)

**Market Evidence:**
- Enterprise MDM market exists ($5B+) - proves demand
- Open-source alternatives (dedupe.io, splink) have active communities - proves pain
- Gap: No unified service combining NER + resolution + canonical IDs + self-hosted + API

---

### 6. Success Criteria (How We Know It Works)

**Technical:**
- [ ] >90% accuracy on test dataset (entity matching correctness)
- [ ] <500ms p95 latency (match requests through full pipeline)
- [ ] Multi-domain validation (works on 2+ domains: companies, products)
- [ ] 7-stage pipeline works end-to-end (exact → graph)
- [ ] FastMCP integration (Claude/GPT-4 can use as tools)
- [ ] Self-hosted deployment (single `docker-compose up` command)

**User Validation:**
- [ ] User can extract entities from arbitrary text
- [ ] User can resolve entities to canonical IDs OR create new
- [ ] User can CRUD/MERGE entities via REST API
- [ ] User can integrate with LLMs via FastMCP
- [ ] User deploys in <1 day (vs 6 months for enterprise MDM)

**Decision Gate:**
- After Bullet #6 (reranking): If accuracy <85%, evaluate architecture
- After Bullet #8 (graph): If accuracy <90%, add LLM (Bullet #9)
- After Bullet #10 (FastMCP): If LLM integration works, ship MVP

---

### 7. SEED Phase Verdict

✅ **APPROVED - Proceed to DESIGN Phase**

**Justification:**
1. ✅ ONE specific problem for ONE specific user (platform engineers need entity intelligence)
2. ✅ THREE existing solutions evaluated (enterprise MDM, Python libraries, custom code)
3. ✅ Clear boundaries (NOT enterprise governance, NOT full KG platform)
4. ✅ 10x simpler (cost, time, complexity vs alternatives)
5. ✅ Evidence of demand (research, user request, market gap)
6. ✅ Measurable success criteria (>90% accuracy, <500ms latency, multi-domain)

**Risk Factors:**
- ⚠️ Accuracy: May need LLM integration (Bullet #9) if 7-stage pipeline <90%
- ⚠️ Complexity: Graph boosting (Bullet #8) may not justify operational cost
- ⚠️ Adoption: Requires users comfortable with Docker/self-hosting

**Mitigation:**
- Tracer bullets allow early validation (can stop at Bullet #6 if good enough)
- Optional stages (graph, LLM) defer complexity until proven necessary
- Docker Compose deployment keeps self-hosting simple

---

### 8. Key Insights from SEED

**What makes this valuable:**
- Fills gap between expensive enterprise MDM and low-level Python libraries
- Zero-shot approach (GLiNER for NER, arbitrary domains) eliminates per-domain training
- Unified service (NER + resolution + canonical IDs) in single API
- LLM-ready (FastMCP) enables new use cases (conversational entity management)

**What makes this achievable:**
- Research-backed architecture (7-stage pipeline validated)
- Lightweight tech stack (EmbeddingGemma 308M, CPU-friendly)
- BEACON tracer bullets (daily-shippable increments)
- Clear escape hatches (can disable stages, upgrade models)

**Why build this now:**
- LLM applications need entity resolution (RAG, knowledge graphs)
- Self-hosted AI trend (users want local control)
- Open-source ML models mature (GLiNER, EmbeddingGemma production-ready)
- Gap in market (no open-source unified entity intelligence service)

---

## Next Phase: DESIGN

SEED phase validated the idea. Now DESIGN phase decomposes into tracer bullets:

**DESIGN Deliverables:**
- [x] Architecture document (`01-final-architecture-document.md`)
- [x] ADRs for major decisions (ADR-001 through ADR-008)
- [x] Tracer bullet decomposition (10 bullets, 40-48 hours)
- [x] Initial roadmap (`Roadmap/README.md`)

**Status:** DESIGN phase complete, ready for BUILD phase (Bullet #1)

---

*SEED Evaluation: 2025-10-07*
*Approved by: Claude (BEACON Framework Assistant)*
*Next Review: After Bullet #6 (validate MVP core accuracy)*
