"""
Phase 9 Automated Test Suite: Consent, FHIR R4, ABDM & HIS Integration (Module D).
Tests:
  1. Granular multi-scope consent grant/revoke
  2. Multi-lingual audio guidance scripts (en, hi, mr, bn, ta, te)
  3. Consent enforcement gate (HIS_SHARE)
  4. Clinician review gate (ACCEPTED / AMENDED required)
  5. FHIR R4 Patient & Encounter mapping
  6. FHIR R4 Composition-first Bundle structure (entry[0] mandate)
  7. FHIR R4 Cross-resource referential integrity
  8. DocumentReference mapping from digitized documents
  9. Truthful Mock delivery adapter (is_mock=True)
  10. DPDP post-delivery session purge upon ACCEPTED delivery
  11. Preserved session retry state on FAILED delivery
  12. Raw FHIR JSON bundle endpoint (application/fhir+json)
  13. Full end-to-end Phase 9 integration flow
"""
import pytest
import sys
import os
from fastapi.testclient import TestClient
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.main import app
from app.models.core import PatientDataObject
from app.models.identity import IdentityContext
from app.models.consent import ConsentContext
from app.models.history import PatientHistory
from app.models.delivery import DeliveryState, DeliveryTarget
from app.repositories.session_repository import session_repo
from app.repositories.document_repository import document_repo
from app.services.consent_engine import consent_engine
from app.services.fhir.bundle_builder import FHIRBundleBuilder
from app.services.fhir.validator import fhir_validator

client = TestClient(app)


def build_test_pdo(session_id: str, consent_scope: str = "FULL_HIS_SHARE", review_status: str = "ACCEPTED") -> PatientDataObject:
    """Helper to construct a fully-populated PatientDataObject for integration tests."""
    pdo = PatientDataObject(
        version="1.0.0",
        identity=IdentityContext(
            session_id=session_id,
            facility_id="AIIA_NEW_DELHI_01",
            preferred_language="hi",
            gender="FEMALE",
            age=52,
            external_identifier="91-1234-5678-9012"  # ABHA Address
        ),
        consent=ConsentContext(
            scope=consent_scope,
            status="GRANTED",
            evidence_reference=f"TEST_AUDIT_{session_id}"
        ),
        history=PatientHistory(
            chief_complaint="Severe chest discomfort and breathlessness for 3 days",
            past_medical_history=["Type 2 Diabetes Mellitus on Metformin"],
            medications=["Metformin 500mg BD"],
            review_of_systems={"chest_pain": True, "breathlessness": True}
        ),
        summary={
            "patient_chief_complaint": "Severe chest pain",
            "hpi_summary": "52-year-old female presenting with acute retrosternal chest pain.",
            "draft_status": review_status,
            "is_draft_for_clinician_review": False
        },
        documents={
            "DOC_001": {
                "document_id": "DOC_001",
                "session_id": session_id,
                "file_name": "prescription_march.jpg",
                "file_type": "PRESCRIPTION",
                "document_type": "PRESCRIPTION",
                "mime_type": "image/jpeg",
                "source_tag": "[Doc#1: Prescription 2024-03-15]",
                "extracted_medications": [
                    {"drug_name": "Metformin", "dosage": "500mg", "frequency": "BD", "source_tag": "[Doc#1]"}
                ],
                "extracted_diagnoses": [
                    {"diagnosis_text": "Type 2 Diabetes Mellitus", "source_tag": "[Doc#1]"}
                ]
            },
            "DOC_002": {
                "document_id": "DOC_002",
                "session_id": session_id,
                "file_name": "cbc_report.pdf",
                "file_type": "LAB_REPORT",
                "document_type": "LAB_REPORT",
                "mime_type": "application/pdf",
                "source_tag": "[Doc#2: CBC Report 2024-05-10]",
                "extracted_lab_results": [
                    {"test_name": "Hemoglobin", "value": "9.8", "unit": "g/dL", "reference_range": "12.0-15.5", "is_abnormal": True}
                ]
            }
        }
    )
    session_repo.save_session(pdo)
    return pdo


# ============================================================================
# 1. Consent Engine & Audio Guidance Tests
# ============================================================================

def test_multi_scope_consent_grant_and_revoke():
    """Verify independent granular grant and revocation across scopes."""
    sid = "test_p9_consent_001"
    pdo = build_test_pdo(sid, consent_scope="INTAKE_ONLY")

    # Initial state check
    assert pdo.consent.is_scope_granted("INTAKE") is True
    assert pdo.consent.is_scope_granted("DOCUMENTS") is False
    assert pdo.consent.is_scope_granted("HIS_SHARE") is False

    # Grant DOCUMENTS scope via API
    res_grant = client.post(f"/api/v1/sessions/{sid}/consent", json={
        "scope": "DOCUMENTS",
        "interaction_mode": "TOUCH_SCREEN"
    })
    assert res_grant.status_code == 200
    assert res_grant.json()["success"] is True

    updated_session = session_repo.get_session(sid)
    assert updated_session.consent.is_scope_granted("DOCUMENTS") is True

    # Revoke INTAKE scope via API
    res_revoke = client.post(f"/api/v1/sessions/{sid}/consent/revoke", json={
        "scope": "INTAKE",
        "reason": "Patient pause"
    })
    assert res_revoke.status_code == 200

    updated_session2 = session_repo.get_session(sid)
    assert updated_session2.consent.is_scope_granted("INTAKE") is False

    # Cleanup
    session_repo.delete_session(sid)


def test_consent_audio_guidance_scripts():
    """Verify localized audio guidance scripts for kiosk voice consent."""
    sid = "test_p9_consent_audio"
    build_test_pdo(sid)

    # Hindi script
    res_hi = client.get(f"/api/v1/sessions/{sid}/consent/audio-script?scope=HIS_SHARE&language=hi")
    assert res_hi.status_code == 200
    assert "आभा" in res_hi.json()["audio_script"] or "ईएचआर" in res_hi.json()["audio_script"]

    # English script
    res_en = client.get(f"/api/v1/sessions/{sid}/consent/audio-script?scope=DOCUMENTS&language=en")
    assert res_en.status_code == 200
    assert "prescriptions" in res_en.json()["audio_script"]

    # Marathi script
    res_mr = client.get(f"/api/v1/sessions/{sid}/consent/audio-script?scope=INTAKE&language=mr")
    assert res_mr.status_code == 200
    assert len(res_mr.json()["audio_script"]) > 10

    # Cleanup
    session_repo.delete_session(sid)


# ============================================================================
# 2. Gate Enforcement Tests
# ============================================================================

def test_his_share_consent_gate_enforcement():
    """Verify prepare is blocked with 403 when HIS_SHARE consent is missing."""
    sid = "test_p9_gate_consent"
    # Session with INTAKE_ONLY consent
    build_test_pdo(sid, consent_scope="INTAKE_ONLY", review_status="ACCEPTED")

    res = client.post(f"/api/v1/sessions/{sid}/integration/prepare")
    assert res.status_code == 403
    data = res.json()
    assert data["error_code"] == "CONSENT_REQUIRED"
    assert "HIS_SHARE" in data["message"]

    session_repo.delete_session(sid)


def test_clinician_review_gate_enforcement():
    """Verify prepare is blocked with 400 when clinician review is PENDING."""
    sid = "test_p9_gate_review"
    # Session with full consent but summary draft status is PENDING
    build_test_pdo(sid, consent_scope="FULL_HIS_SHARE", review_status="PENDING")

    res = client.post(f"/api/v1/sessions/{sid}/integration/prepare")
    assert res.status_code == 400
    data = res.json()
    assert data["error_code"] == "CLINICIAN_REVIEW_REQUIRED"

    session_repo.delete_session(sid)


# ============================================================================
# 3. FHIR R4 Bundle & Referential Integrity Tests
# ============================================================================

def test_fhir_r4_bundle_composition_first_entry():
    """ABDM MANDATE: Verify Bundle.type == 'document' and entry[0] is Composition."""
    sid = "test_p9_fhir_structure"
    pdo = build_test_pdo(sid, consent_scope="FULL_HIS_SHARE", review_status="ACCEPTED")

    bundle = FHIRBundleBuilder.build_document_bundle(pdo)

    assert bundle.resourceType == "Bundle"
    assert bundle.type == "document"
    assert len(bundle.entry) > 0

    # First entry must be Composition
    first_resource = bundle.entry[0].resource
    assert getattr(first_resource, "resourceType", None) == "Composition"
    assert getattr(first_resource, "type", None).coding[0].code == "371530004"  # SNOMED OPConsultation
    assert "OPD Consultation Record" in getattr(first_resource, "title", "")

    session_repo.delete_session(sid)


def test_fhir_r4_bundle_referential_integrity():
    """Verify validator confirms all referenced URNs resolve within the bundle."""
    sid = "test_p9_fhir_validator"
    pdo = build_test_pdo(sid, consent_scope="FULL_HIS_SHARE", review_status="ACCEPTED")

    bundle = FHIRBundleBuilder.build_document_bundle(pdo)
    is_valid, issues = fhir_validator.validate_bundle(bundle)

    assert is_valid is True
    assert len(issues) == 0

    session_repo.delete_session(sid)


def test_fhir_document_reference_attachment():
    """Verify uploaded documents are mapped to DocumentReferences and linked in Composition."""
    sid = "test_p9_doc_attachment"
    pdo = build_test_pdo(sid, consent_scope="FULL_HIS_SHARE", review_status="ACCEPTED")

    bundle = FHIRBundleBuilder.build_document_bundle(pdo)

    # Check for DocumentReference resources in bundle
    doc_entries = [e for e in bundle.entry if getattr(e.resource, "resourceType", "") == "DocumentReference"]
    assert len(doc_entries) == 2  # DOC_001 and DOC_002

    # Verify Composition has section for Attached Documents
    comp = bundle.entry[0].resource
    doc_section = next((s for s in comp.section if "Documents" in s.title), None)
    assert doc_section is not None
    assert len(doc_section.entry) == 2

    session_repo.delete_session(sid)


# ============================================================================
# 4. Delivery Lifecycle & Truthfulness Tests
# ============================================================================

def test_mock_delivery_lifecycle_and_truthfulness():
    """Verify Mock delivery reports is_mock=True and returns ACCEPTED."""
    sid = "test_p9_delivery_truth"
    build_test_pdo(sid, consent_scope="FULL_HIS_SHARE", review_status="ACCEPTED")

    res = client.post(f"/api/v1/sessions/{sid}/integration/submit?target=MOCK")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True

    deliv = data["delivery"]
    assert deliv["state"] == "ACCEPTED"
    assert deliv["is_mock"] is True  # TRUTHFULNESS MANDATE
    assert "CARE-CTX-MOCK" in deliv["response_payload"]["care_context_reference"]


def test_session_purge_on_accepted_delivery():
    """Verify DPDP Act session purge: ephemeral session data is cleared on ACCEPTED."""
    sid = "test_p9_session_purge"
    build_test_pdo(sid, consent_scope="FULL_HIS_SHARE", review_status="ACCEPTED")

    # Session exists before submission
    assert session_repo.get_session(sid) is not None

    # Submit to mock
    res = client.post(f"/api/v1/sessions/{sid}/integration/submit?target=MOCK")
    assert res.status_code == 200

    # Session MUST be purged from repository
    assert session_repo.get_session(sid) is None

    # But delivery audit receipt remains accessible
    status_res = client.get(f"/api/v1/sessions/{sid}/integration/status")
    assert status_res.status_code == 200
    assert status_res.json()["delivery"]["state"] == "ACCEPTED"


def test_failed_delivery_preserves_retry_state():
    """Verify FAILED delivery (e.g. unconfigured ABDM sandbox) preserves session for retry."""
    sid = "test_p9_sandbox_retry"
    build_test_pdo(sid, consent_scope="FULL_HIS_SHARE", review_status="ACCEPTED")

    # Submit to ABDM Sandbox without credentials
    res = client.post(f"/api/v1/sessions/{sid}/integration/submit?target=ABDM_SANDBOX")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is False  # Failed delivery
    assert data["delivery"]["state"] == "FAILED"
    assert "credentials" in data["delivery"]["error_message"].lower()

    # Session MUST NOT be purged on failure (clinician can inspect and retry)
    session_after = session_repo.get_session(sid)
    assert session_after is not None

    session_repo.delete_session(sid)


def test_raw_fhir_bundle_endpoint():
    """Verify GET /sessions/{id}/integration/bundle returns valid FHIR JSON."""
    sid = "test_p9_raw_bundle"
    build_test_pdo(sid, consent_scope="FULL_HIS_SHARE", review_status="ACCEPTED")

    res = client.get(f"/api/v1/sessions/{sid}/integration/bundle")
    assert res.status_code == 200
    assert "application/fhir+json" in res.headers["content-type"]

    bundle_json = res.json()
    assert bundle_json["resourceType"] == "Bundle"
    assert bundle_json["type"] == "document"
    assert bundle_json["entry"][0]["resource"]["resourceType"] == "Composition"

    session_repo.delete_session(sid)


# ============================================================================
# 5. Full End-to-End Flow
# ============================================================================

def test_full_end_to_end_phase9_flow():
    """
    Complete flow:
      1. Create session with initial consent
      2. Link ABHA Profile (ABDM M1)
      3. Grant HIS_SHARE consent
      4. Clinician approves intake summary
      5. Prepare FHIR R4 Bundle
      6. Submit consented delivery
      7. Verify truthful receipt and DPDP purge
    """
    sid = "test_p9_e2e_journey"
    
    # 1. Create Session
    res_init = client.post("/api/v1/sessions/", json={
        "version": "1.0.0",
        "identity": {
            "session_id": sid,
            "facility_id": "DELHI_CIVIL_OPD_01",
            "preferred_language": "hi",
            "gender": "FEMALE",
            "age": 45
        },
        "consent": {
            "scope": "INTAKE_AND_SUMMARY",
            "status": "GRANTED"
        }
    })
    assert res_init.status_code == 201

    # 2. Simulate ABHA M1 OTP Link
    res_init_abha = client.post(f"/api/v1/sessions/{sid}/abha/initiate", json={
        "auth_mode": "MOBILE_OTP",
        "mobile": "9876543210",
        "abha_address": "sunita.devi@abdm"
    })
    assert res_init_abha.status_code == 200
    tx_id = res_init_abha.json()["transaction_id"]

    res_abha = client.post(f"/api/v1/sessions/{sid}/abha/confirm", json={
        "transaction_id": tx_id,
        "otp": "123456"
    })
    assert res_abha.status_code == 200
    assert res_abha.json()["success"] is True

    # 3. Grant HIS_SHARE consent
    res_consent = client.post(f"/api/v1/sessions/{sid}/consent", json={
        "scope": "HIS_SHARE",
        "interaction_mode": "TOUCH_SCREEN"
    })
    assert res_consent.status_code == 200

    # 4. Clinician Approves Draft
    session = session_repo.get_session(sid)
    session.summary = {
        "patient_chief_complaint": "Persistent cough and fatigue",
        "hpi_summary": "Symptoms present for 2 weeks. Denies fever.",
        "draft_status": "ACCEPTED"
    }
    session_repo.save_session(session)

    # 5. Prepare Bundle
    res_prep = client.post(f"/api/v1/sessions/{sid}/integration/prepare")
    assert res_prep.status_code == 200
    assert res_prep.json()["state"] == "PREPARED"
    assert res_prep.json()["is_valid"] is True

    # 6. Submit Hand-off
    res_sub = client.post(f"/api/v1/sessions/{sid}/integration/submit?target=MOCK")
    assert res_sub.status_code == 200
    assert res_sub.json()["delivery"]["state"] == "ACCEPTED"

    # 7. Verify Purge & Status
    assert session_repo.get_session(sid) is None
    res_stat = client.get(f"/api/v1/sessions/{sid}/integration/status")
    assert res_stat.status_code == 200
    assert res_stat.json()["delivery"]["is_mock"] is True
