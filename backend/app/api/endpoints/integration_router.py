from fastapi import APIRouter, HTTPException, status, Query, Response
from typing import Optional, Literal
from app.repositories.session_repository import session_repo
from app.middleware.error_handler import MediKioskException
from app.services.delivery.delivery_service import delivery_service
from app.models.delivery import DeliveryTarget

router = APIRouter()


@router.post("/{session_id}/integration/prepare")
def prepare_fhir_bundle(session_id: str):
    """
    Generate and validate an ABDM NRCeS-compliant FHIR R4 Document Bundle
    from the current session's clinical facts and clinician-reviewed summary.
    Enforces:
      - Active 'HIS_SHARE' consent gate
      - Clinician review gate (draft must be ACCEPTED or AMENDED)
    """
    session = session_repo.get_session(session_id)
    if not session:
        raise MediKioskException(
            error_code="SESSION_NOT_FOUND",
            message=f"Intake session '{session_id}' not found.",
            status_code=status.HTTP_404_NOT_FOUND
        )

    bundle, validation_issues = delivery_service.prepare_bundle(session)
    bundle_dict = bundle.model_dump(by_alias=True)

    return {
        "success": True,
        "session_id": session_id,
        "state": "PREPARED",
        "bundle_id": bundle.id,
        "total_entries": len(bundle.entry),
        "is_valid": len(validation_issues) == 0,
        "validation_issues": validation_issues,
        "bundle": bundle_dict
    }


@router.post("/{session_id}/integration/submit")
async def submit_integration_delivery(
    session_id: str,
    target: str = Query(default="MOCK", description="Delivery target: MOCK | ABDM_SANDBOX | HOSPITAL_HIS")
):
    """
    Submit consented FHIR R4 Bundle to the designated external integration target.
    Enforces truthful status reporting (is_mock=True on mock submissions).
    Upon confirmed 'ACCEPTED' delivery, automatically purges ephemeral session data (DPDP Act).
    """
    session = session_repo.get_session(session_id)
    if not session:
        raise MediKioskException(
            error_code="SESSION_NOT_FOUND",
            message=f"Intake session '{session_id}' not found.",
            status_code=status.HTTP_404_NOT_FOUND
        )

    record = await delivery_service.submit_delivery(session=session, target=target)
    return {
        "success": record.state == "ACCEPTED",
        "delivery": record.model_dump(),
        "message": f"Clinical hand-off submitted to {record.target.value} with status '{record.state.value}'."
    }


@router.get("/{session_id}/integration/status")
def get_integration_delivery_status(session_id: str):
    """
    Query delivery status and audit receipt for an intake session.
    Retrieves records for both active and post-purged sessions.
    """
    record = delivery_service.get_delivery_status(session_id)
    if not record:
        raise MediKioskException(
            error_code="NOT_FOUND",
            message=f"No delivery record found for session '{session_id}'.",
            status_code=status.HTTP_404_NOT_FOUND
        )
    return {
        "session_id": session_id,
        "delivery": record.model_dump()
    }


@router.get("/{session_id}/integration/bundle")
def get_fhir_bundle_json(session_id: str):
    """
    Inspect the raw FHIR R4 Bundle in standard application/fhir+json format.
    """
    session = session_repo.get_session(session_id)
    if not session:
        raise MediKioskException(
            error_code="SESSION_NOT_FOUND",
            message=f"Intake session '{session_id}' not found.",
            status_code=status.HTTP_404_NOT_FOUND
        )

    bundle, _ = delivery_service.prepare_bundle(session)
    import json
    return Response(
        content=json.dumps(bundle.model_dump(by_alias=True), indent=2),
        media_type="application/fhir+json"
    )
