from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
from app.models.speech import SpeechRecognitionResult, SpeechSynthesisResult

class BaseSpeechAdapter(ABC):
    """
    Abstract Base Adapter defining the standard contract for all Speech (ASR & TTS) providers.
    Ensures provider-agnostic execution, capability checking, and safe fallbacks.
    """
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def transcribe(
        self, audio_bytes: bytes, audio_format: str = "webm", language: str = "hi"
    ) -> Tuple[bool, str, float, str]:
        """
        Transcribe audio bytes to text in the given language.
        Returns: (success, transcript, confidence, error_message)
        """
        pass

    @abstractmethod
    async def synthesize(
        self, text: str, language: str = "hi", gender: str = "female", audio_format: str = "wav"
    ) -> Tuple[bool, str, str]:
        """
        Synthesize text to audio.
        Returns: (success, audio_base64, error_message)
        """
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Verify provider availability, latency, and credentials."""
        pass
