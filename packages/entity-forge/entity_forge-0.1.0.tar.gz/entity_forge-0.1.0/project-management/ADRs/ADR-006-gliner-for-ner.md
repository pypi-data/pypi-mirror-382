# ADR-006: GLiNER for Zero-Shot Named Entity Recognition

**Status:** Accepted

**Date:** 2025-10-07

**Deciders:** Architecture Team

**Context:**
The Entity Intelligence Service requires Named Entity Recognition (NER) to extract entities from arbitrary text inputs before resolution. Requirements:
- Zero/few-shot learning (no training per domain)
- Arbitrary entity types (companies, products, people, locations, custom domains)
- Self-hosted inference (no API calls)
- Lightweight enough for CPU inference
- High recall (better to over-extract than miss entities)

Options considered:
- **Option A**: GLiNER (generalist zero-shot NER)
- **Option B**: spaCy with transformer models (requires training per domain)
- **Option C**: Flair NER (slower, heavier)
- **Option D**: LLM-based extraction (high latency, deferred to Bullet #9)

## Decision

Use **GLiNER (Generalist and Lightweight Named Entity Recognition)** for zero-shot entity extraction.

**Model Choice:** Start with `gliner_multi-v2.1` (multilingual, 209M params) for MVP, upgrade to `gliner_large-v2.1` (459M params) if recall insufficient.

## Rationale

**Pros of GLiNER:**
- **Zero-shot**: Works on arbitrary entity types without training ("extract: company, product, technology")
- **Arbitrary Types**: Define entity labels at inference time, not training
- **Lightweight**: 209M params (multi) or 459M params (large) - runs on CPU
- **Fast Inference**: 100-200ms for typical documents on CPU
- **Multilingual**: gliner_multi supports 100+ languages
- **High Recall**: Generalist approach tends to over-extract (good for matching stage)
- **Self-Hosted**: HuggingFace model, no API calls
- **Research Validated**: Mentioned in `claude_enhanced-ner-proposal-v2.md` research

**Why not spaCy:**
- Requires training per domain (not zero-shot)
- Entity types fixed at training time
- Would need separate model for companies, products, people, etc.
- Defeats "arbitrary domain" requirement

**Why not Flair:**
- Slower inference (LSTM-based, not transformer efficient)
- Heavier models (>1GB)
- Not zero-shot (requires training per domain)

**Why not LLM-based:**
- High latency (500-2000ms per extraction)
- More expensive (API costs or GPU hosting)
- Deferred to Bullet #9 for difficult cases

## Consequences

### Positive:
- Works across arbitrary domains immediately
- No training pipeline needed
- Fast inference on CPU (<200ms)
- High recall (catches more entities than precision-focused models)
- Multilingual support
- Easy to add new entity types (just change labels)

### Negative:
- Lower precision than domain-trained models (over-extracts)
- May extract false positives (mitigated by resolution stage)
- 209M-459M params requires ~500MB-1GB RAM

### Neutral:
- Over-extraction acceptable (resolution stage filters)
- Can upgrade to larger model if recall insufficient

## Escape Hatch

If GLiNER recall <80% on test dataset:
1. Upgrade from `gliner_multi-v2.1` (209M) to `gliner_large-v2.1` (459M)
2. Fine-tune GLiNER on domain-specific examples (GLiNER supports fine-tuning)
3. Hybrid approach: GLiNER + LLM for difficult cases (Bullet #9)

If GLiNER precision too low (>50% false positives):
1. Add confidence threshold filtering
2. Use resolution pipeline to filter unlikely matches
3. Consider domain-specific spaCy model as alternative

## Implementation Notes

### Model Loading
```python
from gliner import GLiNER

# Load model once at startup
model = GLiNER.from_pretrained("urchade/gliner_multi-v2.1")  # or gliner_large-v2.1

# For production: Cache model in Docker image
# Dockerfile:
# RUN python -c "from gliner import GLiNER; GLiNER.from_pretrained('urchade/gliner_multi-v2.1')"
```

### Zero-Shot Entity Extraction
```python
def extract_entities(text: str, entity_types: list[str]) -> list[Entity]:
    """
    Extract entities of arbitrary types from text.

    Args:
        text: Input text (e.g., "IBM announced a partnership with Microsoft")
        entity_types: Entity types to extract (e.g., ["company", "product"])

    Returns:
        List of extracted entities with labels and spans
    """
    # GLiNER returns: [{"text": "IBM", "label": "company", "start": 0, "end": 3}, ...]
    entities = model.predict_entities(
        text,
        labels=entity_types,
        threshold=0.5  # Confidence threshold (0.0-1.0)
    )

    return [
        Entity(
            text=ent["text"],
            kind=ent["label"],
            start_char=ent["start"],
            end_char=ent["end"],
            confidence=ent.get("score", 1.0)
        )
        for ent in entities
    ]
```

### API Endpoint Integration
```python
from pydantic import BaseModel

class ExtractRequest(BaseModel):
    text: str
    entity_types: list[str] = ["company", "person", "product", "location"]

@app.post("/extract")
async def extract_endpoint(request: ExtractRequest):
    """Extract entities from text using GLiNER"""
    entities = extract_entities(request.text, request.entity_types)

    # For each extracted entity, attempt to resolve to canonical ID
    results = []
    for entity in entities:
        match_result = await resolve_entity(
            kind=entity.kind,
            text=entity.text,
            context={"source_text": request.text}
        )
        results.append({
            "extracted_text": entity.text,
            "entity_type": entity.kind,
            "match": match_result  # Canonical ID or None (create new)
        })

    return {"entities": results}
```

### Domain-Specific Entity Types
```python
# Companies domain
company_types = ["company", "corporation", "organization"]

# Legal domain
legal_types = ["party", "plaintiff", "defendant", "law_firm", "judge"]

# Scientific domain
science_types = ["chemical", "protein", "gene", "disease", "drug"]

# Pop culture domain
popculture_types = ["character", "franchise", "creator", "publisher"]

# API allows user to specify domain OR custom types
@app.post("/extract")
async def extract_endpoint(
    request: ExtractRequest,
    domain: str | None = None
):
    if domain == "companies":
        entity_types = company_types
    elif domain == "legal":
        entity_types = legal_types
    elif domain == "custom":
        entity_types = request.entity_types  # User-provided
    else:
        # Default: general-purpose types
        entity_types = ["company", "person", "product", "location", "organization"]

    entities = extract_entities(request.text, entity_types)
    ...
```

### Batch Processing for Performance
```python
def extract_entities_batch(texts: list[str], entity_types: list[str]) -> list[list[Entity]]:
    """Process multiple texts in batch for better throughput"""
    batch_results = model.batch_predict_entities(
        texts,
        labels=entity_types,
        threshold=0.5,
        batch_size=8  # Adjust based on available RAM
    )

    return [
        [Entity(text=ent["text"], kind=ent["label"], ...) for ent in results]
        for results in batch_results
    ]
```

## Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| Inference latency | <200ms | Per document (100-500 words) on CPU |
| Recall | >80% | Catches 80%+ of relevant entities |
| Precision | >50% | Acceptable (resolution filters false positives) |
| Memory | <1GB | Model + inference overhead |
| Throughput | >10 docs/s | Batch processing on single CPU |

## Model Comparison

| Model | Params | RAM | Latency | Languages | Zero-Shot |
|-------|--------|-----|---------|-----------|-----------|
| gliner_multi-v2.1 | 209M | ~500MB | ~100ms | 100+ | ✅ |
| gliner_large-v2.1 | 459M | ~1GB | ~200ms | 100+ | ✅ |
| spaCy en_core_web_trf | 460M | ~1GB | ~150ms | 1 (English) | ❌ (requires training) |
| Flair NER | 1.1GB | ~2GB | ~500ms | Many | ❌ (requires training) |

**Decision:** Start with `gliner_multi-v2.1` for MVP (lighter, faster), upgrade to `gliner_large-v2.1` if recall insufficient.

## Integration with Resolution Pipeline

GLiNER provides the **input** to the 7-stage resolution pipeline:

```python
async def extract_and_resolve(text: str, entity_types: list[str]) -> list[dict]:
    """Complete pipeline: Extract → Resolve → Return canonical IDs"""

    # Stage 1: Extract entities with GLiNER
    extracted = extract_entities(text, entity_types)

    # Stage 2: For each extracted entity, run through resolution pipeline
    results = []
    for entity in extracted:
        match_result = await resolution_pipeline.resolve(
            kind=entity.kind,
            canonical_name=entity.text,
            context={"source_text": text}
        )

        results.append({
            "extracted_text": entity.text,
            "entity_type": entity.kind,
            "canonical_id": match_result.entity_id if match_result else None,
            "confidence": match_result.confidence if match_result else 0.0,
            "canonical_name": match_result.canonical_name if match_result else None
        })

    return results
```

## Fine-Tuning Strategy (Future)

If domain-specific accuracy required:
1. Collect labeled examples (100-1000 entities per type)
2. Fine-tune GLiNER on domain data:
```python
from gliner import GLiNER

model = GLiNER.from_pretrained("urchade/gliner_multi-v2.1")

# Fine-tune on domain examples
model.train(
    train_data=domain_examples,
    epochs=5,
    batch_size=8
)

model.save_pretrained("./models/gliner-finetuned-companies")
```
3. Evaluate on held-out test set
4. Deploy if F1 > 85%

## Alternatives Considered

### spaCy with Transformers
- **Pros**: Production-proven, fast, good accuracy when trained
- **Cons**: Requires training per domain, not zero-shot, fixed entity types
- **Decision**: GLiNER's zero-shot capability better for arbitrary domains

### Flair NER
- **Pros**: Good accuracy, supports many languages
- **Cons**: Slow inference, requires training, heavier models
- **Decision**: GLiNER faster and zero-shot

### LLM-based Extraction (Bullet #9)
- **Pros**: Highest accuracy, best for ambiguous cases
- **Cons**: High latency (500-2000ms), requires LLM infrastructure
- **Decision**: Defer to Bullet #9, use GLiNER for MVP

### Hugging Face Transformers (NER pipeline)
- **Pros**: Easy to use, many pre-trained models
- **Cons**: Models trained on fixed entity types (PER, ORG, LOC), not arbitrary
- **Decision**: GLiNER allows custom entity types at inference

## References

- [GLiNER Repository](https://github.com/urchade/GLiNER)
- [GLiNER Paper: "Generalist and Lightweight Model for Named Entity Recognition"](https://arxiv.org/abs/2311.08526)
- [GLiNER Models on HuggingFace](https://huggingface.co/urchade)
- Research: `claude_enhanced-ner-proposal-v2.md` (recommends GLiNER for zero-shot)
- Research: `claude_llm-pipeline.md` (uses GLiNER + REBEL for extraction)
- BEACON Principle: Simplicity - zero-shot beats custom training for MVP

## Review Date

After Bullet #4 (vector search implemented): Measure GLiNER recall/precision on test dataset.
- If recall ≥ 80%: Continue with gliner_multi-v2.1
- If recall < 80%: Upgrade to gliner_large-v2.1 or consider fine-tuning
- If precision < 50%: Add confidence thresholding or resolution filtering
