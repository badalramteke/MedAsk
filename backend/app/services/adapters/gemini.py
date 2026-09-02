import os
import json
import time
import httpx
from typing import Dict, Any, Optional
from app.services.adapters.base import BaseModelAdapter
from app.models.ai import ModelTaskRequest, ModelTaskResponse


class GeminiAdapter(BaseModelAdapter):
    """
    Fallback Cloud Provider Adapter for Google Gemini Models.
    """
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(name="gemini")
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    async def health_check(self) -> Dict[str, Any]:
        if not self.api_key:
            return {"status": "unconfigured", "error": "GEMINI_API_KEY not set"}
        return {"status": "configured"}

    async def generate_structured(self, request: ModelTaskRequest, system_prompt: str) -> ModelTaskResponse:
        start_time = time.time()
        if not self.api_key:
            return ModelTaskResponse(
                success=False, capability=request.capability, provider_used=self.name, error_message="GEMINI_API_KEY missing"
            )
        endpoint = f"{self.base_url}/gemini-1.5-flash:generateContent?key={self.api_key}"
        payload = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"parts": [{"text": request.untrusted_input}]}],
            "generationConfig": {"temperature": 0.1, "response_mime_type": "application/json"}
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(endpoint, json=payload)
                latency = round((time.time() - start_time) * 1000, 2)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "{}")
                        return ModelTaskResponse(
                            success=True,
                            capability=request.capability,
                            provider_used=self.name,
                            model_name="gemini-1.5-flash",
                            prompt_version=request.prompt_version,
                            latency_ms=latency,
                            confidence_score=0.90,
                            raw_response=text,
                            structured_payload=json.loads(text) if text.startswith("{") else {"raw": text}
                        )
                return ModelTaskResponse(
                    success=False, capability=request.capability, provider_used=self.name, latency_ms=latency, error_message=f"HTTP {res.status_code}"
                )
        except Exception as e:
            return ModelTaskResponse(
                success=False, capability=request.capability, provider_used=self.name, latency_ms=round((time.time() - start_time) * 1000, 2), error_message=str(e)
            )

    async def generate_multimodal(self, request: ModelTaskRequest, system_prompt: str) -> ModelTaskResponse:
        return await self.generate_structured(request, system_prompt)
