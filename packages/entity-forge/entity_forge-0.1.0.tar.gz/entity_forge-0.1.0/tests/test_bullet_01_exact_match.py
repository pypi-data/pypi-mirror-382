"""
Acceptance Tests for Bullet #1: Hardcoded Exact Match

Success Criteria:
- FastAPI service runs on port 8000
- POST /match accepts entity text
- Returns hardcoded matches (in-memory dictionary)
- Includes confidence score (1.0 for exact, 0.0 for no match)
- Unit tests pass
- Can demo: "IBM" → canonical ID
"""

from fastapi.testclient import TestClient
from entity_forge.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["bullet"] == 1


def test_exact_match_ibm():
    """Test exact match for IBM"""
    response = client.post("/match", json={"text": "IBM", "kind": "company"})
    assert response.status_code == 200
    data = response.json()
    assert data["canonical_id"] == "550e8400-e29b-41d4-a716-446655440001"
    assert data["canonical_name"] == "IBM"
    assert data["confidence"] == 1.0
    assert data["method"] == "exact"


def test_exact_match_microsoft():
    """Test exact match for Microsoft"""
    response = client.post("/match", json={"text": "Microsoft", "kind": "company"})
    assert response.status_code == 200
    data = response.json()
    assert data["canonical_id"] == "550e8400-e29b-41d4-a716-446655440002"
    assert data["canonical_name"] == "Microsoft"
    assert data["confidence"] == 1.0
    assert data["method"] == "exact"


def test_exact_match_person():
    """Test exact match for person entity"""
    response = client.post("/match", json={"text": "John Smith", "kind": "person"})
    assert response.status_code == 200
    data = response.json()
    assert data["canonical_id"] == "550e8400-e29b-41d4-a716-446655440005"
    assert data["canonical_name"] == "John Smith"
    assert data["confidence"] == 1.0
    assert data["method"] == "exact"


def test_exact_match_product():
    """Test exact match for product entity"""
    response = client.post("/match", json={"text": "iPhone", "kind": "product"})
    assert response.status_code == 200
    data = response.json()
    assert data["canonical_id"] == "550e8400-e29b-41d4-a716-446655440006"
    assert data["canonical_name"] == "iPhone"
    assert data["confidence"] == 1.0
    assert data["method"] == "exact"


def test_no_match():
    """Test no match for unknown entity"""
    response = client.post("/match", json={"text": "UnknownCompany", "kind": "company"})
    assert response.status_code == 200
    data = response.json()
    assert data["canonical_id"] is None
    assert data["canonical_name"] is None
    assert data["confidence"] == 0.0
    assert data["method"] == "exact"


def test_case_sensitive():
    """Test that matching is case-sensitive (Bullet #1 limitation)"""
    response = client.post(
        "/match",
        json={"text": "ibm", "kind": "company"},  # lowercase
    )
    assert response.status_code == 200
    data = response.json()
    # Should NOT match (exact match is case-sensitive)
    assert data["canonical_id"] is None
    assert data["confidence"] == 0.0


def test_different_kind_no_match():
    """Test that kind matters for matching"""
    response = client.post(
        "/match",
        json={"text": "IBM", "kind": "person"},  # wrong kind
    )
    assert response.status_code == 200
    data = response.json()
    # Should NOT match (IBM is a company, not a person)
    assert data["canonical_id"] is None
    assert data["confidence"] == 0.0


def test_validation_empty_text():
    """Test validation for empty text"""
    response = client.post("/match", json={"text": "", "kind": "company"})
    assert response.status_code == 422  # Validation error


def test_validation_empty_kind():
    """Test validation for empty kind"""
    response = client.post("/match", json={"text": "IBM", "kind": ""})
    assert response.status_code == 422  # Validation error


def test_validation_missing_fields():
    """Test validation for missing required fields"""
    response = client.post(
        "/match",
        json={"text": "IBM"},  # missing kind
    )
    assert response.status_code == 422  # Validation error
