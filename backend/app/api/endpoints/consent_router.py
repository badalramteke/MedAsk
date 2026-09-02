from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal
from app.repositories.session_repository import session_repo
from app.middleware.error_handler import MediKioskException

router = APIRouter()

class ConsentGrantRequest(BaseModel):
    """Request to record patient affirmative consent event."""
    scope: Literal["INTAKE_ONLY", "INTAKE_AND_SUMMARY", "DOCUMENTS_PROCESSING", "FULL_HIS_SHARE"] = Field(
        ..., description="The scope of consent being granted"
    )
    interaction_mode: Literal["TOUCH_SCREEN", "VOICE_CONFIRMED"] = Field(
        default="TOUCH_SCREEN", description="How consent was captured from patient"
    )
    language: str = Field(default="en", description="Language in which consent notice was presented")
    evidence_reference: Optional[str] = Field(None, description="Optional digital signature / audio timestamp ID")


class ConsentRevokeRequest(BaseModel):
    """Request to revoke a previously granted consent scope."""
    scope: Literal["INTAKE_ONLY", "INTAKE_AND_SUMMARY", "DOCUMENTS_PROCESSING", "FULL_HIS_SHARE"]
    reason: Optional[str] = Field(None, description="Optional reason for revocation")


@router.get("/{session_id}/consent")
def get_session_consent(session_id: str):
    """Retrieve current consent scope, status, and policy information."""
    session = session_repo.get_session(session_id)
    if not session:
        raise MediKioskException(
            error_code="SESSION_NOT_FOUND",
            message=f"Intake session '{session_id}' not found.",
            status_code=status.HTTP_404_NOT_FOUND
        )
    return {
        "session_id": session_id,
        "consent": session.consent.model_dump()
    }


@router.post("/{session_id}/consent")
def grant_session_consent(session_id: str, req: ConsentGrantRequest):
    """
    Record explicit affirmative consent under DPDP Act 2023 & ABDM Consent Architecture.
    Updates the session's active consent scope and timestamps.
    """
    session = session_repo.get_session(session_id)
    if not session:
        raise MediKioskException(
            error_code="SESSION_NOT_FOUND",
            message=f"Intake session '{session_id}' not found.",
            status_code=status.HTTP_404_NOT_FOUND
        )

    session.consent.scope = req.scope
    session.consent.status = "GRANTED"
    session.consent.granted_at = datetime.utcnow()
    session.consent.evidence_reference = req.evidence_reference or f"CONSENT_AUDIT_{req.interaction_mode}_{session_id[:8]}"
    session_repo.save_session(session)

    return {
        "success": True,
        "session_id": session_id,
        "scope": session.consent.scope,
        "status": session.consent.status,
        "granted_at": session.consent.granted_at.isoformat(),
        "interaction_mode": req.interaction_mode,
        "message": f"Consent granted for scope '{req.scope}'."
    }


@router.post("/{session_id}/consent/revoke")
def revoke_session_consent(session_id: str, req: ConsentRevokeRequest):
    """
    Revoke previously granted consent scope.
    Stops further processing and flags the session scope as REVOKED.
    """
    session = session_repo.get_session(session_id)
    if not session:
        raise MediKioskException(
            error_code="SESSION_NOT_FOUND",
            message=f"Intake session '{session_id}' not found.",
            status_code=status.HTTP_404_NOT_FOUND
        )

    session.consent.status = "REVOKED"
    session_repo.save_session(session)

    return {
        "success": True,
        "session_id": session_id,
        "scope": req.scope,
        "status": "REVOKED",
        "message": f"Consent for scope '{req.scope}' has been revoked. Further processing halted."
    }
