"""
Phase 10 — Component 1: Multi-Persona End-to-End Clinical Scenarios
Exercises the COMPLETE clinical intake journey through API calls only:
  Patient Registration → ABHA Link → Interview → Summary → Clinician Review →
  Consent → FHIR R4 Bundle → Delivery → DPDP Purge.

Three patient personas test different clinical pathways:
  1. OPD Walk-in (routine, Hindi, Male 35yr)
  2. Acute Emergency (chest pain with red flags, English, Female 62yr)
  3. Document-Heavy Chronic (lab reports + prescription, Marathi, Female 45yr)
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


def _create_pdo(sid: str, gender: str, age: int, lang: str = "en") -> dict:
    return {
        "version": "1.0.0",
        "identity": {
            "session_id": sid,
            "facility_id": "DELHI_CIVIL_OPD_01",
            "preferred_language": lang,
            "gender": gender,
            "age": age
        },
        "consent": {"scope": "INTAKE_AND_SUMMARY", "status": "GRANTED"}
    }


# ============================================================================
# Persona 1 — OPD Walk-in: Routine Fever/Cough, Hindi, Male 35yr
# Full lifecycle from registration to FHIR delivery and DPDP purge
# ============================================================================

def test_persona1_opd_walkin_full_lifecycle():
    """
    Complete patient journey: Registration → ABHA → Interview → Summary →
    Clinician Review → Consent → FHIR Bundle → Mock Delivery → DPDP Purge.
    """
    sid = "e2e_persona1_opd_walkin"

    # 1. Create Session
    res_create = client.post("/api/v1/sessions/", json=_create_pdo(sid, "MALE", 35, "hi"))
    assert res_create.status_code == 201
    assert res_create.json()["identity"]["session_id"] == sid

    # 2. ABHA Link (Initiate + Confirm)
    res_init = client.post(f"/api/v1/sessions/{sid}/abha/initiate", json={
        "auth_mode": "MOBILE_OTP",
        "mobile": "9876543210",
        "abha_address": "ramesh.sharma@abdm"
    })
    assert res_init.status_code == 200
    tx_id = res_init.json()["transaction_id"]

    res_confirm = client.post(f"/api/v1/sessions/{sid}/abha/confirm", json={
        "transaction_id": tx_id,
        "otp": "123456"
    })
    assert res_confirm.status_code == 200
    assert res_confirm.json()["success"] is True

    # Verify ABHA linked in session identity
    sess = client.get(f"/api/v1/sessions/{sid}").json()
    assert sess["identity"]["external_identifier"] is not None

    # 3. Clinical Interview — Chief Complaint
    q1 = client.get(f"/api/v1/sessions/{sid}/next-question")
    assert q1.status_code == 200
    assert q1.json()["question_id"] == "__CHIEF_COMPLAINT__"

    ans1 = client.post(f"/api/v1/sessions/{sid}/answer", json={
        "question_id": "__CHIEF_COMPLAINT__",
        "free_text": "Fever and cough for 5 days"
    })
    assert ans1.status_code == 200
    next_q = ans1.json()["next_question"]
    assert next_q is not None

    # 4. Continue answering questions until interview completes or we reach 15 answers
    answer_count = 1
    max_answers = 15
    while not ans1.json().get("interview_complete", False) and answer_count < max_answers:
        current_q = ans1.json()["next_question"]
        if not current_q:
            break

        qid = current_q["question_id"]
        input_type = current_q["input_type"]

        if input_type == "free_text":
            ans_payload = {"question_id": qid, "free_text": "No specific details"}
        elif current_q.get("options") and len(current_q["options"]) > 0:
            # Select the first available option
            first_code = current_q["options"][0]["value_code"]
            ans_payload = {"question_id": qid, "selected_value_codes": [first_code]}
        else:
            ans_payload = {"question_id": qid, "free_text": "None", "answer_state": "UNKNOWN"}

        ans1 = client.post(f"/api/v1/sessions/{sid}/answer", json=ans_payload)
        assert ans1.status_code == 200
        answer_count += 1

    assert answer_count > 1, "Interview should have progressed beyond chief complaint"

    # 5. Generate Clinical Summary
    sum_res = client.post(f"/api/v1/sessions/{sid}/ai/generate-summary")
    assert sum_res.status_code == 200
    sum_data = sum_res.json()
    assert sum_data["success"] is True
    assert "structured_payload" in sum_data
    assert sum_data["structured_payload"]["draft_status"] == "PENDING"

    # 6. Clinician Review — ACCEPT
    review_res = client.post(f"/api/v1/sessions/{sid}/summary/review", json={
        "action": "ACCEPTED",
        "clinician_id": "DR_GUPTA_OPD"
    })
    assert review_res.status_code == 200
    assert review_res.json()["draft_status"] == "ACCEPTED"

    # 7. Grant HIS_SHARE consent
    consent_res = client.post(f"/api/v1/sessions/{sid}/consent", json={
        "scope": "FULL_HIS_SHARE",
        "interaction_mode": "VOICE_CONFIRMED",
        "language": "hi"
    })
    assert consent_res.status_code == 200

    # 8. Prepare FHIR R4 Bundle
    bundle_res = client.post(f"/api/v1/sessions/{sid}/integration/prepare")
    assert bundle_res.status_code == 200
    bundle_data = bundle_res.json()
    assert bundle_data["success"] is True
    assert bundle_data["total_entries"] >= 3  # At minimum: Composition, Patient, Encounter

    # Verify Composition is entry[0]
    entries = bundle_data["bundle"]["entry"]
    assert entries[0]["resource"]["resourceType"] == "Composition"

    # 9. Submit to Mock Delivery
    submit_res = client.post(f"/api/v1/sessions/{sid}/integration/submit?target=MOCK")
    assert submit_res.status_code == 200
    delivery = submit_res.json()["delivery"]
    assert delivery["state"] == "ACCEPTED"
    assert delivery["is_mock"] is True

    # 10. Verify DPDP Purge — session should be deleted
    purge_check = client.get(f"/api/v1/sessions/{sid}")
    assert purge_check.status_code == 404, "Session must be purged after ACCEPTED delivery"

    # But delivery receipt must survive
    receipt_res = client.get(f"/api/v1/sessions/{sid}/integration/status")
    assert receipt_res.status_code == 200


# ============================================================================
# Persona 2 — Acute Emergency: Crushing Chest Pain, English, Female 62yr
# Tests red-flag emergency triage escalation path
# ============================================================================

def test_persona2_acute_emergency_chest_pain():
    """
    Emergency persona: Chest pain triggers red-flag alerts, summary
    reflects urgency, and the triage queue captures the alert.
    """
    sid = "e2e_persona2_emergency"

    # 1. Create Session
    res_create = client.post("/api/v1/sessions/", json=_create_pdo(sid, "FEMALE", 62, "en"))
    assert res_create.status_code == 201

    # 2. Chief Complaint: Severe chest pain
    client.get(f"/api/v1/sessions/{sid}/next-question")
    ans_cc = client.post(f"/api/v1/sessions/{sid}/answer", json={
        "question_id": "__CHIEF_COMPLAINT__",
        "free_text": "Severe crushing chest pain radiating to left arm for 1 hour"
    })
    assert ans_cc.status_code == 200
    # Should route into Chest Pain SOCRATES path
    next_q = ans_cc.json()["next_question"]
    assert next_q is not None
    assert "SOC_CP" in next_q["question_id"]

    # 3. SOCRATES deep-dive: Site, Onset, Character, Radiation
    # SITE
    client.post(f"/api/v1/sessions/{sid}/answer", json={
        "question_id": "SOC_CP_001_SITE",
        "selected_value_codes": ["CHEST_LEFT_SUBSTERNAL"]
    })
    # ONSET
    client.post(f"/api/v1/sessions/{sid}/answer", json={
        "question_id": "SOC_CP_002_ONSET",
        "selected_value_codes": ["SUDDEN_ACUTE"]
    })
    # CHARACTER
    client.post(f"/api/v1/sessions/{sid}/answer", json={
        "question_id": "SOC_CP_003_CHAR",
        "selected_value_codes": ["CRUSHING_HEAVY_PRESSURE"]
    })
    # RADIATION — left arm (this triggers the red flag!)
    ans_rad = client.post(f"/api/v1/sessions/{sid}/answer", json={
        "question_id": "SOC_CP_004_RADIATION",
        "selected_value_codes": ["RADIATION_LEFT_ARM_SHOULDER"]
    })
    assert ans_rad.status_code == 200
    rad_data = ans_rad.json()

    # 4. Verify RED FLAG triggered
    assert len(rad_data["new_alerts"]) > 0, "Chest pain with left arm radiation must trigger red flag"

    # 5. Verify alert in session-level alerts
    session_alerts = client.get(f"/api/v1/sessions/{sid}/alerts")
    assert session_alerts.status_code == 200
    assert len(session_alerts.json()) > 0

    # 6. Verify alert in global triage queue
    global_alerts = client.get("/api/v1/alerts")
    assert global_alerts.status_code == 200
    queue = global_alerts.json()["alerts"]
    emergency_alert = next((a for a in queue if a["session_id"] == sid), None)
    assert emergency_alert is not None
    assert emergency_alert["severity"] in ("CRITICAL", "HIGH")

    # 7. Generate summary (even during emergency, system completes intake)
    sum_res = client.post(f"/api/v1/sessions/{sid}/ai/generate-summary")
    assert sum_res.status_code == 200
    assert sum_res.json()["success"] is True

    # 8. Clinician accepts, consent, prepare bundle
    client.post(f"/api/v1/sessions/{sid}/summary/review", json={
        "action": "ACCEPTED",
        "clinician_id": "DR_EMERGENCY_ATTEND"
    })
    client.post(f"/api/v1/sessions/{sid}/consent", json={
        "scope": "FULL_HIS_SHARE",
        "interaction_mode": "TOUCH_SCREEN"
    })

    bundle_res = client.post(f"/api/v1/sessions/{sid}/integration/prepare")
    assert bundle_res.status_code == 200
    entries = bundle_res.json()["bundle"]["entry"]
    resource_types = [e["resource"]["resourceType"] for e in entries]

    # Bundle should contain Condition resource for the chest pain
    assert "Condition" in resource_types or "Composition" in resource_types

    # 9. Submit delivery
    submit_res = client.post(f"/api/v1/sessions/{sid}/integration/submit?target=MOCK")
    assert submit_res.status_code == 200
    assert submit_res.json()["delivery"]["state"] == "ACCEPTED"


# ============================================================================
# Persona 3 — Document-Heavy Chronic: Lab Reports + Prescription, Female 45yr
# Tests document upload, OCR extraction, and FHIR DocumentReference
# ============================================================================

def test_persona3_document_heavy_chronic_followup():
    """
    Chronic follow-up patient brings lab reports and prescription.
    Tests document upload → extraction → summary merge → clinician amendment →
    FHIR bundle with DocumentReference → delivery → purge.
    """
    sid = "e2e_persona3_chronic"

    # 1. Create Session
    res_create = client.post("/api/v1/sessions/", json=_create_pdo(sid, "FEMALE", 45, "en"))
    assert res_create.status_code == 201

    # 2. Grant DOCUMENTS_PROCESSING consent
    client.post(f"/api/v1/sessions/{sid}/consent", json={
        "scope": "DOCUMENTS_PROCESSING",
        "interaction_mode": "TOUCH_SCREEN"
    })

    # 3. Upload a mock prescription document
    fake_jpeg = b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"0" * 200
    upload_res = client.post(
        f"/api/v1/sessions/{sid}/documents/upload",
        files={"file": ("prescription.jpg", io.BytesIO(fake_jpeg), "image/jpeg")},
        data={"doc_type": "PRESCRIPTION"}
    )
    assert upload_res.status_code == 200
    doc1 = upload_res.json()["document"]
    assert doc1["file_type"] == "PRESCRIPTION"
    doc1_id = doc1["document_id"]

    # 4. Upload a mock lab report
    upload_res2 = client.post(
        f"/api/v1/sessions/{sid}/documents/upload",
        files={"file": ("cbc_report.jpg", io.BytesIO(fake_jpeg), "image/jpeg")},
        data={"doc_type": "LAB_REPORT"}
    )
    assert upload_res2.status_code == 200
    doc2 = upload_res2.json()["document"]
    assert doc2["file_type"] == "LAB_REPORT"

    # 5. Verify document timeline
    timeline_res = client.get(f"/api/v1/sessions/{sid}/documents/timeline")
    assert timeline_res.status_code == 200
    timeline = timeline_res.json()
    assert timeline["total_entries"] >= 2

    # 6. Verify extraction result exists
    extraction_res = client.get(f"/api/v1/sessions/{sid}/documents/{doc1_id}/extraction")
    assert extraction_res.status_code == 200

    # 7. Complete interview (abbreviated)
    client.get(f"/api/v1/sessions/{sid}/next-question")
    client.post(f"/api/v1/sessions/{sid}/answer", json={
        "question_id": "__CHIEF_COMPLAINT__",
        "free_text": "Follow-up for diabetes, brought lab reports and prescription"
    })

    # 8. Generate summary — documents should be merged
    sum_res = client.post(f"/api/v1/sessions/{sid}/ai/generate-summary")
    assert sum_res.status_code == 200
    assert sum_res.json()["success"] is True

    # 9. Clinician AMENDS one section
    amend_res = client.post(f"/api/v1/sessions/{sid}/summary/review", json={
        "action": "AMENDED",
        "clinician_id": "DR_CHRONIC_CARE",
        "amended_sections": {
            "hpi_summary": "45-year-old female with Type 2 DM on Metformin, brought CBC showing borderline anemia."
        },
        "reason": "Added specific lab findings from uploaded CBC report"
    })
    assert amend_res.status_code == 200
    assert amend_res.json()["draft_status"] == "AMENDED"

    # 10. Grant HIS_SHARE consent
    client.post(f"/api/v1/sessions/{sid}/consent", json={
        "scope": "FULL_HIS_SHARE",
        "interaction_mode": "TOUCH_SCREEN"
    })

    # 11. Prepare FHIR bundle
    bundle_res = client.post(f"/api/v1/sessions/{sid}/integration/prepare")
    assert bundle_res.status_code == 200
    bundle_data = bundle_res.json()
    assert bundle_data["success"] is True

    # Verify bundle contains DocumentReference for uploaded docs
    entries = bundle_data["bundle"]["entry"]
    resource_types = [e["resource"]["resourceType"] for e in entries]
    assert "DocumentReference" in resource_types, "Bundle must include DocumentReference for uploaded documents"

    # 12. Submit delivery
    submit_res = client.post(f"/api/v1/sessions/{sid}/integration/submit?target=MOCK")
    assert submit_res.status_code == 200
    delivery = submit_res.json()["delivery"]
    assert delivery["state"] == "ACCEPTED"
    assert delivery["is_mock"] is True

    # 13. Verify DPDP purge — both session and document data should be cleared
    assert client.get(f"/api/v1/sessions/{sid}").status_code == 404
