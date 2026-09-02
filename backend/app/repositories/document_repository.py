from typing import Dict, List, Optional
from app.models.document import DocumentMetadata

class DocumentRepository:
    """In-memory store for uploaded medical document metadata and staged file references."""
    def __init__(self):
        self._documents: Dict[str, DocumentMetadata] = {}

    def add_document(self, doc: DocumentMetadata) -> DocumentMetadata:
        self._documents[doc.document_id] = doc
        return doc

    def get_document(self, document_id: str) -> Optional[DocumentMetadata]:
        return self._documents.get(document_id)

    def list_by_session(self, session_id: str) -> List[DocumentMetadata]:
        return [doc for doc in self._documents.values() if doc.session_id == session_id]

    def count_by_session(self, session_id: str) -> int:
        return len(self.list_by_session(session_id))

document_repo = DocumentRepository()
