"""
Phase 8 Test Suite: Medical Document Digitization Module (Module B)
Tests: OCR extraction, entity extraction, lab abnormal flagging, timeline,
       upload+process endpoint, imaging route, clinician review.
13 tests total — all using mock adapters for deterministic offline testing.
Uses synchronous patterns matching existing test suites.
"""
import pytest
import asyncio
import sys
import os
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

# Ensure the backend app is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.main import app
from app.models.document import (
    DocumentMetadata, DocumentExtractionResult, AbnormalLabFlag,
    ExtractedMedication, ExtractedLabResult, ExtractedDiagnosis,
    DocumentTimelineEntry, DocumentReviewPatch,
)
from app.models.provenance import Provenance
from app.repositories.document_repository import DocumentRepository
from app.services.document.lab_normalizer import LabValueNormalizer
from app.services.document.timeline_organizer import TimelineOrganizer

client = TestClient(app)


def run_async(coro):
    """Helper to run async functions in synchronous tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# ============================================================================
# Test 1: MockOCRAdapter returns text for prescription
# ============================================================================

def test_ocr_mock_adapter_prescription():
    """MockOCRAdapter returns realistic prescription text deterministically."""
    from app.services.ocr.mock_ocr_adapter import MockOCRAdapter

    adapter = MockOCRAdapter()
    success, text, confidence, error = run_async(
        adapter.extract_text(b"fake", "image/jpeg", document_type="PRESCRIPTION")
    )

    assert success is True
    assert "Metformin" in text
    assert "Amlodipine" in text
    assert "15-Mar-2024" in text
    assert confidence > 0.5
    assert error == ""


# ============================================================================
# Test 2: MockOCRAdapter returns text for lab report
# ============================================================================

def test_ocr_mock_adapter_lab_report():
    """MockOCRAdapter returns realistic lab report text with values and ranges."""
    from app.services.ocr.mock_ocr_adapter import MockOCRAdapter

    adapter = MockOCRAdapter()
    success, text, confidence, error = run_async(
        adapter.extract_text(b"fake", "image/jpeg", document_type="LAB_REPORT")
    )

    assert success is True
    assert "Hemoglobin" in text
    assert "9.8" in text
    assert "HbA1c" in text
    assert len(text) > 100


# ============================================================================
# Test 3: OCR cascade falls back to MockOCRAdapter
# ============================================================================

def test_ocr_service_cascade_fallback():
    """OCRService cascade falls to MockOCRAdapter when Tesseract unavailable."""
    from app.services.ocr.ocr_service import OCRService

    service = OCRService()
    result = run_async(service.extract_text(
        image_bytes=b"\xff\xd8\xff\xe0" + b"\x00" * 50,
        mime_type="image/jpeg",
        document_type="LAB_REPORT",
    ))

    assert result["success"] is True
    assert len(result["text"]) > 50
    assert result["engine_used"] in ("TESSERACT", "MOCK_OCR")
    assert result["latency_ms"] >= 0


# ============================================================================
# Test 4: MockOCRAdapter is always online
# ============================================================================

def test_ocr_mock_adapter_always_available():
    """MockOCRAdapter health check always returns online."""
    from app.services.ocr.mock_ocr_adapter import MockOCRAdapter

    adapter = MockOCRAdapter()
    status = run_async(adapter.health_check())

    assert status["status"] == "online"
    assert status["offline_ready"] is True


# ============================================================================
# Test 5: IMAGING_SCAN returns no text (skip OCR)
# ============================================================================

def test_ocr_imaging_scan_skips_ocr():
    """IMAGING_SCAN type routes to MedGemma Multimodal, no OCR text returned."""
    from app.services.ocr.ocr_service import OCRService

    service = OCRService()
    result = run_async(service.extract_text(
        image_bytes=b"\xff\xd8\xff\xe0" + b"\x00" * 50,
        mime_type="image/jpeg",
        document_type="IMAGING_SCAN",
    ))

    assert result["success"] is False
    assert result["needs_vision_fallback"] is True
    assert result["engine_used"] == "NONE"


# ============================================================================
# Test 6: Date extraction from prescription text
# ============================================================================

def test_entity_extractor_date_extraction_prescription():
    """Entity extractor parses date from prescription OCR text."""
    from app.services.document.entity_extractor import DocumentEntityExtractor

    extractor = DocumentEntityExtractor()
    sample_text = """Dr. Rajesh Kumar, MBBS
Date: 15-Mar-2024
Rx:
1. Tab. Metformin 500mg - twice daily
Diagnosis: Type 2 Diabetes Mellitus"""

    doc_date, confidence = extractor._extract_date_from_text(sample_text)
    assert doc_date == "2024-03-15"
    assert confidence in ("PRINTED", "CONTEXTUAL")


# ============================================================================
# Test 7: Date extraction from lab report text
# ============================================================================

def test_entity_extractor_date_extraction_lab_report():
    """Entity extractor finds date in lab report text."""
    from app.services.document.entity_extractor import DocumentEntityExtractor

    extractor = DocumentEntityExtractor()
    sample_text = """Pathology Laboratory
Complete Blood Count (CBC)
Date: 10-May-2024
Hemoglobin: 9.8 g/dL"""

    doc_date, confidence = extractor._extract_date_from_text(sample_text)
    assert doc_date == "2024-05-10"
    assert confidence in ("PRINTED", "CONTEXTUAL")


# ============================================================================
# Test 8: Hemoglobin 9.8 flagged as abnormal for female
# ============================================================================

def test_lab_value_abnormal_flagging():
    """Hemoglobin 9.8 g/dL correctly flagged as abnormal for female patient."""
    normalizer = LabValueNormalizer()
    lab_results = [
        {"test_name": "Hemoglobin", "value": "9.8", "source_tag": "[Doc#1: CBC]"},
        {"test_name": "HbA1c", "value": "8.2", "source_tag": "[Doc#1: CBC]"},
    ]

    flags = normalizer.flag_abnormals(lab_results, gender="female", source_tag="[Doc#1]")

    assert len(flags) >= 1
    hb_flag = next((f for f in flags if f.test_name == "Hemoglobin"), None)
    assert hb_flag is not None
    assert hb_flag.severity in ("LOW", "MODERATE", "HIGH")
    assert hb_flag.ref_range_low == 12.0
    assert hb_flag.ref_range_high == 15.5

    hba1c_flag = next((f for f in flags if f.test_name == "HbA1c"), None)
    assert hba1c_flag is not None  # 8.2 >> 5.7 threshold


# ============================================================================
# Test 9: Normal lab values NOT flagged
# ============================================================================

def test_normal_lab_values_not_flagged():
    """Normal values within reference range produce zero abnormal flags."""
    normalizer = LabValueNormalizer()
    lab_results = [
        {"test_name": "Hemoglobin", "value": "14.0", "source_tag": "[Doc#1]"},
        {"test_name": "Platelet Count", "value": "250", "source_tag": "[Doc#1]"},
        {"test_name": "TSH", "value": "2.5", "source_tag": "[Doc#1]"},
    ]

    flags = normalizer.flag_abnormals(lab_results, gender="male", source_tag="[Doc#1]")
    assert len(flags) == 0


# ============================================================================
# Test 10: Document upload + inline processing endpoint
# ============================================================================

def test_document_upload_and_process_endpoint():
    """POST /sessions/{id}/documents/upload processes document synchronously."""
    from app.repositories.session_repository import session_repo
    from app.repositories.document_repository import document_repo

    # Create mock session with consent
    mock_session = MagicMock()
    mock_session.session_id = "TEST_DOC_UPLOAD"
    mock_session.consent = MagicMock()
    mock_session.consent.status = "GRANTED"
    mock_session.consent.scope = "DOCUMENTS_PROCESSING"
    mock_session.documents = {}
    session_repo._store["TEST_DOC_UPLOAD"] = mock_session

    # Minimal JPEG bytes
    jpeg_bytes = b"\xff\xd8\xff\xe0" + b"\x00" * 100

    response = client.post(
        "/api/v1/sessions/TEST_DOC_UPLOAD/documents/upload",
        files={"file": ("lab_report.jpg", jpeg_bytes, "image/jpeg")},
        data={"doc_type": "LAB_REPORT"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "document" in data
    assert data["document"]["file_type"] == "LAB_REPORT"
    assert data["document"]["ocr_status"] in ("PROCESSED", "FAILED", "PROCESSING")

    # Cleanup
    doc_id = data["document"]["document_id"]
    document_repo.clear_session("TEST_DOC_UPLOAD")
    session_repo._store.pop("TEST_DOC_UPLOAD", None)


# ============================================================================
# Test 11: Timeline chronological sorting
# ============================================================================

def test_document_timeline_sorting():
    """Timeline organizer sorts documents: known dates ascending, unknown dates last."""
    organizer = TimelineOrganizer()

    results = [
        DocumentExtractionResult(
            document_id="DOC_001", session_id="S1", document_type="LAB_REPORT",
            source_tag="[Doc#1]", document_date="2024-05-10",
            date_confidence="PRINTED", date_uncertainty=False,
            provenance=Provenance(source_type="AI_EXTRACTED", source_id="mock"),
        ),
        DocumentExtractionResult(
            document_id="DOC_002", session_id="S1", document_type="PRESCRIPTION",
            source_tag="[Doc#2]", document_date="2024-03-15",
            date_confidence="PRINTED", date_uncertainty=False,
            provenance=Provenance(source_type="AI_EXTRACTED", source_id="mock"),
        ),
        DocumentExtractionResult(
            document_id="DOC_003", session_id="S1", document_type="DISCHARGE_SUMMARY",
            source_tag="[Doc#3]", document_date=None,
            date_confidence="UNKNOWN", date_uncertainty=True,
            provenance=Provenance(source_type="AI_EXTRACTED", source_id="mock"),
        ),
    ]

    timeline = organizer.sort_chronologically(results)

    assert len(timeline) == 3
    assert timeline[0].document_id == "DOC_002"  # Mar 2024 (earliest)
    assert timeline[1].document_id == "DOC_001"  # May 2024
    assert timeline[2].document_id == "DOC_003"  # Unknown date last
    assert timeline[2].date_uncertainty is True


# ============================================================================
# Test 12: Clinician review APPROVE
# ============================================================================

def test_clinician_document_review_approve():
    """Clinician APPROVE action sets review_status=APPROVED."""
    repo = DocumentRepository()

    extraction = DocumentExtractionResult(
        document_id="DOC_REV_001", session_id="S_REV", document_type="LAB_REPORT",
        source_tag="[Doc#1]", review_status="PENDING",
        provenance=Provenance(source_type="AI_EXTRACTED", source_id="mock"),
    )

    repo.save_extraction_result(extraction)
    result = repo.update_review_status("DOC_REV_001", "APPROVED")

    assert result is not None
    assert result.review_status == "APPROVED"


# ============================================================================
# Test 13: Provenance tracking on extraction result
# ============================================================================

def test_extraction_result_provenance_tracking():
    """DocumentExtractionResult correctly stores provenance metadata."""
    extraction = DocumentExtractionResult(
        document_id="DOC_PROV_001", session_id="S_PROV",
        document_type="PRESCRIPTION", source_tag="[Doc#1: Prescription]",
        ocr_engine_used="tesseract",
        provenance=Provenance(
            source_type="AI_EXTRACTED", source_id="ModelService:mock",
            confidence=0.85,
        ),
    )

    assert extraction.provenance.source_type == "AI_EXTRACTED"
    assert extraction.provenance.confidence == 0.85
    assert extraction.review_status == "PENDING"
    assert extraction.ocr_engine_used == "tesseract"
    assert extraction.date_uncertainty is True  # Default
