from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from typing import Optional, Any, Dict
import logging

logger = logging.getLogger("medikiosk.errors")

class ErrorResponse(BaseModel):
    error_code: str
    message: str
    correlation_id: str
    retry_guidance: Optional[str] = None
    details: Optional[Any] = None

class MediKioskException(Exception):
    """Base domain exception with standardized error code support."""
    def __init__(
        self,
        error_code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        retry_guidance: Optional[str] = None,
        details: Optional[Any] = None
    ):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.retry_guidance = retry_guidance
        self.details = details
        super().__init__(message)


def get_correlation_id(request: Request) -> str:
    return getattr(request.state, "correlation_id", "unknown-req-id")


async def medikiosk_exception_handler(request: Request, exc: MediKioskException) -> JSONResponse:
    correlation_id = get_correlation_id(request)
    logger.warning(f"MediKioskException [{exc.error_code}] on {request.url.path}: {exc.message} (Correlation: {correlation_id})")
    
    payload = ErrorResponse(
        error_code=exc.error_code,
        message=exc.message,
        correlation_id=correlation_id,
        retry_guidance=exc.retry_guidance,
        details=exc.details
    ).model_dump()
    
    return JSONResponse(status_code=exc.status_code, content=payload)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    correlation_id = get_correlation_id(request)
    
    # Map common HTTP status codes to stable error categories
    status_to_code = {
        400: "VALIDATION_FAILED",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "SESSION_NOT_FOUND" if "session" in request.url.path.lower() else "NOT_FOUND",
        409: "SESSION_CONFLICT",
        413: "DOCUMENT_REJECTED",
        415: "DOCUMENT_REJECTED",
        422: "VALIDATION_FAILED",
        429: "RATE_LIMITED",
        502: "PROCESSING_INVALID_OUTPUT",
        503: "PROCESSING_UNAVAILABLE",
    }
    
    code = status_to_code.get(exc.status_code, "INTERNAL_ERROR")
    logger.info(f"HTTPException [{code}] status {exc.status_code} on {request.url.path}: {exc.detail}")
    
    payload = ErrorResponse(
        error_code=code,
        message=str(exc.detail),
        correlation_id=correlation_id,
        retry_guidance="Check request parameters and try again."
    ).model_dump()
    
    return JSONResponse(status_code=exc.status_code, content=payload)


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    correlation_id = get_correlation_id(request)
    logger.info(f"Validation error on {request.url.path}: {exc.errors()} (Correlation: {correlation_id})")
    
    safe_errors = []
    for err in exc.errors():
        safe_errors.append({
            "field": " -> ".join(str(loc) for loc in err.get("loc", [])),
            "issue": err.get("msg", "Invalid field value")
        })
    
    payload = ErrorResponse(
        error_code="VALIDATION_FAILED",
        message="Request payload failed validation schema.",
        correlation_id=correlation_id,
        retry_guidance="Correct input fields according to schema and retry.",
        details=safe_errors
    ).model_dump()
    
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=payload)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    correlation_id = get_correlation_id(request)
    # Log the full exception internally for engineers/monitoring
    logger.error(f"Unhandled system exception on {request.url.path} (Correlation: {correlation_id}): {exc}", exc_info=True)
    
    # Return zero-leakage safe error to the client
    payload = ErrorResponse(
        error_code="INTERNAL_ERROR",
        message="An internal server error occurred. Please contact hospital technical support.",
        correlation_id=correlation_id,
        retry_guidance="Do not retry immediately; check system readiness or request assistance."
    ).model_dump()
    
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=payload)
