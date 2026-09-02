import uuid
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from typing import List, Optional
from app.models.document import DocumentMetadata
from app.repositories.document_repository import document_repo
from app.repositories.session_repository import session_repo
from app.middleware.error_handler import MediKioskException

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
    Upload and stage a medical document (Prescription, Lab Report, Discharge Summary, Scan).
    Validates file size, magic bytes, session quota, and consent prerequisites.
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
        ocr_status="PENDING",
        extracted_text_preview=None
    )

    document_repo.add_document(doc_meta)
    
    # Track document in session dictionary
    session.documents[doc_id] = doc_meta.model_dump()
    session_repo.save_session(session)

    return {
        "success": True,
        "document": doc_meta.model_dump(),
        "message": f"Document uploaded successfully and staged as {source_tag}."
    }


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
