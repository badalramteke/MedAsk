import os
import json
import time
import httpx
from typing import Dict, Any, Optional
from app.services.adapters.base import BaseModelAdapter
from app.models.ai import ModelTaskRequest, ModelTaskResponse, ModelCapability


class ColabMedGemmaAdapter(BaseModelAdapter):
    """
    Primary Provider Adapter for MedGemma 4B / 27B hosted on Google Colab GPU via FastAPI / vLLM gateway.
    """
    def __init__(self, base_url: Optional[str] = None):
        super().__init__(name="colab_medgemma")
        self._explicit_base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "MediKiosk-Backend/1.0",
            "ngrok-skip-browser-warning": "true",
        }

    @property
    def base_url(self) -> str:
        url = self._explicit_base_url or os.getenv("COLAB_MEDGEMMA_URL", "")
        return url.rstrip("/")

    async def health_check(self) -> Dict[str, Any]:
        if not self.base_url:
            return {"status": "unconfigured", "error": "COLAB_MEDGEMMA_URL not set"}
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(f"{self.base_url}/health", headers=self.headers)
                if res.status_code == 200:
                    return {"status": "online", "code": 200, "details": res.json()}
                return {"status": "degraded", "code": res.status_code}
        except Exception as e:
            return {"status": "offline", "error": str(e)}

    async def generate_structured(self, request: ModelTaskRequest, system_prompt: str) -> ModelTaskResponse:
        start_time = time.time()
        endpoint = f"{self.base_url}/api/v1/clinical-infer"
        payload = {
            "system_prompt": system_prompt,
            "user_prompt": request.untrusted_input,
            "temperature": 0.1,
            "max_tokens": 650,
        }

        timeout = float(os.getenv("MEDGEMMA_TIMEOUT_SECONDS", "5.0"))
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                res = await client.post(endpoint, json=payload, headers=self.headers)
                latency = round((time.time() - start_time) * 1000, 2)

                if res.status_code == 200:
                    data = res.json()
                    raw_text = data.get("result", "")
                    parsed_json = self._extract_json(raw_text)
                    return ModelTaskResponse(
                        success=True,
                        capability=request.capability,
                        provider_used=self.name,
                        model_name=data.get("model", "google/medgemma-1.5-4b-it"),
                        prompt_version=request.prompt_version,
                        latency_ms=latency,
                        confidence_score=0.95,
                        raw_response=raw_text,
                        structured_payload=parsed_json,
                    )
                else:
                    return ModelTaskResponse(
                        success=False,
                        capability=request.capability,
                        provider_used=self.name,
                        latency_ms=latency,
                        error_message=f"HTTP {res.status_code}: {res.text}",
                    )
        except Exception as e:
            latency = round((time.time() - start_time) * 1000, 2)
            return ModelTaskResponse(
                success=False,
                capability=request.capability,
                provider_used=self.name,
                latency_ms=latency,
                error_message=str(e),
            )

    async def generate_multimodal(self, request: ModelTaskRequest, system_prompt: str) -> ModelTaskResponse:
        start_time = time.time()
        endpoint = f"{self.base_url}/api/v1/multimodal-infer"
        payload = {
            "system_prompt": system_prompt,
            "user_prompt": request.untrusted_input,
            "image_base64": request.image_base64 or "",
            "temperature": 0.1,
            "max_tokens": 650,
        }

        timeout = float(os.getenv("MEDGEMMA_TIMEOUT_SECONDS", "5.0"))
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                res = await client.post(endpoint, json=payload, headers=self.headers)
                latency = round((time.time() - start_time) * 1000, 2)

                if res.status_code == 200:
                    data = res.json()
                    raw_text = data.get("result", "")
                    parsed_json = self._extract_json(raw_text)
                    return ModelTaskResponse(
                        success=True,
                        capability=request.capability,
                        provider_used=self.name,
                        model_name=data.get("model", "google/medgemma-1.5-4b-it"),
                        prompt_version=request.prompt_version,
                        latency_ms=latency,
                        confidence_score=0.92,
                        raw_response=raw_text,
                        structured_payload=parsed_json,
                    )
                else:
                    return ModelTaskResponse(
                        success=False,
                        capability=request.capability,
                        provider_used=self.name,
                        latency_ms=latency,
                        error_message=f"HTTP {res.status_code}: {res.text}",
                    )
        except Exception as e:
            latency = round((time.time() - start_time) * 1000, 2)
            return ModelTaskResponse(
                success=False,
                capability=request.capability,
                provider_used=self.name,
                latency_ms=latency,
                error_message=str(e),
            )

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Strip markdown json codeblocks if present and parse."""
        cleaned = text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        # Direct parse attempt
        try:
            return json.loads(cleaned)
        except Exception:
            pass

        # Regex fallback to extract outermost JSON object {...}
        import re
        match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except Exception:
                pass

        return {"raw_text": text}
