from fastapi import APIRouter
from app.api.endpoints import (
    sessions,
    consent_router,
    documents_router,
    alerts_router,
    ops_router,
    voice_router,
    integration_router
)

api_router = APIRouter()

# 1. Session & Intake Lifecycle, ABHA Auth, Summary & Questioning
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])

# 2. Granular Consent Scopes & Revocation (DPDP)
api_router.include_router(consent_router.router, prefix="/sessions", tags=["consent"])

# 3. Medical Document Upload & Staging
api_router.include_router(documents_router.router, prefix="/sessions", tags=["documents"])

# 4. Consented FHIR R4 Bundle Delivery, ABDM & HIS Integration (Module D)
api_router.include_router(integration_router.router, prefix="/sessions", tags=["integration"])

# 5. Voice Intake Engine & Accessibility Navigation (Module E)
api_router.include_router(voice_router.router, prefix="/voice", tags=["voice"])

# 6. Emergency Red-Flag Triage Queue
api_router.include_router(alerts_router.router, prefix="", tags=["alerts"])

# 7. System Operations, Liveness & Readiness Probes
api_router.include_router(ops_router.router, prefix="", tags=["operations"])
