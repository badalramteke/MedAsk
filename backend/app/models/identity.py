from pydantic import BaseModel, Field
from typing import Optional

class IdentityContext(BaseModel):
    """
    Manages the session and identity context for the clinical intake workflow.
    """
    session_id: str = Field(..., description="Internal unique identifier for the intake session.")
    patient_reference: Optional[str] = Field(None, description="Internal patient reference, if known and linked.")
    external_identifier: Optional[str] = Field(None, description="External identity, like ABHA ID, if verified.")
    preferred_language: str = Field(default="en", description="Language code (e.g., 'en', 'hi', 'mr').")
    facility_id: str = Field(..., description="Identifier for the deployment location or hospital.")
