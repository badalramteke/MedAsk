import time
from typing import Dict, Tuple
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

class IdempotencyMemoryStore:
    """In-memory cache for response replay on duplicate idempotent requests."""
    def __init__(self, ttl_seconds: int = 120):
        self.ttl = ttl_seconds
        self.cache: Dict[str, Tuple[float, int, bytes, dict]] = {}

    def get(self, key: str):
        now = time.time()
        if key in self.cache:
            ts, status_code, body, headers = self.cache[key]
            if now - ts < self.ttl:
                return status_code, body, headers
            else:
                del self.cache[key]
        return None

    def set(self, key: str, status_code: int, body: bytes, headers: dict):
        self.cache[key] = (time.time(), status_code, body, headers)

idempotency_store = IdempotencyMemoryStore()

class IdempotencyMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle X-Idempotency-Key on mutating HTTP methods (POST, PATCH, DELETE).
    Returns cached response if key is seen within TTL, avoiding duplicate execution.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        idempotency_key = request.headers.get("X-Idempotency-Key")
        if not idempotency_key or request.method not in ("POST", "PATCH", "DELETE"):
            return await call_next(request)

        # Build compound key combining route path + idempotency key
        compound_key = f"{request.url.path}:{idempotency_key}"
        cached = idempotency_store.get(compound_key)
        if cached:
            status_code, body, headers = cached
            headers["X-Cache-Lookup"] = "HIT-IDEMPOTENT"
            return Response(content=body, status_code=status_code, headers=headers, media_type="application/json")

        # Execute downstream
        response = await call_next(request)
        
        # Only cache successful responses
        if 200 <= response.status_code < 300:
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
            
            headers_dict = dict(response.headers)
            idempotency_store.set(compound_key, response.status_code, response_body, headers_dict)
            return Response(content=response_body, status_code=response.status_code, headers=headers_dict, media_type=response.media_type)

        return response
