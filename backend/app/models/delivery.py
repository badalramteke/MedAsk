from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal
from datetime import datetime
from enum import Enum


class DeliveryState(str, Enum):
    PREPARED = "PREPARED"
    QUEUED = "QUEUED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


class DeliveryTarget(str, Enum):
    MOCK = "MOCK"
    ABDM_SANDBOX = "ABDM_SANDBOX"
    HOSPITAL_HIS = "HOSPITAL_HIS"


class DeliveryRecord(BaseModel):
    """
    Tracks truthful delivery state of consented clinical hand-off to external systems.
    Per PHASES.md: must expose is_mock=True when using simulated adapters;
    never falsely report certified or completed status.
    """
    delivery_id: str = Field(..., description="Unique delivery attempt ID")
    session_id: str = Field(..., description="Associated intake session ID")
    state: DeliveryState = Field(default=DeliveryState.PREPARED)
    target: DeliveryTarget = Field(default=DeliveryTarget.MOCK)
    is_mock: bool = Field(default=True, description="True if delivery is simulated / test; False ONLY for live certified endpoints")
    fhir_bundle_id: Optional[str] = Field(None, description="ID of generated FHIR Bundle")
    bundle_hash: Optional[str] = Field(None, description="SHA256 checksum of generated FHIR Bundle")
    total_resources: int = Field(default=0, description="Total FHIR resources in the package")
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    response_payload: Optional[Dict[str, Any]] = Field(default_factory=dict)
    error_message: Optional[str] = None
