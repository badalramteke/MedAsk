from pydantic import BaseModel, Field
from typing import Optional

class IdentityContext(BaseModel):
    """
    Manages the session and identity context for the clinical intake workflow.
    """
<<<<<<< HEAD
    session_id: str = Field(..., description="Internal unique identifier for the intake session.", examples=["sess-demo-001"])
    patient_reference: Optional[str] = Field(None, description="Internal patient reference, if known and linked.", examples=["PAT_1001"])
    external_identifier: Optional[str] = Field(None, description="External identity, like ABHA ID, if verified.", examples=["ABHA_99887766"])
    preferred_language: str = Field(default="en", description="Language code (e.g., 'en', 'hi', 'mr').", examples=["en"])
    facility_id: str = Field(..., description="Identifier for the deployment location or hospital.", examples=["HOSP_AIIMS_DELHI"])
=======
    session_id: str = Field(..., description="Internal unique identifier for the intake session.")
    patient_reference: Optional[str] = Field(None, description="Internal patient reference, if known and linked.")
    external_identifier: Optional[str] = Field(None, description="External identity, like ABHA ID, if verified.")
    preferred_language: str = Field(default="en", description="Language code (e.g., 'en', 'hi', 'mr').")
    facility_id: str = Field(..., description="Identifier for the deployment location or hospital.")
    gender: Optional[str] = Field(default=None, description="Patient gender (e.g., 'FEMALE', 'MALE', 'OTHER').")
    age: Optional[int] = Field(default=None, description="Patient age in years.")
>>>>>>> 08044f9174ea2fb3ea978904b0babdf267e1e08b
