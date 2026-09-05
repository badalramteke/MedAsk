from fastapi import Request
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any

class MediKioskException(Exception):
    """
    Standardized application exception for MediKiosk clinical core.
    Maps to ERROR_CODES.md structured error responses.
    """
    def __init__(
        self,
        error_code: str,
        message: str,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None
    ):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)

async def medikiosk_exception_handler(request: Request, exc: MediKioskException):
    correlation_id = request.headers.get("X-Correlation-ID", "kiosk-unknown")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "message": exc.message,
            "correlation_id": correlation_id,
            "details": exc.details,
        },
    )
