# ADR-004: FastAPI + Python for Service Layer

**Status:** Accepted

**Date:** 2025-10-07

**Deciders:** Architecture Team

**Context:**
The Entity Intelligence Service requires a web framework for RESTful API exposure with:

- Async I/O for concurrent database operations (PostgreSQL, vector search)
- Auto-generated OpenAPI documentation
- Strong Python ML ecosystem integration (transformers, sentence-transformers, splink)
- Type safety and modern Python features (3.11+)
- Low operational complexity for self-hosted deployment

Options considered:

- **Option A**: FastAPI + asyncpg (async Python)
- **Option B**: Go + Chi/Gin (compiled, fast)
- **Option C**: Rust + Actix-Web (maximum performance)
- **Option D**: Node.js + Express (JavaScript ecosystem)

## Decision

Use **FastAPI with Python 3.12+, asyncpg for database, and httpx for HTTP clients** as the service layer framework.

## Rationale

**Pros of FastAPI + Python:**

- **Async-first**: Native async/await for PostgreSQL (asyncpg), vector search, LLM calls
- **Auto-documentation**: OpenAPI/Swagger UI automatically generated from type hints
- **Type safety**: Pydantic models with runtime validation
- **ML ecosystem**: Direct access to transformers, sentence-transformers, splink, GLiNER
- **Rapid development**: Python's expressiveness accelerates MVP delivery
- **Research consensus**: All 6 research documents used Python examples
- **Dependency injection**: Built-in DI container for clean architecture
- **WebSocket support**: Can add real-time features if needed later

**Why not Go:**

- No native ML libraries (requires Python bindings via CGo)
- Smaller NLP/ML ecosystem
- Faster execution not critical for MVP (<500ms target achievable in Python)
- More verbose than Python for API endpoints

**Why not Rust:**

- Steep learning curve, slower development
- ML ecosystem immature (tokenizers exists, but limited sentence-transformers support)
- Overkill for MVP performance requirements
- Can rewrite performance-critical paths later if needed

**Why not Node.js:**

- Weaker ML ecosystem (mostly Python-first libraries)
- TypeScript adds complexity without Python's ML benefits
- Async patterns more mature in Python for this use case

## Consequences

### Positive:

- Rapid MVP development (tight Python ML integration)
- Type-safe API with Pydantic validation
- Auto-generated API documentation
- Single language for service + ML pipeline
- Large ecosystem for NLP/ML dependencies
- Easy deployment (Docker with uvicorn)

### Negative:

- Slower than compiled languages (Go/Rust)
- GIL limitations (mitigated by async I/O, not CPU-bound)
- Higher memory footprint than Go/Rust
- Python dependency management complexity

### Neutral:

- Performance sufficient for MVP (can optimize later)
- Clear upgrade path to compiled languages if needed

## Escape Hatch

If Python performance becomes bottleneck (>500ms p95 latency):

1. Profile to identify hot paths (likely: vector search, fuzzy matching)
2. Rewrite performance-critical paths in Rust (via PyO3) or Go
3. Keep FastAPI for API layer, call compiled code as extensions
4. Example: RapidFuzz already uses Rust under the hood via Cython

Alternative: Migrate to Go + Python sidecar for ML if language separation needed.

## Implementation Notes

### Project Structure

```
service/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── api/                 # API routes
│   │   ├── entities.py      # /entities endpoints
│   │   ├── match.py         # /match endpoints
│   │   └── health.py        # /health, /metrics
│   ├── core/                # Business logic
│   │   ├── resolution.py    # Multi-stage pipeline
│   │   ├── ner.py           # GLiNER integration
│   │   └── embeddings.py    # EmbeddingGemma wrapper
│   ├── db/                  # Database layer
│   │   ├── models.py        # SQLAlchemy models
│   │   └── repositories.py  # Data access
│   └── config.py            # Configuration management
├── tests/
├── pyproject.toml           # uv project file
└── Dockerfile
```

### FastAPI App Initialization

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncpg

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize connection pool
    app.state.db_pool = await asyncpg.create_pool(
        dsn=settings.database_url,
        min_size=5,
        max_size=20
    )
    # Load embedding model once
    app.state.embedder = SentenceTransformer(
        "google/embedding-gemma-308m",
        device="cpu"
    )
    yield
    # Shutdown: Close pool
    await app.state.db_pool.close()

app = FastAPI(
    title="Entity Intelligence Service",
    version="0.1.0",
    lifespan=lifespan
)
```

### Async Database Operations

```python
async def create_entity(pool: asyncpg.Pool, entity: EntityCreate) -> Entity:
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO entity (kind, canonical_name, attributes, embedding_text)
            VALUES ($1, $2, $3, $4)
            RETURNING entity_id, created_at
            """,
            entity.kind,
            entity.canonical_name,
            entity.attributes,
            entity.embedding
        )
        return Entity(entity_id=row['entity_id'], **entity.dict())
```

### Pydantic Models for Type Safety

```python
from pydantic import BaseModel, Field
from uuid import UUID

class EntityCreate(BaseModel):
    kind: str = Field(..., min_length=1, max_length=100)
    canonical_name: str = Field(..., min_length=1, max_length=500)
    aliases: list[str] = Field(default_factory=list)
    attributes: dict = Field(default_factory=dict)

class EntityResponse(EntityCreate):
    entity_id: UUID
    confidence: float
    created_at: datetime
```

### Dependency Injection for Clean Architecture

```python
from fastapi import Depends
import asyncpg

async def get_db_pool(request: Request) -> asyncpg.Pool:
    return request.app.state.db_pool

@app.post("/entities", response_model=EntityResponse)
async def create_entity_endpoint(
    entity: EntityCreate,
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    return await create_entity(pool, entity)
```

## Performance Targets

| Metric      | Target     | Notes                                |
| ----------- | ---------- | ------------------------------------ |
| API latency | <500ms p95 | Match requests through full pipeline |
| Throughput  | >100 req/s | Single instance on 2 CPU cores       |
| Memory      | <2GB       | Service + embeddings + models        |
| Cold start  | <10s       | Docker container startup             |

## Python Version and Dependencies

**Python Version:** 3.11+ (required for performance improvements and asyncpg compatibility)

**Core Dependencies:**

```toml
[project]
name = "entity-intelligence-service"
version = "0.1.0"
requires-python = ">=3.11"

dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "asyncpg>=0.30.0",
    "pydantic>=2.9.0",
    "pydantic-settings>=2.6.0",
    "httpx>=0.27.0",
    "sentence-transformers>=3.2.0",
    "rapidfuzz>=3.10.0",
    "gliner>=0.2.0",
]
```

## Deployment Configuration

### Docker

```dockerfile
FROM python:3.11-slim

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml .
RUN uv pip install --system -r pyproject.toml

COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Uvicorn Production Settings

```python
# For production deployment
uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 2 \
    --loop uvloop \
    --log-level info
```

## Alternatives Considered

### Go + Chi/Gin

- **Pros**: 3-5x faster execution, lower memory, simpler deployment
- **Cons**: No ML ecosystem, requires Python bridge for models
- **Decision**: Not viable without native ML support

### Rust + Actix-Web

- **Pros**: Maximum performance, memory safety, fearless concurrency
- **Cons**: Steep learning curve, immature ML ecosystem, slower development
- **Decision**: Overkill for MVP, can optimize later

### Node.js + Express

- **Pros**: Large ecosystem, async-native, good TypeScript support
- **Cons**: Weaker ML ecosystem, Python wrappers add complexity
- **Decision**: Python's ML advantage outweighs Node.js benefits

### Django + DRF

- **Pros**: Batteries-included, ORM, admin interface
- **Cons**: Synchronous by default, heavier framework, slower than FastAPI
- **Decision**: FastAPI's async-first design better for our I/O-bound workload

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [asyncpg](https://github.com/MagicStack/asyncpg) - Fastest PostgreSQL driver for Python
- [Pydantic](https://docs.pydantic.dev/) - Data validation via Python type hints
- Research: All 6 documents used Python examples (implicit consensus)
- BEACON Principle: Simplicity - use language with best ML ecosystem

## Review Date

After Bullet #5 (hybrid fusion implemented): Assess if Python performance acceptable for 500ms p95 target.

- If latency < 500ms p95: Continue with Python
- If latency > 500ms p95: Profile hot paths, consider Rust extensions for bottlenecks
