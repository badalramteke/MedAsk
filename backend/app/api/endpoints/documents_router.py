import uuid
import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from typing import List, Optional
from app.models.document import DocumentMetadata, DocumentExtractionResult, DocumentReviewPatch
from app.repositories.document_repository import document_repo
from app.repositories.session_repository import session_repo
from app.middleware.error_handler import MediKioskException

logger = logging.getLogger("documents_router")
router = APIRouter()

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB limit
MAX_DOCS_PER_SESSION = 5

ALLOWED_MIME_TYPES = {
    "image/jpeg": [b"\xff\xd8\xff"],
    "image/jpg": [b"\xff\xd8\xff"],
    "image/png": [b"\x89PNG\r\n\x1a\n"],
    "application/pdf": [b"%PDF-"],
}

def validate_magic_bytes(content: bytes, declared_mime: str) -> bool:
    """Validate file content matches declared image/pdf signatures."""
    if declared_mime not in ALLOWED_MIME_TYPES:
        return False
    signatures = ALLOWED_MIME_TYPES[declared_mime]
    return any(content.startswith(sig) for sig in signatures)


@router.post("/{session_id}/documents/upload")
async def upload_document(
    session_id: str,
    file: UploadFile = File(...),
    doc_type: str = Form(default="OTHER"),
):
    """
    Upload a medical document and immediately process it (synchronous OCR + entity extraction).
    Phase 8: Processing runs inline at upload — patient waits briefly and sees extraction results.

    Pipeline:
      Text docs (PRESCRIPTION, LAB_REPORT, DISCHARGE_SUMMARY) → OCR → MedGemma entity extraction
      Imaging (IMAGING_SCAN) → direct MedGemma Multimodal vision
    """
    session = session_repo.get_session(session_id)
    if not session:
        raise MediKioskException(
            error_code="SESSION_NOT_FOUND",
            message=f"Intake session '{session_id}' not found.",
            status_code=status.HTTP_404_NOT_FOUND
        )

    # Verify DPDP / ABDM consent scope
    if session.consent.status != "GRANTED" or session.consent.scope not in ("DOCUMENTS_PROCESSING", "INTAKE_AND_SUMMARY", "FULL_HIS_SHARE"):
        raise MediKioskException(
            error_code="CONSENT_REQUIRED",
            message="Document processing consent has not been granted for this session.",
            status_code=status.HTTP_403_FORBIDDEN,
            retry_guidance="Obtain explicit DOCUMENTS_PROCESSING consent before uploading files."
        )

    # Check quota
    current_count = document_repo.count_by_session(session_id)
    if current_count >= MAX_DOCS_PER_SESSION:
        raise MediKioskException(
            error_code="DOCUMENT_REJECTED",
            message=f"Session upload quota exceeded. Maximum {MAX_DOCS_PER_SESSION} documents permitted per intake.",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # Read and validate size
    content = await file.read()
    file_size = len(content)
    if file_size > MAX_FILE_SIZE:
        raise MediKioskException(
            error_code="DOCUMENT_REJECTED",
            message=f"File exceeds maximum size of 10MB ({file_size / (1024*1024):.2f}MB uploaded).",
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        )

    mime_type = file.content_type or "application/octet-stream"
    if not validate_magic_bytes(content, mime_type):
        raise MediKioskException(
            error_code="DOCUMENT_REJECTED",
            message=f"File format or magic bytes rejected. Permitted formats: JPEG, PNG, PDF. Declared MIME: {mime_type}",
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            retry_guidance="Upload a valid standard JPG, PNG, or PDF file."
        )

    # Create document metadata
    doc_index = current_count + 1
    doc_id = f"DOC_{uuid.uuid4().hex[:8].upper()}"
    source_tag = f"[Doc#{doc_index}: {doc_type.replace('_', ' ').title()}]"

    doc_meta = DocumentMetadata(
        document_id=doc_id,
        session_id=session_id,
        file_name=file.filename or "uploaded_document",
        file_type=doc_type if doc_type in ("PRESCRIPTION", "LAB_REPORT", "DISCHARGE_SUMMARY", "IMAGING_SCAN", "OTHER") else "OTHER",
        mime_type=mime_type,
        file_size_bytes=file_size,
        source_tag=source_tag,
        is_readable=True,
        ocr_status="PROCESSING",
        extracted_text_preview=None
    )

    document_repo.add_document(doc_meta)
    # Stage file bytes temporarily for OCR processing
    document_repo.store_file_bytes(doc_id, content)

    # Track document in session dictionary
    session.documents[doc_id] = doc_meta.model_dump()
    session_repo.save_session(session)

    # ======================================================================
    # Phase 8: Synchronous OCR + Entity Extraction at Upload
    # ======================================================================
    extraction_result = None
    try:
        extraction_result = await _process_document(
            doc_meta=doc_meta,
            file_bytes=content,
            session_id=session_id,
        )
    except Exception as e:
        logger.error(f"Document processing failed for {doc_id}: {e}")
        doc_meta.ocr_status = "FAILED"
        document_repo.update_document(doc_meta)
    finally:
        # DPDP: Purge raw file bytes from memory and repository after processing
        document_repo.purge_file_bytes(doc_id)
        content = None  # Release memory reference

    response = {
        "success": True,
        "document": doc_meta.model_dump(),
        "message": f"Document uploaded and processed as {source_tag}.",
    }
    if extraction_result:
        response["extraction"] = extraction_result.model_dump()
        response["abnormal_flags"] = [f.model_dump() for f in extraction_result.abnormal_flags]
    return response


async def _process_document(
    doc_meta: DocumentMetadata,
    file_bytes: bytes,
    session_id: str,
) -> Optional[DocumentExtractionResult]:
    """
    Internal: Run the three-path document processing pipeline.
    Path 1A: Printed text → Tesseract OCR → MedGemma text entity extraction
    Path 1B: Handwritten → Tesseract confidence check → MedGemma Vision fallback
    Path 2:  Medical imaging → direct MedGemma Multimodal (no OCR)
    """
    from app.services.ocr.ocr_service import ocr_service
    from app.services.document.entity_extractor import entity_extractor
    from app.services.document.lab_normalizer import lab_normalizer
    from app.services.model_service import model_service
    from app.models.provenance import Provenance
    import base64

    doc_type = doc_meta.file_type

    # ---- Path 2: Medical Imaging → direct MedGemma Multimodal ----
    if doc_type == "IMAGING_SCAN":
        image_b64 = base64.b64encode(file_bytes).decode("utf-8")
        model_response = await model_service.analyze_medical_image(
            image_base64=image_b64,
            modality_hint="MEDICAL_IMAGING",
            session_id=session_id,
        )

        extraction = DocumentExtractionResult(
            document_id=doc_meta.document_id,
            session_id=session_id,
            document_type=doc_type,
            source_tag=doc_meta.source_tag,
            ocr_raw_text_length=0,
            ocr_engine_used="medgemma_multimodal",
            document_date=None,
            date_confidence="UNKNOWN",
            date_uncertainty=True,
            clinician_review_flags=["Medical imaging — requires radiologist review"],
            review_status="PENDING",
            provenance=Provenance(
                source_type="AI_EXTRACTED",
                source_id=f"ModelService:{model_response.provider_used}",
                confidence=model_response.confidence_score,
            ),
        )

        doc_meta.ocr_status = "PROCESSED"
        doc_meta.ocr_engine_used = "medgemma_multimodal"
        document_repo.update_document(doc_meta)
        document_repo.save_extraction_result(extraction)
        return extraction

    # ---- Path 1A/1B: Text Documents → OCR → Entity Extraction ----
    ocr_result = await ocr_service.extract_text(
        image_bytes=file_bytes,
        mime_type=doc_meta.mime_type,
        document_type=doc_type,
    )

    ocr_engine = ocr_result.get("engine_used", "NONE")
    ocr_text = ocr_result.get("text", "")
    ocr_confidence = ocr_result.get("confidence", 0.0)
    needs_vision = ocr_result.get("needs_vision_fallback", False)

    # Path 1B: If handwriting confidence is too low, fall back to MedGemma Vision
    if needs_vision and doc_type == "PRESCRIPTION":
        logger.info(f"Handwriting confidence {ocr_confidence:.2f} below threshold. Using MedGemma Vision.")
        image_b64 = base64.b64encode(file_bytes).decode("utf-8")
        model_response = await model_service.analyze_medical_image(
            image_base64=image_b64,
            modality_hint="HANDWRITTEN_PRESCRIPTION",
            session_id=session_id,
        )
        ocr_engine = "medgemma_vision_handwriting"

        # If MedGemma Vision returned structured data, use it
        if model_response.success and model_response.structured_payload:
            extraction = DocumentExtractionResult(
                document_id=doc_meta.document_id,
                session_id=session_id,
                document_type=doc_type,
                source_tag=doc_meta.source_tag,
                ocr_raw_text_length=0,
                ocr_engine_used=ocr_engine,
                document_date=model_response.structured_payload.get("document_date"),
                date_confidence="INFERRED",
                date_uncertainty=True,
                clinician_review_flags=[
                    "Handwritten document — processed via MedGemma Vision (Tesseract confidence below threshold)"
                ],
                review_status="PENDING",
                provenance=Provenance(
                    source_type="AI_EXTRACTED",
                    source_id=f"ModelService:{model_response.provider_used}",
                    confidence=model_response.confidence_score,
                ),
            )

            doc_meta.ocr_status = "PROCESSED"
            doc_meta.ocr_engine_used = ocr_engine
            document_repo.update_document(doc_meta)
            document_repo.save_extraction_result(extraction)
            return extraction

    # No OCR text extracted at all — fail gracefully
    if not ocr_text:
        doc_meta.ocr_status = "FAILED"
        doc_meta.ocr_engine_used = ocr_engine
        document_repo.update_document(doc_meta)
        return None

    # Path 1A: Feed OCR text to MedGemma for entity extraction
    doc_meta.extracted_text_preview = ocr_text[:200] if len(ocr_text) > 200 else ocr_text
    extraction = await entity_extractor.extract_entities(
        ocr_text=ocr_text,
        document_id=doc_meta.document_id,
        session_id=session_id,
        document_type=doc_type,
        source_tag=doc_meta.source_tag,
        ocr_engine_used=ocr_engine,
    )

    # Run lab value abnormal flagging
    if extraction.extracted_lab_results:
        abnormals = lab_normalizer.flag_abnormals(
            extracted_lab_results=[lr.model_dump() for lr in extraction.extracted_lab_results],
            gender="female",  # Default; will be session-aware in future
            source_tag=doc_meta.source_tag,
        )
        extraction.abnormal_flags = abnormals

        # Mark abnormal labs in the results themselves
        for lab in extraction.extracted_lab_results:
            for flag in abnormals:
                if lab.test_name == flag.test_name:
                    lab.is_abnormal = True
                    lab.abnormality_severity = flag.severity

    doc_meta.ocr_status = "PROCESSED"
    doc_meta.ocr_engine_used = ocr_engine
    document_repo.update_document(doc_meta)
    document_repo.save_extraction_result(extraction)

    # Purge OCR raw text from local scope (DPDP)
    ocr_text = None
    return extraction


# ======================================================================
# Existing Endpoints (Phase 6 — unchanged)
# ======================================================================

@router.get("/{session_id}/documents")
def list_session_documents(session_id: str):
    """List all staged medical documents for an intake session."""
    session = session_repo.get_session(session_id)
    if not session:
        raise MediKioskException(
            error_code="SESSION_NOT_FOUND",
            message=f"Intake session '{session_id}' not found.",
            status_code=status.HTTP_404_NOT_FOUND
        )

    docs = document_repo.list_by_session(session_id)
    return {
        "session_id": session_id,
        "total_documents": len(docs),
        "documents": [d.model_dump() for d in docs]
    }


@router.get("/{session_id}/documents/{document_id}")
def get_document_details(session_id: str, document_id: str):
    """Retrieve detailed metadata for a specific staged document."""
    doc = document_repo.get_document(document_id)
    if not doc or doc.session_id != session_id:
        raise MediKioskException(
            error_code="NOT_FOUND",
            message=f"Document '{document_id}' not found in session '{session_id}'.",
            status_code=status.HTTP_404_NOT_FOUND
        )
    return doc.model_dump()


# ======================================================================
# Phase 8: New Endpoints
# ======================================================================

@router.get("/{session_id}/documents/{document_id}/extraction")
def get_extraction_result(session_id: str, document_id: str):
    """
    Retrieve the structured extraction result for a processed document.
    Returns medications, lab values, diagnoses, procedures, abnormal flags, and timeline date.
    """
    extraction = document_repo.get_extraction_result(document_id)
    if not extraction or extraction.session_id != session_id:
        raise MediKioskException(
            error_code="NOT_FOUND",
            message=f"No extraction result found for document '{document_id}' in session '{session_id}'.",
            status_code=status.HTTP_404_NOT_FOUND
        )
    return extraction.model_dump()


@router.get("/{session_id}/documents/timeline")
def get_document_timeline(session_id: str):
    """
    Get chronologically sorted medical document timeline for a session.
    Dates are sorted oldest → newest. Documents with uncertain dates are appended at the end.
    """
    from app.services.document.timeline_organizer import timeline_organizer

    session = session_repo.get_session(session_id)
    if not session:
        raise MediKioskException(
            error_code="SESSION_NOT_FOUND",
            message=f"Intake session '{session_id}' not found.",
            status_code=status.HTTP_404_NOT_FOUND
        )

    results = document_repo.get_document_timeline(session_id)
    timeline = timeline_organizer.sort_chronologically(results)

    return {
        "session_id": session_id,
        "total_entries": len(timeline),
        "timeline": [entry.model_dump() for entry in timeline]
    }


@router.post("/{session_id}/documents/{document_id}/review")
def review_document_extraction(
    session_id: str,
    document_id: str,
    review: DocumentReviewPatch,
):
    """
    Clinician review action on a document extraction result.
    Actions: APPROVE (accept as-is), AMEND (accept with corrections), REJECT (discard).
    Only APPROVED/AMENDED results will be used in Phase 9 FHIR payload generation.
    """
    from app.models.provenance import Provenance

    extraction = document_repo.get_extraction_result(document_id)
    if not extraction or extraction.session_id != session_id:
        raise MediKioskException(
            error_code="NOT_FOUND",
            message=f"No extraction result found for document '{document_id}' in session '{session_id}'.",
            status_code=status.HTTP_404_NOT_FOUND
        )

    if review.action == "APPROVE":
        extraction.review_status = "APPROVED"
    elif review.action == "AMEND":
        extraction.review_status = "AMENDED"
        if review.amendments:
            for key, value in review.amendments.items():
                if hasattr(extraction, key):
                    setattr(extraction, key, value)
        # Record clinician provenance on amendment
        extraction.provenance = Provenance(
            source_type="CLINICIAN_EDITED",
            source_id="clinician_review",
            confidence=1.0,
            review_status="APPROVED",
        )
    elif review.action == "REJECT":
        extraction.review_status = "REJECTED"

    document_repo.save_extraction_result(extraction)

    return {
        "success": True,
        "document_id": document_id,
        "review_status": extraction.review_status,
        "message": f"Document extraction {review.action.lower()}ed by clinician.",
        "reviewer_notes": review.reviewer_notes,
    }
