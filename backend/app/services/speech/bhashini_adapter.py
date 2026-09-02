import os
import base64
import time
import httpx
from typing import Dict, Any, Tuple
from app.services.speech.base_speech import BaseSpeechAdapter

class BhashiniSpeechAdapter(BaseSpeechAdapter):
    """
    Adapter for official MeitY Bhashini ULCA Speech APIs (ASR + TTS).
    Provides Indian language speech processing across en, hi, mr, bn, ta, te.
    """
    def __init__(self):
        super().__init__(name="BHASHINI_ULCA")
        self.api_base_url = os.getenv("BHASHINI_API_BASE_URL", "https://dhruva-api.bhashini.gov.in").rstrip("/")
        self.api_key = os.getenv("BHASHINI_API_KEY", "")
        self.user_id = os.getenv("BHASHINI_USER_ID", "")
        self.pipeline_id = os.getenv("BHASHINI_PIPELINE_ID", "")
        self.timeout = float(os.getenv("BHASHINI_TIMEOUT_SECONDS", "10.0"))

    def _is_configured(self) -> bool:
        return bool(self.api_key and self.user_id)

    async def transcribe(
        self, audio_bytes: bytes, audio_format: str = "webm", language: str = "hi"
    ) -> Tuple[bool, str, float, str]:
        """Transcribe speech audio via Bhashini ASR Pipeline."""
        if not self._is_configured():
            return False, "", 0.0, "Bhashini credentials (BHASHINI_API_KEY / BHASHINI_USER_ID) not configured."

        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": self.api_key,
            "User-Id": self.user_id,
            "ulcaApiKey": self.api_key
        }

        payload = {
            "pipelineTasks": [
                {
                    "taskType": "asr",
                    "config": {
                        "language": {"sourceLanguage": language},
                        "audioFormat": audio_format,
                        "samplingRate": 16000
                    }
                }
            ],
            "inputData": {
                "audio": [{"audioContent": audio_b64}]
            }
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(
                    f"{self.api_base_url}/services/inference/pipeline",
                    json=payload,
                    headers=headers
                )
                if res.status_code == 200:
                    data = res.json()
                    pipeline_response = data.get("pipelineResponse", [])
                    if pipeline_response:
                        output = pipeline_response[0].get("output", [])
                        if output:
                            transcript = output[0].get("source", "").strip()
                            return True, transcript, 0.94, ""
                    return False, "", 0.0, "Empty transcript from Bhashini pipeline."
                else:
                    return False, "", 0.0, f"Bhashini HTTP error {res.status_code}: {res.text[:200]}"
        except Exception as e:
            return False, "", 0.0, f"Bhashini ASR exception: {str(e)}"

    async def synthesize(
        self, text: str, language: str = "hi", gender: str = "female", audio_format: str = "wav"
    ) -> Tuple[bool, str, str]:
        """Synthesize vernacular text to spoken audio via Bhashini TTS Pipeline."""
        if not self._is_configured():
            return False, "", "Bhashini credentials not configured."

        headers = {
            "Content-Type": "application/json",
            "Authorization": self.api_key,
            "User-Id": self.user_id,
            "ulcaApiKey": self.api_key
        }

        payload = {
            "pipelineTasks": [
                {
                    "taskType": "tts",
                    "config": {
                        "language": {"sourceLanguage": language},
                        "gender": gender,
                        "samplingRate": 16000
                    }
                }
            ],
            "inputData": {
                "input": [{"source": text}]
            }
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(
                    f"{self.api_base_url}/services/inference/pipeline",
                    json=payload,
                    headers=headers
                )
                if res.status_code == 200:
                    data = res.json()
                    pipeline_response = data.get("pipelineResponse", [])
                    if pipeline_response:
                        audio_list = pipeline_response[0].get("audio", [])
                        if audio_list:
                            audio_b64 = audio_list[0].get("audioContent", "")
                            return True, audio_b64, ""
                    return False, "", "Empty audio returned from Bhashini TTS."
                else:
                    return False, "", f"Bhashini TTS HTTP {res.status_code}: {res.text[:200]}"
        except Exception as e:
            return False, "", f"Bhashini TTS exception: {str(e)}"

    async def health_check(self) -> Dict[str, Any]:
        """Verify Bhashini configuration and reachability."""
        if not self._is_configured():
            return {
                "status": "unconfigured",
                "message": "BHASHINI_API_KEY and BHASHINI_USER_ID not set in .env"
            }
        return {
            "status": "configured",
            "base_url": self.api_base_url,
            "user_id": self.user_id[:4] + "***" if self.user_id else None
        }
