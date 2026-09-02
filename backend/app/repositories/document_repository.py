from typing import Dict, List, Optional
from app.models.document import DocumentMetadata, DocumentExtractionResult, DocumentTimelineEntry


class DocumentRepository:
    """
    In-memory store for uploaded medical document metadata, staged file bytes,
    and Phase 8 extraction results.

    Storage lifecycle (per OCR_PIPELINE.md):
    - File bytes: held temporarily until OCR processing completes, then purged
    - Extraction results: held until Phase 9 FHIR push confirms, then cleared
    - Metadata: minimal audit trail retained
    """
    def __init__(self):
        self._documents: Dict[str, DocumentMetadata] = {}
        self._extraction_results: Dict[str, DocumentExtractionResult] = {}
        self._file_bytes: Dict[str, bytes] = {}  # Ephemeral: purged after OCR

    # ---- Document Metadata CRUD (Phase 6 — unchanged) ----

    def add_document(self, doc: DocumentMetadata) -> DocumentMetadata:
        self._documents[doc.document_id] = doc
        return doc

    def get_document(self, document_id: str) -> Optional[DocumentMetadata]:
        return self._documents.get(document_id)

    def list_by_session(self, session_id: str) -> List[DocumentMetadata]:
        return [doc for doc in self._documents.values() if doc.session_id == session_id]

    def count_by_session(self, session_id: str) -> int:
        return len(self.list_by_session(session_id))

    def update_document(self, doc: DocumentMetadata) -> DocumentMetadata:
        """Update existing document metadata (e.g., ocr_status after processing)."""
        self._documents[doc.document_id] = doc
        return doc

    # ---- Temporary File Byte Buffer (DPDP ephemeral storage) ----

    def store_file_bytes(self, document_id: str, file_bytes: bytes):
        """Stage raw file bytes temporarily for OCR processing."""
        self._file_bytes[document_id] = file_bytes

    def get_file_bytes(self, document_id: str) -> Optional[bytes]:
        """Retrieve staged file bytes for processing."""
        return self._file_bytes.get(document_id)

    def purge_file_bytes(self, document_id: str):
        """
        DPDP: Delete raw file bytes after OCR processing is complete.
        Per DATA_MINIMIZATION.md: 'delete volatile capture frames after permitted processing'
        """
        if document_id in self._file_bytes:
            del self._file_bytes[document_id]

    # ---- Phase 8: Extraction Result CRUD ----

    def save_extraction_result(self, result: DocumentExtractionResult) -> DocumentExtractionResult:
        """Store structured extraction output from OCR + MedGemma processing."""
        self._extraction_results[result.document_id] = result
        return result

    def get_extraction_result(self, document_id: str) -> Optional[DocumentExtractionResult]:
        """Retrieve extraction result for a specific document."""
        return self._extraction_results.get(document_id)

    def list_extraction_results_by_session(self, session_id: str) -> List[DocumentExtractionResult]:
        """List all extraction results for a session."""
        return [r for r in self._extraction_results.values() if r.session_id == session_id]

    def update_review_status(self, document_id: str, status: str, amendments: Optional[Dict] = None) -> Optional[DocumentExtractionResult]:
        """Update clinician review status on an extraction result."""
        result = self._extraction_results.get(document_id)
        if result:
            result.review_status = status
            if amendments and status == "AMENDED":
                # Apply partial amendments to extraction fields
                for key, value in amendments.items():
                    if hasattr(result, key):
                        setattr(result, key, value)
            self._extraction_results[document_id] = result
        return result

    def get_document_timeline(self, session_id: str) -> List[DocumentExtractionResult]:
        """Get all extraction results for timeline synthesis."""
        return self.list_extraction_results_by_session(session_id)

    # ---- Session cleanup ----

    def clear_session(self, session_id: str):
        """
        Clear all documents, extraction results, and file bytes for a session.
        Called after Phase 9 FHIR push confirmation or session termination.
        """
        doc_ids = [doc.document_id for doc in self.list_by_session(session_id)]
        for doc_id in doc_ids:
            self._documents.pop(doc_id, None)
            self._extraction_results.pop(doc_id, None)
            self._file_bytes.pop(doc_id, None)


document_repo = DocumentRepository()

