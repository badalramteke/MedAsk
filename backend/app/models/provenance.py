from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal

class Provenance(BaseModel):
    """
    Tracks the origin and confidence of data within the PatientDataObject.
    """
    source_type: Literal["PATIENT_REPORTED", "CLINICIAN_EDITED", "AI_EXTRACTED", "AI_GENERATED", "INTEGRATION_SYSTEM"] = Field(
        ..., description="The type of actor that produced this data."
    )
    source_id: str = Field(
        ..., description="Identifier for the source (e.g., model name, plugin ID, user ID)."
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="When this data was captured or generated."
    )
    confidence: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="For AI/extracted data, a confidence score between 0.0 and 1.0."
    )
    review_status: Literal["PENDING", "APPROVED", "REJECTED", "NOT_APPLICABLE"] = Field(
        default="NOT_APPLICABLE", description="Status of human review."
    )
