from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal

class TriageAlertItem(BaseModel):
    """
    Staff-facing emergency triage alert item.
    """
    alert_id: str = Field(..., description="Unique alert identifier")
    session_id: str = Field(..., description="Intake session that triggered the alert")
    facility_id: str = Field(default="GENERAL", description="Hospital facility location")
    patient_gender: Optional[str] = None
    patient_age: Optional[int] = None
    flag_id: str = Field(..., description="Clinical flag rule identifier")
    severity: Literal["CRITICAL", "HIGH", "MODERATE", "INFORMATIONAL"] = Field(default="CRITICAL")
    message: str = Field(..., description="Alert description and recommended triage action")
    status: Literal["TRIGGERED", "ACKNOWLEDGED", "RESOLVED"] = Field(default="TRIGGERED")
    triggered_at: datetime = Field(default_factory=datetime.utcnow)
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    triage_notes: Optional[str] = None


class AlertAcknowledgeRequest(BaseModel):
    staff_id: str = Field(..., description="Staff/Nurse ID acknowledging the alert")
    triage_action: str = Field(..., description="Action taken e.g. FAST_TRACK_ECG, VITALS_CHECK, ESCALATED_TO_CMO")
    notes: Optional[str] = Field(None, description="Optional notes on patient status")
