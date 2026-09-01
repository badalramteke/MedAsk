from fastapi import APIRouter
from app.api.endpoints import sessions, consent_router, documents_router, alerts_router, ops_router

api_router = APIRouter()

# 1. Session & Intake Lifecycle, ABHA Auth, Summary & Questioning
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])

# 2. Granular Consent Scopes & Revocation (DPDP)
api_router.include_router(consent_router.router, prefix="/sessions", tags=["consent"])

# 3. Medical Document Upload & Staging
api_router.include_router(documents_router.router, prefix="/sessions", tags=["documents"])

# 4. Emergency Red-Flag Triage Queue
api_router.include_router(alerts_router.router, prefix="", tags=["alerts"])

# 5. System Operations, Liveness & Readiness Probes
api_router.include_router(ops_router.router, prefix="", tags=["operations"])
