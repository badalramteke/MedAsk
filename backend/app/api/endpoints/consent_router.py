from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal
from app.repositories.session_repository import session_repo
from app.middleware.error_handler import MediKioskException
from app.services.consent_engine import consent_engine

router = APIRouter()

SUPPORTED_SCOPES = Literal[
    "INTAKE_ONLY", "INTAKE_AND_SUMMARY", "DOCUMENTS_PROCESSING", "FULL_HIS_SHARE",
    "INTAKE", "DOCUMENTS", "SUMMARY", "HIS_SHARE"
]


class ConsentGrantRequest(BaseModel):
    """Request to record patient affirmative consent event."""
    scope: SUPPORTED_SCOPES = Field(
        ..., description="The scope of consent being granted (INTAKE, DOCUMENTS, SUMMARY, HIS_SHARE or composite)"
    )
    interaction_mode: Literal["TOUCH_SCREEN", "VOICE_CONFIRMED"] = Field(
        default="TOUCH_SCREEN", description="How consent was captured from patient"
    )
    language: str = Field(default="en", description="Language in which consent notice was presented")
    evidence_reference: Optional[str] = Field(None, description="Optional digital signature / audio timestamp ID")


class ConsentRevokeRequest(BaseModel):
    """Request to revoke a previously granted consent scope."""
    scope: SUPPORTED_SCOPES
    reason: Optional[str] = Field(None, description="Optional reason for revocation")


@router.get("/{session_id}/consent")
def get_session_consent(session_id: str):
    """Retrieve current consent scope, status, policy, and granular scope breakdown."""
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
    Updates the session's active consent scope and audit timestamps.
    """
    session = session_repo.get_session(session_id)
    if not session:
        raise MediKioskException(
            error_code="SESSION_NOT_FOUND",
            message=f"Intake session '{session_id}' not found.",
            status_code=status.HTTP_404_NOT_FOUND
        )

    updated_consent = consent_engine.grant_scope(
        session=session,
        scope=req.scope,
        interaction_mode=req.interaction_mode,
        evidence_reference=req.evidence_reference,
        language=req.language
    )
    session_repo.save_session(session)

    return {
        "success": True,
        "session_id": session_id,
        "scope": updated_consent.scope,
        "status": updated_consent.status,
        "granted_at": updated_consent.granted_at.isoformat() if updated_consent.granted_at else datetime.utcnow().isoformat(),
        "interaction_mode": req.interaction_mode,
        "granular_scopes": {k: v.model_dump() for k, v in updated_consent.scopes.items()},
        "message": f"Consent granted for scope '{req.scope}'."
    }


@router.post("/{session_id}/consent/revoke")
def revoke_session_consent(session_id: str, req: ConsentRevokeRequest):
    """
    Revoke previously granted consent scope.
    Stops further processing for that scope under DPDP Act.
    """
    session = session_repo.get_session(session_id)
    if not session:
        raise MediKioskException(
            error_code="SESSION_NOT_FOUND",
            message=f"Intake session '{session_id}' not found.",
            status_code=status.HTTP_404_NOT_FOUND
        )

    updated_consent = consent_engine.revoke_scope(
        session=session,
        scope=req.scope,
        reason=req.reason
    )
    session_repo.save_session(session)

    return {
        "success": True,
        "session_id": session_id,
        "scope": req.scope,
        "status": updated_consent.status,
        "message": f"Consent for scope '{req.scope}' has been revoked. Further processing halted."
    }


@router.get("/{session_id}/consent/audio-script")
def get_consent_audio_script(
    session_id: str,
    scope: str = Query(default="INTAKE", description="Consent scope to explain"),
    language: str = Query(default="en", description="Patient preferred language code (en, hi, mr, bn, ta, te)")
):
    """
    Retrieve localized audio guidance text for kiosk TTS playback.
    Enables zero-training voice-assisted consent under ABDM and DPDP Act.
    """
    session = session_repo.get_session(session_id)
    if not session:
        raise MediKioskException(
            error_code="SESSION_NOT_FOUND",
            message=f"Intake session '{session_id}' not found.",
            status_code=status.HTTP_404_NOT_FOUND
        )

    script_text = consent_engine.get_audio_consent_script(scope=scope, language=language)
    return {
        "session_id": session_id,
        "scope": scope.upper(),
        "language": language.lower(),
        "audio_script": script_text
    }
