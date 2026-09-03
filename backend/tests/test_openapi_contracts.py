"""
Phase 10 — Component 6: OpenAPI Contract & Schema Validation
Verifies that every mounted API endpoint is properly documented in the OpenAPI schema,
error responses follow the standardized MediKioskException contract, and the schema itself
is a valid OpenAPI 3.x document.
"""
import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.main import app

client = TestClient(app)


# ============================================================================
# 1. OpenAPI Schema Export
# ============================================================================

def test_openapi_schema_is_valid_json():
    """GET /openapi.json returns a valid OpenAPI 3.x document."""
    res = client.get("/openapi.json")
    assert res.status_code == 200
    schema = res.json()
    assert "openapi" in schema
    assert schema["openapi"].startswith("3.")
    assert "info" in schema
    assert schema["info"]["title"] == "MediKiosk Clinical Intake API"
    assert "paths" in schema
    assert len(schema["paths"]) > 0


# ============================================================================
# 2. All Endpoints Documented
# ============================================================================

# The expected API surface area from router.py and all mounted endpoint files
EXPECTED_PATH_FRAGMENTS = [
    # Sessions (sessions.py)
    "/api/v1/sessions/",
    "/sessions/{session_id}",
    "/sessions/{session_id}/abha/initiate",
    "/sessions/{session_id}/abha/confirm",
    "/sessions/{session_id}/next-question",
    "/sessions/{session_id}/answer",
    "/sessions/{session_id}/voice/answer",
    "/sessions/{session_id}/ai/generate-summary",
    "/sessions/{session_id}/summary/review",
    "/sessions/{session_id}/summary",
    "/sessions/{session_id}/summary/stream",
    "/sessions/{session_id}/ai/structure-narration",
    # Consent (consent_router.py)
    "/sessions/{session_id}/consent",
    "/sessions/{session_id}/consent/revoke",
    # Documents (documents_router.py)
    "/sessions/{session_id}/documents/upload",
    "/sessions/{session_id}/documents",
    # Integration (integration_router.py)
    "/sessions/{session_id}/integration/prepare",
    "/sessions/{session_id}/integration/submit",
    "/sessions/{session_id}/integration/status",
    "/sessions/{session_id}/integration/bundle",
    # Voice (voice_router.py)
    "/voice/transcribe",
    "/voice/synthesize",
    "/voice/health",
    # Alerts (alerts_router.py)
    "/alerts",
    # Operations (ops_router.py)
    "/health",
    "/ready",
]


def test_all_expected_endpoints_documented_in_openapi():
    """Verify that every critical endpoint appears in the OpenAPI paths."""
    res = client.get("/openapi.json")
    schema = res.json()
    all_paths = list(schema["paths"].keys())
    all_paths_joined = " ".join(all_paths)

    missing = []
    for fragment in EXPECTED_PATH_FRAGMENTS:
        found = any(fragment in p for p in all_paths)
        if not found:
            missing.append(fragment)

    assert len(missing) == 0, f"Missing endpoints in OpenAPI schema: {missing}"


def test_openapi_paths_count_minimum():
    """The API must expose at least 25 documented path entries."""
    res = client.get("/openapi.json")
    schema = res.json()
    path_count = len(schema["paths"])
    assert path_count >= 25, f"Expected >=25 paths, found {path_count}"


# ============================================================================
# 3. Error Contract Consistency
# ============================================================================

def test_404_error_follows_standard_contract():
    """Non-existent session returns 404 with standardized error structure."""
    res = client.get("/api/v1/sessions/nonexistent_session_xyz")
    assert res.status_code == 404
    data = res.json()
    # Must follow MediKioskException contract
    assert "error_code" in data
    assert "message" in data
    assert data["error_code"] == "SESSION_NOT_FOUND"


def test_409_conflict_follows_standard_contract():
    """Duplicate session creation returns 409 with standardized error structure."""
    sid = "test_openapi_dup_001"
    pdo = {
        "version": "1.0.0",
        "identity": {
            "session_id": sid,
            "facility_id": "TEST_FAC",
            "preferred_language": "en",
            "gender": "MALE",
            "age": 30
        },
        "consent": {"scope": "INTAKE_AND_SUMMARY", "status": "GRANTED"}
    }
    client.post("/api/v1/sessions/", json=pdo)
    res2 = client.post("/api/v1/sessions/", json=pdo)
    assert res2.status_code == 409
    data = res2.json()
    assert "error_code" in data
    assert data["error_code"] == "SESSION_CONFLICT"


def test_422_validation_error_contract():
    """Invalid request body returns 422 with structured validation error."""
    res = client.post("/api/v1/sessions/", json={
        "version": "1.0.0"
        # Missing required 'identity' and 'consent'
    })
    assert res.status_code == 422
    data = res.json()
    assert "detail" in data or "error_code" in data
