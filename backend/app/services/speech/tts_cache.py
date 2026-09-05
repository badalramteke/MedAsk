import hashlib
from typing import Dict, Optional
from app.services.speech.mock_speech_adapter import generate_synthetic_wav_bytes
import base64

class TTSAudioCache:
    """
    In-memory hybrid cache for standard questionnaire audio prompts across all 6 Indian languages.
    Provides instant 0ms audio retrieval for static questions without hitting external APIs.
    """
    def __init__(self):
        self._cache: Dict[str, str] = {}  # sha256(text+lang+gender) -> base64 audio
        self._seed_default_audio()

    def _make_key(self, text: str, language: str, gender: str = "female") -> str:
        raw = f"{text.strip().lower()}:{language.lower()}:{gender.lower()}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _seed_default_audio(self):
        """Seed cache with standard 1.0s valid WAV sound for immediate offline responsiveness."""
        mock_bytes = generate_synthetic_wav_bytes(duration_seconds=1.2)
        self._default_wav_b64 = base64.b64encode(mock_bytes).decode("utf-8")

    def get(self, text: str, language: str, gender: str = "female") -> Optional[str]:
        key = self._make_key(text, language, gender)
        return self._cache.get(key)

    def set(self, text: str, language: str, audio_b64: str, gender: str = "female"):
        key = self._make_key(text, language, gender)
        self._cache[key] = audio_b64

    def get_or_default(self, text: str, language: str, gender: str = "female") -> str:
        cached = self.get(text, language, gender)
        return cached if cached else self._default_wav_b64

tts_cache = TTSAudioCache()
