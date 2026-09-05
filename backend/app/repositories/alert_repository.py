from typing import Dict, List, Optional
from datetime import datetime
from app.models.alert import TriageAlertItem

class AlertRepository:
    """In-memory global store for hospital triage staff alerts."""
    def __init__(self):
        self._alerts: Dict[str, TriageAlertItem] = {}

    def add_alert(self, alert: TriageAlertItem) -> TriageAlertItem:
        self._alerts[alert.alert_id] = alert
        return alert

    def get_alert(self, alert_id: str) -> Optional[TriageAlertItem]:
        return self._alerts.get(alert_id)

    def list_alerts(self, facility_id: Optional[str] = None, status: Optional[str] = None) -> List[TriageAlertItem]:
        alerts = list(self._alerts.values())
        if facility_id:
            alerts = [a for a in alerts if a.facility_id == facility_id]
        if status:
            alerts = [a for a in alerts if a.status == status]
        # Return newest first
        return sorted(alerts, key=lambda x: x.triggered_at, reverse=True)

    def list_by_session(self, session_id: str) -> List[TriageAlertItem]:
        return [a for a in self._alerts.values() if a.session_id == session_id]

    def acknowledge_alert(self, alert_id: str, staff_id: str, action: str, notes: Optional[str] = None) -> Optional[TriageAlertItem]:
        alert = self._alerts.get(alert_id)
        if not alert:
            return None
        alert.status = "ACKNOWLEDGED"
        alert.acknowledged_by = staff_id
        alert.acknowledged_at = datetime.utcnow()
        alert.triage_notes = f"Action: {action}. Notes: {notes or 'None'}"
        return alert

alert_repo = AlertRepository()
