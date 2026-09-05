import os
import sys
import io
import pytest
from fastapi.testclient import TestClient

# Add backend to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.models.core import PatientDataObject
from app.models.identity import IdentityContext
from app.models.consent import ConsentContext

client = TestClient(app)

def create_test_pdo(session_id: str, gender: str = "MALE", age: int = 52) -> dict:
    return {
        "version": "1.0.0",
        "identity": {
            "session_id": session_id,
            "facility_id": "AIIA_NEW_DELHI_01",
            "preferred_language": "en",
            "gender": gender,
            "age": age,
            "external_identifier": None,
            "patient_reference": None
        },
        "consent": {
            "scope": "INTAKE_AND_SUMMARY",
            "status": "GRANTED",
            "evidence_reference": "TEST_AUDIT_REF_001"
        },
        "documents": {},
        "summary": {},
        "alerts": {},
        "integration_status": {},
        "plugin_outputs": {}
    }


# ============================================================================
# 1. Operations & Health Endpoints
# ============================================================================

def test_liveness_probes():
    # Root health
    res1 = client.get("/health")
    assert res1.status_code == 200
    assert res1.json()["status"] == "ok"

    # API v1 health
    res2 = client.get("/api/v1/health")
    assert res2.status_code == 200
    assert res2.json()["status"] == "healthy"


def test_deep_readiness_probe():
    res = client.get("/api/v1/ready")
    assert res.status_code == 200
    data = res.json()
    assert "status" in data
    assert "checks" in data
    assert "ai_providers" in data["checks"]
    assert "ocr_engine" in data["checks"]


def test_ai_provider_health():
    res = client.get("/api/v1/ai/health")
    assert res.status_code == 200
    data = res.json()
    assert "mock" in data or "colab_medgemma" in data


# ============================================================================
# 2. Middleware, Correlation, & Error Contracts
# ============================================================================

def test_correlation_id_middleware():
    custom_corr_id = "test-corr-uuid-12345"
    res = client.get("/api/v1/health", headers={"X-Correlation-ID": custom_corr_id})
    assert res.status_code == 200
    assert res.headers.get("X-Correlation-ID") == custom_corr_id

    # Auto-generation when absent
    res2 = client.get("/api/v1/health")
    assert "X-Correlation-ID" in res2.headers


def test_standardized_error_format():
    # Attempting to fetch non-existent session
    res = client.get("/api/v1/sessions/non_existent_session_9999")
    assert res.status_code == 404
    err = res.json()
    assert err["error_code"] == "SESSION_NOT_FOUND"
    assert "message" in err
    assert "correlation_id" in err


def test_idempotency_middleware():
    sid = "test_idemp_session_001"
    payload = create_test_pdo(sid)
    idemp_key = "idemp-key-abc-001"

    # First request
    res1 = client.post("/api/v1/sessions/", json=payload, headers={"X-Idempotency-Key": idemp_key})
    assert res1.status_code == 201

    # Replay with same idempotency key
    res2 = client.post("/api/v1/sessions/", json=payload, headers={"X-Idempotency-Key": idemp_key})
    assert res2.status_code == 201
    assert res2.headers.get("X-Cache-Lookup") == "HIT-IDEMPOTENT"


# ============================================================================
# 3. ABDM Milestone 1 (M1): ABHA Verification & Linking
# ============================================================================

def test_abdm_m1_abha_linking_flow():
    sid = "test_abha_session_001"
    client.post("/api/v1/sessions/", json=create_test_pdo(sid))

    # 1. Initiate ABHA auth
    init_res = client.post(f"/api/v1/sessions/{sid}/abha/initiate", json={
        "auth_mode": "MOBILE_OTP",
        "abha_address": "ramesh.sharma@abdm",
        "mobile": "9876543210"
    })
    assert init_res.status_code == 200
    init_data = init_res.json()
    assert "transaction_id" in init_data
    assert init_data["is_mock_sandbox"] is True
    tx_id = init_data["transaction_id"]

    # 2. Confirm OTP (Sandbox default: 123456)
    confirm_res = client.post(f"/api/v1/sessions/{sid}/abha/confirm", json={
        "transaction_id": tx_id,
        "otp": "123456"
    })
    assert confirm_res.status_code == 200
    confirm_data = confirm_res.json()
    assert confirm_data["success"] is True
    assert confirm_data["abha_address"] == "ramesh.sharma@abdm"

    # 3. Verify session identity now reflects ABHA
    sess_res = client.get(f"/api/v1/sessions/{sid}")
    assert sess_res.status_code == 200
    sess = sess_res.json()
    assert sess["identity"]["external_identifier"] == "ramesh.sharma@abdm"
    assert sess["identity"]["patient_reference"].startswith("PAT_")


# ============================================================================
# 4. DPDP & ABDM Granular Consent Lifecycle
# ============================================================================

def test_consent_lifecycle():
    sid = "test_consent_session_001"
    client.post("/api/v1/sessions/", json=create_test_pdo(sid))

    # Inspect initial consent
    res1 = client.get(f"/api/v1/sessions/{sid}/consent")
    assert res1.status_code == 200
    assert res1.json()["consent"]["status"] == "GRANTED"

    # Revoke consent
    res2 = client.post(f"/api/v1/sessions/{sid}/consent/revoke", json={
        "scope": "INTAKE_AND_SUMMARY",
        "reason": "Patient requested privacy pause"
    })
    assert res2.status_code == 200
    assert res2.json()["status"] == "REVOKED"

    # Grant full consent
    res3 = client.post(f"/api/v1/sessions/{sid}/consent", json={
        "scope": "FULL_HIS_SHARE",
        "interaction_mode": "VOICE_CONFIRMED",
        "language": "hi"
    })
    assert res3.status_code == 200
    assert res3.json()["scope"] == "FULL_HIS_SHARE"
    assert res3.json()["status"] == "GRANTED"


# ============================================================================
# 5. Conversational Intake & Emergency Triage Escalation
# ============================================================================

def test_intake_questioning_and_triage_alerts():
    sid = "test_intake_alert_session_001"
    client.post("/api/v1/sessions/", json=create_test_pdo(sid))

    # 1. Start intake -> Get Chief Complaint
    q1_res = client.get(f"/api/v1/sessions/{sid}/next-question")
    assert q1_res.status_code == 200
    q1 = q1_res.json()
    assert q1["question_id"] == "__CHIEF_COMPLAINT__"

    # 2. Submit chief complaint -> transitions to SOC_CP_001_SITE
    ans1_res = client.post(f"/api/v1/sessions/{sid}/answer", json={
        "question_id": "__CHIEF_COMPLAINT__",
        "free_text": "Chest pain for 2 hours"
    })
    assert ans1_res.status_code == 200
    ans1 = ans1_res.json()
    assert ans1["next_question"]["question_id"] == "SOC_CP_001_SITE"

    # 3. Answer SITE -> transitions to ONSET
    ans2_res = client.post(f"/api/v1/sessions/{sid}/answer", json={
        "question_id": "SOC_CP_001_SITE",
        "selected_value_codes": ["CHEST_LEFT_SUBSTERNAL"]
    })
    assert ans2_res.status_code == 200
    assert ans2_res.json()["next_question"]["question_id"] == "SOC_CP_002_ONSET"

    # 4. Answer ONSET -> transitions to CHAR
    ans3_res = client.post(f"/api/v1/sessions/{sid}/answer", json={
        "question_id": "SOC_CP_002_ONSET",
        "selected_value_codes": ["SUDDEN_ACUTE"]
    })
    assert ans3_res.status_code == 200
    assert ans3_res.json()["next_question"]["question_id"] == "SOC_CP_003_CHAR"

    # 5. Answer CHAR -> transitions to RADIATION
    ans4_res = client.post(f"/api/v1/sessions/{sid}/answer", json={
        "question_id": "SOC_CP_003_CHAR",
        "selected_value_codes": ["CRUSHING_HEAVY_PRESSURE"]
    })
    assert ans4_res.status_code == 200
    assert ans4_res.json()["next_question"]["question_id"] == "SOC_CP_004_RADIATION"

    # 6. Answer RADIATION with RADIATION_LEFT_ARM_SHOULDER -> triggers RF_CARD_001_CHEST_PAIN_RADIATION red flag
    ans5_res = client.post(f"/api/v1/sessions/{sid}/answer", json={
        "question_id": "SOC_CP_004_RADIATION",
        "selected_value_codes": ["RADIATION_LEFT_ARM_SHOULDER"]
    })
    assert ans5_res.status_code == 200
    ans5 = ans5_res.json()
    assert len(ans5["new_alerts"]) > 0

    # 7. Verify session alerts endpoint
    sess_alerts_res = client.get(f"/api/v1/sessions/{sid}/alerts")
    assert sess_alerts_res.status_code == 200
    assert len(sess_alerts_res.json()) > 0

    # 8. Verify global nurse queue contains this alert
    global_alerts_res = client.get("/api/v1/alerts")
    assert global_alerts_res.status_code == 200
    alerts_list = global_alerts_res.json()["alerts"]
    assert len(alerts_list) > 0
    target_alert = next((a for a in alerts_list if a["session_id"] == sid), None)
    assert target_alert is not None
    assert target_alert["status"] == "TRIGGERED"

    # 9. Triage nurse acknowledges the alert
    ack_res = client.post(f"/api/v1/alerts/{target_alert['alert_id']}/acknowledge", json={
        "staff_id": "NURSE_PRIYA_04",
        "triage_action": "FAST_TRACK_ECG",
        "notes": "Patient routed immediately to Resuscitation Bay 2"
    })
    assert ack_res.status_code == 200
    assert ack_res.json()["status"] == "ACKNOWLEDGED"


# ============================================================================
# 6. Document Upload, Security Validation & Staging
# ============================================================================

def test_document_upload_and_magic_byte_validation():
    sid = "test_doc_session_001"
    # Create session with INTAKE_ONLY consent (no doc consent)
    pdo = create_test_pdo(sid)
    pdo["consent"]["scope"] = "INTAKE_ONLY"
    client.post("/api/v1/sessions/", json=pdo)

    # 1. Attempt upload without doc consent -> 403 CONSENT_REQUIRED
    fake_jpeg = b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"0"*100
    res_unauth = client.post(
        f"/api/v1/sessions/{sid}/documents/upload",
        files={"file": ("report.jpg", io.BytesIO(fake_jpeg), "image/jpeg")},
        data={"doc_type": "LAB_REPORT"}
    )
    assert res_unauth.status_code == 403
    assert res_unauth.json()["error_code"] == "CONSENT_REQUIRED"

    # 2. Grant DOCUMENTS_PROCESSING consent
    client.post(f"/api/v1/sessions/{sid}/consent", json={
        "scope": "DOCUMENTS_PROCESSING",
        "interaction_mode": "TOUCH_SCREEN"
    })

    # 3. Attempt upload of spoofed executable (.exe content disguised as image/jpeg) -> 415 DOCUMENT_REJECTED
    malicious_bytes = b"MZ\x90\x00\x03\x00\x00\x00" + b"A"*100
    res_rejected = client.post(
        f"/api/v1/sessions/{sid}/documents/upload",
        files={"file": ("virus.jpg", io.BytesIO(malicious_bytes), "image/jpeg")},
        data={"doc_type": "PRESCRIPTION"}
    )
    assert res_rejected.status_code == 415
    assert res_rejected.json()["error_code"] == "DOCUMENT_REJECTED"

    # 4. Valid JPEG upload
    res_ok = client.post(
        f"/api/v1/sessions/{sid}/documents/upload",
        files={"file": ("valid_prescription.jpg", io.BytesIO(fake_jpeg), "image/jpeg")},
        data={"doc_type": "PRESCRIPTION"}
    )
    assert res_ok.status_code == 200
    doc_data = res_ok.json()["document"]
    assert doc_data["file_type"] == "PRESCRIPTION"
    assert doc_data["source_tag"] == "[Doc#1: Prescription]"
    doc_id = doc_data["document_id"]

    # 5. List and inspect document
    list_res = client.get(f"/api/v1/sessions/{sid}/documents")
    assert list_res.status_code == 200
    assert list_res.json()["total_documents"] == 1

    detail_res = client.get(f"/api/v1/sessions/{sid}/documents/{doc_id}")
    assert detail_res.status_code == 200
    assert detail_res.json()["document_id"] == doc_id


# ============================================================================
# 7. Clinical Summary Synthesis & Clinician Review Actions
# ============================================================================

def test_summary_synthesis_and_clinician_review():
    sid = "test_summary_review_session_001"
    client.post("/api/v1/sessions/", json=create_test_pdo(sid))

    # Advance intake so facts exist
    client.get(f"/api/v1/sessions/{sid}/next-question")
    client.post(f"/api/v1/sessions/{sid}/answer", json={
        "question_id": "__CHIEF_COMPLAINT__",
        "free_text": "Severe chest pain and breathlessness"
    })

    # 1. Synthesize summary
    sum_res = client.post(f"/api/v1/sessions/{sid}/ai/generate-summary")
    assert sum_res.status_code == 200
    payload = sum_res.json()["structured_payload"]
    assert payload["draft_status"] == "PENDING"
    assert payload["is_draft_for_clinician_review"] is True
    assert "provenance" in payload

    # 2. Clinician amends summary
    amend_res = client.post(f"/api/v1/sessions/{sid}/summary/review", json={
        "action": "AMENDED",
        "clinician_id": "DR_ARVIND_KUMAR_MD",
        "amended_sections": {
            "hpi_summary": "52-year-old male with acute retrosternal chest pain for 2 hours, amended by attending physician."
        }
    })
    assert amend_res.status_code == 200
    assert amend_res.json()["draft_status"] == "AMENDED"

    # 3. Clinician approves final record
    accept_res = client.post(f"/api/v1/sessions/{sid}/summary/review", json={
        "action": "ACCEPTED",
        "clinician_id": "DR_ARVIND_KUMAR_MD"
    })
    assert accept_res.status_code == 200
    assert accept_res.json()["draft_status"] == "ACCEPTED"
    assert accept_res.json()["review_status"] == "APPROVED"

    # 4. Fetch updated summary
    final_res = client.get(f"/api/v1/sessions/{sid}/summary")
    assert final_res.status_code == 200
    assert final_res.json()["draft_status"] == "ACCEPTED"
    assert final_res.json()["provenance"]["source_id"] == "DR_ARVIND_KUMAR_MD"


def test_sse_summary_streaming():
    sid = "test_sse_session_001"
    client.post("/api/v1/sessions/", json=create_test_pdo(sid))

    # Advance intake so facts exist
    client.get(f"/api/v1/sessions/{sid}/next-question")
    client.post(f"/api/v1/sessions/{sid}/answer", json={
        "question_id": "__CHIEF_COMPLAINT__",
        "free_text": "Fever with chills and body ache for 3 days"
    })

    # Stream summary draft via SSE
    with client.stream("GET", f"/api/v1/sessions/{sid}/summary/stream") as stream_res:
        assert stream_res.status_code == 200
        assert "text/event-stream" in stream_res.headers.get("content-type", "")
        events = []
        for line in stream_res.iter_lines():
            if line:
                events.append(line)
        assert len(events) > 0
        assert any("status" in ev or "complete" in ev for ev in events)


# ============================================================================
# 8. Session Termination & DPDP Purge
# ============================================================================

def test_session_termination():
    sid = "test_purge_session_001"
    client.post("/api/v1/sessions/", json=create_test_pdo(sid))

    del_res = client.delete(f"/api/v1/sessions/{sid}")
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "TERMINATED"

    # Ensure session no longer found
    check_res = client.get(f"/api/v1/sessions/{sid}")
    assert check_res.status_code == 404
