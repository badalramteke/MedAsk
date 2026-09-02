import os
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.middleware.correlation import CorrelationIdMiddleware
from app.middleware.idempotency import IdempotencyMiddleware
from app.middleware.error_handler import (
    MediKioskException,
    medikiosk_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    unhandled_exception_handler
)

app = FastAPI(
    title="MediKiosk Clinical Intake API",
    description="AI-Powered Clinical History, Medical Document Digitization, and ABDM/FHIR Interoperability Platform.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 1. CORS Middleware
allowed_origins = os.getenv("MEDIKIOSK_ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in allowed_origins if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Correlation & Idempotency Middleware
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(IdempotencyMiddleware)

# 3. Standardized Error Handlers (conforming to docs/api/ERROR_CODES.md)
app.add_exception_handler(MediKioskException, medikiosk_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# 4. Master API v1 Router
app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["operations"])
def root_health():
    """Root level liveness probe."""
    return {"status": "ok", "service": "medikiosk-core", "version": "1.0.0"}
