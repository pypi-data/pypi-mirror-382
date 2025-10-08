# Session: Bullet #1 - Hardcoded Exact Match

**Date:** 2025-10-07
**Duration:** ~1.5 hours
**Status:** ✅ COMPLETE
**Branch:** `feature/bullet-01-exact-match`

---

## Objective

Prove end-to-end plumbing works with hardcoded exact match endpoint.

**Success Criteria:**
- [x] FastAPI service runs on port 8000
- [x] POST `/match` accepts entity text
- [x] Returns hardcoded matches (in-memory dictionary)
- [x] Includes confidence score (1.0 for exact, 0.0 for no match)
- [x] Unit tests pass (11/11 passing)
- [x] Can demo: "IBM" → canonical ID

---

## What Was Built

### 1. Project Structure
```
/workspace/
├── src/all_the_things/
│   ├── __init__.py
│   └── main.py                    # FastAPI app with /match endpoint
├── tests/
│   └── test_bullet_01_exact_match.py  # 11 acceptance tests
├── pyproject.toml                 # uv project config (package: all-the-things)
└── .venv/                         # Virtual environment
```

### 2. Core Implementation

**File:** [src/all_the_things/main.py](../../src/all_the_things/main.py)

**Key Components:**
- `MatchRequest` model: Validates input (text, kind)
- `MatchResponse` model: Returns canonical_id, canonical_name, confidence, method
- `HARDCODED_ENTITIES` dictionary: 6 entities (companies, person, product)
- `/health` endpoint: Health check
- `/match` endpoint: Exact match lookup

**Hardcoded Entities:**
- IBM (company) → `550e8400-e29b-41d4-a716-446655440001`
- Microsoft (company) → `550e8400-e29b-41d4-a716-446655440002`
- Apple (company) → `550e8400-e29b-41d4-a716-446655440003`
- Google (company) → `550e8400-e29b-41d4-a716-446655440004`
- John Smith (person) → `550e8400-e29b-41d4-a716-446655440005`
- iPhone (product) → `550e8400-e29b-41d4-a716-446655440006`

### 3. Testing

**File:** [tests/test_bullet_01_exact_match.py](../../tests/test_bullet_01_exact_match.py)

**Test Coverage:** 11 tests, all passing ✅
1. `test_health_check` - Health endpoint returns 200
2. `test_exact_match_ibm` - Exact match for IBM company
3. `test_exact_match_microsoft` - Exact match for Microsoft
4. `test_exact_match_person` - Exact match for person entity
5. `test_exact_match_product` - Exact match for product entity
6. `test_no_match` - No match returns None with confidence 0.0
7. `test_case_sensitive` - Case sensitivity (lowercase "ibm" doesn't match)
8. `test_different_kind_no_match` - Kind matters (IBM as person doesn't match)
9. `test_validation_empty_text` - Validates empty text (422 error)
10. `test_validation_empty_kind` - Validates empty kind (422 error)
11. `test_validation_missing_fields` - Validates missing fields (422 error)

**Test Results:**
```
============================= test session starts ==============================
tests/test_bullet_01_exact_match.py::test_health_check PASSED            [  9%]
tests/test_bullet_01_exact_match.py::test_exact_match_ibm PASSED         [ 18%]
tests/test_bullet_01_exact_match.py::test_exact_match_microsoft PASSED   [ 27%]
tests/test_bullet_01_exact_match.py::test_exact_match_person PASSED      [ 36%]
tests/test_bullet_01_exact_match.py::test_exact_match_product PASSED     [ 45%]
tests/test_bullet_01_exact_match.py::test_no_match PASSED                [ 54%]
tests/test_bullet_01_exact_match.py::test_case_sensitive PASSED          [ 63%]
tests/test_bullet_01_exact_match.py::test_different_kind_no_match PASSED [ 72%]
tests/test_bullet_01_exact_match.py::test_validation_empty_text PASSED   [ 81%]
tests/test_bullet_01_exact_match.py::test_validation_empty_kind PASSED   [ 90%]
tests/test_bullet_01_exact_match.py::test_validation_missing_fields PASSED [100%]

============================== 11 passed in 0.22s
```

### 4. Demo

**Started server:**
```bash
uv run uvicorn all_the_things.main:app --host 0.0.0.0 --port 8000
```

**Manual Testing:**
```bash
# Health check
$ curl http://localhost:8000/health
{"status":"healthy","version":"0.1.0","bullet":1}

# Exact match - IBM
$ curl -X POST http://localhost:8000/match \
  -H "Content-Type: application/json" \
  -d '{"text": "IBM", "kind": "company"}'
{"canonical_id":"550e8400-e29b-41d4-a716-446655440001","canonical_name":"IBM","confidence":1.0,"method":"exact"}

# No match - Unknown company
$ curl -X POST http://localhost:8000/match \
  -H "Content-Type: application/json" \
  -d '{"text": "UnknownCompany", "kind": "company"}'
{"canonical_id":null,"canonical_name":null,"confidence":0.0,"method":"exact"}
```

---

## Key Decisions

### 1. Project Setup
- **Tool:** Used `uv` for dependency management (modern, fast)
- **Python Version:** 3.11+ (async support, modern features)
- **Dependencies:** FastAPI, uvicorn, pydantic (minimal for Bullet #1)

### 2. API Design
- **Endpoint:** POST `/match` (not GET - body required)
- **Request Model:** `{text: str, kind: str}` - simple, extensible
- **Response Model:** `{canonical_id, canonical_name, confidence, method}`
  - `canonical_id`: UUID string or null
  - `confidence`: 0.0-1.0 float
  - `method`: "exact" (will evolve: "fuzzy", "vector", etc.)

### 3. Validation
- Pydantic validation: Empty strings rejected (422 error)
- Missing fields rejected (422 error)
- Clean error messages via FastAPI

### 4. Testing Approach
- Test-first: Wrote acceptance tests before manual demo
- FastAPI TestClient: No need for actual HTTP server in tests
- 11 tests cover: happy paths, edge cases, validation

---

## Lessons Learned

### What Worked Well ✅
1. **uv is fast:** Setup and dependency installation < 2 minutes
2. **FastAPI + Pydantic:** Automatic validation and docs (OpenAPI at `/docs`)
3. **Test-first:** Caught issues early (import path correction)
4. **Simple dictionary:** Hardcoded approach proves plumbing without complexity
5. **Absolute imports:** Following project standard from the start

### What Needed Adjustment ⚠️
1. **Import paths:** Initially used `from src.all_the_things.main`, corrected to `from all_the_things.main` (absolute imports)
2. **Dependency groups:** Used correct `[dependency-groups]` format in pyproject.toml
3. **Package name:** Renamed from `entity-intelligence-service` to `all-the-things` (more memorable!)

### Known Limitations (By Design) 🔧
1. **Case sensitivity:** "IBM" matches, "ibm" doesn't (will fix in Bullet #2 with fuzzy)
2. **No typos:** "Microsft" doesn't match (will fix in Bullet #2)
3. **In-memory only:** No persistence (will fix in Bullet #3 with Postgres)
4. **Limited entities:** Only 6 hardcoded (will expand in future bullets)

---

## Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Time to Complete | 2-3h | ~1.5h | ✅ Under budget |
| Tests Passing | 100% | 11/11 (100%) | ✅ |
| Latency | <10ms | <5ms | ✅ (hardcoded lookup) |
| Coverage | N/A | Manual (will add in future) | - |

---

## Next Steps

### Immediate (Bullet #2)
- [ ] Install RapidFuzz library
- [ ] Add fuzzy matching stage (Levenshtein distance)
- [ ] Update tests: "Microsft" → Microsoft
- [ ] Handle case insensitivity
- [ ] Keep exact match as priority (fallback to fuzzy)

### Future Bullets
- Bullet #3: PostgreSQL persistence + CRUD
- Bullet #4: Vector search with EmbeddingGemma
- Bullet #5: Hybrid fusion (dense + sparse)
- Bullet #6: Cross-encoder reranking

---

## Artifacts Created

### Code
- [src/all_the_things/main.py](../../src/all_the_things/main.py) - 91 lines
- [src/all_the_things/__init__.py](../../src/all_the_things/__init__.py) - 3 lines
- [tests/test_bullet_01_exact_match.py](../../tests/test_bullet_01_exact_match.py) - 150 lines
- [pyproject.toml](../../pyproject.toml) - Package: all-the-things, CLI: aat

### Documentation
- This session document

### Git
- Branch: `feature/bullet-01-exact-match` (ready to commit)

---

## Would I Sign This? ✅ YES

**Quality Check:**
- [x] Tests pass (11/11)
- [x] Code is clean and readable
- [x] API works end-to-end
- [x] Documentation clear
- [x] Follows project conventions (absolute imports)
- [x] No broken windows
- [x] Ready to demo to user

**Confidence:** High - Bullet #1 objective achieved, foundation solid for Bullet #2.

---

*Session completed: 2025-10-07 13:10 UTC*
*Next session: Bullet #2 - Fuzzy Matching*
