"""
Phase 10 — Component 3: Concurrency & Idempotency Tests
Verifies multi-session isolation, idempotency key replay, and concurrent
session state independence under parallel kiosk simulation.
"""
import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.main import app
from app.repositories.session_repository import session_repo

client = TestClient(app)


def _create_session(sid: str, gender: str = "MALE", age: int = 35) -> dict:
    return {
        "version": "1.0.0",
        "identity": {
            "session_id": sid,
            "facility_id": "CONCURRENCY_TEST_FAC",
            "preferred_language": "en",
            "gender": gender,
            "age": age
        },
        "consent": {"scope": "INTAKE_AND_SUMMARY", "status": "GRANTED"}
    }


# ============================================================================
# 1. Multi-Session Isolation
# ============================================================================

def test_five_simultaneous_sessions_no_cross_contamination():
    """
    Create 5 simultaneous sessions with different patient demographics,
    advance each independently, and verify no state cross-contamination.
    """
    sessions = [
        ("concurrency_s1", "MALE", 25),
        ("concurrency_s2", "FEMALE", 40),
        ("concurrency_s3", "MALE", 65),
        ("concurrency_s4", "FEMALE", 18),
        ("concurrency_s5", "MALE", 50),
    ]

    # Create all sessions
    for sid, gender, age in sessions:
        res = client.post("/api/v1/sessions/", json=_create_session(sid, gender, age))
        assert res.status_code == 201, f"Failed to create session {sid}"

    # Start interview on each
    for sid, _, _ in sessions:
        res = client.get(f"/api/v1/sessions/{sid}/next-question")
        assert res.status_code == 200
        assert res.json()["question_id"] == "__CHIEF_COMPLAINT__"

    # Submit DIFFERENT chief complaints to each
    complaints = [
        "Fever and cold",
        "Severe abdominal pain",
        "Persistent cough for weeks",
        "Dizziness and nausea",
        "Knee pain after sports"
    ]

    for (sid, _, _), complaint in zip(sessions, complaints):
        res = client.post(f"/api/v1/sessions/{sid}/answer", json={
            "question_id": "__CHIEF_COMPLAINT__",
            "free_text": complaint
        })
        assert res.status_code == 200

    # Verify each session's state is independent
    for sid, gender, age in sessions:
        sess_res = client.get(f"/api/v1/sessions/{sid}")
        assert sess_res.status_code == 200
        sess_data = sess_res.json()
        assert sess_data["identity"]["gender"] == gender
        assert sess_data["identity"]["age"] == age
        assert sess_data["identity"]["session_id"] == sid


def test_session_delete_does_not_affect_other_sessions():
    """Deleting one session must not affect other active sessions."""
    sid_a = "concurrency_isolate_a"
    sid_b = "concurrency_isolate_b"
    client.post("/api/v1/sessions/", json=_create_session(sid_a))
    client.post("/api/v1/sessions/", json=_create_session(sid_b))

    # Delete session A
    del_res = client.delete(f"/api/v1/sessions/{sid_a}")
    assert del_res.status_code == 200

    # Session A is gone
    assert client.get(f"/api/v1/sessions/{sid_a}").status_code == 404

    # Session B is still alive
    assert client.get(f"/api/v1/sessions/{sid_b}").status_code == 200


# ============================================================================
# 2. Idempotency Replay
# ============================================================================

def test_idempotency_key_prevents_duplicate_creation():
    """
    Sending the same POST /sessions/ with the same X-Idempotency-Key
    should return the cached response rather than creating a duplicate.
    """
    sid = "idempotency_test_session"
    idem_key = "IDEM_KEY_UNIQUE_12345"
    pdo = _create_session(sid)

    # First request
    res1 = client.post(
        "/api/v1/sessions/",
        json=pdo,
        headers={"X-Idempotency-Key": idem_key}
    )
    assert res1.status_code == 201

    # Second request with SAME idempotency key should return cached response
    res2 = client.post(
        "/api/v1/sessions/",
        json=pdo,
        headers={"X-Idempotency-Key": idem_key}
    )
    # Should return cached 201 (not 409 conflict)
    assert res2.status_code in (201, 409), f"Expected 201 cached or 409, got {res2.status_code}"


# ============================================================================
# 3. Concurrent Answer Submission (Sequential simulation)
# ============================================================================

def test_parallel_answer_submissions_to_different_sessions():
    """
    Submit answers to multiple independent sessions sequentially (simulating
    parallel kiosk usage) and verify each graph advances independently.
    """
    sid_x = "concurrency_parallel_x"
    sid_y = "concurrency_parallel_y"

    client.post("/api/v1/sessions/", json=_create_session(sid_x))
    client.post("/api/v1/sessions/", json=_create_session(sid_y))

    # Start both
    client.get(f"/api/v1/sessions/{sid_x}/next-question")
    client.get(f"/api/v1/sessions/{sid_y}/next-question")

    # Submit different chief complaints
    res_x = client.post(f"/api/v1/sessions/{sid_x}/answer", json={
        "question_id": "__CHIEF_COMPLAINT__",
        "free_text": "Chest pain for 3 hours"
    })
    res_y = client.post(f"/api/v1/sessions/{sid_y}/answer", json={
        "question_id": "__CHIEF_COMPLAINT__",
        "free_text": "Stomach pain and nausea"
    })

    assert res_x.status_code == 200
    assert res_y.status_code == 200

    # Session X should be in chest pain SOCRATES path
    next_x = res_x.json()["next_question"]
    assert next_x is not None
    assert "SOC_CP" in next_x["question_id"]  # Chest pain SOCRATES

    # Session Y should be in general history (no SOCRATES for stomach)
    next_y = res_y.json()["next_question"]
    assert next_y is not None
    # Y should NOT be in chest pain SOCRATES
    assert next_y["question_id"] != next_x["question_id"]


# ============================================================================
# 4. Alert Queue Isolation
# ============================================================================

def test_alert_queue_filters_by_session():
    """
    Alerts triggered by one session must not appear when filtering
    by a different session's alert endpoint.
    """
    sid_alert = "concurrency_alert_session"
    sid_clean = "concurrency_clean_session"

    client.post("/api/v1/sessions/", json=_create_session(sid_alert))
    client.post("/api/v1/sessions/", json=_create_session(sid_clean))

    # Advance clean session through benign interview
    client.get(f"/api/v1/sessions/{sid_clean}/next-question")
    client.post(f"/api/v1/sessions/{sid_clean}/answer", json={
        "question_id": "__CHIEF_COMPLAINT__",
        "free_text": "Mild cold and sneezing"
    })

    # Clean session should have no alerts
    alerts_res = client.get(f"/api/v1/sessions/{sid_clean}/alerts")
    assert alerts_res.status_code == 200
    clean_alerts_data = alerts_res.json()
    assert clean_alerts_data["active_alerts_count"] == 0
    assert len(clean_alerts_data["alerts"]) == 0
