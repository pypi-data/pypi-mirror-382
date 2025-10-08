# ADR-005: Defer LLM Integration to Bullet #9 with OpenAI-Compatible API

**Status:** Accepted

**Date:** 2025-10-07

**Deciders:** Architecture Team

**Context:**
The Entity Intelligence Service includes LLM capabilities for:
- Domain identification (e.g., "Is this a company, person, or product?")
- Few-shot entity extraction enhancement
- Match adjudication when confidence is uncertain (0.6-0.8 range)
- Relationship proposal and entity discovery

LLMs add latency (200-500ms per call) and operational complexity (model hosting, API costs). Research documents show LLM integration as valuable but not critical for basic entity resolution.

Options considered:
- **Option A**: Integrate LLMs from Bullet #1 (comprehensive but complex)
- **Option B**: Defer to Bullet #9 (after core pipeline proven)
- **Option C**: No LLM integration (pure heuristic/ML)

LLM Infrastructure Options:
- **Dev Environment**: LM Studio (localhost:1234) for local testing
- **Production Options**: vLLM, OpenAI API, Anthropic API, self-hosted inference servers
- **API Standard**: OpenAI-compatible API for maximum flexibility

## Decision

**Defer LLM integration to Bullet #9** (after 7-stage resolution pipeline, reranking, probabilistic, and graph are proven) and **use OpenAI-compatible API standard** for flexible LLM infrastructure.

**LLM Infrastructure Strategy:**
- **Development**: LM Studio (localhost:1234) with models like Gemma 3n E2B-IT
- **Production**: Configurable OpenAI-compatible endpoint (vLLM, OpenAI, Anthropic, etc.)
- **Configuration-driven**: Environment-specific YAML for easy switching

## Rationale

**Why defer to Bullet #9:**
- **YAGNI Principle**: Prove entity resolution works without LLMs first
- **Complexity Management**: LLMs add hosting, latency, cost considerations
- **Incremental Validation**: Measure baseline accuracy before adding LLM boost
- **Latency Budget**: Reserve 200-500ms LLM latency for uncertain cases only
- **Clear Success Criteria**: If 7-stage pipeline achieves >90% accuracy, LLM optional
- **Faster MVP**: Bullets 1-8 can ship without LLM infrastructure

**Why OpenAI-compatible API:**
- **Maximum Flexibility**: Swap between providers without code changes
- **Development Simplicity**: LM Studio provides OpenAI-compatible endpoint locally
- **Production Options**: Use managed APIs (OpenAI, Anthropic) or self-hosted (vLLM)
- **Standard Protocol**: OpenAI API format is industry standard
- **Cost Control**: Can switch to cheaper providers or self-hosted as needed

**When LLM provides value:**
1. **Low-confidence matches** (0.6-0.8): "Is 'IBM Corp' the same as 'International Business Machines'?"
2. **Domain ambiguity**: "Is 'Apple' a company or a fruit in this context?"
3. **Relationship extraction**: "Extract mentions of people and companies from legal text"
4. **Few-shot adaptation**: "Here are 3 examples of products in this domain..."

**Baseline without LLM (Bullets 1-8):**
- Exact match → Expert rules → FTS → Fuzzy → Vector → Probabilistic → Graph
- Target: >85% accuracy without LLM (research suggests 80-90% achievable)
- If insufficient, add LLM in Bullet #9

## Consequences

### Positive:
- **Faster MVP**: Ship working system without LLM infrastructure
- **Clear Baseline**: Measure non-LLM performance first
- **Simpler Operations**: Fewer dependencies for initial deployment
- **Cost Control**: Defer LLM costs until proven necessary
- **Development Flexibility**: Use LM Studio locally, switch to production LLMs seamlessly
- **Provider Independence**: Not locked to single LLM vendor

### Negative:
- **Feature Delay**: Domain identification and adjudication come later
- **Potential Redesign**: If LLM proves critical, may need architecture adjustments
- **Two-Phase Development**: Must integrate LLM later (not upfront)

### Neutral:
- **Validation Strategy**: Bullet #8 completion triggers LLM evaluation
- **Clear Trigger**: If accuracy <85% after Bullet #8, prioritize LLM integration

## Implementation Strategy

### Configuration Management

**Development Configuration (LM Studio):**
```yaml
# config/dev.yaml
llm:
  enabled: false  # Disabled until Bullet #9
  api_base: "http://localhost:1234/v1"
  api_key: "not-needed"  # LM Studio doesn't require auth
  model: "gemma-3n-e2b-it"  # Or any model loaded in LM Studio
  max_tokens: 512
  temperature: 0.1  # Low temperature for deterministic matching
  timeout: 5.0  # 5 second timeout
```

**Production Configuration (Managed API):**
```yaml
# config/prod.yaml
llm:
  enabled: true
  api_base: "https://api.openai.com/v1"  # Or Anthropic, vLLM endpoint
  api_key: "${OPENAI_API_KEY}"  # Environment variable
  model: "gpt-4o-mini"  # Fast, cost-effective
  max_tokens: 512
  temperature: 0.1
  timeout: 5.0
```

**Production Configuration (Self-Hosted vLLM):**
```yaml
# config/prod-selfhosted.yaml
llm:
  enabled: true
  api_base: "http://vllm-service:8000/v1"  # Internal vLLM service
  api_key: "not-needed"
  model: "Qwen/Qwen2.5-7B-Instruct"  # Or any vLLM-compatible model
  max_tokens: 512
  temperature: 0.1
  timeout: 5.0
```

### OpenAI-Compatible Client Implementation

```python
from openai import AsyncOpenAI
from pydantic_settings import BaseSettings

class LLMSettings(BaseSettings):
    enabled: bool = False
    api_base: str = "http://localhost:1234/v1"
    api_key: str = "not-needed"
    model: str = "gemma-3n-e2b-it"
    max_tokens: int = 512
    temperature: float = 0.1
    timeout: float = 5.0

class LLMClient:
    def __init__(self, settings: LLMSettings):
        self.settings = settings
        if settings.enabled:
            self.client = AsyncOpenAI(
                base_url=settings.api_base,
                api_key=settings.api_key,
                timeout=settings.timeout
            )
        else:
            self.client = None

    async def adjudicate_match(
        self,
        query_entity: str,
        candidate_entity: str,
        context: dict
    ) -> dict:
        """Use LLM to adjudicate uncertain matches"""
        if not self.settings.enabled:
            return {"decision": "skip", "reason": "LLM disabled"}

        prompt = f"""
        Are these entities the same?

        Query: {query_entity}
        Candidate: {candidate_entity}
        Context: {context}

        Respond with JSON: {{"match": true/false, "confidence": 0.0-1.0, "reasoning": "..."}}
        """

        response = await self.client.chat.completions.create(
            model=self.settings.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=self.settings.max_tokens,
            temperature=self.settings.temperature
        )

        return parse_json_response(response.choices[0].message.content)
```

### Bullet #9 Integration Points

**Use Case 1: Domain Identification (NER enhancement)**
```python
async def identify_domain(text: str, llm: LLMClient) -> str:
    """Ask LLM to identify entity domain (person, company, product, etc.)"""
    if not llm.settings.enabled:
        return "unknown"  # Fall back to heuristics

    prompt = f"What type of entity is this? Options: person, company, product, location, other.\n\nText: {text}"
    response = await llm.client.chat.completions.create(...)
    return parse_domain(response)
```

**Use Case 2: Match Adjudication (low-confidence matches)**
```python
async def resolve_with_llm_fallback(
    query: Entity,
    candidates: list[Match],
    llm: LLMClient
) -> Match:
    """Use LLM when confidence is uncertain (0.6-0.8)"""
    top_match = candidates[0]

    if top_match.confidence > 0.8:
        return top_match  # High confidence, no LLM needed

    if top_match.confidence < 0.6:
        return None  # Too low, create new entity

    # Uncertain range (0.6-0.8): Ask LLM
    if llm.settings.enabled:
        decision = await llm.adjudicate_match(
            query_entity=query.canonical_name,
            candidate_entity=top_match.entity.canonical_name,
            context={"attributes": query.attributes}
        )
        if decision["match"]:
            top_match.confidence = decision["confidence"]
            return top_match

    return None  # Create new entity
```

**Use Case 3: Few-Shot Entity Extraction**
```python
async def extract_with_few_shot(
    text: str,
    examples: list[str],
    llm: LLMClient
) -> list[Entity]:
    """Use LLM for few-shot entity extraction in new domain"""
    if not llm.settings.enabled:
        return []  # Fall back to GLiNER zero-shot

    prompt = f"Extract entities like these examples:\n{examples}\n\nText: {text}"
    response = await llm.client.chat.completions.create(...)
    return parse_entities(response)
```

### Testing Strategy

**Development Testing with LM Studio:**
1. Start LM Studio with Gemma 3n E2B-IT
2. Enable LLM in config: `llm.enabled = true`
3. Test adjudication on uncertain matches (0.6-0.8 confidence)
4. Measure latency impact and accuracy lift

**Production Readiness:**
1. Benchmark latency: LM Studio (localhost) vs OpenAI API vs vLLM
2. Cost analysis: OpenAI API pricing vs self-hosted vLLM
3. Failover strategy: If LLM times out, fall back to non-LLM decision
4. Load testing: Can service handle LLM latency spike?

## Performance Targets (Bullet #9)

| Metric | Target | Notes |
|--------|--------|-------|
| LLM Latency | <500ms p95 | For adjudication calls only |
| LLM Hit Rate | <20% of requests | Only low-confidence matches |
| Accuracy Lift | +5-10% | Improvement over non-LLM baseline |
| Fallback Rate | <1% | LLM timeout/error fallback |

## Escape Hatch

**If LLM proves unnecessary:**
- Keep LLM disabled in config (`llm.enabled = false`)
- 7-stage pipeline already achieves >90% accuracy
- Remove LLM code in future refactor (but keep OpenAI client for future flexibility)

**If LLM proves critical:**
- Integrate earlier in pipeline (not just adjudication)
- Consider fine-tuned model for domain-specific tasks
- Explore smaller models (Qwen 2.5 7B, Phi-3, Gemma 3n) for lower latency

**If OpenAI API insufficient:**
- Implement custom protocol for specialized LLM servers
- Keep OpenAI as primary, add fallback protocols
- Unlikely: OpenAI API is industry standard

## Alternatives Considered

### Integrate LLM from Bullet #1
- **Pros**: Full capabilities available immediately
- **Cons**: Adds complexity before proving core pipeline works
- **Decision**: YAGNI - defer until proven necessary

### No LLM Integration
- **Pros**: Simplest architecture, no hosting complexity
- **Cons**: Misses potential accuracy gains, limits domain adaptation
- **Decision**: Keep option open, evaluate at Bullet #8

### Custom LLM Protocol (Not OpenAI-Compatible)
- **Pros**: Optimize for specific models (e.g., GGUF local inference)
- **Cons**: Lock-in to custom protocol, no provider flexibility
- **Decision**: OpenAI API is standard, provides flexibility

### Hardcoded vLLM
- **Pros**: Optimized for self-hosted inference
- **Cons**: Can't use LM Studio for dev, can't switch to OpenAI/Anthropic
- **Decision**: OpenAI-compatible API allows all options (including vLLM)

## References

- Research: `claude_legal-prd.md` (shows LLM for adjudication, optional)
- Research: `claude_enhanced-ner-proposal-v2.md` (local LLM with Gemma 3n)
- Research: `claude_llm-pipeline.md` (LLM-orchestrated extraction, advanced use case)
- [OpenAI API Specification](https://platform.openai.com/docs/api-reference)
- [LM Studio](https://lmstudio.ai/) - Local LLM inference with OpenAI-compatible API
- [vLLM](https://github.com/vllm-project/vllm) - Fast inference with OpenAI-compatible server
- BEACON Principle: YAGNI - build what's needed, add complexity when proven necessary

## Review Date

After Bullet #8 (graph boosting complete): Evaluate if LLM integration necessary.
- If accuracy ≥ 90%: LLM optional (nice-to-have for edge cases)
- If accuracy < 90%: Prioritize LLM integration in Bullet #9
- Measure accuracy lift: LLM vs non-LLM on same test dataset
