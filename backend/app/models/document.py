from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal

class DocumentMetadata(BaseModel):
    """
    Metadata for uploaded patient medical documents.
    """
    document_id: str = Field(..., description="Unique document identifier")
    session_id: str = Field(..., description="Associated intake session ID")
    file_name: str = Field(..., description="Original filename")
    file_type: Literal["PRESCRIPTION", "LAB_REPORT", "DISCHARGE_SUMMARY", "IMAGING_SCAN", "OTHER"] = Field(
        default="OTHER", description="Classification of medical document"
    )
    mime_type: str = Field(..., description="MIME type e.g. image/jpeg, application/pdf")
    file_size_bytes: int = Field(..., description="File size in bytes")
    source_tag: str = Field(..., description="Provenance citation tag e.g. [Doc#1: Lab Report 2024-05-10]")
    is_readable: bool = Field(default=True, description="Whether the document is legible for OCR")
    ocr_status: Literal["PENDING", "PROCESSING", "PROCESSED", "FAILED"] = Field(default="PENDING")
    extracted_text_preview: Optional[str] = Field(None, description="Preview of OCR extracted text")
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
