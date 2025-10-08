# ADR-003: Multi-Stage Resolution Pipeline

**Status:** Accepted

**Date:** 2025-10-07

**Deciders:** Architecture Team

**Context:**
Entity resolution requires balancing **accuracy** (finding correct matches) with **latency** (fast responses). Different matching techniques excel at different scenarios:
- Exact match: Fast (5ms), perfect precision, zero recall for variants
- Fuzzy match: Medium speed (50ms), handles typos, misses semantic similarity
- Vector search: Good semantic understanding, computationally expensive
- Probabilistic: High recall, complex multi-field matching, slower

Single-stage approaches force a one-size-fits-all tradeoff. Users report better results from hybrid systems that combine multiple techniques.

## Decision

Implement a **7-stage gracefully degrading resolution pipeline** with:
1. Early exit on high confidence (avoid unnecessary computation)
2. Reciprocal Rank Fusion (RRF) to combine results from multiple stages
3. Cross-encoder reranking for final precision boost
4. Configurable per-request (enable/disable stages)

### Pipeline Stages

| Stage | Method | Latency | Confidence | When to Use |
|-------|--------|---------|------------|-------------|
| 1 | Exact Match | <5ms | 1.0 | Normalized string equality |
| 2 | Expert Rules | <10ms | 0.95 | Domain-specific patterns (LLC, Inc, "Doe, John") |
| 3 | Full-Text Search | <20ms | 0.85 | Postgres FTS + pg_trgm |
| 4 | Fuzzy Matching | <50ms | 0.8 | RapidFuzz (typos, abbreviations) |
| 5 | Vector Similarity | <30ms | 0.75 | EmbeddingGemma + pgvector HNSW |
| 6 | Probabilistic | <200ms | 0.7 | Splink multi-field evidence |
| 7 | Graph Boosting | <100ms | 0.65 | Memgraph relationship context |

**Total worst-case latency**: ~400ms (within 500ms p95 target)

## Rationale

**Pros of multi-stage approach:**
- **Optimal latency/accuracy**: Fast stages handle easy cases, slow stages for hard cases
- **Early exit**: 80%+ matches resolved in <50ms (stages 1-4)
- **Graceful degradation**: System remains functional if a stage fails
- **Configurable**: Users can disable expensive stages for speed
- **Complementary strengths**: Each stage catches different match types
- **Research-validated**: Legal PRD shows 95%+ accuracy with this approach

**Why RRF fusion:**
- Parameter-free (no weights to tune)
- Handles varying result set sizes
- Formula: `score = sum(1/(60 + rank_i))` across all stages
- Proven effective in hybrid retrieval systems

**Why cross-encoder reranking:**
- Boosts precision by 10-15 points (research-validated)
- Only applied to top K candidates (efficient)
- Catches subtle semantic differences

## Consequences

### Positive:
- High accuracy (>90% target achievable)
- Fast for common cases (<50ms for 80%+ queries)
- Flexible (stages can be enabled/disabled per request)
- Explainable (audit trail shows which stage matched)
- Resilient (graceful degradation if stage fails)

### Negative:
- Complex implementation (7 stages to develop)
- More code to maintain
- Debugging more difficult (which stage failed?)
- Worst-case latency higher (400ms vs <100ms single-stage)

### Neutral:
- Staged delivery aligns with tracer bullet approach
- Each bullet adds one stage, works end-to-end

## Implementation Strategy

### Tracer Bullet Progression
- **Bullet #1**: Stage 1 only (exact match)
- **Bullet #2**: Add stage 4 (fuzzy, skip 2-3 for now)
- **Bullet #3**: Postgres persistence (foundation for stages 3, 5)
- **Bullet #4**: Add stage 5 (vector search)
- **Bullet #5**: Add stage 3 (FTS) + RRF fusion
- **Bullet #6**: Add cross-encoder reranking
- **Bullet #7**: Add stage 6 (probabilistic with Splink)
- **Bullet #8**: Add stage 7 (graph boosting with Memgraph)
- **Bullet #9**: Add stage 2 (expert rules, domain-specific)

### Pipeline Architecture
```python
class ResolutionPipeline:
    def __init__(self):
        self.stages = [
            ExactMatchStage(),
            ExpertRuleStage(),
            FullTextSearchStage(),
            FuzzyMatchingStage(),
            VectorSimilarityStage(),
            ProbabilisticLinkingStage(),
            GraphBoostingStage()
        ]

    async def resolve(self, entity: Entity, config: MatchConfig) -> MatchResult:
        results = []
        audit_trail = []

        for stage in self.stages:
            if not config.is_enabled(stage.name):
                continue

            stage_result = await stage.match(entity)
            audit_trail.append(stage_result.metrics)

            # Early exit on high confidence
            if stage_result.top_confidence >= stage.threshold:
                return MatchResult(
                    matches=stage_result.matches,
                    audit_trail=audit_trail,
                    method=stage.name
                )

            results.extend(stage_result.matches)

        # Fuse results via RRF
        fused = self.rrf_fusion(results)

        # Rerank top K
        reranked = await self.rerank(fused[:10], entity)

        return MatchResult(
            matches=reranked,
            audit_trail=audit_trail,
            method="multi_stage_fusion"
        )
```

### RRF Fusion Implementation
```python
def rrf_fusion(self, results: List[StageResult], k: int = 60) -> List[Match]:
    """Reciprocal Rank Fusion across all stages"""
    entity_scores = defaultdict(float)

    for stage_result in results:
        for rank, match in enumerate(stage_result.matches, start=1):
            entity_scores[match.entity_id] += 1.0 / (k + rank)

    # Sort by fused score descending
    return sorted(
        entity_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )
```

## Configuration

### Per-Request Configuration
```json
{
  "config": {
    "stages": ["exact", "fuzzy", "vector"],  // Enable specific stages
    "confidence_threshold": 0.7,
    "early_exit": true,                      // Exit on first high-confidence match
    "include_audit_trail": true
  }
}
```

### Service-Level Defaults
```yaml
resolution:
  stages:
    exact_match:
      enabled: true
      confidence_threshold: 1.0
    expert_rules:
      enabled: true
      confidence_threshold: 0.95
    full_text_search:
      enabled: true
      confidence_threshold: 0.85
    fuzzy_matching:
      enabled: true
      confidence_threshold: 0.8
    vector_similarity:
      enabled: true
      confidence_threshold: 0.75
    probabilistic_linking:
      enabled: true
      confidence_threshold: 0.7
    graph_boosting:
      enabled: false  # Expensive, enable when needed
      confidence_threshold: 0.65

  fusion:
    method: "rrf"
    k: 60

  reranking:
    enabled: true
    model: "cross-encoder/ms-marco-MiniLM-L-12-v2"
    top_k: 10
```

## Alternatives Considered

### Single-Stage (Vector Search Only)
- **Pros**: Simple, consistent latency
- **Cons**: Misses exact matches (waste of compute), lower accuracy
- **Decision**: Multi-stage provides better accuracy/latency tradeoff

### Two-Stage (Exact + Vector)
- **Pros**: Simpler than 7 stages
- **Cons**: Gap in matching capability (misses fuzzy/FTS patterns)
- **Decision**: 7 stages provide better coverage

### Learned Ensemble (ML model to fuse)
- **Pros**: Potentially better fusion than RRF
- **Cons**: Requires training data, model maintenance, overfitting risk
- **Decision**: RRF is parameter-free and proven effective

### Sequential (No parallel stage execution)
- **Pros**: Simpler to implement
- **Cons**: Higher latency (can't parallelize independent stages)
- **Decision**: Use async/await for parallel stage execution where possible

## Performance Monitoring

### Metrics to Track
- Stage execution time (p50, p95, p99)
- Stage hit rate (% of queries where stage finds match)
- Fusion effectiveness (how often fusion beats best single stage)
- Reranker lift (precision improvement from reranking)
- End-to-end latency distribution

### Success Criteria (Bullet #6+)
- 80%+ queries resolved in <50ms (early exit)
- 95%+ queries resolved in <500ms
- Overall accuracy >90% on test dataset
- Each stage contributes >5% unique matches

## References

- Research: `claude_legal-prd.md` (7-stage pipeline blueprint)
- Research: `chatgpt_canonical-entity-id-service.md` (RRF fusion formula)
- [RRF Paper](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf)
- [Cross-Encoder Reranking](https://www.sbert.net/examples/applications/cross-encoder/README.html)
- BEACON Principle: Tracer bullets - each bullet adds one stage

## Review Date

After Bullet #6 (hybrid fusion + reranking): Evaluate if 7 stages necessary or if some can be consolidated/removed.
