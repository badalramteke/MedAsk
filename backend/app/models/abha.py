from pydantic import BaseModel, Field
from typing import Optional, Literal

class AbhaAuthInitRequest(BaseModel):
    """Request to initiate ABDM M1 authentication (OTP / Demographic verification)."""
    auth_mode: Literal["MOBILE_OTP", "AADHAAR_OTP", "DEMO_AUTH"] = Field(
        default="MOBILE_OTP", description="Authentication mode for ABHA verification"
    )
    abha_address: Optional[str] = Field(None, description="ABHA address e.g. name@abdm")
    abha_number: Optional[str] = Field(None, description="14-digit ABHA number")
    mobile: Optional[str] = Field(None, description="10-digit mobile number")
    aadhaar_last4: Optional[str] = Field(None, description="Last 4 digits of Aadhaar (if Aadhaar OTP)")


class AbhaAuthInitResponse(BaseModel):
    transaction_id: str
    auth_mode: str
    message: str
    is_mock_sandbox: bool = Field(default=True)


class AbhaAuthConfirmRequest(BaseModel):
    transaction_id: str
    otp: str = Field(..., description="6-digit OTP code")


class AbhaAuthConfirmResponse(BaseModel):
    success: bool
    abha_number: str
    abha_address: str
    name: str
    gender: str
    dob: str
    mobile: Optional[str] = None
    linked_session_id: str
    message: str
