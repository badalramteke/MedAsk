from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal

class ConsentContext(BaseModel):
    """
    Manages consent scopes and lifecycle for the session.
    """
    scope: Literal["INTAKE_ONLY", "INTAKE_AND_SUMMARY", "DOCUMENTS_PROCESSING", "FULL_HIS_SHARE"] = Field(
        ..., description="The scope of consent granted.", examples=["INTAKE_AND_SUMMARY"]
    )
    status: Literal["GRANTED", "REVOKED", "EXPIRED", "PENDING"] = Field(
        ..., description="Current status of the consent.", examples=["GRANTED"]
    )
    evidence_reference: Optional[str] = Field(
        None, description="Reference to signed document, digital signature, or audit log."
    )
    granted_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(None)
