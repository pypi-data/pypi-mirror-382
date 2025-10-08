# ADR-008: FastMCP Wrapper for LLM Integration

**Status:** Accepted

**Date:** 2025-10-07

**Deciders:** Architecture Team

**Context:**
The Entity Intelligence Service should be accessible to LLMs (Claude, GPT-4, local models) via the Model Context Protocol (MCP). MCP enables LLMs to:
- Query for canonical entity IDs given text
- Create new entities discovered during conversation
- Resolve ambiguous entity mentions
- Access entity CRUD operations as tools

Requirements:
- Wrap existing REST API with MCP protocol
- Expose key operations as MCP tools (extract, match, create, update)
- Follow MCP best practices (clear tool descriptions, structured inputs/outputs)
- Self-hosted (no external dependencies)

Options considered:
- **Option A**: FastMCP Python library (wraps FastAPI)
- **Option B**: Custom MCP server implementation
- **Option C**: Use REST API directly (no MCP wrapper)

## Decision

Use **FastMCP to wrap the FastAPI service** and expose entity operations as MCP tools.

**Deployment Strategy:**
- Bullet #10: Add FastMCP wrapper after core pipeline proven
- Single Python codebase: FastAPI (HTTP) + FastMCP (MCP) share logic
- Optional deployment: Run with/without MCP based on use case

## Rationale

**Pros of FastMCP:**
- **Zero Boilerplate**: Automatically converts FastAPI endpoints to MCP tools
- **Single Codebase**: Share validation, business logic between HTTP and MCP
- **Type Safety**: Pydantic models ensure correct MCP tool schemas
- **Python Native**: Integrates seamlessly with existing FastAPI service
- **Async Support**: Works with async/await patterns
- **Automatic Documentation**: Tool descriptions from docstrings

**Why not custom MCP server:**
- More code to maintain
- Duplicates FastAPI endpoint logic
- FastMCP provides best practices out-of-box

**Why not REST only:**
- LLMs benefit from structured tool calling (MCP)
- MCP provides standardized protocol for tool discovery
- Better user experience than manual API calls

## Consequences

### Positive:
- **LLM Integration**: Claude, GPT-4, local LLMs can use service as tools
- **Code Reuse**: FastAPI and FastMCP share business logic
- **Standardized Protocol**: MCP handles tool discovery, invocation, errors
- **Easy Testing**: Test both HTTP and MCP interfaces

### Negative:
- **Additional Dependency**: FastMCP library to maintain
- **Two Protocols**: Need to understand both HTTP and MCP
- **MCP Clients Required**: Users need MCP-compatible LLM clients

### Neutral:
- **Optional Feature**: Service works fine without MCP
- **Can Remove**: If MCP proves unnecessary, easy to remove

## Implementation Strategy

### Project Structure
```
service/
├── app/
│   ├── main.py              # FastAPI app
│   ├── mcp.py               # FastMCP wrapper
│   ├── api/                 # Shared logic
│   │   ├── entities.py
│   │   └── match.py
│   └── core/                # Business logic
│       └── resolution.py
└── pyproject.toml
```

### FastMCP Integration
```python
# app/mcp.py
from fastmcp import FastMCP
from app.api.entities import EntityCreate, EntityResponse
from app.core.resolution import resolve_entity

# Create MCP server
mcp = FastMCP("Entity Intelligence Service")

@mcp.tool()
async def extract_and_match(
    text: str,
    entity_types: list[str] = ["company", "person", "product"]
) -> dict:
    """
    Extract entities from text and match to canonical IDs.

    Args:
        text: Input text containing entities
        entity_types: Types of entities to extract

    Returns:
        List of extracted entities with canonical IDs or new entity indicators
    """
    # Use existing business logic
    from app.core.ner import extract_entities
    from app.core.resolution import resolve_entity

    extracted = extract_entities(text, entity_types)
    results = []

    for entity in extracted:
        match = await resolve_entity(entity)
        results.append({
            "text": entity.text,
            "type": entity.kind,
            "canonical_id": match.entity_id if match else None,
            "canonical_name": match.canonical_name if match else None,
            "confidence": match.confidence if match else 0.0,
            "is_new": match is None
        })

    return {"entities": results}


@mcp.tool()
async def create_entity(
    kind: str,
    canonical_name: str,
    aliases: list[str] = [],
    attributes: dict = {}
) -> dict:
    """
    Create a new canonical entity.

    Args:
        kind: Entity type (e.g., "company", "person")
        canonical_name: Canonical name for the entity
        aliases: Alternative names
        attributes: Additional metadata (JSON object)

    Returns:
        Created entity with UUID
    """
    # Use existing business logic
    from app.core.entities import create_entity as _create

    entity = EntityCreate(
        kind=kind,
        canonical_name=canonical_name,
        aliases=aliases,
        attributes=attributes
    )

    result = await _create(entity)
    return result.dict()


@mcp.tool()
async def get_entity(entity_id: str) -> dict:
    """
    Retrieve entity by canonical ID.

    Args:
        entity_id: UUID of the entity

    Returns:
        Entity details including aliases and attributes
    """
    from app.core.entities import get_entity as _get

    entity = await _get(entity_id)
    if not entity:
        return {"error": "Entity not found"}

    return entity.dict()


@mcp.tool()
async def merge_entities(
    target_id: str,
    source_ids: list[str]
) -> dict:
    """
    Merge multiple entities into a single canonical entity.

    Args:
        target_id: UUID of target (surviving) entity
        source_ids: UUIDs of entities to merge into target

    Returns:
        Merged entity with combined aliases and attributes
    """
    from app.core.entities import merge_entities as _merge

    result = await _merge(target_id, source_ids)
    return result.dict()


# Run MCP server
if __name__ == "__main__":
    mcp.run()
```

### Dual-Mode Deployment

**Option 1: HTTP Only (FastAPI)**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Option 2: MCP Only**
```bash
python -m app.mcp
```

**Option 3: Both (Recommended)**
```yaml
# docker-compose.yml
services:
  entity-service-http:
    build: .
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"

  entity-service-mcp:
    build: .
    command: python -m app.mcp
    environment:
      - MCP_PORT=3000
    ports:
      - "3000:3000"
```

### MCP Client Usage Example

**With Claude Desktop:**
```json
{
  "mcpServers": {
    "entity-intelligence": {
      "command": "docker",
      "args": ["run", "-p", "3000:3000", "entity-service-mcp"]
    }
  }
}
```

**In Conversation:**
```
User: Extract companies from this text: "IBM and Microsoft announced a partnership"

Claude: I'll use the extract_and_match tool...
→ [Calls MCP tool: extract_and_match(text="...", entity_types=["company"])]
← Result: {
    "entities": [
      {"text": "IBM", "canonical_id": "uuid-123", "canonical_name": "International Business Machines Corporation"},
      {"text": "Microsoft", "canonical_id": "uuid-456", "canonical_name": "Microsoft Corporation"}
    ]
  }

Claude: I found two companies:
- IBM (canonical: International Business Machines Corporation)
- Microsoft (canonical: Microsoft Corporation)
```

## MCP Tool Design Principles

### 1. Clear Descriptions
```python
@mcp.tool()
async def extract_and_match(text: str) -> dict:
    """
    Extract entities from text and match to canonical IDs.

    This tool performs Named Entity Recognition (NER) followed by
    entity resolution to identify canonical entity IDs.

    Use this when:
    - User provides free text with entity mentions
    - You need to identify companies, people, or products
    - You want canonical IDs for master data management

    Args:
        text: Input text containing entities (e.g., "IBM announced...")

    Returns:
        List of extracted entities with:
        - text: Extracted mention
        - canonical_id: UUID if matched, None if new entity
        - confidence: Match confidence (0.0-1.0)
    """
```

### 2. Structured Inputs/Outputs
```python
from pydantic import BaseModel, Field

class ExtractRequest(BaseModel):
    text: str = Field(..., description="Text to extract entities from")
    entity_types: list[str] = Field(
        default=["company", "person", "product"],
        description="Types of entities to extract"
    )

class ExtractResponse(BaseModel):
    entities: list[dict] = Field(
        ...,
        description="Extracted entities with canonical IDs"
    )

@mcp.tool()
async def extract_and_match(request: ExtractRequest) -> ExtractResponse:
    """Extract entities from text"""
    ...
```

### 3. Error Handling
```python
@mcp.tool()
async def get_entity(entity_id: str) -> dict:
    """Retrieve entity by ID"""
    try:
        entity = await _get(entity_id)
        if not entity:
            return {
                "error": "not_found",
                "message": f"Entity {entity_id} not found"
            }
        return entity.dict()
    except ValueError as e:
        return {
            "error": "invalid_id",
            "message": str(e)
        }
```

## Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| Tool invocation latency | <10ms | MCP overhead only |
| End-to-end latency | <500ms | Same as HTTP API |
| Concurrent tools | >10 | Multiple LLM tool calls |

## Dependencies

```toml
[project.dependencies]
fastapi = ">=0.115.0"
fastmcp = ">=0.1.0"  # Add FastMCP
uvicorn = ">=0.32.0"
```

## Alternatives Considered

### Custom MCP Server Implementation
- **Pros**: Full control over MCP protocol
- **Cons**: Duplicates FastAPI logic, more code to maintain
- **Decision**: FastMCP reuses FastAPI logic, less code

### LangChain Tools
- **Pros**: Works with LangChain agents
- **Cons**: LangChain-specific, not MCP protocol standard
- **Decision**: MCP is protocol-agnostic, works with any LLM

### OpenAI Function Calling (No MCP)
- **Pros**: Works with OpenAI API directly
- **Cons**: OpenAI-specific, not self-hosted, not protocol standard
- **Decision**: MCP works with Claude, GPT-4, local LLMs

## Testing Strategy

### Unit Tests
```python
import pytest
from fastmcp.testing import MCPTestClient

@pytest.fixture
async def mcp_client():
    return MCPTestClient(mcp)

async def test_extract_and_match(mcp_client):
    result = await mcp_client.call_tool(
        "extract_and_match",
        text="IBM announced a partnership with Microsoft",
        entity_types=["company"]
    )

    assert len(result["entities"]) == 2
    assert result["entities"][0]["text"] == "IBM"
    assert result["entities"][0]["canonical_id"] is not None
```

### Integration Tests
```python
async def test_mcp_end_to_end():
    # Start MCP server
    async with MCPServer(mcp):
        # Connect LLM client
        client = MCPClient("http://localhost:3000")

        # Discover tools
        tools = await client.list_tools()
        assert "extract_and_match" in [t.name for t in tools]

        # Call tool
        result = await client.call_tool("extract_and_match", {...})
        assert result["entities"]
```

## Deployment Checklist

- [ ] FastMCP installed and configured
- [ ] All tools have clear descriptions
- [ ] Pydantic models for structured inputs/outputs
- [ ] Error handling for common failure modes
- [ ] Unit tests for each MCP tool
- [ ] Integration tests with MCP client
- [ ] Documentation for LLM users
- [ ] Docker image includes MCP server

## References

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Model Context Protocol (MCP)](https://spec.modelcontextprotocol.io/)
- [Anthropic MCP Guide](https://docs.anthropic.com/en/docs/build-with-claude/mcp)
- Research: `initial-problem.md` (explicitly requests FastMCP wrapper)
- BEACON Principle: Build what's requested, make it easy to use

## Review Date

After Bullet #10 (FastMCP wrapper implemented): Evaluate LLM integration quality.
- Does Claude/GPT-4 successfully use tools?
- Are tool descriptions clear enough?
- Is error handling sufficient?
- Should we add more tools (search, bulk operations)?
