"""
Phase 10 — Component 4: Failure Cascade & Resilience Tests
Verifies graceful degradation, proper error reporting, delivery failure state preservation,
and mid-flow consent revocation behavior.
"""
import os
import sys
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.main import app
from app.repositories.session_repository import session_repo

client = TestClient(app)


def _create_session(sid: str, gender: str = "MALE", age: int = 40) -> dict:
    return {
        "version": "1.0.0",
        "identity": {
            "session_id": sid,
            "facility_id": "RESILIENCE_TEST_FAC",
            "preferred_language": "en",
            "gender": gender,
            "age": age
        },
        "consent": {"scope": "INTAKE_AND_SUMMARY", "status": "GRANTED"}
    }


# ============================================================================
# 1. Invalid Session Access (404)
# ============================================================================

def test_get_nonexistent_session_returns_404():
    """Accessing a session that doesn't exist returns clean 404."""
    res = client.get("/api/v1/sessions/phantom_session_99999")
    assert res.status_code == 404
    assert res.json()["error_code"] == "SESSION_NOT_FOUND"


def test_answer_on_nonexistent_session_returns_404():
    """Submitting an answer to a non-existent session returns 404."""
    res = client.post("/api/v1/sessions/phantom_session_99999/answer", json={
        "question_id": "__CHIEF_COMPLAINT__",
        "free_text": "headache"
    })
    assert res.status_code == 404


def test_summary_on_nonexistent_session_returns_404():
    """Getting summary for non-existent session returns 404."""
    res = client.get("/api/v1/sessions/phantom_session_99999/summary")
    assert res.status_code == 404


# ============================================================================
# 2. Duplicate Session Creation (409 Conflict)
# ============================================================================

def test_duplicate_session_creation_returns_409():
    """Creating a session with an existing ID returns 409 Conflict."""
    sid = "test_resilience_dup_session"
    client.post("/api/v1/sessions/", json=_create_session(sid))
    res2 = client.post("/api/v1/sessions/", json=_create_session(sid))
    assert res2.status_code == 409
    assert res2.json()["error_code"] == "SESSION_CONFLICT"


# ============================================================================
# 3. Delivery Failure Preserves Session State for Retry
# ============================================================================

def test_delivery_failure_preserves_session_state():
    """
    When delivery to ABDM_SANDBOX fails (no credentials configured),
    the session data MUST be preserved for retry — NOT purged.
    """
    sid = "test_resilience_delivery_fail"
    client.post("/api/v1/sessions/", json=_create_session(sid))

    # Complete a minimal interview
    client.get(f"/api/v1/sessions/{sid}/next-question")
    client.post(f"/api/v1/sessions/{sid}/answer", json={
        "question_id": "__CHIEF_COMPLAINT__",
        "free_text": "Persistent headache for a week"
    })

    # Generate and approve summary
    client.post(f"/api/v1/sessions/{sid}/ai/generate-summary")
    client.post(f"/api/v1/sessions/{sid}/summary/review", json={
        "action": "ACCEPTED",
        "clinician_id": "DR_RESILIENCE_TEST"
    })

    # Grant HIS_SHARE consent
    client.post(f"/api/v1/sessions/{sid}/consent", json={
        "scope": "FULL_HIS_SHARE",
        "interaction_mode": "TOUCH_SCREEN"
    })

    # Submit to ABDM_SANDBOX (will fail since no credentials)
    res = client.post(f"/api/v1/sessions/{sid}/integration/submit?target=ABDM_SANDBOX")
    assert res.status_code == 200
    delivery_data = res.json()["delivery"]
    assert delivery_data["state"] == "FAILED"

    # Session MUST still exist (not purged)
    session_check = client.get(f"/api/v1/sessions/{sid}")
    assert session_check.status_code == 200


# ============================================================================
# 4. Consent Revocation Mid-Flow
# ============================================================================

def test_consent_revocation_blocks_subsequent_delivery():
    """
    If HIS_SHARE consent is granted, bundle is prepared, then consent is revoked,
    a subsequent prepare attempt must be blocked with 403.
    """
    sid = "test_resilience_consent_revoke"
    client.post("/api/v1/sessions/", json=_create_session(sid))

    # Interview + summary
    client.get(f"/api/v1/sessions/{sid}/next-question")
    client.post(f"/api/v1/sessions/{sid}/answer", json={
        "question_id": "__CHIEF_COMPLAINT__",
        "free_text": "Back pain"
    })
    client.post(f"/api/v1/sessions/{sid}/ai/generate-summary")
    client.post(f"/api/v1/sessions/{sid}/summary/review", json={
        "action": "ACCEPTED",
        "clinician_id": "DR_REVOKE_TEST"
    })

    # Grant HIS_SHARE consent
    client.post(f"/api/v1/sessions/{sid}/consent", json={
        "scope": "FULL_HIS_SHARE",
        "interaction_mode": "TOUCH_SCREEN"
    })

    # First prepare should succeed
    res1 = client.post(f"/api/v1/sessions/{sid}/integration/prepare")
    assert res1.status_code == 200
    assert res1.json()["success"] is True

    # Revoke consent
    client.post(f"/api/v1/sessions/{sid}/consent/revoke", json={
        "scope": "FULL_HIS_SHARE",
        "reason": "Patient changed their mind"
    })

    # Second prepare should fail with 403
    res2 = client.post(f"/api/v1/sessions/{sid}/integration/prepare")
    assert res2.status_code == 403
    assert res2.json()["error_code"] == "CONSENT_REQUIRED"


# ============================================================================
# 5. Summary Generation Without Interview Answers
# ============================================================================

def test_summary_without_interview_returns_400():
    """
    Attempting to generate a summary before any interview answers
    exist should return a clear validation error.
    """
    sid = "test_resilience_no_interview"
    client.post("/api/v1/sessions/", json=_create_session(sid))

    # Try to generate summary without answering any questions
    res = client.post(f"/api/v1/sessions/{sid}/ai/generate-summary")
    assert res.status_code == 400
    assert res.json()["error_code"] == "VALIDATION_FAILED"


# ============================================================================
# 6. Clinician Review Without Summary
# ============================================================================

def test_review_without_summary_returns_400():
    """
    Attempting clinician review before any summary was generated
    should return a validation error.
    """
    sid = "test_resilience_no_summary"
    client.post("/api/v1/sessions/", json=_create_session(sid))

    res = client.post(f"/api/v1/sessions/{sid}/summary/review", json={
        "action": "ACCEPTED",
        "clinician_id": "DR_NO_SUMMARY"
    })
    assert res.status_code == 400
    assert res.json()["error_code"] == "VALIDATION_FAILED"
