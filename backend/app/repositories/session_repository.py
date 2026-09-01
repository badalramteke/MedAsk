from typing import Dict, Optional
from app.models.core import PatientDataObject

class SessionRepository:
    """
    Mock repository for Phase 1 to store PatientDataObject instances in memory.
    Will be replaced by a Redis/Postgres backed repository in future phases.
    """
    def __init__(self):
        self._store: Dict[str, PatientDataObject] = {}

    def get_session(self, session_id: str) -> Optional[PatientDataObject]:
        return self._store.get(session_id)

    def save_session(self, pdo: PatientDataObject) -> PatientDataObject:
        self._store[pdo.identity.session_id] = pdo
        return pdo

    def delete_session(self, session_id: str) -> bool:
        if session_id in self._store:
            del self._store[session_id]
            return True
        return False

# Global singleton for mock purposes
session_repo = SessionRepository()
