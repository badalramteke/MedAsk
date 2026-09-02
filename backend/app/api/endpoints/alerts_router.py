from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from app.models.alert import TriageAlertItem, AlertAcknowledgeRequest
from app.repositories.alert_repository import alert_repo
from app.repositories.session_repository import session_repo
from app.middleware.error_handler import MediKioskException

router = APIRouter()

@router.get("/alerts")
def get_global_triage_queue(
    facility_id: Optional[str] = Query(None, description="Filter by hospital facility ID"),
    status_filter: Optional[str] = Query(None, alias="status", description="TRIGGERED | ACKNOWLEDGED | RESOLVED")
):
    """
    Global emergency triage queue for hospital nursing desks and triage doctors.
    Lists active red flags across all kiosks in real-time, sorted newest first.
    """
    alerts = alert_repo.list_alerts(facility_id=facility_id, status=status_filter)
    return {
        "total_active_alerts": len(alerts),
        "alerts": [a.model_dump() for a in alerts]
    }


@router.get("/sessions/{session_id}/alerts")
def get_session_alerts(session_id: str):
    """Retrieve red-flag triage alerts triggered during a specific intake session."""
    session = session_repo.get_session(session_id)
    if not session:
        raise MediKioskException(
            error_code="SESSION_NOT_FOUND",
            message=f"Intake session '{session_id}' not found.",
            status_code=status.HTTP_404_NOT_FOUND
        )

    alerts = alert_repo.list_by_session(session_id)
    return {
        "session_id": session_id,
        "active_alerts_count": len(alerts),
        "alerts": [a.model_dump() for a in alerts]
    }


@router.post("/alerts/{alert_id}/acknowledge")
def acknowledge_triage_alert(alert_id: str, req: AlertAcknowledgeRequest):
    """
    Triage nurse or doctor acknowledges an emergency red-flag alert.
    Updates alert status to ACKNOWLEDGED with staff signature and triage notes.
    """
    updated = alert_repo.acknowledge_alert(
        alert_id=alert_id,
        staff_id=req.staff_id,
        action=req.triage_action,
        notes=req.notes
    )
    if not updated:
        raise MediKioskException(
            error_code="NOT_FOUND",
            message=f"Alert with ID '{alert_id}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND
        )

    return {
        "success": True,
        "alert_id": alert_id,
        "status": updated.status,
        "acknowledged_by": updated.acknowledged_by,
        "acknowledged_at": updated.acknowledged_at.isoformat(),
        "triage_notes": updated.triage_notes,
        "message": f"Triage alert acknowledged by staff member {req.staff_id}."
    }
