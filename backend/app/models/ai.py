from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime
from app.models.provenance import Provenance


class ModelCapability(str, Enum):
    TEXT_NARRATION_STRUCTURING = "TEXT_NARRATION_STRUCTURING"
    MEDICAL_IMAGE_ANALYSIS = "MEDICAL_IMAGE_ANALYSIS"
    SUMMARY_SYNTHESIS = "SUMMARY_SYNTHESIS"
    FOLLOWUP_PROPOSAL = "FOLLOWUP_PROPOSAL"


class ModelTaskRequest(BaseModel):
    capability: ModelCapability
    task_name: str = Field(..., description="E.g., 'structure_narration', 'synthesize_summary', 'analyze_image'")
    prompt_version: str = Field(default="v1.0.0")
    language: str = Field(default="en")
    untrusted_input: str = Field(..., description="Raw text, transcription, or OCR payload from patient/document")
    document_sources: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Source documents with metadata")
    image_base64: Optional[str] = Field(default=None, description="Base64-encoded image for multimodal tasks")
    session_id: Optional[str] = Field(default=None)


class StructuredNarrationResult(BaseModel):
    primary_symptom: Optional[str] = Field(None, description="Standardized symptom name e.g. chest_pain, headache")
    site: Optional[str] = Field(None, description="Anatomical location")
    onset: Optional[str] = Field(None, description="How and when it began")
    character: Optional[str] = Field(None, description="Pain/symptom character (sharp, dull, crushing)")
    radiation: Optional[str] = Field(None, description="Radiation direction/site")
    severity: Optional[str] = Field(None, description="Severity estimate")
    associated_symptoms: List[str] = Field(default_factory=list)
    uncertainty_notes: Optional[str] = Field(None, description="Ambiguities noted in narration")


class MedicalImageFindings(BaseModel):
    modality: str = Field(..., description="e.g. CHEST_XRAY, SONOGRAPHY_USG, CT_SCAN, MRI")
    anatomical_region: Optional[str] = None
    candidate_observations: List[str] = Field(default_factory=list, description="Descriptive visual patterns observed")
    uncertainty_level: str = Field(default="MODERATE", description="LOW, MODERATE, HIGH")
    requires_radiologist_review: bool = Field(default=True)


class SourceAttributedFinding(BaseModel):
    finding_text: str = Field(..., description="Clinical observation or test range")
    source_tag: str = Field(..., description="e.g. [Patient-Reported], [Doc#1: CBC Lab 2024-05-10], [Doc#2: Prescription]")
    category: str = Field(default="HISTORY", description="CHIEF_COMPLAINT, HPI, LAB_INVESTIGATION, MEDICATION, IMAGING")


class ClinicalSummaryDraft(BaseModel):
    patient_chief_complaint: str
    hpi_summary: str
    past_history_summary: Optional[str] = None
    medications_and_allergies: Optional[str] = None
    investigations_and_lab_summary: Optional[str] = None
    imaging_findings_summary: Optional[str] = None
    menstrual_reproductive_summary: Optional[str] = None
    source_citations: List[SourceAttributedFinding] = Field(default_factory=list)
    is_draft_for_clinician_review: bool = Field(default=True)


class ModelTaskResponse(BaseModel):
    success: bool
    capability: ModelCapability
    provider_used: str = Field(..., description="e.g. colab_medgemma, gemini, groq, mock")
    model_name: str = Field(default="medgemma")
    prompt_version: str = Field(default="v1.0.0")
    latency_ms: float = Field(default=0.0)
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)
    safety_validation_passed: bool = Field(default=True)
    raw_response: Optional[str] = None
    structured_payload: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
