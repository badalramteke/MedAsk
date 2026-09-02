import os
import base64
import httpx
from typing import Dict, Any, Tuple
from app.services.speech.base_speech import BaseSpeechAdapter

class GeminiAudioAdapter(BaseSpeechAdapter):
    """
    Online fallback speech adapter using Google Gemini 1.5 Flash Multimodal Audio.
    Transcribes audio clips into accurate Indian language text.
    """
    def __init__(self):
        super().__init__(name="GEMINI_AUDIO")
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.model_name = os.getenv("GEMINI_AUDIO_MODEL", "gemini-1.5-flash")
        self.endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent"
        self.timeout = float(os.getenv("GEMINI_AUDIO_TIMEOUT", "12.0"))

    def _is_configured(self) -> bool:
        return bool(self.api_key and not self.api_key.startswith("your_"))

    async def transcribe(
        self, audio_bytes: bytes, audio_format: str = "webm", language: str = "hi"
    ) -> Tuple[bool, str, float, str]:
        """Transcribe speech audio using Gemini 1.5 Flash."""
        if not self._is_configured():
            return False, "", 0.0, "GEMINI_API_KEY not configured for Gemini Audio fallback."

        mime_map = {
            "webm": "audio/webm",
            "wav": "audio/wav",
            "mp3": "audio/mp3",
            "ogg": "audio/ogg"
        }
        mime_type = mime_map.get(audio_format.lower(), "audio/wav")
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

        prompt = (
            f"You are a high-accuracy medical audio transcriber. "
            f"Transcribe the spoken speech in this audio clip accurately into text in language '{language}'. "
            f"Output ONLY the exact verbatim transcript. Do not add explanations or notes."
        )

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": mime_type,
                                "data": audio_b64
                            }
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.0,
                "maxOutputTokens": 256
            }
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(
                    f"{self.endpoint}?key={self.api_key}",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            transcript = parts[0].get("text", "").strip()
                            return True, transcript, 0.91, ""
                    return False, "", 0.0, "No transcript in Gemini response."
                else:
                    return False, "", 0.0, f"Gemini Audio HTTP {res.status_code}: {res.text[:200]}"
        except Exception as e:
            return False, "", 0.0, f"Gemini Audio exception: {str(e)}"

    async def synthesize(
        self, text: str, language: str = "hi", gender: str = "female", audio_format: str = "wav"
    ) -> Tuple[bool, str, str]:
        """Gemini generateContent is text/vision only; TTS fallback delegates to Mock/Local."""
        return False, "", "Gemini API does not directly serve standalone binary TTS audio."

    async def health_check(self) -> Dict[str, Any]:
        """Verify Gemini API key status."""
        return {
            "status": "online" if self._is_configured() else "unconfigured",
            "model": self.model_name
        }
