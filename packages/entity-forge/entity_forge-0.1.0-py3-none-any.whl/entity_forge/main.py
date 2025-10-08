"""
Entity Forge - Main Application

Bullet #1: Hardcoded exact match endpoint
"""

from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI(
    title="Entity Forge",
    version="0.1.0",
    description="Entity intelligence service for NER and entity resolution",
)

# Hardcoded entity dictionary for Bullet #1
# Format: {(kind, canonical_name): entity_id}
HARDCODED_ENTITIES = {
    ("company", "IBM"): "550e8400-e29b-41d4-a716-446655440001",
    ("company", "Microsoft"): "550e8400-e29b-41d4-a716-446655440002",
    ("company", "Apple"): "550e8400-e29b-41d4-a716-446655440003",
    ("company", "Google"): "550e8400-e29b-41d4-a716-446655440004",
    ("person", "John Smith"): "550e8400-e29b-41d4-a716-446655440005",
    ("product", "iPhone"): "550e8400-e29b-41d4-a716-446655440006",
}


class MatchRequest(BaseModel):
    """Request model for entity matching"""

    text: str = Field(..., min_length=1, description="Entity text to match")
    kind: str = Field(
        ...,
        min_length=1,
        description="Entity type (e.g., 'company', 'person', 'product')",
    )


class MatchResponse(BaseModel):
    """Response model for entity matching"""

    canonical_id: Optional[str] = Field(
        None, description="UUID of canonical entity (None if no match)"
    )
    canonical_name: Optional[str] = Field(None, description="Canonical name of entity")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Match confidence score (0.0-1.0)"
    )
    method: str = Field(..., description="Matching method used")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "0.1.0", "bullet": 1}


@app.post("/match", response_model=MatchResponse)
async def match_entity(request: MatchRequest) -> MatchResponse:
    """
    Match entity text to canonical ID.

    Bullet #1: Exact match only (hardcoded dictionary)

    Args:
        request: Entity text and kind

    Returns:
        Canonical ID, name, confidence, and method
    """
    # Exact match lookup
    key = (request.kind, request.text)

    if key in HARDCODED_ENTITIES:
        # Exact match found
        return MatchResponse(
            canonical_id=HARDCODED_ENTITIES[key],
            canonical_name=request.text,
            confidence=1.0,
            method="exact",
        )
    else:
        # No match
        return MatchResponse(
            canonical_id=None, canonical_name=None, confidence=0.0, method="exact"
        )
