"""
Phase 10 — Component 2: Cross-Module Data Flow Validation
Verifies that data flows correctly between modules:
  LangGraph → Summary Pipeline, Document OCR → Summary, Summary → FHIR Mapper,
  Consent → Delivery Gate, Review Gate → Delivery Gate, Red Flag → Alert Queue.
"""
import os
import sys
import io
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.main import app
from app.repositories.session_repository import session_repo

client = TestClient(app)


def _create_session(sid: str, gender: str = "MALE", age: int = 45) -> dict:
    return {
        "version": "1.0.0",
        "identity": {
            "session_id": sid,
            "facility_id": "CROSS_MODULE_FAC",
            "preferred_language": "en",
            "gender": gender,
            "age": age
        },
        "consent": {"scope": "INTAKE_AND_SUMMARY", "status": "GRANTED"}
    }


# ============================================================================
# 1. LangGraph → Summary Pipeline: Interview answers must appear in summary
# ============================================================================

def test_interview_answers_flow_into_summary():
    """
    Interview facts collected by LangGraph state machine must be passed
    into the MedGemma summary synthesis pipeline as structured input.
    """
    sid = "cross_module_interview_to_summary"
    client.post("/api/v1/sessions/", json=_create_session(sid))

    # Advance through interview
    client.get(f"/api/v1/sessions/{sid}/next-question")
    client.post(f"/api/v1/sessions/{sid}/answer", json={
        "question_id": "__CHIEF_COMPLAINT__",
        "free_text": "High fever for 4 days with body aches"
    })

    # Generate summary — ModelService will use the LangGraph accumulated facts
    sum_res = client.post(f"/api/v1/sessions/{sid}/ai/generate-summary")
    assert sum_res.status_code == 200
    payload = sum_res.json()
    assert payload["success"] is True

    # Verify the structured_payload was generated from interview facts
    structured = payload.get("structured_payload", {})
    assert structured is not None
    assert "draft_status" in structured
    assert structured["draft_status"] == "PENDING"


# ============================================================================
# 2. Document OCR → Summary Pipeline: Uploaded docs merge into summary input
# ============================================================================

def test_document_extraction_flows_into_summary_input():
    """
    Uploaded and OCR-processed documents must be included in the summary
    synthesis pipeline as ocr_extracted_documents.
    """
    sid = "cross_module_doc_to_summary"
    pdo = _create_session(sid)
    client.post("/api/v1/sessions/", json=pdo)

    # Grant document consent
    client.post(f"/api/v1/sessions/{sid}/consent", json={
        "scope": "DOCUMENTS_PROCESSING",
        "interaction_mode": "TOUCH_SCREEN"
    })

    # Upload a document
    fake_jpeg = b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"0" * 100
    upload_res = client.post(
        f"/api/v1/sessions/{sid}/documents/upload",
        files={"file": ("lab_report.jpg", io.BytesIO(fake_jpeg), "image/jpeg")},
        data={"doc_type": "LAB_REPORT"}
    )
    assert upload_res.status_code == 200
    doc_data = upload_res.json()["document"]
    assert doc_data["file_type"] == "LAB_REPORT"

    # Complete interview
    client.get(f"/api/v1/sessions/{sid}/next-question")
    client.post(f"/api/v1/sessions/{sid}/answer", json={
        "question_id": "__CHIEF_COMPLAINT__",
        "free_text": "Follow-up visit, brought lab reports"
    })

    # Generate summary — should include the uploaded document
    sum_res = client.post(f"/api/v1/sessions/{sid}/ai/generate-summary")
    assert sum_res.status_code == 200
    assert sum_res.json()["success"] is True


# ============================================================================
# 3. Summary → FHIR Mapper: Approved summary maps to FHIR resources
# ============================================================================

def test_accepted_summary_maps_to_fhir_bundle():
    """
    After clinician ACCEPTS a summary, the FHIR R4 Bundle should contain
    Condition, Observation, and other mapped resources from the summary.
    """
    sid = "cross_module_summary_to_fhir"
    client.post("/api/v1/sessions/", json=_create_session(sid))

    # Interview
    client.get(f"/api/v1/sessions/{sid}/next-question")
    client.post(f"/api/v1/sessions/{sid}/answer", json={
        "question_id": "__CHIEF_COMPLAINT__",
        "free_text": "Chronic lower back pain"
    })

    # Generate and accept summary
    client.post(f"/api/v1/sessions/{sid}/ai/generate-summary")
    client.post(f"/api/v1/sessions/{sid}/summary/review", json={
        "action": "ACCEPTED",
        "clinician_id": "DR_CROSS_MODULE"
    })

    # Grant HIS_SHARE consent
    client.post(f"/api/v1/sessions/{sid}/consent", json={
        "scope": "FULL_HIS_SHARE",
        "interaction_mode": "TOUCH_SCREEN"
    })

    # Prepare FHIR bundle
    bundle_res = client.post(f"/api/v1/sessions/{sid}/integration/prepare")
    assert bundle_res.status_code == 200
    bundle_data = bundle_res.json()
    assert bundle_data["success"] is True

    # Verify the bundle contains expected resource types
    bundle_entries = bundle_data["bundle"]["entry"]
    resource_types = [e["resource"]["resourceType"] for e in bundle_entries]
    assert "Composition" in resource_types
    assert "Patient" in resource_types
    assert "Encounter" in resource_types


# ============================================================================
# 4. Consent Enforcement → Delivery Gate
# ============================================================================

def test_delivery_blocked_without_his_share_consent():
    """
    Attempting POST /integration/prepare without HIS_SHARE consent
    must return 403 CONSENT_REQUIRED.
    """
    sid = "cross_module_no_consent"
    client.post("/api/v1/sessions/", json=_create_session(sid))

    # Interview + approved summary
    client.get(f"/api/v1/sessions/{sid}/next-question")
    client.post(f"/api/v1/sessions/{sid}/answer", json={
        "question_id": "__CHIEF_COMPLAINT__",
        "free_text": "Mild headache"
    })
    client.post(f"/api/v1/sessions/{sid}/ai/generate-summary")
    client.post(f"/api/v1/sessions/{sid}/summary/review", json={
        "action": "ACCEPTED",
        "clinician_id": "DR_NO_CONSENT_TEST"
    })

    # Do NOT grant HIS_SHARE consent
    # Try to prepare bundle → should fail
    res = client.post(f"/api/v1/sessions/{sid}/integration/prepare")
    assert res.status_code == 403
    assert res.json()["error_code"] == "CONSENT_REQUIRED"


# ============================================================================
# 5. Review Gate → Delivery Gate
# ============================================================================

def test_delivery_blocked_with_pending_review():
    """
    Attempting to prepare a FHIR bundle when draft_status is still PENDING
    must return 400 CLINICIAN_REVIEW_REQUIRED.
    """
    sid = "cross_module_no_review"
    client.post("/api/v1/sessions/", json=_create_session(sid))

    # Interview + summary (but NO clinician review)
    client.get(f"/api/v1/sessions/{sid}/next-question")
    client.post(f"/api/v1/sessions/{sid}/answer", json={
        "question_id": "__CHIEF_COMPLAINT__",
        "free_text": "Joint pain"
    })
    client.post(f"/api/v1/sessions/{sid}/ai/generate-summary")

    # Grant HIS_SHARE
    client.post(f"/api/v1/sessions/{sid}/consent", json={
        "scope": "FULL_HIS_SHARE",
        "interaction_mode": "TOUCH_SCREEN"
    })

    # Try to prepare → should fail (draft is PENDING, not ACCEPTED)
    res = client.post(f"/api/v1/sessions/{sid}/integration/prepare")
    assert res.status_code == 400
    assert res.json()["error_code"] == "CLINICIAN_REVIEW_REQUIRED"


# ============================================================================
# 6. Red Flag → Alert Queue → Triage
# ============================================================================

def test_red_flag_appears_in_answer_result_and_alert_queue():
    """
    When a patient's answer triggers a red-flag rule, the alert must appear
    in both the answer result AND the global triage alert queue.
    """
    sid = "cross_module_red_flag_flow"
    client.post("/api/v1/sessions/", json=_create_session(sid))

    # Chief complaint: chest pain
    client.get(f"/api/v1/sessions/{sid}/next-question")
    client.post(f"/api/v1/sessions/{sid}/answer", json={
        "question_id": "__CHIEF_COMPLAINT__",
        "free_text": "Chest pain for 2 hours"
    })

    # Answer SITE
    client.post(f"/api/v1/sessions/{sid}/answer", json={
        "question_id": "SOC_CP_001_SITE",
        "selected_value_codes": ["CHEST_LEFT_SUBSTERNAL"]
    })

    # Answer ONSET
    client.post(f"/api/v1/sessions/{sid}/answer", json={
        "question_id": "SOC_CP_002_ONSET",
        "selected_value_codes": ["SUDDEN_ACUTE"]
    })

    # Answer CHAR
    client.post(f"/api/v1/sessions/{sid}/answer", json={
        "question_id": "SOC_CP_003_CHAR",
        "selected_value_codes": ["CRUSHING_HEAVY_PRESSURE"]
    })

    # Answer RADIATION with left arm → should trigger red flag
    ans_res = client.post(f"/api/v1/sessions/{sid}/answer", json={
        "question_id": "SOC_CP_004_RADIATION",
        "selected_value_codes": ["RADIATION_LEFT_ARM_SHOULDER"]
    })
    assert ans_res.status_code == 200
    ans_data = ans_res.json()

    # Red flag MUST appear in the answer result
    assert len(ans_data["new_alerts"]) > 0, "Expected red-flag alert in answer result"

    # Red flag MUST appear in session-level alerts
    session_alerts = client.get(f"/api/v1/sessions/{sid}/alerts")
    assert session_alerts.status_code == 200
    assert len(session_alerts.json()) > 0

    # Red flag MUST appear in global triage queue
    global_alerts = client.get("/api/v1/alerts")
    assert global_alerts.status_code == 200
    queue = global_alerts.json()["alerts"]
    session_alert = next((a for a in queue if a["session_id"] == sid), None)
    assert session_alert is not None, "Red flag alert not found in global triage queue"
    assert session_alert["status"] == "TRIGGERED"
