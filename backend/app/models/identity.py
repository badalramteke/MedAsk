from pydantic import BaseModel, Field
from typing import Optional

class IdentityContext(BaseModel):
    """
    Manages the session and identity context for the clinical intake workflow.
    """
    session_id: str = Field(..., description="Internal unique identifier for the intake session.", examples=["sess-demo-001"])
    patient_reference: Optional[str] = Field(None, description="Internal patient reference, if known and linked.", examples=["PAT_1001"])
    external_identifier: Optional[str] = Field(None, description="External identity, like ABHA ID, if verified.", examples=["ABHA_99887766"])
    preferred_language: str = Field(default="en", description="Language code (e.g., 'en', 'hi', 'mr').", examples=["en"])
    facility_id: str = Field(..., description="Identifier for the deployment location or hospital.", examples=["HOSP_AIIMS_DELHI"])
