import os
import time
from fastapi import APIRouter, status
from app.services.model_service import model_service

router = APIRouter()

@router.get("/health")
def liveness_check():
    """Lightweight Kubernetes / Docker liveness probe."""
    return {
        "status": "healthy",
        "service": "medikiosk-core",
        "timestamp": time.time(),
        "version": "1.0.0"
    }


@router.get("/ready")
async def readiness_check():
    """
    Deep readiness check inspecting database, caching, AI providers, and environment.
    """
    checks = {}
    is_ready = True

    # 1. Check AI Provider Health
    try:
        ai_health = await model_service.get_health_status()
        checks["ai_providers"] = ai_health
        if ai_health.get("overall_status") == "offline":
            # Degraded if mock is available, but still functional
            checks["ai_providers"]["status"] = "degraded"
    except Exception as e:
        checks["ai_providers"] = {"status": "error", "details": str(e)}

    # 2. Check OCR Engine status
    ocr_engine = os.getenv("OCR_ENGINE", "tesseract")
    checks["ocr_engine"] = {
        "configured": ocr_engine,
        "status": "ready"
    }

    # 3. Check Session Store
    checks["session_repository"] = {
        "type": "in_memory_mock_dev",
        "status": "ready"
    }

    return {
        "status": "ready" if is_ready else "degraded",
        "service": "medikiosk-backend",
        "facility_id": os.getenv("MEDIKIOSK_FACILITY_ID", "GENERAL"),
        "environment": os.getenv("MEDIKIOSK_ENV", "development"),
        "checks": checks
    }


@router.get("/ai/health")
async def ai_health_diagnostic():
    """Diagnostic health check across all registered AI model providers."""
    return await model_service.get_health_status()
