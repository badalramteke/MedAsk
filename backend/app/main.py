from fastapi import FastAPI
from app.api.router import api_router

app = FastAPI(
    title="MediKiosk API",
    description="Core backend for the MediKiosk platform.",
    version="1.0.0"
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "medikiosk-core"}
