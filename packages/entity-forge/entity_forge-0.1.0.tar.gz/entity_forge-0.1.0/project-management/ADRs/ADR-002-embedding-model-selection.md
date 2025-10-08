# ADR-002: EmbeddingGemma-308M for Dense Embeddings

**Status:** Accepted

**Date:** 2025-10-07

**Deciders:** Architecture Team

**Context:**
The Entity Intelligence Service requires dense vector embeddings for semantic entity matching. Requirements:
- Lightweight (runs on CPU or modest GPU)
- Multilingual support (100+ languages)
- Good accuracy for entity resolution
- Self-hosted (no external API calls)
- Fine-tunable for domain adaptation

Options considered:
- **Option A**: EmbeddingGemma-308M (308M params, lightweight)
- **Option B**: Qwen3-Embedding-4B (4B params, SOTA MTEB)
- **Option C**: OpenAI text-embedding-3-small (API-based)

## Decision

Use **EmbeddingGemma-308M** as the embedding model for MVP, with upgrade path to Qwen3-Embedding-4B if accuracy insufficient.

**Reranker**: Use `cross-encoder/ms-marco-MiniLM-L-12-v2` for cross-encoder reranking (proven, smaller than Qwen3-Reranker-4B).

## Rationale

**Pros of EmbeddingGemma-308M:**
- **Lightweight**: 308M params, <200MB RAM with quantization
- **CPU-friendly**: Runs efficiently without GPU for MVP
- **Multilingual**: 100+ languages out-of-box
- **Matryoshka representation**: Configurable dimensions (128, 256, 512, 768)
- **Best-in-class under 500M**: Top performer on MTEB for its size
- **Fine-tunable**: Can adapt to domain-specific entity types
- **Apache 2.0 license**: Fully open-source
- **Fast inference**: Sufficient for <500ms latency target

**Why not Qwen3-Embedding-4B:**
- 4B parameters (13× larger)
- Requires GPU or high-end CPU
- Overkill for MVP
- Can upgrade if EmbeddingGemma < 85% accuracy
- Higher operational complexity

**Why not OpenAI API:**
- External dependency (violates self-hosted requirement)
- Cost per embedding
- Network latency
- No fine-tuning capability
- Data privacy concerns

## Consequences

### Positive:
- Low resource requirements (runs on laptop)
- Fast development iteration (quick model loading)
- Multilingual by default
- Can fine-tune on domain data
- Matryoshka allows dimension optimization (trade size/accuracy)

### Negative:
- Accuracy may be lower than SOTA models (Qwen3-Embedding-4B)
- 8K context max (vs 32K for Qwen3)
- Newer model (less battle-tested than sentence-transformers)

### Neutral:
- Sufficient for MVP validation
- Clear upgrade path if needed

## Escape Hatch

If EmbeddingGemma-308M achieves <85% matching accuracy:
1. Upgrade to **Qwen3-Embedding-4B** (SOTA performance, 32K context)
2. Keep same architecture (pgvector, HNSW index)
3. Re-embed existing entities (one-time migration)
4. Evaluate accuracy improvement

Alternative escape: Fine-tune EmbeddingGemma-308M on domain-specific entity pairs before upgrading.

## Implementation Notes

### Model Loading
```python
from sentence_transformers import SentenceTransformer

embedder = SentenceTransformer(
    "google/embedding-gemma-308m",
    device="cpu",  # or "cuda" for GPU
    trust_remote_code=True
)
```

### Embedding Generation
```python
# Generate embeddings with normalization
embeddings = embedder.encode(
    texts,
    normalize_embeddings=True,  # For cosine similarity
    show_progress_bar=False,
    batch_size=32
)
```

### Matryoshka Dimension Selection
```python
# Start with 768 (full), can reduce to 256 or 128 if storage/speed critical
# Reduction via truncation: embedding[:256]
```

### Cross-Encoder Reranking
```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-12-v2",
    max_length=512
)

# Rerank top K candidates
scores = reranker.predict([
    (query_text, candidate_text)
    for candidate_text in candidate_texts
])
```

## Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| Embedding time | <50ms per entity | Batch of 32 |
| Accuracy | >85% on companies domain | Will measure in Bullet #4 |
| Recall@10 | >90% | Top 10 candidates include correct match |
| Latency contribution | <30ms | Part of 500ms total budget |

## Fine-Tuning Strategy (Future)

If accuracy insufficient before upgrading model:
1. Generate positive/negative entity pairs (1K-10K)
2. Fine-tune with contrastive loss
3. Evaluate on held-out test set
4. Deploy if F1 > 85%

Research shows 5-8% accuracy improvement possible through domain fine-tuning.

## Alternatives Considered

### Qwen3-Embedding-4B
- **Pros**: SOTA MTEB scores, 32K context, MRL support
- **Cons**: 4B params (heavy), requires GPU, slower inference
- **Decision**: Upgrade option if EmbeddingGemma insufficient

### sentence-transformers/all-MiniLM-L12-v2
- **Pros**: Widely used, proven, lightweight
- **Cons**: English-only, older architecture, lower accuracy than EmbeddingGemma
- **Decision**: EmbeddingGemma superior for multilingual + accuracy

### OpenAI text-embedding-3-small
- **Pros**: Good accuracy, no hosting required
- **Cons**: API cost, latency, no self-hosted, violates requirements
- **Decision**: Not viable for self-hosted requirement

## References

- [EmbeddingGemma Model Card](https://huggingface.co/google/embedding-gemma-308m)
- [MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard)
- Research: `claude_enhanced-ner-proposal-v2.md` (recommends EmbeddingGemma-308M)
- Research: `chatgpt_canonical-entity-id-service.md` (recommends Qwen3, we chose lighter for MVP)
- BEACON Principle: Simplicity first, can upgrade if proven necessary

## Review Date

After Bullet #4 (vector search implemented): Measure accuracy on test dataset.
- If accuracy ≥ 85%: Continue with EmbeddingGemma
- If accuracy < 85%: Evaluate fine-tuning vs upgrade to Qwen3-Embedding-4B
