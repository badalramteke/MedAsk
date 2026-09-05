from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Literal
from app.models.provenance import Provenance


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
    extracted_text_preview: Optional[str] = Field(None, description="Preview of OCR extracted text (first 200 chars)")
    ocr_engine_used: Optional[str] = Field(None, description="tesseract | paddleocr | medgemma_vision_handwriting | mock")
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# Phase 8: Document Entity Extraction Models (Module B)
# ============================================================================

class ExtractedMedication(BaseModel):
    """A single medication extracted from a scanned prescription or discharge summary."""
    drug_name: str = Field(..., description="Medication name as written/printed")
    dosage: Optional[str] = Field(None, description="Dosage e.g. '500mg', '10ml'")
    frequency: Optional[str] = Field(None, description="Frequency e.g. 'twice daily', 'BD'")
    route: Optional[str] = Field(None, description="Route e.g. 'oral', 'IV', 'topical'")
    duration: Optional[str] = Field(None, description="Duration e.g. '5 days', '2 weeks'")
    source_tag: str = Field(..., description="Provenance e.g. [Doc#1: Prescription 2024-03-15]")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)


class ExtractedLabResult(BaseModel):
    """A single lab test result extracted from a scanned lab report."""
    test_name: str = Field(..., description="Lab test name e.g. 'Hemoglobin', 'Blood Glucose Fasting'")
    value: str = Field(..., description="Extracted value as string e.g. '12.5', '98'")
    unit: Optional[str] = Field(None, description="Unit e.g. 'g/dL', 'mg/dL', 'mIU/L'")
    reference_range: Optional[str] = Field(None, description="Reference range as printed e.g. '12.0-15.5 g/dL'")
    is_abnormal: bool = Field(default=False, description="Whether value falls outside reference range")
    abnormality_severity: Optional[Literal["LOW", "MODERATE", "HIGH"]] = Field(
        None, description="Severity of abnormality if out-of-range"
    )
    source_tag: str = Field(..., description="Provenance e.g. [Doc#2: CBC Lab 2024-05-10]")
    confidence: float = Field(default=0.85, ge=0.0, le=1.0)


class ExtractedDiagnosis(BaseModel):
    """A diagnosis mention extracted from a document — NOT a MediKiosk-generated diagnosis."""
    diagnosis_text: str = Field(..., description="Diagnosis as written in the source document")
    icd_hint: Optional[str] = Field(
        None, description="Best-effort ICD code hint — NOT clinical truth, for search/indexing only"
    )
    source_tag: str = Field(..., description="Provenance e.g. [Doc#3: Discharge Summary 2024-01-20]")
    confidence: float = Field(default=0.75, ge=0.0, le=1.0)


class AbnormalLabFlag(BaseModel):
    """Flag raised when an extracted lab value falls outside standard reference ranges."""
    test_name: str = Field(..., description="Normalized lab test name")
    extracted_value: str = Field(..., description="The numeric value as extracted")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    ref_range_low: Optional[float] = Field(None, description="Lower bound of reference range")
    ref_range_high: Optional[float] = Field(None, description="Upper bound of reference range")
    severity: Literal["LOW", "MODERATE", "HIGH"] = Field(
        ..., description="LOW: borderline, MODERATE: clinically notable, HIGH: critical deviation"
    )
    source_tag: str = Field(..., description="Source document provenance tag")


class DocumentExtractionResult(BaseModel):
    """
    Complete structured extraction output from a single processed medical document.
    This is the primary output contract of Phase 8 Module B.
    All entities are extraction CANDIDATES for clinician review — never final clinical records.
    """
    document_id: str = Field(..., description="Links to DocumentMetadata.document_id")
    session_id: str = Field(..., description="Links to intake session")
    document_type: str = Field(..., description="PRESCRIPTION | LAB_REPORT | DISCHARGE_SUMMARY | IMAGING_SCAN")
    source_tag: str = Field(..., description="Provenance citation tag")
    ocr_raw_text_length: int = Field(default=0, description="Character count of OCR text (raw text NOT stored — DPDP)")
    ocr_engine_used: str = Field(default="mock", description="tesseract | medgemma_vision_handwriting | mock")
    document_date: Optional[str] = Field(None, description="ISO date string or None if undetermined")
    date_confidence: Literal["PRINTED", "CONTEXTUAL", "INFERRED", "UNKNOWN"] = Field(
        default="UNKNOWN", description="How the date was determined"
    )
    date_uncertainty: bool = Field(default=True, description="True if date is inferred or unknown")
    extracted_medications: List[ExtractedMedication] = Field(default_factory=list)
    extracted_lab_results: List[ExtractedLabResult] = Field(default_factory=list)
    extracted_diagnoses: List[ExtractedDiagnosis] = Field(default_factory=list)
    extracted_procedures: List[str] = Field(default_factory=list, description="Plain text procedures/surgeries")
    abnormal_flags: List[AbnormalLabFlag] = Field(default_factory=list)
    clinician_review_flags: List[str] = Field(
        default_factory=list,
        description="Contradictions, low-confidence items, unreadable sections flagged for the doctor"
    )
    review_status: Literal["PENDING", "APPROVED", "AMENDED", "REJECTED"] = Field(default="PENDING")
    provenance: Optional[Provenance] = Field(None, description="AI extraction provenance tracking")
    processed_at: datetime = Field(default_factory=datetime.utcnow)


class DocumentTimelineEntry(BaseModel):
    """A single entry in the patient's chronological medical document timeline."""
    document_id: str
    document_type: str
    document_date: Optional[str] = Field(None, description="ISO date string")
    date_uncertainty: bool = Field(default=True)
    date_confidence: str = Field(default="UNKNOWN")
    summary_text: str = Field(..., description="Brief one-line summary for timeline display")
    source_tag: str
    has_abnormals: bool = Field(default=False)
    total_medications: int = Field(default=0)
    total_lab_results: int = Field(default=0)
    total_diagnoses: int = Field(default=0)


class DocumentReviewPatch(BaseModel):
    """Clinician's review action on a document extraction result."""
    action: Literal["APPROVE", "AMEND", "REJECT"] = Field(..., description="Clinician's decision")
    amendments: Optional[Dict] = Field(
        None, description="Partial corrections to extracted fields (only for AMEND action)"
    )
    reviewer_notes: Optional[str] = Field(None, description="Clinician's notes on why they amended/rejected")

